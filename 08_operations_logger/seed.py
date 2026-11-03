"""Create data/ops_log.db with SIMULATED sample entries (safe to run twice)."""
from datetime import timedelta
from pathlib import Path

from src import db
from src.timeutil import now_utc, to_text

DB_PATH = Path(__file__).parent / "data" / "ops_log.db"

# (hours ago, kind, severity, action, status) - all SIMULATED
SAMPLES = [
    (30, "EVENT", "INFO", "SIMULATED: Shift start, console checks complete", "CLOSED"),
    (22, "EVENT", "INFO", "SIMULATED: Ground station pass AOS, telemetry nominal", "CLOSED"),
    (20, "ANOMALY", "WARNING", "SIMULATED: Battery temperature trending high, monitoring", "OPEN"),
    (15, "EVENT", "INFO", "SIMULATED: Attitude correction burn executed", "CLOSED"),
    (11, "ANOMALY", "CRITICAL", "SIMULATED: Reaction wheel 2 current spike, wheel disabled", "OPEN"),
    (9, "ANOMALY", "WARNING", "SIMULATED: Brief downlink dropout, resolved on next pass", "CLOSED"),
    (6, "EVENT", "INFO", "SIMULATED: Safe mode exited, payload re-enabled", "CLOSED"),
    (2, "EVENT", "WARNING", "SIMULATED: Command uplink retried once, accepted", "CLOSED"),
]


def main() -> None:
    DB_PATH.parent.mkdir(exist_ok=True)
    DB_PATH.unlink(missing_ok=True)  # start fresh so running twice is safe
    conn = db.connect(DB_PATH)
    now = now_utc()
    for hours_ago, kind, severity, action, status in SAMPLES:
        db.add_entry(conn, kind, severity, action, to_text(now - timedelta(hours=hours_ago)), status)
    conn.close()
    print(f"Seeded {len(SAMPLES)} SIMULATED entries into {DB_PATH}")


if __name__ == "__main__":
    main()
