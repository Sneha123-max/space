from datetime import datetime, timezone

import pytest

from src import config, loader, scheduler
from src.models import Request


def utc(h, m, s=0):
    return datetime(2026, 11, 10, h, m, s, tzinfo=timezone.utc)


def test_expand_request_exact_times():
    cmds = scheduler.expand_request(Request("R1", utc(2, 0), 120, "X"))
    assert [c.step for c in cmds] == ["POWER_ON", "POINT", "CAPTURE", "SAVE"]
    assert cmds[1].time == utc(2, 0, 30)                      # POINT = +30 s
    assert cmds[2].time == utc(2, 0, 30 + config.POINT_TO_CAPTURE_S)
    assert cmds[3].time == utc(2, 3, 0)   # capture 02:00:50 + 120 s + 10 s


def test_overlap_detected_and_clean_schedule_is_quiet():
    a = Request("A", utc(2, 0), 120, "X")
    overlapping = Request("B", utc(2, 1), 60, "Y")
    far = Request("C", utc(3, 0), 60, "Z")
    assert any("OVERLAP" in w for w in scheduler.find_warnings([a, overlapping]))
    assert scheduler.find_warnings([a, far]) == []


def test_too_close_warning_and_collision():
    a = Request("A", utc(2, 0), 120, "X")           # ends 02:03:00
    close = Request("B", utc(2, 3, 30), 60, "Y")    # 30 s gap < 60 s
    assert any("TOO CLOSE" in w for w in scheduler.find_warnings([a, close]))
    same = Request("C", utc(2, 0), 120, "Y")        # identical timing -> collisions
    assert any("COLLISION" in w for w in scheduler.find_warnings([a, same]))


def test_loader_sorts_and_rejects_bad_input(tmp_path):
    good = tmp_path / "g.csv"
    good.write_text("request_id,start_utc,duration_s,target\n"
                    "B,2026-11-10T03:00:00Z,10,X\nA,2026-11-10T02:00:00Z,10,Y\n")
    assert [r.request_id for r in loader.load_requests(str(good))] == ["A", "B"]

    bad = tmp_path / "b.csv"
    bad.write_text("request_id,start_utc,duration_s,target\nA,not-a-time,10,X\n")
    with pytest.raises(ValueError, match="bad start_utc"):
        loader.load_requests(str(bad))
    with pytest.raises(ValueError, match="not found"):
        loader.load_requests(str(tmp_path / "nope.csv"))
