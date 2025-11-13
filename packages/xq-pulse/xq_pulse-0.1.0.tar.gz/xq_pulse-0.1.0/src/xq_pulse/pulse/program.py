from __future__ import annotations

import textwrap

import numpy as np
import pint
from attrs import define, field, frozen, validators
from plotly import graph_objects as go

from xq_pulse.pulse.expression import Literal, Parameter
from xq_pulse.pulse.pulse import AcquisitionTarget, DelayPulse, ForLoopPulse, Pulse, SequencePulse, UnrolledPulse
from xq_pulse.util import unit


@frozen
class ParameterSweep:
    parameter: Parameter = field(validator=validators.instance_of(Parameter))
    index_parameter: Parameter = field(validator=validators.instance_of(Parameter))
    start: Literal = field(validator=validators.instance_of(pint.Quantity))
    stop: Literal = field(validator=validators.instance_of(pint.Quantity))
    step: Literal = field(validator=validators.instance_of(pint.Quantity))

    def __attrs_post_init__(self) -> None:
        parameter_unit = self.parameter.unit
        assert self.start.is_compatible_with(parameter_unit), (
            f"ParameterSweep start unit {self.start.units} is not compatible with parameter unit {parameter_unit}"
        )
        assert self.stop.is_compatible_with(parameter_unit), (
            f"ParameterSweep stop unit {self.stop.units} is not compatible with parameter unit {parameter_unit}"
        )
        assert self.step.is_compatible_with(parameter_unit), (
            f"ParameterSweep step unit {self.step.units} is not compatible with parameter unit {parameter_unit}"
        )
        assert self.index_parameter.unit.is_compatible_with(unit.dimensionless), (
            f"ParameterSweep index parameter unit {self.index_parameter.unit} is not dimensionless"
        )

    @property
    def values(self) -> np.ndarray:
        values = (
            np.arange(
                self.start.m,
                # Add a small epsilon to avoid the stop value being excluded due to floating point precision
                (self.stop + self.step * 1e-3).m_as(self.start.u),
                self.step.m_as(self.start.u),
            )
            * self.start.u
        )
        return values


@define
class PulseProgram:
    root: Pulse
    acquisition_targets: list[AcquisitionTarget] = field(factory=list)
    parameter_sweeps: list[ParameterSweep] = field(factory=list)

    def __repr__(self):
        body = ""
        body += f"acquisition_targets={self.acquisition_targets},"
        body += "\n"
        body += f"parameter_sweeps={self.parameter_sweeps},"
        body += "\n"
        body += f"root={self.root},"
        body = textwrap.indent(body, " " * 4)
        return f"""PulseProgram(
{body}
)"""

    def simplify(self) -> PulseProgram:
        return PulseProgram(
            root=self.root.simplify(),
            acquisition_targets=self.acquisition_targets,
            parameter_sweeps=self.parameter_sweeps,
        )

    def _unroll_parameter_sweeps(self) -> ForLoopPulse:
        """
        Turn each parameter sweep into a ForLoopPulse.
        """
        body: Pulse = self.root
        for sweep in self.parameter_sweeps:
            body = ForLoopPulse(
                start=sweep.start,
                stop=sweep.stop,
                step=sweep.step,
                loop_parameter=sweep.parameter,
                index_parameter=sweep.index_parameter,
                body=body,
            )
        return body

    @property
    def duration(self):
        return self._unroll_parameter_sweeps().duration

    def unroll(self) -> UnrolledPulse:
        """
        Unroll the program, including all parameter sweeps.
        """
        return self._unroll_parameter_sweeps().unroll()

    def plot(self, show=True) -> go.Figure | None:
        return self._unroll_parameter_sweeps().plot(show=show)

    def append(self, other: PulseProgram, *, gap: pint.Quantity = 0 * unit.s) -> PulseProgram:
        """Return a new program that runs `self`, waits `gap`, then runs `other`."""
        if other.parameter_sweeps:
            raise ValueError('Appending programs with parameter sweeps is not supported.')

        pulses: list[Pulse] = [self.root]
        if not isinstance(gap, pint.Quantity):
            raise TypeError('gap must be provided as a pint.Quantity')
        if not gap.is_compatible_with(unit.s):
            raise ValueError(f'gap duration must be in units of time, got {gap.units}')
        if gap.magnitude < 0:
            raise ValueError('gap duration must be non-negative.')
        if gap.magnitude > 0:
            pulses.append(DelayPulse(duration=gap))
        pulses.append(other.root)

        return PulseProgram(
            root=SequencePulse(pulses=tuple(pulses)),
            acquisition_targets=list(self.acquisition_targets),
            parameter_sweeps=list(self.parameter_sweeps),
        )
