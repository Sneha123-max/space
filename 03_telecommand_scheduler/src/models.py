"""Small data containers used by the other modules."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Request:
    """One imaging request read from the CSV."""
    request_id: str
    start: datetime      # UTC
    duration_s: int
    target: str


@dataclass(frozen=True)
class Command:
    """One timed command that we would uplink to the spacecraft."""
    request_id: str
    step: str            # POWER_ON, POINT, CAPTURE or SAVE
    time: datetime       # UTC
    target: str
