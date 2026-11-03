Interview notes: Telemetry Anomaly Detector (simulated data)
Concept: a spacecraft sends telemetry; ground software checks it against warning and critical limits.
This project does that on SIMULATED battery voltage and temperature, clearly labelled [SIMULATED].
Tech stack: pure Python standard library (random, csv, argparse), pytest for tests.
The simulator uses a fixed seed, so the same data and the same alerts appear every run.
Limits live in one config file: battery below 7.2 V warns, below 6.8 V is critical; temperature above 35 C or 45 C.
Challenge: noise makes a value jump across a limit for one sample and the alert flaps on and off.
Fix: debounce - an alert fires only after 3 samples in a row, and clears only after 3 normal samples.
I proved it with a test: a one-sample glitch gives no alert, three bad samples give one alert.
Alerts go to the terminal and output/alerts.log, with UTC time inside and IST only for display.
To explain it: data comes in, each sample gets a level, debounce confirms it, then an alert line is written.
