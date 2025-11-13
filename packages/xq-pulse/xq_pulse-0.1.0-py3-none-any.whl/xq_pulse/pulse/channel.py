from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum
from typing import TYPE_CHECKING

from attrs import field, frozen, validators

if TYPE_CHECKING:
    from xq_pulse.pulse.pulse import LeafPulse


class ChannelType(str, Enum):
    LASER = "laser"
    DRIVE = "drive"
    ACQUISITION = "acquisition"


@frozen
class Channel(ABC):
    name: str
    type: ChannelType = field(
        validator=validators.instance_of(ChannelType),
    )

    @abstractmethod
    def can_generate(self, pulse: LeafPulse) -> bool:
        """Return True iff this channel can generate the given pulse."""
        ...
