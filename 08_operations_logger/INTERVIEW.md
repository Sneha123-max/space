Operations Logger - interview notes
Concept: a shift log where controllers record events and anomalies, then hand open issues to the next shift.
Real control rooms rely on clear logs and handovers so nothing important is forgotten.
Stack: Python, argparse for the CLI, sqlite3 (built in) for storage, pytest for tests.
All times are stored in UTC and converted to IST only when shown, to avoid time zone mistakes.
Anomalies start OPEN and stay in the handover until someone closes them; events start CLOSED.
Challenge: choosing a time format that SQL can compare, so "last 24 hours" works with a simple query.
I used 'YYYY-MM-DD HH:MM:SS' text in UTC, which sorts correctly as plain text.
Safety: every SQL query uses ? placeholders, and a test proves a DROP TABLE text is stored harmlessly.
To explain it: walk through add, then list, then close, then handover, showing the SQLite table each time.
The sample data is SIMULATED, and the DB logic sits in one small module so it is easy to test.
