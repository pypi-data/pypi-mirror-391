from __future__ import annotations

import textwrap
from abc import ABC, abstractmethod
from collections import ChainMap
from typing import TYPE_CHECKING, Iterator, Optional

import numpy as np
import pint
from attrs import Factory, field, frozen, validators
from frozendict import frozendict
from intervaltree import Interval, IntervalTree
from plotly import graph_objects as go
from typing_extensions import assert_never, override

from xq_pulse.pulse import expression
from xq_pulse.pulse.channel import Channel
from xq_pulse.pulse.envelope import Envelope, SquareEnvelope
from xq_pulse.pulse.expression import (
    Expression,
    ExpressionUnitValidator,
    Literal,
    Parameter,
    Parameterized,
    bind,
    eval_expression,
    simplify,
)
from xq_pulse.util import unit, units

if TYPE_CHECKING:
    from xq_pulse.pulse.parameter import Binding


class ActivePulseIntervals:
    _intervals: IntervalTree

    def __init__(self, unrolled_pulse: UnrolledPulse):
        """
        Break the sequence up at points where the active pulses change.

        """
        intervals = unrolled_pulse.intervals.copy()
        intervals.split_overlaps()
        intervals.merge_overlaps(
            data_reducer=lambda old, new: (*old, new),
            data_initializer=tuple(),
        )
        self._intervals = intervals

    def __getitem__(self, key: pint.Quantity) -> set[LeafPulse]:
        """
        Get a tuple of the active pulses at a given time.
        """
        assert isinstance(key, pint.Quantity), f"Key {key} is not a Quantity"
        assert key.is_compatible_with(unit.s), f"Key {key} is not a time unit but {key.u}"
        intervals_at_time: Iterator[Interval] = self._intervals[key]
        assert len(intervals_at_time) == 1, f"Expected 1 interval at time {key} but got {len(intervals_at_time)}"
        single_interval = next(iter(intervals_at_time))
        assert isinstance(single_interval, Interval), f"Expected an Interval but got {type(single_interval)}"
        assert isinstance(single_interval.data, tuple), (
            f"Expected a tuple of pulses but got {type(single_interval.data)}"
        )

        return set(iter(single_interval.data))

    def __len__(self) -> int:
        return len(self._intervals)

    def __iter__(self) -> Iterator[tuple[pint.Quantity, set[LeafPulse]]]:
        for interval in sorted(self._intervals, key=lambda x: x.begin):
            yield (
                interval.end - interval.begin,
                set(pulse for pulse in interval.data if not isinstance(pulse, DelayPulse)),
            )

    def __repr__(self) -> str:
        body = "\n".join(f"  {duration}: {pulses}" for duration, pulses in self)
        return f"ActivePulseIntervals(\n{body}\n)"


