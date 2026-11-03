"""Reads the two CSV files and checks them. All times become UTC datetimes."""
import csv
from dataclasses import dataclass
from datetime import datetime, timezone


class InputError(Exception):
    """Raised for bad user input; main.py prints it as one line."""


@dataclass
class Request:
    request_id: str
    priority: int
    start: datetime
    end: datetime
    battery_wh: float
    storage_mb: float


@dataclass
class Window:
    start: datetime
    end: datetime


def parse_utc(text: str, where: str) -> datetime:
    """Turn '2026-03-10T08:00:00Z' into a timezone-aware UTC datetime."""
    try:
        # Older Pythons do not understand a trailing 'Z', so swap it for +00:00.
        value = datetime.fromisoformat(text.strip().replace("Z", "+00:00"))
    except ValueError:
        raise InputError(f"{where}: bad time '{text}' (use e.g. 2026-03-10T08:00:00Z)")
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)  # assume UTC if no zone given
    return value.astimezone(timezone.utc)


def _read_rows(path: str, columns: list[str]) -> list[dict]:
    """Open a CSV and make sure it has the columns we need."""
    try:
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            missing = [c for c in columns if c not in (reader.fieldnames or [])]
            if missing:
                raise InputError(f"{path}: missing column(s): {', '.join(missing)}")
            rows = list(reader)
    except OSError:
        raise InputError(f"cannot read file '{path}'")
    if not rows:
        raise InputError(f"{path}: no data rows")
    return rows


def load_requests(path: str) -> list[Request]:
    cols = ["request_id", "priority", "start_utc", "end_utc", "battery_wh", "storage_mb"]
    requests = []
    for n, row in enumerate(_read_rows(path, cols), start=2):  # line 1 is the header
        where = f"{path} line {n}"
        try:
            req = Request(
                request_id=row["request_id"].strip(),
                priority=int(row["priority"]),
                start=parse_utc(row["start_utc"], where),
                end=parse_utc(row["end_utc"], where),
                battery_wh=float(row["battery_wh"]),
                storage_mb=float(row["storage_mb"]),
            )
        except (ValueError, TypeError, AttributeError):
            raise InputError(f"{where}: priority, battery_wh and storage_mb must be numbers")
        if req.end <= req.start:
            raise InputError(f"{where}: end_utc must be after start_utc")
        if req.battery_wh < 0 or req.storage_mb < 0:
            raise InputError(f"{where}: battery_wh and storage_mb cannot be negative")
        requests.append(req)
    return requests


def load_windows(path: str) -> list[Window]:
    windows = []
    for n, row in enumerate(_read_rows(path, ["start_utc", "end_utc"]), start=2):
        where = f"{path} line {n}"
        win = Window(parse_utc(row["start_utc"], where), parse_utc(row["end_utc"], where))
        if win.end <= win.start:
            raise InputError(f"{where}: end_utc must be after start_utc")
        windows.append(win)
    return windows
