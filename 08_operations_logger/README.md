# Operations Logger

## 1. What it does
Logs spacecraft operations events and anomaly reports (UTC time, severity, action, open/closed) in SQLite.
Lets you list entries, close issues, and print a shift handover report (open issues first, then recent events).
All sample data is SIMULATED; times are stored in UTC and shown in UTC and IST.

## 2. Setup
PowerShell:
```
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```
Linux/macOS:
```
python3 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
```

## 3. Run
Create the database with SIMULATED sample data (safe to run twice, it resets the file):
```
.\.venv\Scripts\python.exe seed.py          # Linux/macOS: ./.venv/bin/python seed.py
.\.venv\Scripts\python.exe main.py --help   # Linux/macOS: ./.venv/bin/python main.py --help
```
Commands: `add --kind ANOMALY --severity WARNING --action "text"`, `list [--status OPEN]`, `close ID`, `handover [--hours 24]`.

## 4. Example commands
Output below was captured from a real run (Linux/macOS: use `./.venv/bin/python`).

```
.\.venv\Scripts\python.exe main.py list --status OPEN
```
```
 ID  UTC                  IST                  KIND     SEVERITY  STATUS  ACTION
  3  2026-11-01 21:15:40  2026-11-02 02:45:40  ANOMALY  WARNING   OPEN    SIMULATED: Battery temperature trending high, monitoring
  5  2026-11-02 06:15:40  2026-11-02 11:45:40  ANOMALY  CRITICAL  OPEN    SIMULATED: Reaction wheel 2 current spike, wheel disabled
```

```
.\.venv\Scripts\python.exe main.py add --kind ANOMALY --severity WARNING --action "Star tracker noise above limit"
```
```
Added entry 9
```

```
.\.venv\Scripts\python.exe main.py handover --hours 12
```
```
SHIFT HANDOVER REPORT (times shown in UTC and IST)

OPEN ISSUES (3)
 ID  UTC                  IST                  KIND     SEVERITY  STATUS  ACTION
  3  2026-11-01 21:15:40  2026-11-02 02:45:40  ANOMALY  WARNING   OPEN    SIMULATED: Battery temperature trending high, monitoring
  5  2026-11-02 06:15:40  2026-11-02 11:45:40  ANOMALY  CRITICAL  OPEN    SIMULATED: Reaction wheel 2 current spike, wheel disabled
  9  2026-11-02 17:15:41  2026-11-02 22:45:41  ANOMALY  WARNING   OPEN    Star tracker noise above limit

RECENT EVENTS, CLOSED, LAST 12 HOURS (3)
 ID  UTC                  IST                  KIND     SEVERITY  STATUS  ACTION
  6  2026-11-02 08:15:40  2026-11-02 13:45:40  ANOMALY  WARNING   CLOSED  SIMULATED: Brief downlink dropout, resolved on next pass
  7  2026-11-02 11:15:40  2026-11-02 16:45:40  EVENT    INFO      CLOSED  SIMULATED: Safe mode exited, payload re-enabled
  8  2026-11-02 15:15:40  2026-11-02 20:45:40  EVENT    WARNING   CLOSED  SIMULATED: Command uplink retried once, accepted
```
Your times will differ: the seed data is placed relative to "now".

## 5. Tests
PowerShell: `.\.venv\Scripts\python.exe -m pytest -q`
Linux/macOS: `./.venv/bin/python -m pytest -q`
Tests use a temporary database file, never `data/ops_log.db`.

## 6. How it works
- `main.py` reads the command line (argparse) and calls the functions in `src/db.py`.
- `src/db.py` is the only place that touches SQLite. Every query uses `?` placeholders, so user text can never run as SQL.
- The table has CHECK rules, so only valid kind, severity and status values can be stored.
- Events default to CLOSED, anomalies default to OPEN until you run `close ID`.
- `src/timeutil.py` keeps UTC in the database and converts to IST (UTC+05:30) only for display.
- `src/report.py` builds the text tables; the handover shows open issues first, then closed entries from the last N hours.
- Bad input (unknown id, bad time, empty action) prints one `error:` line on stderr and exits with code 1.
