# Interview notes: Telemetry Dashboard
Concept: telemetry is a stream of spacecraft health numbers; here battery voltage and temperature are SIMULATED.
I store each sample in SQLite, then a live terminal dashboard reads the newest rows and redraws.
Stack: Python, sqlite3 from the standard library, rich (Live, Table, Panel) and pytest.
Data is made from sine waves plus noise with a fixed seed, so results are repeatable and testable.
The trend line uses the block characters ▁ to █, scaled between the lowest and highest recent value.
That drawing code is a pure function, so tests can check it without a screen.
Challenge: block characters crashed on Windows pipes (cp1252), so I set stdout to UTF-8.
Times are stored in UTC and converted to IST only for display, to avoid time-zone mistakes.
Grafana is an optional extra that I wrote a config for but did not run, and I say so honestly.
To explain it: data in, store, read latest, draw trend; a controller watches trends to spot problems early.
