from __future__ import annotations

import threading
from contextlib import contextmanager
from typing import Generator, get_args

import pint
from attrs import define, field

from xq_pulse.pulse.envelope import Envelope, SquareEnvelope
from xq_pulse.pulse.expression import Literal, Parameter, Parameterized
from xq_pulse.pulse.program import ParameterSweep, PulseProgram
from xq_pulse.pulse.pulse import (
    AcquisitionPulse,
    AcquisitionTarget,
    DelayPulse,
    DrivePulse,
    ForLoopPulse,
    LaserPulse,
    ParallelPulse,
    Pulse,
    SequencePulse,
)
from xq_pulse.util import unit

# Global context stack for managing pulse context
_context_stack = threading.local()
_PULSE_TYPES: tuple[type, ...] = tuple(get_args(Pulse))


def _get_context_stack() -> list[PulseContext]:
    """Get the current context stack, initializing if needed."""
    if not hasattr(_context_stack, "stack"):
        _context_stack.stack = []
    return _context_stack.stack


def _push_context(context: PulseContext) -> None:
    """Push a context onto the stack."""
    _get_context_stack().append(context)


def _pop_context() -> PulseContext:
    """Pop and return the top context from the stack."""
    stack = _get_context_stack()
    if not stack:
        raise RuntimeError("No context available on stack")
    return stack.pop()


def _get_current_context() -> PulseContext:
    """Get the current context without removing it from the stack."""
    stack = _get_context_stack()
    if not stack:
        raise RuntimeError("No context available on stack")
    return stack[-1]


def _get_current_program() -> PulseProgram | None:
    if not hasattr(_context_stack, "program"):
        _context_stack.program = None
    return _context_stack.program


def _set_current_program(program: PulseProgram | None) -> None:
    _context_stack.program = program


def ensure_quantity(value: Literal | int | float) -> Literal:
    """Return the value as a pint quantity, coercing bare numbers to dimensionless."""
    if isinstance(value, pint.Quantity):
        return value
    if isinstance(value, (int, float)):
        return value * unit.dimensionless
    raise AssertionError(f"Expected pint.Quantity but received {type(value).__name__}")


def normalize_expression(value: Literal | Parameter) -> Literal | Parameter:
    """Convert literal inputs to quantities while allowing other expressions to pass through."""
    if isinstance(value, Parameterized):
        return value
    return ensure_quantity(value)


@define
class PulseContext:
    """Simple pulse context that collects pulses."""

    pulses: list[Pulse] = field(factory=list)

    def add_pulse(self, pulse: Pulse) -> None:
        """Add a pulse to this context."""
        self.pulses.append(pulse)


@contextmanager
def pulse_program() -> Generator[PulseProgram, None, None]:
    """Main context manager for creating a pulse program."""
    assert len(_get_context_stack()) == 0, (
        f"pulse_program cannot be nested in other DSL contexts, there were {len(_get_context_stack())} entries above it."
    )
    assert _get_current_program() is None, (
        f"There was already a pulse_program context {_get_current_program()} when pulse_program was called."
    )

    context = PulseContext()
    _push_context(context)
    dummy_pulse = DelayPulse(duration=1 * unit.ns)
    program = PulseProgram(root=dummy_pulse)
    _set_current_program(program)
    try:
        yield program
    finally:
        _pop_context()
        _set_current_program(None)
        program.root = SequencePulse(pulses=tuple(context.pulses))

        assert len(_get_context_stack()) == 0, (
            f"DSL context stack was not empty after pulse_program body. {len(_get_context_stack())} elements left."
        )
        assert len(context.pulses) > 0, "No pulses defined in the program context"


@contextmanager
def parameter_sweep(start: Literal, stop: Literal, step: Literal):
    assert len(_get_context_stack()) == 1, "Sweeps must be declared before any pulses are added to the program"
    program = _get_current_program()
    assert program is not None, "No program available in current context"
    start_q = ensure_quantity(start)
    stop_q = ensure_quantity(stop)
    step_q = ensure_quantity(step)
    sweep = ParameterSweep(
        parameter=Parameter(name="sweep_param", unit=start_q.units),
        index_parameter=Parameter(name="sweep_idx", unit=unit.dimensionless),
        start=start_q,
        stop=stop_q,
        step=step_q,
    )
    MAX_SWEEP_ELEMENTS = 10_000
    assert len(sweep.values) < MAX_SWEEP_ELEMENTS, (
        f"Failed to create parameter sweep from {start_q:.2f#~P} to {stop_q:.2f#~P} in steps of {step_q:.2f#~P}. Sweep would contain {len(sweep.values):,d} elements, this is too long. Maximum is {MAX_SWEEP_ELEMENTS:,d}."
    )
    program.parameter_sweeps.append(sweep)
    yield (sweep.index_parameter, sweep.parameter)


