# Mission Planner

## What it does
Reads imaging requests (priority, battery cost, storage cost) and ground station visibility windows from CSV files.
Greedily accepts requests by priority if battery, storage, visibility and no-overlap rules all pass.
Prints an accepted table, a rejected table (one clear reason each) and totals. Sample data is SIMULATED.

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
No seed step is needed. Run the demo:
```
.\.venv\Scripts\python.exe main.py plan --requests data/requests.csv --visibility data/visibility.csv --battery-wh 500 --storage-mb 2000
```
(Linux/macOS: use `./.venv/bin/python`.) Times are shown in IST; the data files are in UTC.

## Example commands

1. Full demo with 500 Wh and 2000 MB:
```
python main.py plan --requests data/requests.csv --visibility data/visibility.csv --battery-wh 500 --storage-mb 2000
```
```
SIMULATED sample data. Times shown in IST (UTC+05:30)

ACCEPTED
ID       Pri  Start  End    Wh   MB
-------  ---  -----  -----  ---  ---
REQ-001  1    13:40  13:55  60   300
REQ-002  1    15:35  16:00  80   400
REQ-004  2    16:10  16:30  90   350
REQ-006  3    18:40  19:10  100  500
REQ-007  3    21:10  21:40  120  300

REJECTED
ID       Pri  Start  End    Reason
-------  ---  -----  -----  ----------------------------
REQ-003  2    13:50  14:10  overlaps REQ-001
REQ-005  2    17:30  18:00  no ground station visibility
REQ-008  4    21:50  22:10  battery budget exceeded
REQ-009  4    00:40  01:00  storage budget exceeded
...
Totals: 5 accepted, 7 rejected
Battery: 450 / 500 Wh used
Storage: 1850 / 2000 MB used
```

2. A tight budget (200 Wh, 800 MB) rejects more:
```
python main.py plan --battery-wh 200 --storage-mb 800
```
```
ACCEPTED
ID       Pri  Start  End    Wh  MB
-------  ---  -----  -----  --  ---
REQ-001  1    13:40  13:55  60  300
REQ-002  1    15:35  16:00  80  400
REQ-011  5    19:00  19:20  25  60

REJECTED
ID       Pri  Start  End    Reason
-------  ---  -----  -----  ----------------------------
REQ-003  2    13:50  14:10  overlaps REQ-001
REQ-004  2    16:10  16:30  battery budget exceeded
...
Totals: 3 accepted, 9 rejected
Battery: 165 / 200 Wh used
Storage: 760 / 800 MB used
```

3. Bad input gives one clear line and a non-zero exit code:
```
python main.py plan --requests nope.csv
```
```
error: cannot read file 'nope.csv'
```

## Tests
PowerShell: `.\.venv\Scripts\python.exe -m pytest -q`
Linux/macOS: `./.venv/bin/python -m pytest -q`

## How it works
1. `src/loader.py` reads both CSVs, checks them, and turns times into UTC datetimes.
2. `src/planner.py` sorts requests by priority, then start time, and goes through them one by one.
3. For each request it checks, in order: fits inside one visibility window, no overlap with an accepted request, enough battery, enough storage. The first failing check becomes the reason.
4. Accepted requests use up the battery and storage budgets.
5. `src/report.py` prints the tables and totals, converting times to IST only for display.
