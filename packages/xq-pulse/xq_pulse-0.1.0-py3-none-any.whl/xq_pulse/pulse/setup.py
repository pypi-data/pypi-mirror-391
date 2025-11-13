from __future__ import annotations

from abc import ABC, abstractmethod

from attrs import field, frozen, validators

from xq_pulse.pulse.channel import Channel
from xq_pulse.pulse.program import PulseProgram


@frozen
class Setup(ABC):
    """Abstract base class for hardware setups.

    A concrete setup specifies the available hardware `channels` and provides a
    `run` implementation that executes a `PulseProgram`.
    """

    channels: frozenset[Channel] = field(
        converter=lambda iterable: frozenset(iterable),
        validator=validators.deep_iterable(
            member_validator=validators.instance_of(Channel),
            iterable_validator=validators.instance_of(frozenset),
        ),
        repr=True,
    )

    def channel(self, name: str) -> Channel:
        """Return the channel with the given name."""
        for channel in self.channels:
            if channel.name == name:
                return channel
        raise KeyError(f"No channel with name {name!r} in setup")

    @abstractmethod
    def run(self, program: PulseProgram) -> None:
        """Execute the given `PulseProgram` on this setup."""
        ...
