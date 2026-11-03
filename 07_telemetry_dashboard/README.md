# Telemetry Dashboard (SIMULATED data)

## 1. What it does
Generates 500 SIMULATED battery-voltage and temperature samples and stores them in SQLite.
Shows a live-updating terminal dashboard (rich) with latest values, min/max and block-character trends.
An optional `grafana/` folder shows how to view the same data in a local Grafana (not tested).

## 2. Setup
Windows (PowerShell):

    python -m venv .venv
    .\.venv\Scripts\python.exe -m pip install -r requirements.txt

Linux/macOS:

    python3 -m venv .venv
    ./.venv/bin/python -m pip install -r requirements.txt

## 3. Run
Create the database first (safe to run twice), then start the dashboard:

    .\.venv\Scripts\python.exe seed.py
    .\.venv\Scripts\python.exe main.py live --db data/telemetry.db --refresh 1 --max-seconds 10

Linux/macOS: use `./.venv/bin/python` instead. Leave out `--max-seconds` to run until Ctrl+C.
Add `--feed` to append one new SIMULATED row per refresh so the numbers really move.

## 4. Example commands
1. Seed the database:

        python seed.py

   Output:

        SIMULATED data: inserted 500 samples into data/telemetry.db
        First: ('2025-01-01T00:00:00Z', 27.99, 34.9)
        Last:  ('2025-01-01T08:19:00Z', 27.54, 5.3)

2. Live dashboard for a few seconds (final frame shown; on a real terminal it redraws in place):

        python main.py live --db data/telemetry.db --refresh 1 --max-seconds 10

   Output:

        ┌────────────────────── SIMULATED Spacecraft Telemetry ───────────────────────┐
        │ ┌─────────────┬────────┬───────┬───────┐                                    │
        │ │ Signal      │ Latest │ Min   │ Max   │                                    │
        │ ├─────────────┼────────┼───────┼───────┤                                    │
        │ │ Battery (V) │ 27.54  │ 25.94 │ 30.09 │                                    │
        │ │ Temp (C)    │ 5.3    │ 4.0   │ 35.7  │                                    │
        │ └─────────────┴────────┴───────┴───────┘                                    │
        │ Battery trend (last 40): ▆▆▆▆▇▇▇▇▇████████▇█▇▇▇▇▇▆▆▆▅▅▄▄▄▃▃▃▂▂▂▁▁           │
        │ Temp trend    (last 40): ████▇▇▇▇▆▆▆▅▅▅▅▄▄▄▄▃▃▃▃▂▂▂▂▂▂▂▂▁▁▁▁▁▁▁▁▁           │
        │ Latest sample: 2025-01-01 13:49:00 IST  |  Ctrl+C to quit                   │
        └─────────────────────────────────────────────────────────────────────────────┘

3. Bad input (missing database) gives a one-line error and exit code 1:

        python main.py live --db nope.db

   Output:

        error: database not found: nope.db (run 'python seed.py' first)

## 5. Tests
Windows: `.\.venv\Scripts\python.exe -m pytest -q`
Linux/macOS: `./.venv/bin/python -m pytest -q`

## 6. How it works
- `src/simulate.py` makes fake samples from sine waves plus noise, with a fixed random seed, so every run is identical.
- `src/db.py` holds the SQLite table `telemetry(id, ts_utc, battery_v, temp_c)` and simple queries.
- `src/trend.py` has one pure function, `sparkline`, that maps numbers to the blocks ▁▂▃▄▅▆▇█.
- `src/dashboard.py` reads the newest 40 rows plus min/max and redraws with `rich.live.Live`.
- Times are stored in UTC and converted to IST (UTC+05:30) only when shown on screen.
- Grafana is optional and was not run or tested; see `grafana/README.md`.
