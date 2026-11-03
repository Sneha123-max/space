"""Makes SIMULATED telemetry samples (no real spacecraft data)."""
import math
import random
from datetime import datetime, timedelta, timezone

START_UTC = datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc)  # fixed start so output repeats


def make_sample(index: int, rng: random.Random) -> tuple[str, float, float]:
    """Return (ts_utc, battery_v, temp_c) for sample number `index` (one per minute)."""
    ts = (START_UTC + timedelta(minutes=index)).strftime("%Y-%m-%dT%H:%M:%SZ")
    # Battery slowly swings like an orbit day/night cycle (90 samples ~ one orbit) plus noise.
    battery = 28.0 + 2.0 * math.sin(2 * math.pi * index / 90) + rng.gauss(0, 0.05)
    # Temperature follows the same cycle, shifted, with its own noise.
    temp = 20.0 + 15.0 * math.cos(2 * math.pi * index / 90) + rng.gauss(0, 0.5)
    return ts, round(battery, 2), round(temp, 1)


def make_samples(count: int, seed: int = 42) -> list[tuple[str, float, float]]:
    """Make `count` samples using a fixed seed, so every run gives the same data."""
    rng = random.Random(seed)
    return [make_sample(i, rng) for i in range(count)]
