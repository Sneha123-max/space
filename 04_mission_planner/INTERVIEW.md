Mission Planner - interview notes
Concept: a satellite can only do so much per pass, so we choose which imaging requests to run.
Each request costs battery and storage, and must happen while a ground station can see the satellite.
The planner is greedy: take the highest priority first, keep it if it still fits, otherwise reject it.
Tech stack: plain Python 3, argparse for the CLI, csv and datetime from the standard library, pytest.
All times are stored in UTC and only converted to IST when printed, to avoid time zone bugs.
Challenge: giving every rejected request exactly one clear reason, so checks run in a fixed order.
Greedy is simple and fast but not always optimal; a smarter solver could fit more requests.
To explain it: sort, loop, check four rules, update the budgets, print two tables.
Demo with the bundled SIMULATED data, then show a tight battery budget changing the result.
