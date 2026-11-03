"""Compute the sub-satellite (ground track) points with Skyfield."""
from pathlib import Path

import numpy as np
from skyfield.api import EarthSatellite, load, wgs84


def load_satellite(tle_path: str):
    """Read a 3-line TLE file (name + 2 lines) and return (satellite, timescale)."""
    path = Path(tle_path)
    if not path.is_file():
        raise ValueError(f"TLE file not found: {tle_path}")
    lines = [ln.strip() for ln in path.read_text().splitlines() if ln.strip()]
    if len(lines) < 3 or not lines[1].startswith("1 ") or not lines[2].startswith("2 "):
        raise ValueError(f"TLE file needs a name line, then lines '1 ...' and '2 ...': {tle_path}")
    # builtin=True means no internet download is needed for time data.
    ts = load.timescale(builtin=True)
    try:
        sat = EarthSatellite(lines[1], lines[2], lines[0], ts)
    except ValueError as err:
        raise ValueError(f"Bad TLE in {tle_path}: {err}") from err
    return sat, ts


def compute_track(sat, ts, hours: float, step_seconds: float, start=None):
    """Return (lats, lons, times); lats/lons in degrees, lons in -180..180.

    start is a UTC datetime; if None we start at the TLE epoch so the demo is repeatable.
    """
    if hours <= 0 or step_seconds <= 0:
        raise ValueError("--hours and --step-seconds must be greater than 0")
    t0 = ts.from_datetime(start) if start is not None else sat.epoch
    count = int(hours * 3600 / step_seconds) + 1
    # One Skyfield time array holding every sample, offset in days from the start.
    times = ts.tt_jd(t0.tt + np.arange(count) * step_seconds / 86400.0)
    geocentric = sat.at(times)
    subpoint = wgs84.subpoint(geocentric)  # point on Earth directly below the satellite
    return subpoint.latitude.degrees, subpoint.longitude.degrees, times


def split_at_dateline(lats, lons):
    """Cut the track into segments wherever longitude jumps by more than 180 degrees.

    Without this, matplotlib would draw a line straight across the whole map
    when the satellite crosses the +/-180 edge.
    """
    segments = []
    start = 0
    for i in range(1, len(lons)):
        if abs(lons[i] - lons[i - 1]) > 180:
            segments.append((lats[start:i], lons[start:i]))
            start = i
    segments.append((lats[start:], lons[start:]))
    return segments