@frozen
class UnrolledPulse:
    """
    Aggregates the result of unrolling a pulse tree.
    """

    intervals: IntervalTree
    source_by_unrolled: frozendict[int, Pulse]
    unrolled_by_source: frozendict[int, tuple[LeafPulse]]

    @classmethod
    def from_pulse(cls, pulse: LeafPulse, source: Pulse) -> UnrolledPulse:
        """Create an UnrolledPulse from a single pulse and its source."""
        duration: pint.Quantity = units.round_time(eval_expression(pulse.duration))
        assert isinstance(duration, pint.Quantity), (
            f"Evaluating the pulse duration did not yield a Quantity but {type(duration).__name__}: {duration}"
        )
        assert duration.is_compatible_with(unit.s), f"Pulse duration is not a time unit but {duration.u}"
        return cls(
            intervals=IntervalTree([Interval(0 * unit.s, duration, pulse)]),
            source_by_unrolled={id(pulse): source},
            unrolled_by_source={id(source): (pulse,)},
        )

    @classmethod
    def empty(cls) -> UnrolledPulse:
        return cls(
            intervals=IntervalTree(),
            source_by_unrolled=frozendict(),
            unrolled_by_source=frozendict(),
        )

    @property
    def pulse_starts(self) -> list[pint.Quantity]:
        return sorted(set([interval.begin for interval in self.intervals]))

    @property
    def pulse_ends(self) -> list[pint.Quantity]:
        return [interval.end for interval in self.intervals]

    @property
    def unrolled_pulses(self) -> list[LeafPulse]:
        return [interval.data for interval in self.intervals]

    @property
    def source_pulses(self) -> list[Pulse]:
        return list(self.source_by_unrolled.values())

    def __getitem__(self, key: pint.Quantity) -> set[LeafPulse]:
        return set([interval.data for interval in self.intervals[key]])

    def append(self, other: UnrolledPulse) -> UnrolledPulse:
        """Append two UnrolledPulses where the other occurs after this one (self)."""
        self_duration = self.intervals.end()
        if isinstance(self_duration, int) and self_duration == 0:
            self_duration = 0 * unit.s
        self_duration = units.round_time(self_duration)

        other_intervals_shifted = IntervalTree(
            [
                Interval(
                    begin=units.round_time(interval.begin + self_duration),
                    end=units.round_time(interval.end + self_duration),
                    data=interval.data,
                )
                for interval in other.intervals
            ]
        )
        return UnrolledPulse(
            intervals=self.intervals | other_intervals_shifted,
            source_by_unrolled=self.source_by_unrolled | other.source_by_unrolled,
            unrolled_by_source=frozendict(
                {
                    source_id: (
                        *self.unrolled_by_source.get(source_id, ()),
                        *other.unrolled_by_source.get(source_id, ()),
                    )
                    for source_id in set(self.unrolled_by_source.keys() | other.unrolled_by_source.keys())
                }
            ),
        )

    def merge(self, other: UnrolledPulse) -> UnrolledPulse:
        """Merge two UnrolledPulses which start at the same time."""
        return UnrolledPulse(
            intervals=self.intervals | other.intervals,
            source_by_unrolled=self.source_by_unrolled | other.source_by_unrolled,
            unrolled_by_source=frozendict(
                {
                    source_id: (
                        *self.unrolled_by_source.get(source_id, ()),
                        *other.unrolled_by_source.get(source_id, ()),
                    )
                    for source_id in set(self.unrolled_by_source.keys() | other.unrolled_by_source.keys())
                }
            ),
        )


