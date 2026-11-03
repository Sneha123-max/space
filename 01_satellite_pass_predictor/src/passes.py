"""Find satellite passes over an observer and format them for display."""
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from skyfield.api import EarthSatellite, wgs84

from src.tle import ts

IST = timezone(timedelta(hours=5, minutes=30))  # India Standard Time, display only


@dataclass
class Pass:
    rise: datetime       # all times are stored in UTC
    culminate: datetime
    max_elev: float      # degrees
    set: datetime


def find_passes(sat: EarthSatellite, lat: float, lon: float,
                start: datetime, hours: float, min_elev: float) -> list[Pass]:
    """Return passes that rise above `min_elev` between start and start+hours."""
    observer = wgs84.latlon(lat, lon)
    t0 = ts.from_datetime(start)
    t1 = ts.from_datetime(start + timedelta(hours=hours))
    times, events = sat.find_events(observer, t0, t1, altitude_degrees=min_elev)

    passes: list[Pass] = []
    rise = peak = None
    elev = 0.0
    for t, event in zip(times, events):
        # event 0 = rise, 1 = highest point, 2 = set
        if event == 0:
            rise, peak = t.utc_datetime(), None
        elif event == 1:
            peak = t.utc_datetime()
            elev = (sat - observer).at(t).altaz()[0].degrees
        elif event == 2 and rise is not None and peak is not None:
            passes.append(Pass(rise, peak, elev, t.utc_datetime()))
            rise = peak = None
    # A pass cut off by the window edge lacks a rise, peak or set, so it is skipped.
    return passes


def fmt(dt: datetime, tz: timezone) -> str:
    return dt.astimezone(tz).strftime("%Y-%m-%d %H:%M:%S")


def format_table(passes: list[Pass]) -> str:
    """Build a plain-text table with UTC and IST columns."""
    head = (f"{'Rise (UTC)':<19}  {'Highest (UTC)':<19}  {'Max el':>7}  {'Set (UTC)':<19}  |  "
            f"{'Rise (IST)':<19}  {'Highest (IST)':<19}  {'Set (IST)':<19}")
    rows = [head, "-" * len(head)]
    for p in passes:
        rows.append(f"{fmt(p.rise, timezone.utc):<19}  {fmt(p.culminate, timezone.utc):<19}  "
                    f"{p.max_elev:5.1f} deg  {fmt(p.set, timezone.utc):<19}  |  "
                    f"{fmt(p.rise, IST):<19}  {fmt(p.culminate, IST):<19}  {fmt(p.set, IST):<19}")
    return "\n".join(rows)
