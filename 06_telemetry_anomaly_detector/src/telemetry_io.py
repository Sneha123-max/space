"""Reads and writes the telemetry CSV file."""
import csv
from pathlib import Path

from src import config

COLUMNS = ["timestamp_utc", "battery_v", "temp_c"]


def write_csv(rows: list[dict], path: Path) -> None:
    """Write rows to CSV. First line is a SIMULATED notice."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        f.write(f"{config.LABEL} Simulated telemetry - not real spacecraft data\n")
        writer = csv.DictWriter(f, fieldnames=COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path: Path) -> list[dict]:
    """Read rows back with numbers converted. Raises ValueError on bad input."""
    if not path.is_file():
        raise ValueError(f"telemetry file not found: {path}")
    with path.open(newline="", encoding="utf-8") as f:
        # Skip the SIMULATED notice line (and nothing else).
        lines = [ln for ln in f if not ln.startswith(config.LABEL)]
    reader = csv.DictReader(lines)
    if reader.fieldnames != COLUMNS:
        raise ValueError(f"telemetry file must have columns: {', '.join(COLUMNS)}")
    rows = []
    for number, row in enumerate(reader, start=1):
        try:
            rows.append({
                "timestamp_utc": row["timestamp_utc"],
                "battery_v": float(row["battery_v"]),
                "temp_c": float(row["temp_c"]),
            })
        except (TypeError, ValueError):
            raise ValueError(f"bad number in data row {number} of {path}") from None
    if not rows:
        raise ValueError(f"telemetry file has no data rows: {path}")
    return rows
