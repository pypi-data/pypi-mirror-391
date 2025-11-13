from __future__ import annotations

import math
from abc import ABC, abstractmethod
from typing import Callable

import numpy as np
import pint
from attrs import field, frozen

from xq_pulse.util import unit

DimensionlessLiteral = float | int | pint.Quantity


def _ensure_dimensionless_literal(value: DimensionlessLiteral) -> float:
    """Convert a literal to a float while asserting it is dimensionless."""
    if isinstance(value, pint.Quantity):
        assert value.is_compatible_with(unit.dimensionless), f"Envelope value {value} is not dimensionless"
        return value.to(unit.dimensionless).magnitude
    if isinstance(value, (int, float)):
        return float(value)
    raise TypeError(f"Unsupported literal type {type(value)!r} for envelope values")


def _resolve_dimensionless(value: DimensionlessLiteral) -> float:
    return _ensure_dimensionless_literal(value)


def _validate_dimensionless(_, __, value: DimensionlessLiteral) -> None:
    match value:
        case int() | float():
            return
        case pint.Quantity():
            assert value.is_compatible_with(unit.dimensionless), f"Envelope expression {value} is not dimensionless"
        case _:
            raise TypeError(f"Unsupported expression type {type(value)!r} for envelope")


class Envelope(ABC):
    """Abstract base class representing a pulse envelope in the normalised time domain."""

    @abstractmethod
    def value(self, tau: np.ndarray) -> np.ndarray:
        """Return the envelope samples for normalised time points in [0, 1]."""
        ...

    def sample(self, *, num_samples: int = 201) -> tuple[np.ndarray, np.ndarray]:
        assert num_samples >= 2, "At least two samples are required to describe an envelope"
        tau = np.linspace(0.0, 1.0, num_samples)
        return tau, self.value(tau)

    def discretize(self, duration: pint.Quantity, dt: pint.Quantity) -> tuple[np.ndarray, np.ndarray, pint.Quantity]:
        """Discretise the envelope over a physical duration."""
        assert duration.is_compatible_with(unit.s), "Duration must be a time quantity"
        assert dt.is_compatible_with(unit.s), "dt must be a time quantity"
        duration_s = duration.to(unit.s).magnitude
        dt_s = dt.to(unit.s).magnitude
        assert dt_s > 0, "Sampling interval must be positive"
        sample_count = max(2, int(math.floor(duration_s / dt_s)) + 1)
        tau = np.linspace(0.0, 1.0, sample_count)
        time_axis = tau * duration_s
        return tau, self.value(tau), time_axis * unit.s


@frozen
class SquareEnvelope(Envelope):
    level: DimensionlessLiteral = field(
        default=1 * unit.dimensionless,
        converter=lambda value: value * unit.dimensionless if isinstance(value, (int, float)) else value,
        repr=str,
        validator=_validate_dimensionless,
    )

    def value(self, tau: np.ndarray) -> np.ndarray:
        _ = tau  # Square envelope ignores position, keep signature symmetric
        level = _resolve_dimensionless(self.level)
        return np.full_like(tau, fill_value=level, dtype=float)


@frozen
class EnvelopeSegment:
    end: DimensionlessLiteral = field(
        converter=lambda value: value * unit.dimensionless if isinstance(value, (int, float)) else value,
        validator=_validate_dimensionless,
        repr=str,
    )
    value: DimensionlessLiteral = field(
        converter=lambda value: value * unit.dimensionless if isinstance(value, (int, float)) else value,
        validator=_validate_dimensionless,
        repr=str,
    )


@frozen
class PiecewiseEnvelope(Envelope):
    segments: tuple[EnvelopeSegment, ...] = field()

    def __attrs_post_init__(self) -> None:
        assert len(self.segments) > 0, "Piecewise envelope requires at least one segment"
        literal_segments = all(isinstance(segment.end, pint.Quantity) for segment in self.segments)
        if literal_segments:
            ends = [_ensure_dimensionless_literal(segment.end) for segment in self.segments]
            assert ends[0] > 0.0, "First segment in piecewise envelope must end after tau=0"
            assert all(l1 < l2 for l1, l2 in zip(ends, ends[1:])), "Segment ends must be strictly increasing"
            assert math.isclose(ends[-1], 1.0, rel_tol=1e-9), "Final segment must end at tau=1"

    def value(self, tau: np.ndarray) -> np.ndarray:
        ends = np.array([_resolve_dimensionless(segment.end) for segment in self.segments], dtype=float)
        values = np.array([_resolve_dimensionless(segment.value) for segment in self.segments], dtype=float)
        result = np.empty_like(tau, dtype=float)
        indices = np.searchsorted(ends, tau, side="right")
        indices = np.clip(indices, 0, len(values) - 1)
        result[:] = values[indices]
        return result


@frozen
class CallableEnvelope(Envelope):
    function: Callable[[np.ndarray], np.ndarray]

    def value(self, tau: np.ndarray) -> np.ndarray:
        values = self.function(tau)
        return np.asarray(values, dtype=float)
