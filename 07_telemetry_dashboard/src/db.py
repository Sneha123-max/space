"""Small SQLite helpers for the telemetry table."""
import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE telemetry (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts_utc TEXT NOT NULL,
    battery_v REAL NOT NULL,
    temp_c REAL NOT NULL
)
"""


def reset_db(path: str) -> sqlite3.Connection:
    """Create the file (and folder) and drop/recreate the table, so seeding is repeatable."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.execute("DROP TABLE IF EXISTS telemetry")
    conn.execute(SCHEMA)
    return conn


def insert_samples(conn: sqlite3.Connection, samples: list[tuple[str, float, float]]) -> None:
    """Insert many (ts_utc, battery_v, temp_c) rows in one go and save them."""
    conn.executemany(
        "INSERT INTO telemetry (ts_utc, battery_v, temp_c) VALUES (?, ?, ?)", samples
    )
    conn.commit()


def open_existing(path: str) -> sqlite3.Connection:
    """Open a DB that must already exist (sqlite3 would silently create an empty one)."""
    if not Path(path).is_file():
        raise FileNotFoundError(f"database not found: {path} (run 'python seed.py' first)")
    return sqlite3.connect(path)


def latest_rows(conn: sqlite3.Connection, limit: int) -> list[tuple[str, float, float]]:
    """Return the newest `limit` rows, oldest first (the order a trend line needs)."""
    rows = conn.execute(
        "SELECT ts_utc, battery_v, temp_c FROM telemetry ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    return rows[::-1]


def min_max(conn: sqlite3.Connection) -> tuple[float, float, float, float] | None:
    """Return (min_battery, max_battery, min_temp, max_temp) over ALL rows, or None if empty."""
    row = conn.execute(
        "SELECT MIN(battery_v), MAX(battery_v), MIN(temp_c), MAX(temp_c) FROM telemetry"
    ).fetchone()
    return None if row[0] is None else row
