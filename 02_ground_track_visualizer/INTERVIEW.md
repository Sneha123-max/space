Interview notes: Ground Track Visualizer
Concept: a ground track is the path of the point directly below a satellite as it orbits over the rotating Earth.
Input: a TLE (two-line element set) holds the orbit numbers; mine is a bundled ISS sample, so no internet is needed.
Stack: Python, Skyfield (SGP4 propagation and wgs84.subpoint), numpy, matplotlib (Agg backend), argparse, pytest.
Steps: load the TLE, make a time grid, propagate, convert each position to latitude and longitude.
Plot: a plain lat/lon grid with matplotlib only, so no map libraries or downloads; I mark the ground station on it.
Challenge: longitude wraps from +180 to -180, which draws a false line across the whole map.
Fix: split the track into segments wherever longitude jumps by more than 180 degrees, and draw each segment separately.
Result: the ISS (51.6 degree inclination) never goes beyond about 52 degrees latitude, and a test checks this.
Honest limits: TLE accuracy decays over days, and the data here is a sample, not live.
Explain it as: "Where on Earth is the satellite right now, and when does it pass near my ground station?"
