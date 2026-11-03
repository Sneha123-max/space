# Telecommand Scheduler

## What it does
Reads imaging requests (id, start time, duration, target) from a CSV and sorts them by time.
Expands each into POWER_ON, POINT, CAPTURE, SAVE commands with exact UTC timestamps and safe gaps.
Warns about overlapping requests or colliding commands, then prints a table or exports a CSV.

## Setup
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

## Run
No seed step is needed (sample data is in `data/requests.csv`, SIMULATED requests).
```
.\.venv\Scripts\python.exe main.py build --requests data/requests.csv
```
(Linux/macOS: `./.venv/bin/python main.py build --requests data/requests.csv`)

## Example commands

1. Print the table (first 13 lines shown; the full list has 32 commands, then the warning list):
```
.\.venv\Scripts\python.exe main.py build --requests data/requests.csv
```
```
UTC TIME             IST TIME             REQUEST  STEP     TARGET
2026-11-10 02:00:00  2026-11-10 07:30:00  REQ-001  POWER_ON Mumbai Coast
2026-11-10 02:00:30  2026-11-10 07:30:30  REQ-001  POINT    Mumbai Coast
2026-11-10 02:00:50  2026-11-10 07:30:50  REQ-001  CAPTURE  Mumbai Coast
2026-11-10 02:03:00  2026-11-10 07:33:00  REQ-001  SAVE     Mumbai Coast
2026-11-10 02:10:00  2026-11-10 07:40:00  REQ-002  POWER_ON Chennai Port
2026-11-10 02:10:30  2026-11-10 07:40:30  REQ-002  POINT    Chennai Port
2026-11-10 02:10:50  2026-11-10 07:40:50  REQ-002  CAPTURE  Chennai Port
2026-11-10 02:12:30  2026-11-10 07:42:30  REQ-002  SAVE     Chennai Port
2026-11-10 02:20:00  2026-11-10 07:50:00  REQ-003  POWER_ON Himalaya Glacier
2026-11-10 02:20:30  2026-11-10 07:50:30  REQ-003  POINT    Himalaya Glacier
2026-11-10 02:20:50  2026-11-10 07:50:50  REQ-003  CAPTURE  Himalaya Glacier
2026-11-10 02:22:30  2026-11-10 07:52:30  REQ-004  POWER_ON Delhi Region
...
WARNINGS (1):
  - OVERLAP: REQ-004 starts 90s before REQ-003 finishes
```

2. Only report the warnings (no command list):
```
.\.venv\Scripts\python.exe main.py build --requests data/requests.csv --report-only
```
```
WARNINGS (1):
  - OVERLAP: REQ-004 starts 90s before REQ-003 finishes
```

3. Export to CSV:
```
.\.venv\Scripts\python.exe main.py build --requests data/requests.csv --out output/commands.csv
```
```
Wrote 32 commands to output/commands.csv

WARNINGS (1):
  - OVERLAP: REQ-004 starts 90s before REQ-003 finishes
```
First lines of `output/commands.csv`:
```
time_utc,request_id,step,target
2026-11-10T02:00:00Z,REQ-001,POWER_ON,Mumbai Coast
2026-11-10T02:00:30Z,REQ-001,POINT,Mumbai Coast
2026-11-10T02:00:50Z,REQ-001,CAPTURE,Mumbai Coast
2026-11-10T02:03:00Z,REQ-001,SAVE,Mumbai Coast
```

## Tests
PowerShell: `.\.venv\Scripts\python.exe -m pytest -q`
Linux/macOS: `./.venv/bin/python -m pytest -q`

## How it works
- `src/config.py` holds every gap constant (with the reason for each): POWER_ON to POINT 30 s,
  POINT to CAPTURE 20 s, CAPTURE end to SAVE 10 s, minimum 60 s between requests.
- `src/loader.py` reads and checks the CSV, then sorts requests by start time.
- `src/scheduler.py` makes the 4 steps per request and finds warnings:
  OVERLAP (next request starts before the last SAVE), TOO CLOSE (gap under 60 s),
  COLLISION (two commands at the same second).
- `src/output.py` prints the table (UTC and IST) or writes the CSV (UTC only).
- Bad input gives a one-line error on stderr and exit code 1.
