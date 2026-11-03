# Space Controller Learning Projects

Eight small, local Python CLI projects for learning the basics of spacecraft
operations software. Everything runs offline. All data is bundled sample data
or simulated data (clearly labelled as SIMULATED).

## Projects

| Project | Purpose | Demo command |
|---|---|---|
| [01_satellite_pass_predictor](01_satellite_pass_predictor/README.md) | Predict when a satellite is visible from a ground location (UTC and IST) | `python main.py predict --tle data/iss.tle` |
| [02_ground_track_visualizer](02_ground_track_visualizer/README.md) | Plot a satellite's ground track on a lat/lon map and save a PNG | `python main.py plot --tle data/iss.tle` |
| [03_telecommand_scheduler](03_telecommand_scheduler/README.md) | Turn imaging requests into a timed list of commands and detect overlaps | `python main.py build --requests data/requests.csv` |
| [04_mission_planner](04_mission_planner/README.md) | Greedily accept imaging requests within battery, storage and visibility limits | `python main.py plan --requests data/requests.csv --visibility data/visibility.csv` |
| [05_ground_station_automation](05_ground_station_automation/README.md) | Build a daily contact schedule and scan logs for ERROR and MISSED lines | `python main.py schedule --date 2026-11-02` |
| [06_telemetry_anomaly_detector](06_telemetry_anomaly_detector/README.md) | Detect limit violations in SIMULATED telemetry with debounce | `python main.py detect --telemetry data/telemetry_sim.csv` |
| [07_telemetry_dashboard](07_telemetry_dashboard/README.md) | Live terminal dashboard of SIMULATED telemetry stored in SQLite (optional Grafana) | `python main.py live --db data/telemetry.db` |
| [08_operations_logger](08_operations_logger/README.md) | Log events and anomalies, close issues, print a shift handover | `python main.py handover --hours 24` |

## Set up everything at once

Requires Python 3.10 or newer. Each project gets its own `.venv`; nothing is
installed globally.

PowerShell (Windows):

```powershell
python setup_all.py
```

Linux / macOS:

```bash
python3 setup_all.py
```

`setup_all.py` creates each `.venv`, installs that project's `requirements.txt`,
and runs `seed.py` where a project has one.

## Run any project

Each project folder has its own README with setup, demo commands and tests.

PowerShell (Windows):

```powershell
cd 01_satellite_pass_predictor
.\.venv\Scripts\python.exe main.py --help
```

Linux / macOS:

```bash
cd 01_satellite_pass_predictor
./.venv/bin/python main.py --help
```

## Run the tests for a project

PowerShell (Windows):

```powershell
cd 01_satellite_pass_predictor
.\.venv\Scripts\python.exe -m pytest -q
```

Linux / macOS:

```bash
cd 01_satellite_pass_predictor
./.venv/bin/python -m pytest -q
```

## Rules used in every project

- Times are stored in UTC. IST (UTC+05:30) is shown only when printing.
- Simulated data is always labelled SIMULATED.
- No internet, no API keys, no cloud, no Docker.