@frozen
class AnyPulse(ABC, Parameterized):
    """
    Abstract base class for all pulses.
    Only use this for inheritance.
    For type annotations, use Pulse, which is a union type and supports compile time exhaustiveness checking.
    """

    duration: Expression = field(
        repr=str,
        validator=validators.or_(
            ExpressionUnitValidator(unit.seconds),
            validators.and_(
                units.UnitValidator(unit.seconds),
                validators.ge(1 * unit.ns),
                validators.le(1000 * unit.us),  # Longer pulses are probably unintentional
            ),
        ),
    )

    @property
    def channels(self) -> frozenset[Channel]:
        """
        Recursively collect all hardware channels used by this pulse and its descendants.
        Default for leaves without explicit channel assignment is empty.
        """
        return frozenset()

    @abstractmethod
    def bind(self, binding: Binding, *, source_map: Optional[dict[int, Pulse]] = None) -> Pulse:
        """
        Recursively bind Parameters in the pulse tree to literal values.
        Returns a new pulse with all bound Parameters replaced by their respective values.

        Optionally, a source_map can be provided in which id(bound pulse) -> source pulse is is stored.
        """
        ...

    @abstractmethod
    def unroll(self) -> UnrolledPulse:
        """
        Recursively unroll the pulse tree into individual leaf pulses.
        Returns an UnrolledPulse object containing all unrolling information.
        """
        ...

    @abstractmethod
    def apply_channel_mapping(self, mapping: dict[int, Channel]) -> "Pulse":
        """
        Return a new pulse with channel mappings applied according to mapping from abstract leaf id to Channel.
        Implemented by each concrete pulse type.
        """
        ...

    def plot(self, show=True) -> go.Figure | None:
        container_padding = 0.01
        label_height = 0.015
        height_px = 400
        fig = go.Figure()

        def height(pulse):
            match pulse:
                case DelayPulse():
                    return 0.1
                case ChannelMappedPulse():
                    return height(pulse.pulse) + label_height + container_padding
                case LaserPulse() | DrivePulse() | AcquisitionPulse():
                    return 0.1
                case SequencePulse():
                    return max((height(sp) for sp in pulse.pulses), default=0.0) + label_height + container_padding
                case ParallelPulse():
                    return sum(height(sp) for sp in pulse.pulses) + label_height + container_padding * len(pulse.pulses)
                case ForLoopPulse():
                    return (
                        max((height(iterp) for iterp in pulse.iterations()), default=0.0)
                        + label_height
                        + container_padding
                    )
                case _:
                    raise AssertionError(f"Got unknown pulse type {type(pulse)}")

        def add_outline(x0, x1, y0, y1, line):
            fig.add_shape(
                type="rect",
                x0=x0,
                x1=x1,
                y0=y0,
                y1=y1,
                fillcolor="rgba(0,0,0,0)",
                line=dict(color=line, dash="dot", width=1),
            )

        def add_label(x, y, text):
            fig.add_annotation(
                x=x,
                y=y,
                xanchor="left",
                yanchor="top",
                text=text.replace("\n", "<br>"),
                showarrow=False,
            )

        def add_bar(x0, width, y0, h, fill, line, text, insidetextanchor: str = "middle"):
            fig.add_trace(
                go.Bar(
                    orientation="h",
                    x=[width],
                    base=[x0],
                    y=[y0 + h / 2.0],
                    width=[h],
                    marker=dict(color=fill, line=dict(color=line, width=1)),
                    text=[text],
                    textposition="inside",
                    insidetextanchor=insidetextanchor,
                    textfont=dict(color="black"),
                    hoverinfo="skip",
                    cliponaxis=True,
                )
            )

        def add_envelope_trace(pulse: Pulse, x0: float, y0: float, width: float, height: float, color: str):
            envelope = getattr(pulse, "envelope", None)
            if not isinstance(envelope, Envelope):
                return
            tau, values = envelope.sample(num_samples=121)
            if np.allclose(values, values[0]):
                return
            abs_max = np.max(np.abs(values))
            if abs_max == 0:
                return
            y_center = y0 + height / 2.0
            y_points = y_center + (values / abs_max) * (height / 2.0)
            x_points = x0 + tau * width
            fig.add_trace(
                go.Scatter(
                    x=x_points,
                    y=y_points,
                    mode="lines",
                    line=dict(color=color, width=2),
                    hoverinfo="skip",
                    showlegend=False,
                )
            )

        def draw(pulse: Pulse, x: float, y: float):
            match pulse:
                case DelayPulse():
                    w = eval_expression(pulse.duration).m_as(unit.us)
                    h = height(pulse)
                    add_bar(
                        x,
                        w,
                        y,
                        h,
                        "lightgray",
                        "gray",
                        f"Delay ({eval_expression(pulse.duration):.3g~#C})",
                    )
                case ChannelMappedPulse():
                    # Draw wrapped pulse inside a dotted container with a label
                    h = height(pulse)
                    total = eval_expression(pulse.duration)
                    total_us = total.m_as(unit.us)
                    # Draw child
                    draw(pulse.pulse, x, y)
                    # Outline and in-box label
                    add_outline(x, x + total_us, y, y + h, "gray")
                    label_h = label_height
                    add_bar(
                        x,
                        total_us,
                        y + h - label_h,
                        label_h,
                        "rgba(0,0,0,0)",
                        "rgba(0,0,0,0)",
                        f"Channel: {pulse.channel.name}",
                        insidetextanchor="start",
                    )
                    return
                case LaserPulse():
                    w = eval_expression(pulse.duration).m_as(unit.us)
                    h = height(pulse)
                    add_bar(
                        x,
                        w,
                        y,
                        h,
                        "lightgreen",
                        "green",
                        f"Laser ({eval_expression(pulse.duration):.3g~#C})<br>"
                        f"λ = {eval_expression(pulse.wavelength):.3g~#C}<br>"
                        f"power = {eval_expression(pulse.power):.3g~#C}",
                    )
                    add_envelope_trace(pulse, x, y, w, h, "green")
                case DrivePulse():
                    w = eval_expression(pulse.duration).m_as(unit.us)
                    h = height(pulse)
                    add_bar(
                        x,
                        w,
                        y,
                        h,
                        "pink",
                        "red",
                        f"Drive ({eval_expression(pulse.duration):.3g~#C})<br>"
                        f"freq = {eval_expression(pulse.frequency):.3g~#C}<br>"
                        f"amp = {eval_expression(pulse.amplitude):.3g~#C}<br>"
                        f"phase = {eval_expression(pulse.phase):.3g~#C}",
                    )
                    add_envelope_trace(pulse, x, y, w, h, "red")
                case AcquisitionPulse():
                    w = eval_expression(pulse.duration).m_as(unit.us)
                    h = height(pulse)
                    add_bar(
                        x,
                        w,
                        y,
                        h,
                        "lightblue",
                        "blue",
                        f"Acq ({eval_expression(pulse.duration):.3g~#C})<br>"
                        f"target = {pulse.target}<br>"
                        f"bin = {eval_expression(pulse.bin):.3g~#C}",
                    )
                case SequencePulse():
                    h = height(pulse)
                    total = eval_expression(pulse.duration)
                    total_us = total.m_as(unit.us)
                    # Draw children
                    t = x
                    for sub in pulse.pulses:
                        sub_w = eval_expression(sub.duration).m_as(unit.us)
                        draw(sub, t, y)
                        t += sub_w
                    # Outline and in-box label
                    add_outline(x, x + total_us, y, y + h, "gray")
                    label_h = label_height
                    add_bar(
                        x,
                        total_us,
                        y + h - label_h,
                        label_h,
                        "rgba(0,0,0,0)",
                        "rgba(0,0,0,0)",
                        f"Sequence ({total:.3g~#C})<br>",
                        insidetextanchor="start",
                    )
                case ParallelPulse():
                    h = height(pulse)
                    total = eval_expression(pulse.duration)
                    total_us = total.m_as(unit.us)
                    add_outline(x, x + total_us, y, y + h, "gray")
                    label_h = label_height
                    add_bar(
                        x,
                        total_us,
                        y + h - label_h,
                        label_h,
                        "rgba(0,0,0,0)",
                        "rgba(0,0,0,0)",
                        f"Parallel ({total:.3g~#C})",
                        insidetextanchor="start",
                    )
                    yy = y + container_padding
                    for sub in pulse.pulses:
                        draw(sub, x, yy)
                        yy += height(sub) + container_padding
                case ForLoopPulse():
                    h = height(pulse)
                    total = eval_expression(pulse.duration)
                    total_us = total.m_as(unit.us)
                    add_outline(x, x + total_us, y, y + h, "gray")
                    label_h = label_height
                    add_bar(
                        x,
                        total_us,
                        y + h - label_h,
                        label_h,
                        "rgba(0,0,0,0)",
                        "rgba(0,0,0,0)",
                        f"ForLoop ({total:.3g~#C})",
                        insidetextanchor="start",
                    )
                    t = x
                    for iteration in pulse.iterations():
                        w = eval_expression(iteration.duration).m_as(unit.us)
                        draw(iteration, t, y)
                        t += w
                case _:
                    assert_never(pulse)

        draw(self, 0.0, 0.0)

        total_us = eval_expression(self.duration).m_as(unit.us)
        total_h = height(self)

        fig.update_xaxes(
            title_text="Time [µs]",
            range=[0, total_us],
            showgrid=True,
            zeroline=False,
            showticklabels=True,
            tick0=0,
            dtick=1,
        )
        fig.update_yaxes(
            type="linear",
            range=[0, total_h + 0.05],
            showgrid=False,
            zeroline=True,
            showticklabels=False,
            fixedrange=True,
        )
        fig.update_layout(
            height=height_px,
            margin=dict(l=30, r=10, t=10, b=30),
            template="plotly_white",
            dragmode="pan",
            barmode="overlay",
            transition=dict(duration=0),
            uniformtext=dict(mode="hide", minsize=9),
            showlegend=False,
        )
        if show:
            fig.show(config={"scrollZoom": True})
        else:
            return fig


