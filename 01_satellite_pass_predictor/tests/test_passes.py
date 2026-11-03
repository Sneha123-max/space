from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from src.passes import IST, find_passes, fmt
from src.tle import InputError, epoch_warning, load_satellite

START = datetime(2026, 11, 1, tzinfo=timezone.utc)
TLE = str(Path(__file__).resolve().parent.parent / "data" / "iss.tle")


def test_passes_are_ordered_and_above_min_elevation():
    sat = load_satellite(TLE)
    passes = find_passes(sat, 12.97, 77.59, START, 48, 10)
    assert passes, "ISS should pass over Bangalore in 48 hours"
    for p in passes:
        assert p.rise < p.culminate < p.set
        assert p.max_elev >= 10


def test_higher_min_elevation_gives_fewer_or_equal_passes():
    sat = load_satellite(TLE)
    low = find_passes(sat, 12.97, 77.59, START, 48, 10)
    high = find_passes(sat, 12.97, 77.59, START, 48, 40)
    assert len(high) <= len(low)


def test_ist_is_utc_plus_530():
    t = datetime(2026, 11, 1, 0, 0, 0, tzinfo=timezone.utc)
    assert fmt(t, IST) == "2026-11-01 05:30:00"


def test_old_tle_warns_and_fresh_does_not():
    sat = load_satellite(TLE)
    epoch = sat.epoch.utc_datetime()
    assert "WARNING" in epoch_warning(sat, epoch + timedelta(days=8))
    assert epoch_warning(sat, epoch + timedelta(days=2)) is None


def test_missing_file_is_input_error():
    with pytest.raises(InputError):
        load_satellite("data/nope.tle")
