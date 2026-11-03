# Ground Track Visualizer

## What it does
Reads a bundled ISS sample TLE and uses Skyfield to compute the point on Earth under the satellite over time.
Draws that ground track on a plain lat/lon grid (matplotlib only, no map files), split at the +/-180 edge.
Marks a ground station (default Bangalore) and saves everything as a PNG. Fully offline.

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
No seed step needed. Demo (Windows; on Linux use `./.venv/bin/python`):
```
.\.venv\Scripts\python.exe main.py plot --tle data/iss.tle --hours 3 --step-seconds 60 --station 12.97 77.59 --out output/ground_track.png
```
The `output/` folder is created if missing. Orbit data is a SAMPLE TLE (epoch 2024-01-01), not live data.

## Example commands
1. Default demo:
```
> main.py plot --tle data/iss.tle --hours 3 --step-seconds 60 --station 12.97 77.59 --out output/ground_track.png
Satellite: ISS (ZARYA) - SAMPLE TLE (bundled, epoch 2024-01-01)
Start (UTC): 2024-01-01 12:25:40
Points: 181  Segments (after dateline split): 3
Saved: output/ground_track.png
```
2. Six hours from a chosen UTC time, station in Sydney:
```
> main.py plot --hours 6 --start 2024-01-01T12:00:00 --station -33.87 151.21 --out output/sydney_6h.png
Satellite: ISS (ZARYA) - SAMPLE TLE (bundled, epoch 2024-01-01)
Start (UTC): 2024-01-01 12:00:00
Points: 361  Segments (after dateline split): 5
Saved: output/sydney_6h.png
```
3. Bad input gives one clear line and exit code 1:
```
> main.py plot --tle nope.tle
Error: TLE file not found: nope.tle
```

## Tests
PowerShell: `.\.venv\Scripts\python.exe -m pytest -q`
Linux/macOS: `./.venv/bin/python -m pytest -q`

## How it works
- `src/track.py` loads the TLE, builds a Skyfield satellite, makes a list of times, and calls `wgs84.subpoint()` to get latitude and longitude for each time.
- Longitude wraps from +180 to -180, so `split_at_dateline` cuts the track into pieces wherever longitude jumps by more than 180 degrees. No line is drawn across the map.
- `src/plot.py` draws each piece on a lat/lon grid, marks start, end and the ground station, and saves a PNG using the Agg backend (no window).
- Times are UTC inside the program. Time data is built into Skyfield (`load.timescale(builtin=True)`), so no download is needed.