@frozen
class DelayPulse(AnyPulse):
    def bind(self, binding: Binding, *, source_map: Optional[dict[int, Pulse]] = None) -> DelayPulse:
        result = DelayPulse(duration=bind(self.duration, binding))
        if source_map is not None:
            source_map[id(result)] = self
        return result

    def unroll(self) -> UnrolledPulse:
        return UnrolledPulse.from_pulse(self, self)

    def apply_channel_mapping(self, mapping: dict[int, Channel]) -> "Pulse":
        return self

    @property
    def parameters(self) -> frozenset[Parameter]:
        return frozenset(
            {
                *({self.duration} if isinstance(self.duration, Parameter) else {}),
            }
        )

    @override
    def simplify(self) -> LeafPulse:
        return DelayPulse(duration=simplify(self.duration))


@frozen
class LaserPulse(AnyPulse):
    wavelength: Expression = field(
        repr=str,
        validator=validators.or_(
            ExpressionUnitValidator(unit.meter),
            validators.and_(
                units.UnitValidator(unit.meter),
                validators.gt(400 * unit.nm),
                validators.lt(1000 * unit.nm),
            ),
        ),
    )
    power: Expression = field(
        repr=str,
        validator=validators.or_(
            ExpressionUnitValidator(unit.watt),
            validators.and_(
                units.UnitValidator(unit.watt),
                validators.gt(0 * unit.mW),
                validators.lt(500 * unit.mW),  # Higher powers are probably unintentional
            ),
        ),
    )

    def bind(self, binding: Binding, *, source_map: Optional[dict[int, Pulse]] = None) -> LaserPulse:
        result = LaserPulse(
            duration=bind(self.duration, binding),
            wavelength=bind(self.wavelength, binding),
            power=bind(self.power, binding),
        )
        if source_map is not None:
            source_map[id(result)] = self
        return result

    def unroll(self) -> UnrolledPulse:
        return UnrolledPulse.from_pulse(self, self)

    def apply_channel_mapping(self, mapping: dict[int, Channel]) -> "Pulse":
        ch = mapping.get(id(self))
        if ch is None:
            return self
        return ChannelMappedPulse(pulse=self, channel=ch)

    @property
    def parameters(self) -> frozenset[Parameter]:
        params: set[Parameter] = set()
        for expr in (self.duration, self.wavelength, self.power):
            if isinstance(expr, Parameter):
                params.add(expr)
            elif isinstance(expr, Parameterized):
                params.update(expr.parameters)
        return frozenset(params)

    @override
    def simplify(self) -> LeafPulse:
        return LaserPulse(
            duration=simplify(self.duration),
            wavelength=simplify(self.wavelength),
            power=simplify(self.power),
        )


