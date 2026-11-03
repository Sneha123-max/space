# Satellite Pass Predictor

## What it does
Reads a TLE file (satellite orbit data) and an observer's latitude and longitude.
Lists each pass above a minimum elevation: rise, highest point (with elevation) and set.
Shows every time in UTC and IST, warns if the TLE is older than 7 days, and works fully offline.

## Setup
PowerShell (Windows):
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
No seed step. Demo (PowerShell; on Linux use `./.venv/bin/python`):
```
.\.venv\Scripts\python.exe main.py predict --tle data/iss.tle --lat 12.97 --lon 77.59 --start 2026-11-01T00:00:00Z --hours 24 --min-elev 10
```
Defaults: lat/lon = Bangalore (12.97, 77.59), `--start` = now (UTC), `--hours` 24, `--min-elev` 10.

Note: `data/iss.tle` is a SAMPLE (epoch 2024-02-14). The "TLE is old" warning is expected and correct behaviour.
Predictions from it are for practice only. For real use, replace it with a fresh TLE file.

## Example commands
1. Bangalore, 24 hours:
```
> main.py predict --tle data/iss.tle --lat 12.97 --lon 77.59 --start 2026-11-01T00:00:00Z --hours 24 --min-elev 10
WARNING: TLE epoch 2024-02-14 12:26 UTC is 992.2 days old (> 7). Predictions may be inaccurate.
Satellite: ISS (ZARYA)  Observer: 12.97, 77.59  Min elevation: 10.0 deg
Window: 2026-11-01 00:00 UTC for 24.0 h
Rise (UTC)           Highest (UTC)         Max el  Set (UTC)            |  Rise (IST)           Highest (IST)        Set (IST)
-----------------------------------------------------------------------------------------------------------------------------
2026-11-01 09:32:08  2026-11-01 09:33:40   72.7 deg  2026-11-01 09:35:12  |  2026-11-01 15:02:08  2026-11-01 15:03:40  2026-11-01 15:05:12
2026-11-01 20:22:58  2026-11-01 20:24:02   15.6 deg  2026-11-01 20:25:05  |  2026-11-02 01:52:58  2026-11-02 01:54:02  2026-11-02 01:55:05
```
2. Chennai, 48 hours, low elevation limit:
```
> main.py predict --tle data/iss.tle --lat 13.08 --lon 80.27 --start 2026-11-02T00:00:00Z --hours 48 --min-elev 5
WARNING: TLE epoch 2024-02-14 12:26 UTC is 992.2 days old (> 7). Predictions may be inaccurate.
Satellite: ISS (ZARYA)  Observer: 13.08, 80.27  Min elevation: 5.0 deg
Window: 2026-11-02 00:00 UTC for 48.0 h
Rise (UTC)           Highest (UTC)         Max el  Set (UTC)            |  Rise (IST)           Highest (IST)        Set (IST)
-----------------------------------------------------------------------------------------------------------------------------
2026-11-02 08:54:15  2026-11-02 08:56:24   55.2 deg  2026-11-02 08:58:33  |  2026-11-02 14:24:15  2026-11-02 14:26:24  2026-11-02 14:28:33
2026-11-02 19:44:44  2026-11-02 19:46:38   17.6 deg  2026-11-02 19:48:33  |  2026-11-03 01:14:44  2026-11-03 01:16:38  2026-11-03 01:18:33
2026-11-03 08:16:35  2026-11-03 08:18:33   19.6 deg  2026-11-03 08:20:30  |  2026-11-03 13:46:35  2026-11-03 13:48:33  2026-11-03 13:50:30
2026-11-03 19:06:35  2026-11-03 19:08:42   46.4 deg  2026-11-03 19:10:49  |  2026-11-04 00:36:35  2026-11-04 00:38:42  2026-11-04 00:40:49
```
3. Bad input gives a one-line error and exit code 1:
```
> main.py predict --tle data/iss.tle --lat 95
error: --lat must be between -90 and 90
```
(The wide table is trimmed here to 2 to 4 rows; the real output may have more.)

## Tests
PowerShell: `.\.venv\Scripts\python.exe -m pytest -q`
Linux/macOS: `./.venv/bin/python -m pytest -q`

## How it works
- `src/tle.py` reads the TLE, builds a Skyfield `EarthSatellite`, and checks the epoch age (warns after 7 days).
- `src/passes.py` calls `find_events` with the minimum elevation. Event 0 is rise, 1 is highest point, 2 is set.
- Skyfield uses its built-in timescale, so nothing is downloaded.
- All times are UTC inside the code. IST (UTC+05:30) is added only when printing.
- Passes cut off by the start or end of the window are skipped, because they lack a full rise or set.
