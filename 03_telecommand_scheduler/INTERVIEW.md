Telecommand Scheduler - interview notes
Concept: a satellite takes pictures only if commands reach it at exact times, in the right order.
Each imaging request becomes four commands: POWER_ON, POINT, CAPTURE, SAVE.
The gaps (30 s warm-up, 20 s slew, 10 s save) are named constants in one file, src/config.py.
Tech stack: Python, argparse for the CLI, csv and datetime from the standard library, pytest for tests.
All times are UTC inside the program; IST is only added when printing a table.
Challenge: finding clashes, because one request's SAVE can still be running when the next request starts.
I solved it by sorting requests by time and comparing each request's end with the next start.
I also warn when the gap is under 60 s and when two commands share the same second.
To explain it: read the CSV, sort, expand each row into steps, check clashes, print or export.
The data is SIMULATED, but the flow matches how real operators plan a pass.
