"""Load a TLE file and check how old it is."""
from datetime import datetime, timezone

from skyfield.api import EarthSatellite, load

MAX_AGE_DAYS = 7  # TLEs get inaccurate after about a week

# Offline timescale: no download needed.
ts = load.timescale(builtin=True)


class InputError(Exception):
    """A user mistake (bad file, bad value). Shown as one line, no stack trace."""


def load_satellite(path: str) -> EarthSatellite:
    """Read a 2- or 3-line TLE file and return a Skyfield satellite."""
    try:
        with open(path, encoding="utf-8") as f:
            lines = [ln.rstrip() for ln in f if ln.strip()]
    except OSError as err:
        raise InputError(f"cannot read TLE file '{path}': {err.strerror}")
    # If the file has a name line, it comes first.
    name = "SATELLITE"
    if lines and not lines[0].startswith("1 "):
        name = lines.pop(0).strip()
    if len(lines) < 2 or not lines[0].startswith("1 ") or not lines[1].startswith("2 "):
        raise InputError(f"'{path}' is not a valid TLE file (need lines starting '1 ' and '2 ')")
    try:
        return EarthSatellite(lines[0], lines[1], name, ts)
    except ValueError as err:
        raise InputError(f"invalid TLE data in '{path}': {err}")


def epoch_age_days(sat: EarthSatellite, now: datetime) -> float:
    """Days between the TLE epoch and `now` (both UTC)."""
    return (now - sat.epoch.utc_datetime()).total_seconds() / 86400


def epoch_warning(sat: EarthSatellite, now: datetime) -> str | None:
    """Return a warning text if the TLE is older than 7 days, else None."""
    age = epoch_age_days(sat, now)
    if age > MAX_AGE_DAYS:
        return (f"WARNING: TLE epoch {sat.epoch.utc_strftime('%Y-%m-%d %H:%M')} UTC is "
                f"{age:.1f} days old (> {MAX_AGE_DAYS}). Predictions may be inaccurate.")
    return None


def utc_now() -> datetime:
    return datetime.now(timezone.utc)