@frozen
class DrivePulse(AnyPulse):
    amplitude: Expression = field(
        repr=str,
        validator=validators.or_(
            ExpressionUnitValidator(unit.T),
            validators.and_(
                units.UnitValidator(unit.T),
                validators.gt(0 * unit.T),
                validators.lt(1 * unit.mT),  # Higher amplitudes are probably unintentional
            ),
        ),
    )
    frequency: Expression = field(
        repr=str,
        validator=validators.or_(
            ExpressionUnitValidator(unit.Hz),
            validators.and_(
                units.UnitValidator(unit.Hz),
                validators.gt(0 * unit.Hz),
                validators.lt(20 * unit.GHz),  # Higher frequencies are probably unintentional
            ),
        ),
    )
    phase: Expression = field(
        converter=lambda x: x % (2 * np.pi) if isinstance(x, pint.Quantity) else x,
        repr=str,
        validator=validators.or_(
            ExpressionUnitValidator(unit.rad),
            validators.and_(
                units.UnitValidator(unit.rad),
                validators.ge(0 * unit.rad),
                validators.lt(2 * np.pi * unit.rad),
            ),
        ),
    )
    envelope: Envelope = field(
        factory=SquareEnvelope,
        validator=validators.instance_of(Envelope),
        repr=False,
    )

    def bind(self, binding: Binding, *, source_map: Optional[dict[int, Pulse]] = None) -> DrivePulse:
        result = DrivePulse(
            duration=bind(self.duration, binding),
            amplitude=bind(self.amplitude, binding),
            frequency=bind(self.frequency, binding),
            phase=bind(self.phase, binding),
            envelope=self.envelope,
        )
        if source_map is not None:
            source_map[id(result)] = self
        return result

    def unroll(self) -> UnrolledPulse:
        return UnrolledPulse.from_pulse(self, self)

    def apply_channel_mapping(self, mapping: dict[int, Channel]) -> "Pulse":
        ch = mapping.get(id(self))
        if ch is None:
            return self
        return ChannelMappedPulse(pulse=self, channel=ch)

    @property
    def parameters(self) -> frozenset[Parameter]:
        params: set[Parameter] = set()
        for expr in (self.duration, self.amplitude, self.frequency, self.phase):
            if isinstance(expr, Parameter):
                params.add(expr)
            elif isinstance(expr, Parameterized):
                params.update(expr.parameters)
        return frozenset(params)

    @override
    def simplify(self) -> LeafPulse:
        return DrivePulse(
            duration=simplify(self.duration),
            amplitude=simplify(self.amplitude),
            frequency=simplify(self.frequency),
            phase=simplify(self.phase),
            envelope=self.envelope,
        )


