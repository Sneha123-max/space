from datetime import date
from pathlib import Path

import pytest

from src.schedule import build_schedule, passes_for_day, read_passes

HEADER = "station,aos_utc,los_utc,max_elev_deg\n"


def write_csv(tmp_path: Path, rows: str) -> Path:
    f = tmp_path / "p.csv"
    f.write_text(HEADER + rows)
    return f


def test_only_requested_day_is_kept_and_sorted(tmp_path):
    f = write_csv(tmp_path,
                  "B,2026-11-02T10:00:00,2026-11-02T10:10:00,30\n"
                  "A,2026-11-02T02:00:00,2026-11-02T02:10:00,40\n"
                  "C,2026-11-03T02:00:00,2026-11-03T02:10:00,50\n")
    result = passes_for_day(read_passes(f), date(2026, 11, 2))
    assert [p["station"] for p in result] == ["A", "B"]


def test_schedule_file_shows_utc_and_ist(tmp_path):
    f = write_csv(tmp_path, "A,2026-11-02T03:12:00,2026-11-02T03:22:30,47.5\n")
    out = build_schedule(date(2026, 11, 2), f, tmp_path / "out")
    text = out.read_text()
    assert out.name == "contacts_2026-11-02.txt"
    assert "UTC 03:12:00-03:22:30" in text
    assert "IST 08:42:00-08:52:30" in text  # UTC + 5:30


def test_bad_row_raises_value_error(tmp_path):
    f = write_csv(tmp_path, "A,not-a-time,2026-11-02T03:22:30,47.5\n")
    with pytest.raises(ValueError):
        read_passes(f)
