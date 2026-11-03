"""Turn requests into timed commands and find clashes between them."""

from datetime import timedelta

from . import config
from .models import Command, Request


def expand_request(req: Request) -> list[Command]:
    """Make the four steps for one request, each with an exact UTC time."""
    t_power = req.start
    t_point = t_power + timedelta(seconds=config.POWER_ON_TO_POINT_S)
    t_capture = t_point + timedelta(seconds=config.POINT_TO_CAPTURE_S)
    t_save = t_capture + timedelta(seconds=req.duration_s + config.CAPTURE_TO_SAVE_S)
    steps = [("POWER_ON", t_power), ("POINT", t_point), ("CAPTURE", t_capture), ("SAVE", t_save)]
    return [Command(req.request_id, name, when, req.target) for name, when in steps]


def build_schedule(requests: list[Request]) -> list[Command]:
    """Expand every request and return all commands sorted by time."""
    commands = [cmd for req in requests for cmd in expand_request(req)]
    return sorted(commands, key=lambda c: c.time)


def find_warnings(requests: list[Request]) -> list[str]:
    """Return human-readable warnings; an empty list means all clear."""
    warnings: list[str] = []
    ordered = sorted(requests, key=lambda r: r.start)

    # 1) Compare each request with the next one in time order.
    for first, second in zip(ordered, ordered[1:]):
        first_end = expand_request(first)[-1].time  # SAVE is the last step
        gap = (second.start - first_end).total_seconds()
        if gap < 0:
            warnings.append(f"OVERLAP: {second.request_id} starts {int(-gap)}s before "
                            f"{first.request_id} finishes")
        elif gap < config.MIN_GAP_BETWEEN_REQUESTS_S:
            warnings.append(f"TOO CLOSE: only {int(gap)}s between {first.request_id} and "
                            f"{second.request_id} (need {config.MIN_GAP_BETWEEN_REQUESTS_S}s)")

    # 2) Two different requests sending a command at the very same second.
    seen: dict = {}
    for cmd in build_schedule(requests):
        other = seen.get(cmd.time)
        if other and other.request_id != cmd.request_id:
            warnings.append(f"COLLISION: {other.request_id} {other.step} and "
                            f"{cmd.request_id} {cmd.step} both at {cmd.time:%Y-%m-%d %H:%M:%S}Z")
        seen[cmd.time] = cmd
    return warnings
