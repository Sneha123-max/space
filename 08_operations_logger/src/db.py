"""All SQLite logic lives here. Every query uses ? placeholders (never string formatting)."""
import sqlite3
from datetime import timedelta
from pathlib import Path

from .timeutil import now_utc, parse_utc, to_text

KINDS = ("EVENT", "ANOMALY")
SEVERITIES = ("INFO", "WARNING", "CRITICAL")

SCHEMA = """
CREATE TABLE IF NOT EXISTS entries (
    id       INTEGER PRIMARY KEY,
    ts_utc   TEXT NOT NULL,
    kind     TEXT NOT NULL CHECK (kind IN ('EVENT','ANOMALY')),
    severity TEXT NOT NULL CHECK (severity IN ('INFO','WARNING','CRITICAL')),
    action   TEXT NOT NULL,
    status   TEXT NOT NULL DEFAULT 'CLOSED' CHECK (status IN ('OPEN','CLOSED'))
)
"""


def connect(db_path: Path) -> sqlite3.Connection:
    """Open the database and make sure the table exists."""
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row  # lets us read columns by name
    conn.execute(SCHEMA)
    return conn


def add_entry(conn, kind: str, severity: str, action: str,
              ts_utc: str | None = None, status: str | None = None) -> int:
    """Insert one entry and return its id."""
    kind, severity = kind.upper(), severity.upper()
    if kind not in KINDS:
        raise ValueError(f"kind must be one of {', '.join(KINDS)}")
    if severity not in SEVERITIES:
        raise ValueError(f"severity must be one of {', '.join(SEVERITIES)}")
    if not action.strip():
        raise ValueError("action text must not be empty")
    # Events are done when logged; anomalies stay open until someone closes them.
    status = (status or ("OPEN" if kind == "ANOMALY" else "CLOSED")).upper()
    if status not in ("OPEN", "CLOSED"):
        raise ValueError("status must be OPEN or CLOSED")
    ts_utc = parse_utc(ts_utc) if ts_utc else to_text(now_utc())
    cur = conn.execute(
        "INSERT INTO entries (ts_utc, kind, severity, action, status) VALUES (?, ?, ?, ?, ?)",
        (ts_utc, kind, severity, action.strip(), status),
    )
    conn.commit()
    return cur.lastrowid


def list_entries(conn, status: str | None = None) -> list[sqlite3.Row]:
    """All entries, oldest first, optionally only OPEN or CLOSED."""
    if status is None:
        return conn.execute("SELECT * FROM entries ORDER BY ts_utc, id").fetchall()
    status = status.upper()
    if status not in ("OPEN", "CLOSED"):
        raise ValueError("status must be OPEN or CLOSED")
    return conn.execute(
        "SELECT * FROM entries WHERE status = ? ORDER BY ts_utc, id", (status,)
    ).fetchall()


def close_entry(conn, entry_id: int) -> None:
    """Mark an open entry CLOSED."""
    row = conn.execute("SELECT status FROM entries WHERE id = ?", (entry_id,)).fetchone()
    if row is None:
        raise ValueError(f"no entry with id {entry_id}")
    if row["status"] == "CLOSED":
        raise ValueError(f"entry {entry_id} is already closed")
    conn.execute("UPDATE entries SET status = 'CLOSED' WHERE id = ?", (entry_id,))
    conn.commit()


def handover_data(conn, hours: int = 24, now=None):
    """Return (open_issues, recent_events) for the shift handover."""
    if hours <= 0:
        raise ValueError("--hours must be a positive number")
    since = to_text((now or now_utc()) - timedelta(hours=hours))
    open_issues = conn.execute(
        "SELECT * FROM entries WHERE status = 'OPEN' ORDER BY ts_utc, id"
    ).fetchall()
    # Recent = closed entries inside the time window (open ones are listed above).
    recent = conn.execute(
        "SELECT * FROM entries WHERE ts_utc >= ? AND status = 'CLOSED' ORDER BY ts_utc, id",
        (since,),
    ).fetchall()
    return open_issues, recent