@contextmanager
def parallel():
    """Context manager for parallel pulse execution."""
    context = PulseContext()
    _push_context(context)
    try:
        yield
    finally:
        _pop_context()
        parallel_pulse = ParallelPulse(pulses=tuple(context.pulses))
        parent_context = _get_current_context()
        parent_context.add_pulse(parallel_pulse)


@contextmanager
def sequence():
    """Context manager for sequence pulse execution."""
    context = PulseContext()
    _push_context(context)
    try:
        yield
    finally:
        _pop_context()
        sequence_pulse = SequencePulse(pulses=tuple(context.pulses))
        parent_context = _get_current_context()
        parent_context.add_pulse(sequence_pulse)


@contextmanager
def for_idx(start: Literal, stop: Literal, step: Literal):
    """Context manager for loop execution with index and frequency parameters."""
    start_q = ensure_quantity(start)
    stop_q = ensure_quantity(stop)
    step_q = ensure_quantity(step)
    assert start_q.is_compatible_with(stop_q) and start_q.is_compatible_with(step_q), (
        "start, stop, and step must have compatible units"
    )

    loop_param = Parameter(name="freq", unit=start_q.units)
    index_param = Parameter(name="i", unit=unit.dimensionless)

    context = PulseContext()
    _push_context(context)
    try:
        yield (index_param, loop_param)  # Expose the parameters to the loop body
    finally:
        _pop_context()
        body = SequencePulse(pulses=tuple(context.pulses))
        loop_pulse = ForLoopPulse(
            start=start_q,
            stop=stop_q,
            step=step_q,
            loop_parameter=loop_param,
            index_parameter=index_param,
            body=body,
        )
        parent_context = _get_current_context()
        parent_context.add_pulse(loop_pulse)


def drive(
    duration: Literal | Parameter,
    frequency: Literal | Parameter,
    amplitude: Literal | Parameter,
    phase: Literal | Parameter = 0 * unit.rad,
    envelope: Envelope | None = None,
) -> None:
    """Create a drive pulse and add it to the current context."""
    pulse = DrivePulse(
        duration=normalize_expression(duration),
        frequency=normalize_expression(frequency),
        amplitude=normalize_expression(amplitude),
        phase=normalize_expression(phase),
        envelope=envelope if envelope is not None else SquareEnvelope(),
    )
    _get_current_context().add_pulse(pulse)


def laser(
    duration: Literal | Parameter,
    wavelength: Literal | Parameter,
    power: Literal | Parameter,
) -> None:
    """Create a laser pulse and add it to the current context."""
    pulse = LaserPulse(
        duration=normalize_expression(duration),
        wavelength=normalize_expression(wavelength),
        power=normalize_expression(power),
    )
    _get_current_context().add_pulse(pulse)


def acquisition_target(name: str, bins: int) -> AcquisitionTarget:
    """Create an acquisition target and add it to the current program."""
    target = AcquisitionTarget(name=name, bins=bins)
    program = _get_current_program()
    assert program is not None, "No program available in current context"
    program.acquisition_targets.append(target)
    return target


def acquire(duration: Literal | Parameter, target: AcquisitionTarget, bin: Literal | Parameter) -> None:
    """Create an acquisition pulse and add it to the current context."""
    pulse = AcquisitionPulse(
        duration=normalize_expression(duration),
        target=target,
        bin=normalize_expression(bin),
    )
    _get_current_context().add_pulse(pulse)


def delay(duration: Literal | Parameter) -> None:
    """Create a delay pulse and add it to the current context."""
    pulse = DelayPulse(duration=normalize_expression(duration))
    _get_current_context().add_pulse(pulse)


def pulse(pulse_obj: Pulse) -> None:
    """Add an existing pulse instance to the current context."""
    if not isinstance(pulse_obj, _PULSE_TYPES):
        raise TypeError(f"Expected Pulse instance, received {type(pulse_obj).__name__}")
    _get_current_context().add_pulse(pulse_obj)
