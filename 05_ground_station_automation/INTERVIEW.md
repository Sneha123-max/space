Interview notes: Ground Station Automation
Concept: a satellite is reachable only in short passes, so ground stations need a daily contact schedule.
The schedule builder reads pass times (AOS = signal acquired, LOS = signal lost) and lists each contact in UTC and IST.
The log checker scans station logs and counts ERROR and MISSED lines, so problems are found without reading every log.
Stack: plain Python 3 (argparse, csv, datetime, pathlib) plus pytest, with bash and PowerShell wrappers. No outside libraries.
The wrappers run both steps and exit non-zero if any pass was MISSED.
That exit code lets cron or Task Scheduler flag a bad day automatically.
Challenge: time zones. I keep everything in UTC and convert to IST (UTC+05:30) only when printing.
A pass near midnight crosses a date boundary in IST, so the code picks the day by UTC AOS time.
To explain it: schedule says what should happen, the log checker says what went wrong, the timer repeats it daily. All data is SIMULATED.
