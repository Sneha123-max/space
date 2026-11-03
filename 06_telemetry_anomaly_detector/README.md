# Telemetry Anomaly Detector (SIMULATED data)

## 1. What it does
Generates SIMULATED spacecraft telemetry (battery voltage, temperature) with noise and injected faults.
Checks every sample against warning and critical limits, using a 3-sample debounce so alerts do not flap.
Prints alerts to the terminal and saves them to `output/alerts.log`; every line starts with `[SIMULATED]`.

## 2. Setup
Windows (PowerShell):
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
No seed script is needed; `data/telemetry_sim.csv` is already included. Run the detector:
```
.\.venv\Scripts\python.exe main.py detect --telemetry data/telemetry_sim.csv --alerts output/alerts.log
```
(Linux/macOS: `./.venv/bin/python main.py ...`). Run `main.py` with no arguments to see help.

## 4. Example commands

1. Generate simulated telemetry (fixed seed, so the file is always the same):
```
python main.py simulate --samples 300 --seed 42 --out data/telemetry_sim.csv
[SIMULATED] wrote 300 simulated samples (seed 42) to data/telemetry_sim.csv
```

2. Detect anomalies:
```
python main.py detect --telemetry data/telemetry_sim.csv --alerts output/alerts.log
[SIMULATED] checked 300 simulated samples, debounce N=3
[SIMULATED] 2026-01-01T00:13:50Z (05:43:50 IST) WARNING  battery_v = 6.985V
[SIMULATED] 2026-01-01T00:18:00Z (05:48:00 IST) CLEARED  battery_v back to normal (7.792V)
[SIMULATED] 2026-01-01T00:25:20Z (05:55:20 IST) CRITICAL battery_v = 6.541V
[SIMULATED] 2026-01-01T00:28:50Z (05:58:50 IST) CLEARED  battery_v back to normal (8.153V)
[SIMULATED] 2026-01-01T00:33:50Z (06:03:50 IST) WARNING  temp_c = 37.64C
[SIMULATED] 2026-01-01T00:39:00Z (06:09:00 IST) CLEARED  temp_c back to normal (25.13C)
[SIMULATED] 2026-01-01T00:40:20Z (06:10:20 IST) CRITICAL temp_c = 48.6C
[SIMULATED] 2026-01-01T00:44:00Z (06:14:00 IST) CLEARED  temp_c back to normal (21.45C)
[SIMULATED] 8 alert events
```

3. Bad input gives a one-line error (stderr) and exit code 1:
```
python main.py detect --telemetry nope.csv
[SIMULATED] error: telemetry file not found: nope.csv
```

## 5. Tests
Windows: `.\.venv\Scripts\python.exe -m pytest -q`
Linux/macOS: `./.venv/bin/python -m pytest -q`

## 6. How it works
- `src/config.py` holds all limits (battery < 7.2 V warning, < 6.8 V critical; temperature > 35 C warning, > 45 C critical) and the debounce size N=3.
- `src/simulator.py` makes healthy values (slow wave + noise) using `random.Random(seed)`, then injects faults: a one-sample glitch, battery sags, and heating.
- `src/detector.py` classifies each sample, then applies debounce: the confirmed state changes only after N samples in a row show the new level. This is true for raising and for clearing an alert, so the one-sample glitch is ignored.
- Times are UTC inside the program; IST (UTC+05:30) is added only for display.
- `main.py` is the command-line wrapper (`simulate` and `detect`).
