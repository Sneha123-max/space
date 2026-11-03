"""Build a daily contact schedule from a CSV of pass times."""
import csv
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

# IST is UTC+05:30. We only use it for display, never for calculations.
IST = timezone(timedelta(hours=5, minutes=30))
REQUIRED_COLUMNS = ["station", "aos_utc", "los_utc", "max_elev_deg"]


def parse_utc(text: str) -> datetime:
    """Turn '2026-11-02T03:12:00' into a timezone-aware UTC datetime."""
    return datetime.fromisoformat(text).replace(tzinfo=timezone.utc)


def read_passes(pass_file: Path) -> list[dict]:
    """Read the CSV and return a list of passes. Raises ValueError on bad input."""
    if not pass_file.is_file():
        raise ValueError(f"pass file not found: {pass_file}")
    with pass_file.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None or any(c not in reader.fieldnames for c in REQUIRED_COLUMNS):
            raise ValueError(f"pass file must have columns: {', '.join(REQUIRED_COLUMNS)}")
        passes = []
        for line_no, row in enumerate(reader, start=2):
            try:
                passes.append({
                    "station": row["station"],
                    "aos": parse_utc(row["aos_utc"]),
                    "los": parse_utc(row["los_utc"]),
                    "max_elev": float(row["max_elev_deg"]),
                })
            except (ValueError, TypeError):
                raise ValueError(f"bad value in {pass_file} on line {line_no}") from None
    return passes


def passes_for_day(passes: list[dict], day: date) -> list[dict]:
    """Keep passes whose AOS falls on this UTC day, sorted by AOS time."""
    todays = [p for p in passes if p["aos"].date() == day]
    return sorted(todays, key=lambda p: p["aos"])


def format_schedule(todays: list[dict], day: date) -> str:
    """Make the text of the schedule file (UTC and IST for every contact)."""
    lines = [f"Contact schedule for {day.isoformat()} (UTC day)", ""]
    for i, p in enumerate(todays, start=1):
        minutes = (p["los"] - p["aos"]).total_seconds() / 60
        lines.append(
            f"{i:02d} {p['station']:<11} "
            f"UTC {p['aos']:%H:%M:%S}-{p['los']:%H:%M:%S} | "
            f"IST {p['aos'].astimezone(IST):%H:%M:%S}-{p['los'].astimezone(IST):%H:%M:%S} | "
            f"{minutes:.1f} min | max elev {p['max_elev']:.1f} deg"
        )
    lines.append("")
    lines.append(f"Total contacts: {len(todays)}")
    return "\n".join(lines) + "\n"


def build_schedule(day: date, pass_file: Path, out_dir: Path) -> Path:
    """Read passes, write output/contacts_YYYY-MM-DD.txt and return its path."""
    todays = passes_for_day(read_passes(pass_file), day)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"contacts_{day.isoformat()}.txt"
    out_file.write_text(format_schedule(todays, day), encoding="utf-8")
    return out_file
