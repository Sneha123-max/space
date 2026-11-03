"""The greedy planner: highest priority first, accept if everything still fits."""
from dataclasses import dataclass

from .loader import Request, Window


@dataclass
class Result:
    request: Request
    accepted: bool
    reason: str  # for accepted requests this is just "ok"


def fits_a_window(req: Request, windows: list[Window]) -> bool:
    """The WHOLE request must sit inside ONE visibility window."""
    return any(w.start <= req.start and req.end <= w.end for w in windows)


def plan(requests: list[Request], windows: list[Window],
         battery_wh: float, storage_mb: float) -> list[Result]:
    """Return one Result per request, in the order they were considered."""
    # Lower priority number = more important; ties go to the earlier start.
    ordered = sorted(requests, key=lambda r: (r.priority, r.start))
    accepted: list[Request] = []
    battery_left = battery_wh
    storage_left = storage_mb
    results = []

    for req in ordered:
        reason = "ok"
        # Checks run in a fixed order, so each rejection has exactly one reason.
        if not fits_a_window(req, windows):
            reason = "no ground station visibility"
        else:
            # Two time ranges overlap if each starts before the other ends.
            clash = next((a for a in accepted if req.start < a.end and a.start < req.end), None)
            if clash:
                reason = f"overlaps {clash.request_id}"
            elif req.battery_wh > battery_left:
                reason = "battery budget exceeded"
            elif req.storage_mb > storage_left:
                reason = "storage budget exceeded"

        if reason == "ok":
            accepted.append(req)
            battery_left -= req.battery_wh
            storage_left -= req.storage_mb
        results.append(Result(req, reason == "ok", reason))
    return results
