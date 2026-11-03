import subprocess
import sys
from datetime import datetime, timezone

import pytest

from src.loader import InputError, Request, Window, load_requests
from src.planner import plan


def t(hhmm: str) -> datetime:
    h, m = hhmm.split(":")
    return datetime(2026, 3, 10, int(h), int(m), tzinfo=timezone.utc)


def req(rid, pri, start, end, wh=10, mb=10):
    return Request(rid, pri, t(start), t(end), wh, mb)


WINDOWS = [Window(t("08:00"), t("09:00"))]


def reasons(results):
    return {r.request.request_id: r.reason for r in results}


def test_accepts_request_inside_window():
    res = plan([req("A", 1, "08:10", "08:20")], WINDOWS, 100, 100)
    assert res[0].accepted


def test_rejects_request_straddling_window_edge():
    res = plan([req("A", 1, "08:50", "09:10")], WINDOWS, 100, 100)
    assert reasons(res)["A"] == "no ground station visibility"


def test_overlap_rejects_lower_priority():
    res = plan([req("LOW", 2, "08:15", "08:30"), req("HIGH", 1, "08:10", "08:20")], WINDOWS, 100, 100)
    assert reasons(res) == {"HIGH": "ok", "LOW": "overlaps HIGH"}


def test_battery_and_storage_budgets():
    res = plan([req("A", 1, "08:00", "08:10", wh=60), req("B", 2, "08:20", "08:30", wh=60),
                req("C", 3, "08:40", "08:50", wh=10, mb=200)], WINDOWS, 100, 100)
    assert reasons(res)["B"] == "battery budget exceeded"
    assert reasons(res)["C"] == "storage budget exceeded"


def test_bad_csv_gives_clear_error(tmp_path):
    f = tmp_path / "bad.csv"
    f.write_text("request_id,priority\nA,1\n")
    with pytest.raises(InputError, match="missing column"):
        load_requests(str(f))


def test_cli_missing_file_exits_nonzero():
    out = subprocess.run([sys.executable, "main.py", "plan", "--requests", "nope.csv"],
                         capture_output=True, text=True)
    assert out.returncode != 0 and "Traceback" not in out.stderr
