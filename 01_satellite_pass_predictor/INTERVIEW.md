Interview notes: Satellite Pass Predictor
Concept: it tells you when a satellite like the ISS is visible above the horizon from your location.
A pass has three moments: rise, highest point (culmination) and set.
Input is a TLE, a text file with the satellite's orbit numbers at a given epoch (date).
Tech stack: Python, Skyfield (SGP4 orbit maths), argparse for the CLI, pytest for tests.
Skyfield's find_events does the search; I choose the minimum elevation, e.g. 10 degrees.
Challenge: TLEs go stale, so I warn when the epoch is over 7 days old; my sample file is deliberately old.
Another challenge: time zones. I keep UTC inside the code and convert to IST (UTC+5:30) only for display.
It runs offline because Skyfield has a built-in timescale and I bundle the TLE.
To explain it: give a TLE and a place, get a table of when to look up and how high it climbs.
Next step would be fetching fresh TLEs automatically and adding azimuth (compass direction).
