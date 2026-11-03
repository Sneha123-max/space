"""Builds the rich screen and runs the live-updating loop."""
import random
import sqlite3
import time
from datetime import datetime, timedelta, timezone

from rich.console import Console, Group
from rich.live import Live
from rich.panel import Panel
from rich.table import Table

from src import db
from src.simulate import make_sample
from src.trend import sparkline

TREND_LENGTH = 40  # how many recent samples the trend line shows
IST = timezone(timedelta(hours=5, minutes=30))  # IST is only used for display


def to_ist(ts_utc: str) -> str:
    """Convert a stored UTC timestamp to an IST string for the screen."""
    utc = datetime.strptime(ts_utc, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    return utc.astimezone(IST).strftime("%Y-%m-%d %H:%M:%S IST")


def build_screen(conn: sqlite3.Connection) -> Panel:
    """Read the DB and return one Panel showing latest values, min/max and trends."""
    rows = db.latest_rows(conn, TREND_LENGTH)
    stats = db.min_max(conn)
    if not rows or stats is None:
        return Panel("No telemetry rows yet. Run 'python seed.py'.", title="SIMULATED Telemetry")
    ts, battery, temp = rows[-1]
    bmin, bmax, tmin, tmax = stats

    table = Table(show_header=True, header_style="bold")
    for col in ("Signal", "Latest", "Min", "Max"):
        table.add_column(col)
    table.add_row("Battery (V)", f"{battery:.2f}", f"{bmin:.2f}", f"{bmax:.2f}")
    table.add_row("Temp (C)", f"{temp:.1f}", f"{tmin:.1f}", f"{tmax:.1f}")
    # Trends go on their own lines so 40 characters never get squeezed by table columns.
    trends = (f"Battery trend (last {len(rows)}): {sparkline([r[1] for r in rows])}\n"
              f"Temp trend    (last {len(rows)}): {sparkline([r[2] for r in rows])}")
    footer = f"Latest sample: {to_ist(ts)}  |  Ctrl+C to quit"
    return Panel(Group(table, trends, footer), title="SIMULATED Spacecraft Telemetry")


def append_simulated_row(conn: sqlite3.Connection, rng: random.Random) -> None:
    """Add one new SIMULATED sample after the newest row, so the live view really moves."""
    next_index = conn.execute("SELECT COUNT(*) FROM telemetry").fetchone()[0]
    db.insert_samples(conn, [make_sample(next_index, rng)])


def run_live(db_path: str, refresh: float, max_seconds: float | None, feed: bool) -> None:
    """Redraw the screen every `refresh` seconds until Ctrl+C or `max_seconds` passes."""
    conn = db.open_existing(db_path)
    rng = random.Random()
    start = time.monotonic()
    try:
        with Live(build_screen(conn), console=Console(), refresh_per_second=4) as live:
            while max_seconds is None or time.monotonic() - start < max_seconds:
                time.sleep(refresh)
                if feed:
                    append_simulated_row(conn, rng)
                live.update(build_screen(conn))
    except KeyboardInterrupt:
        pass  # Ctrl+C is the normal way to stop, not an error
    finally:
        conn.close()