@frozen
class AcquisitionTarget:
    name: str
    bins: int


@frozen
class AcquisitionPulse(AnyPulse):
    target: AcquisitionTarget
    bin: Expression = field(
        repr=str,
        validator=validators.or_(
            ExpressionUnitValidator(unit.dimensionless),
            validators.and_(
                units.UnitValidator(unit.dimensionless),
                validators.ge(0 * unit.dimensionless),
            ),
        ),
    )

    def bind(self, binding: Binding, *, source_map: Optional[dict[int, Pulse]] = None) -> AcquisitionPulse:
        result = AcquisitionPulse(
            duration=bind(self.duration, binding),
            target=self.target,
            bin=bind(self.bin, binding),
        )
        if source_map is not None:
            source_map[id(result)] = self
        return result

    def unroll(self) -> UnrolledPulse:
        return UnrolledPulse.from_pulse(self, self)

    def apply_channel_mapping(self, mapping: dict[int, Channel]) -> "Pulse":
        ch = mapping.get(id(self))
        if ch is None:
            return self
        return ChannelMappedPulse(pulse=self, channel=ch)

    @property
    def parameters(self) -> frozenset[Parameter]:
        return frozenset(
            {
                *({self.duration} if isinstance(self.duration, Parameter) else {}),
                *({self.bin} if isinstance(self.bin, Parameter) else {}),
            }
        )

    @override
    def simplify(self) -> LeafPulse:
        return AcquisitionPulse(
            duration=simplify(self.duration),
            target=self.target,
            bin=simplify(self.bin),
        )


@frozen
class ChannelMappedPulse(AnyPulse):
    pulse: LeafPulse
    channel: Channel
    duration: Expression = field(
        repr=str,
        default=Factory(lambda self: self.pulse.duration, takes_self=True),
    )

    def bind(self, binding: Binding, *, source_map: Optional[dict[int, Pulse]] = None) -> ChannelMappedPulse:
        result = ChannelMappedPulse(
            pulse=self.pulse.bind(binding),
            channel=self.channel,
        )
        if source_map is not None:
            source_map[id(result)] = self
        return result

    def unroll(self) -> UnrolledPulse:
        result = UnrolledPulse.from_pulse(self, self)
        return result

    def apply_channel_mapping(self, mapping: dict[int, Channel]) -> "Pulse":
        base = self.pulse
        ch = mapping.get(id(base))
        if ch is None:
            # Drop old wrapper if any and return the base leaf
            return base
        return ChannelMappedPulse(pulse=base, channel=ch)

    @property
    def parameters(self) -> frozenset[Parameter]:
        return self.pulse.parameters

    @property
    def channels(self) -> frozenset[Channel]:
        # Include this pulse's channel and any channels from the inner pulse (if present)
        return frozenset({self.channel, *self.pulse.channels})

    @override
    def simplify(self) -> LeafPulse:
        return ChannelMappedPulse(
            pulse=simplify(self.pulse),
            channel=self.channel,
        )


