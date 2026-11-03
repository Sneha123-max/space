# Run the schedule builder and the log checker. Exit 1 if any MISSED line is found.
# Works from any directory (Task Scheduler starts in System32), so we move to this script's folder.
Set-Location $PSScriptRoot

# Prefer the project venv; fall back to python on PATH.
$py = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $py)) { $py = "python" }

$today = (Get-Date).ToUniversalTime().ToString("yyyy-MM-dd")   # today's date in UTC
& $py main.py schedule --date $today --pass-file data/pass_times.csv
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& $py main.py check-logs --log-dir logs --fail-on-missed
exit $LASTEXITCODE
