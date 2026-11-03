# Ground Station Automation Scripts

## 1. What it does
- Builds a daily contact schedule file (UTC and IST) from a CSV of satellite pass times.
- Scans station log files for ERROR and MISSED lines and prints counts plus the lines.
- Wrapper scripts (`run_all.sh`, `run_all.ps1`) run both and exit non-zero on any MISSED line, so a timer can alert you.

## 2. Setup
Windows (PowerShell):
```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```
Linux/macOS:
```bash
python3 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
```

## 3. Run
No seed step. Sample data is bundled in `data/` and `logs/` (SIMULATED).
```powershell
.\.venv\Scripts\python.exe main.py schedule --date 2026-11-02 --pass-file data/pass_times.csv
.\.venv\Scripts\python.exe main.py check-logs --log-dir logs
```
Run both together (Windows `.\run_all.ps1`, Linux/macOS `./run_all.sh`; first run `chmod +x run_all.sh`).
The wrappers use today's UTC date. The sample logs contain one MISSED line on purpose, so the wrappers exit with code 1.

## 4. Example commands

1. Build a schedule:
```
> python main.py schedule --date 2026-11-02 --pass-file data/pass_times.csv
Wrote output\contacts_2026-11-02.txt
```
The file contains:
```
Contact schedule for 2026-11-02 (UTC day)

01 Bengaluru   UTC 03:12:00-03:22:30 | IST 08:42:00-08:52:30 | 10.5 min | max elev 47.5 deg
02 Lucknow     UTC 05:40:10-05:49:00 | IST 11:10:10-11:19:00 | 8.8 min | max elev 22.1 deg
03 Port Blair  UTC 09:05:00-09:14:45 | IST 14:35:00-14:44:45 | 9.8 min | max elev 63.8 deg
04 Bengaluru   UTC 18:30:20-18:41:00 | IST 00:00:20-00:11:00 | 10.7 min | max elev 35.0 deg
05 Lucknow     UTC 23:50:00-00:00:30 | IST 05:20:00-05:30:30 | 10.5 min | max elev 18.4 deg

Total contacts: 5
```

2. Check logs:
```
> python main.py check-logs --log-dir logs
station_bengaluru.log: 1 ERROR, 1 MISSED
    2026-11-02 03:15:40 ERROR Telemetry frame CRC mismatch (frame 4821)
    2026-11-02 18:35:11 MISSED Scheduled command window skipped (operator not ready)
station_lucknow.log: 1 ERROR, 0 MISSED
    2026-11-02 05:40:10 ERROR Receiver synthesiser unlock at AOS
station_port_blair.log: 0 ERROR, 0 MISSED
TOTAL: 2 ERROR, 1 MISSED in 3 files
```

3. Bad input gives one clear line and exit code 2:
```
> python main.py schedule --date nope
error: --date must look like 2026-11-02
```

## 5. Tests
Windows: `.\.venv\Scripts\python.exe -m pytest -q`
Linux/macOS: `./.venv/bin/python -m pytest -q`

## 6. How it works
`schedule` reads the CSV, keeps passes whose AOS (acquisition of signal) is on the chosen UTC day, sorts them, and writes `output/contacts_YYYY-MM-DD.txt`. Times are stored in UTC and converted to IST (UTC+05:30) only for the text.
`check-logs` reads every `*.log` in a folder and looks at the third word of each line (the level). Only exact `ERROR` and `MISSED` levels count. With `--fail-on-missed` it exits 1 if any MISSED line exists.
The run_all scripts move into their own folder first, so they work no matter where the timer starts them.

### Run on a timer (local only; nothing is registered by this project)

**Linux/macOS cron.** Replace `/path/to/05_ground_station_automation` with the full path of this folder. Edit with `crontab -e`, and add this line to run daily at 00:05 (log output is appended to a file):
```
5 0 * * * /bin/bash /path/to/05_ground_station_automation/run_all.sh >> /path/to/05_ground_station_automation/cron.log 2>&1
```
Cron uses the machine's local time zone. The script itself uses the UTC date.

**Windows Task Scheduler.** Replace `C:\path\to\05_ground_station_automation` with the full path of this folder, then run once in PowerShell:
```powershell
schtasks /Create /TN "GroundStationDaily" /SC DAILY /ST 00:05 /TR 'powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\path\to\05_ground_station_automation\run_all.ps1"'
```
This form is checked for PowerShell 7 (the quotes inside the single quotes reach schtasks intact); the command itself was not run. In classic Windows PowerShell 5.1 inner quotes get dropped, which breaks paths with spaces. From `cmd.exe` use this instead:
```
schtasks /Create /TN "GroundStationDaily" /SC DAILY /ST 00:05 /TR "powershell.exe -NoProfile -ExecutionPolicy Bypass -File \"C:\path\to\05_ground_station_automation\run_all.ps1\""
un_all.ps1\""
```
Check it with `schtasks /Query /TN "GroundStationDaily"` and remove it with `schtasks /Delete /TN "GroundStationDaily" /F`. Task Scheduler records the script's exit code (1 means a MISSED line was found) as the task's "Last Run Result".