@frozen
class SequencePulse(AnyPulse):
    pulses: tuple[Pulse, ...]
    duration: Expression = field(
        repr=str,
        default=Factory(
            lambda self: expression.sum(*(pulse.duration for pulse in self.pulses)),
            takes_self=True,
        ),
    )

    def bind(self, binding: Binding, *, source_map: Optional[dict[int, Pulse]] = None) -> SequencePulse:
        result = SequencePulse(
            pulses=tuple(pulse.bind(binding, source_map=source_map) for pulse in self.pulses),
        )
        if source_map is not None:
            source_map[id(result)] = self
        return result

    def unroll(self) -> UnrolledPulse:
        assert self.is_bound, "Cannot unroll a pulse with free parameters"

        result = UnrolledPulse.empty()
        for subpulse in self.pulses:
            result = result.append(subpulse.unroll())
        return result

    def apply_channel_mapping(self, mapping: dict[int, Channel]) -> "Pulse":
        return SequencePulse(pulses=tuple(p.apply_channel_mapping(mapping) for p in self.pulses))

    @property
    def parameters(self) -> frozenset[Parameter]:
        return frozenset(ChainMap(*(pulse.parameters for pulse in self.pulses)))

    @property
    def channels(self) -> frozenset[Channel]:
        return frozenset().union(*(p.channels for p in self.pulses))

    @override
    def simplify(self) -> Pulse:
        if len(self.pulses) == 1:
            return self.pulses[0].simplify()

        simplified_children: list[Pulse] = [pulse.simplify() for pulse in self.pulses]
        flattened_children: list[Pulse] = []

        for child in simplified_children:
            if isinstance(child, SequencePulse):
                flattened_children.extend(child.pulses)
            else:
                flattened_children.append(child)

        if len(flattened_children) == 1:
            return flattened_children[0]

        return SequencePulse(pulses=tuple(flattened_children))

    def __repr__(self) -> str:
        body = ",\n".join(repr(pulse) for pulse in self.pulses)
        body = textwrap.indent(body, " " * 4)
        return f"""{self.__class__.__name__}(
{body},
)"""


@frozen
class ParallelPulse(AnyPulse):
    pulses: tuple[Pulse, ...]
    duration: Expression = field(
        repr=str,
        default=Factory(
            lambda self: expression.max(*(pulse.duration for pulse in self.pulses)),
            takes_self=True,
        ),
    )

    def bind(self, binding: Binding, *, source_map: Optional[dict[int, Pulse]] = None) -> ParallelPulse:
        result = ParallelPulse(
            pulses=tuple(pulse.bind(binding, source_map=source_map) for pulse in self.pulses),
        )
        if source_map is not None:
            source_map[id(result)] = self
        return result

    @property
    def parameters(self) -> frozenset[Parameter]:
        return frozenset(ChainMap(*(pulse.parameters for pulse in self.pulses)))

    def unroll(self) -> UnrolledPulse:
        result = UnrolledPulse.empty()
        for subpulse in self.pulses:
            result = result.merge(subpulse.unroll())
        return result

    def apply_channel_mapping(self, mapping: dict[int, Channel]) -> "Pulse":
        return ParallelPulse(pulses=tuple(p.apply_channel_mapping(mapping) for p in self.pulses))

    @override
    def simplify(self) -> Pulse:
        if len(self.pulses) == 1:
            return self.pulses[0].simplify()
        return ParallelPulse(pulses=tuple(pulse.simplify() for pulse in self.pulses))

    def __repr__(self) -> str:
        body = ",\n".join(repr(pulse) for pulse in self.pulses)
        body = textwrap.indent(body, " " * 4)
        return f"""{self.__class__.__name__}(
{body},
)"""

    @property
    def channels(self) -> frozenset[Channel]:
        return frozenset().union(*(p.channels for p in self.pulses))


