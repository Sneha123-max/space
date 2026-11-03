from src import db
from src.dashboard import build_screen, to_ist
from src.simulate import make_samples
from src.trend import BLOCKS, sparkline


def test_sparkline_rising_uses_every_block():
    assert sparkline([1, 2, 3, 4, 5, 6, 7, 8]) == BLOCKS


def test_sparkline_flat_and_empty():
    assert sparkline([]) == ""
    assert sparkline([5, 5, 5]) == BLOCKS[3] * 3


def test_samples_are_repeatable():
    assert make_samples(50, seed=42) == make_samples(50, seed=42)
    assert len(make_samples(500)) == 500


def test_ist_conversion():
    assert to_ist("2025-01-01T00:00:00Z") == "2025-01-01 05:30:00 IST"


def test_db_roundtrip_and_screen(tmp_path):
    conn = db.reset_db(str(tmp_path / "t.db"))
    db.insert_samples(conn, make_samples(100))
    rows = db.latest_rows(conn, 40)
    assert len(rows) == 40
    assert rows[0][0] < rows[-1][0]  # oldest first
    bmin, bmax, _, _ = db.min_max(conn)
    assert bmin < bmax
    assert "SIMULATED" in build_screen(conn).title
