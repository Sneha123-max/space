"""All settings in ONE place: limits, debounce size, labels, start time."""
from datetime import datetime, timezone

# Every line we print or write starts with this tag (the data is not real).
LABEL = "[SIMULATED]"

# Limits per channel. "low" channels alarm when BELOW the limit,
# "high" channels alarm when ABOVE the limit.
LIMITS = {
    "battery_v": {"unit": "V", "direction": "low", "warning": 7.2, "critical": 6.8},
    "temp_c": {"unit": "C", "direction": "high", "warning": 35.0, "critical": 45.0},
}

# Debounce: a state change needs this many samples in a row.
DEBOUNCE_N = 3

# Simulated sampling: fixed UTC start time and one sample every 10 seconds.
START_UTC = datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
SAMPLE_SECONDS = 10

# Normal (healthy) behaviour of the simulated spacecraft.
BATTERY_NOMINAL_V = 8.0
TEMP_NOMINAL_C = 25.0
