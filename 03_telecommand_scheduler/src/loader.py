"""Read and check the requests CSV. User mistakes raise ValueError with a clear message."""

import csv
from datetime import datetime, timezone
from pathlib import Path

from .models import Request

REQUIRED_COLUMNS = ["request_id", "start_utc", "duration_s", "target"]


def parse_utc(text: str, line: int) -> datetime:
    """Turn '2026-11-10T02:15:00Z' into a timezone-aware UTC datetime."""
    try:
        # Older Python cannot read a trailing 'Z', so swap it for +00:00.
        moment = datetime.fromisoformat(text.strip().replace("Z", "+00:00"))
    except ValueError:
        raise ValueError(f"line {line}: bad start_utc '{text}' (use e.g. 2026-11-10T02:15:00Z)")
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=timezone.utc)  # no zone given -> assume UTC
    return moment.astimezone(timezone.utc)


def load_requests(path: str) -> list[Request]:
    """Read the CSV and return requests sorted by start time."""
    file = Path(path)
    if not file.is_file():
        raise ValueError(f"requests file not found: {path}")

    requests: list[Request] = []
    seen_ids: set[str] = set()
    with file.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        missing = [c for c in REQUIRED_COLUMNS if c not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"CSV is missing column(s): {', '.join(missing)}")

        for row in reader:
            line = reader.line_num
            request_id = (row["request_id"] or "").strip()
            if not request_id:
                raise ValueError(f"line {line}: empty request_id")
            if request_id in seen_ids:
                raise ValueError(f"line {line}: duplicate request_id '{request_id}'")
            seen_ids.add(request_id)

            try:
                duration = int(row["duration_s"])
            except (TypeError, ValueError):
                raise ValueError(f"line {line}: duration_s must be a whole number")
            if duration <= 0:
                raise ValueError(f"line {line}: duration_s must be greater than 0")

            requests.append(Request(request_id, parse_utc(row["start_utc"] or "", line),
                                    duration, (row["target"] or "").strip()))

    if not requests:
        raise ValueError("CSV has no requests")
    return sorted(requests, key=lambda r: r.start)  # time order
