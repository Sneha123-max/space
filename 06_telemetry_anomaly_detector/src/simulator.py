"""Makes SIMULATED telemetry: healthy values + noise + injected faults."""
import math
import random
from datetime import timedelta

from src import config


def _fault_windows(samples: int) -> list[tuple[str, float, int, int]]:
    """Faults as (channel, forced value, first index, last index).

    Positions are fractions of the run so any --samples size gets the faults.
    """
    def at(fraction: float) -> int:
        return int(samples * fraction)

    return [
        ("battery_v", 6.5, at(0.13), at(0.13)),    # 1-sample glitch: debounce must ignore it
        ("battery_v", 7.0, at(0.27), at(0.35)),    # sag below warning (7.2 V)
        ("battery_v", 6.5, at(0.50), at(0.57)),    # deep sag below critical (6.8 V)
        ("temp_c", 38.0, at(0.67), at(0.77)),      # heating above warning (35 C)
        ("temp_c", 48.0, at(0.80), at(0.87)),      # overheating above critical (45 C)
    ]


def generate(samples: int, seed: int) -> list[dict]:
    """Return a list of SIMULATED samples. Same seed -> same data."""
    rng = random.Random(seed)  # own generator, so results are repeatable
    windows = _fault_windows(samples)
    rows = []
    for i in range(samples):
        # Healthy values: a slow wave (orbit day/night) plus random noise.
        battery = config.BATTERY_NOMINAL_V + 0.15 * math.sin(i / 20) + rng.gauss(0, 0.04)
        temp = config.TEMP_NOMINAL_C + 4 * math.sin(i / 25) + rng.gauss(0, 0.5)
        values = {"battery_v": battery, "temp_c": temp}

        # Injected faults replace the healthy value (plus a little noise).
        for channel, forced, first, last in windows:
            if first <= i <= last:
                values[channel] = forced + rng.gauss(0, 0.03 if channel == "battery_v" else 0.3)

        stamp = config.START_UTC + timedelta(seconds=i * config.SAMPLE_SECONDS)
        rows.append({
            "timestamp_utc": stamp.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "battery_v": round(values["battery_v"], 3),
            "temp_c": round(values["temp_c"], 2),
        })
    return rows