@frozen
class ForLoopPulse(AnyPulse):
    start: Literal = field(
        repr=str,
        validator=validators.instance_of(pint.Quantity),
    )
    stop: Literal = field(
        repr=str,
        validator=validators.instance_of(pint.Quantity),
    )
    step: Literal = field(
        repr=str,
        validator=validators.instance_of(pint.Quantity),
    )
    loop_parameter: Parameter = field(repr=str)
    index_parameter: Parameter = field(repr=str)
    body: SequencePulse
    duration: Expression = field(
        repr=str,
        default=Factory(
            lambda self: expression.sum(
                *(
                    self.body.bind(
                        {
                            self.loop_parameter: value,
                            self.index_parameter: i * unit.dimensionless,
                        }
                    ).duration
                    for i, value in enumerate(self.values)
                )
            ),
            takes_self=True,
        ),
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

    def bind(self, binding: Binding, *, source_map: Optional[dict[int, Pulse]] = None) -> ForLoopPulse:
        result = ForLoopPulse(
            start=self.start,
            stop=self.stop,
            step=self.step,
            loop_parameter=self.loop_parameter,
            index_parameter=self.index_parameter,
            body=self.body.bind(binding, source_map=source_map),
        )
        if source_map is not None:
            source_map[id(result)] = self
        return result

    @property
    def parameters(self) -> frozenset[Parameter]:
        return self.body.parameters.difference({self.loop_parameter, self.index_parameter})

    def iterations(self, *, source_map: Optional[dict[int, Pulse]] = None) -> list[SequencePulse]:
        """
        Returns a list of SequencePulses representing the iterations of the loop.
        Each iteration is a SequencePulse with the body pulse bound to the current loop value and index.
        """
        return [
            self.body.bind(
                binding={
                    self.loop_parameter: value,
                    self.index_parameter: idx * unit.dimensionless,
                },
                source_map=source_map,
            )
            for idx, value in enumerate(self.values)
        ]

    def unroll(self) -> UnrolledPulse:
        assert self.is_bound, "Cannot unroll a pulse with free parameters"

        source_map: dict[int, Pulse] = {}  # id(bound iteration) -> source iteration
        iterations = tuple(self.iterations(source_map=source_map))
        composite = SequencePulse(pulses=iterations)
        unrolled = composite.unroll()

        # The parameter binding in iterations() changes the source pulses.
        # Use the source_map to replace the bound source pulses with the original source pulses.
        source_by_unrolled = {
            unrolled_id: source_map.get(id(source)) for unrolled_id, source in unrolled.source_by_unrolled.items()
        }
        unrolled_by_source = {}
        # While source_id is unique, the source_map may map multiple source_ids to the same source pulse.
        for source_id, unrolled_pulses in unrolled.unrolled_by_source.items():
            key = id(source_map[source_id])
            unrolled_by_source.setdefault(key, []).extend(unrolled_pulses)

        return UnrolledPulse(
            intervals=unrolled.intervals,
            source_by_unrolled=source_by_unrolled,
            unrolled_by_source=frozendict(
                {source_id: tuple(unrolled_pulses) for source_id, unrolled_pulses in unrolled_by_source.items()}
            ),
        )

    def apply_channel_mapping(self, mapping: dict[int, Channel]) -> "Pulse":
        mapped_body = self.body.apply_channel_mapping(mapping)
        assert isinstance(mapped_body, SequencePulse)
        return ForLoopPulse(
            start=self.start,
            stop=self.stop,
            step=self.step,
            loop_parameter=self.loop_parameter,
            index_parameter=self.index_parameter,
            body=mapped_body,
        )

    def __repr__(self) -> str:
        body = ""
        body += f"start={self.start},"
        body += "\n"
        body += f"stop={self.stop},"
        body += "\n"
        body += f"step={self.step},"
        body += "\n"
        body += f"loop_parameter={self.loop_parameter},"
        body += "\n"
        body += f"index_parameter={self.index_parameter},"
        body += "\n"
        body += f"body={self.body},"
        body = textwrap.indent(body, " " * 4)
        return f"""{self.__class__.__name__}(
{body},
)"""

    @property
    def channels(self) -> frozenset[Channel]:
        # Channels used by the loop are those of its body
        return self.body.channels

    @override
    def simplify(self) -> Pulse:
        iterations = self.iterations()
        if len(iterations) == 1:
            return iterations[0].simplify()
        simplified_body = self.body.simplify()
        return ForLoopPulse(
            start=self.start,
            stop=self.stop,
            step=self.step,
            loop_parameter=self.loop_parameter,
            index_parameter=self.index_parameter,
            body=simplified_body
            if isinstance(simplified_body, SequencePulse)
            else SequencePulse(pulses=(simplified_body,)),
        )


LeafPulse = DelayPulse | LaserPulse | DrivePulse | AcquisitionPulse | ChannelMappedPulse
ContainerPulse = SequencePulse | ParallelPulse | ForLoopPulse
Pulse = LeafPulse | ContainerPulse
