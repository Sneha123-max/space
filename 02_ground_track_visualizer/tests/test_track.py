import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from src.track import compute_track, load_satellite, split_at_dateline

ROOT = Path(__file__).resolve().parent.parent
TLE = str(ROOT / "data" / "iss.tle")


def test_iss_track_stays_within_inclination():
    sat, ts = load_satellite(TLE)
    lats, lons, _ = compute_track(sat, ts, hours=3, step_seconds=60)
    assert len(lats) == 181
    assert np.max(np.abs(lats)) <= 52.0  # ISS inclination is about 51.6 deg (geodetic lat adds a little)
    assert np.all(np.abs(lons) <= 180)


def test_split_at_dateline_breaks_on_big_jump():
    lats = np.array([0.0, 1.0, 2.0, 3.0])
    lons = np.array([170.0, 179.0, -179.0, -170.0])
    segments = split_at_dateline(lats, lons)
    assert len(segments) == 2
    assert list(segments[0][1]) == [170.0, 179.0]
    assert list(segments[1][1]) == [-179.0, -170.0]


def test_real_track_has_no_jump_over_180_inside_a_segment():
    sat, ts = load_satellite(TLE)
    lats, lons, _ = compute_track(sat, ts, hours=6, step_seconds=60)
    segments = split_at_dateline(lats, lons)
    assert len(segments) > 1  # 6 hours must cross the edge at least once
    for _, seg_lons in segments:
        assert np.all(np.abs(np.diff(seg_lons)) <= 180)


def test_missing_tle_raises_clear_error():
    with pytest.raises(ValueError, match="not found"):
        load_satellite("no_such_file.tle")


def test_cli_creates_png_and_bad_input_exits_nonzero(tmp_path):
    out = tmp_path / "sub" / "t.png"  # the sub folder does not exist yet
    ok = subprocess.run([sys.executable, "main.py", "plot", "--hours", "1", "--out", str(out)],
                        cwd=ROOT, capture_output=True, text=True)
    assert ok.returncode == 0 and out.stat().st_size > 1000
    bad = subprocess.run([sys.executable, "main.py", "plot", "--station", "99", "0", "--out", str(out)],
                         cwd=ROOT, capture_output=True, text=True)
    assert bad.returncode != 0 and "Traceback" not in bad.stderr
