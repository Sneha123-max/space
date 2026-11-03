#!/usr/bin/env bash
# Run the schedule builder and the log checker. Exit 1 if any MISSED line is found.
# Works from any directory (cron starts in $HOME), so we cd to this script's folder.
cd "$(dirname "$0")" || exit 2

# Prefer the project venv (Linux/macOS or Windows layout); fall back to python3.
if [ -x ./.venv/bin/python ]; then
  PY=./.venv/bin/python
elif [ -x ./.venv/Scripts/python.exe ]; then
  PY=./.venv/Scripts/python.exe
else
  PY=python3
fi

TODAY=$(date -u +%Y-%m-%d)   # today's date in UTC
"$PY" main.py schedule --date "$TODAY" --pass-file data/pass_times.csv || exit $?
"$PY" main.py check-logs --log-dir logs --fail-on-missed
