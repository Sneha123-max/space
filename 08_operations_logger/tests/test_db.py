from datetime import datetime, timedelta, timezone

import pytest

from src import db
from src.timeutil import to_text, utc_text_to_ist


@pytest.fixture
def conn(tmp_path):
    # Each test gets its own throwaway database file.
    connection = db.connect(tmp_path / "test.db")
    yield connection
    connection.close()


def test_event_defaults_closed_and_anomaly_defaults_open(conn):
    ev = db.add_entry(conn, "EVENT", "INFO", "pass started")
    an = db.add_entry(conn, "ANOMALY", "WARNING", "temp high")
    rows = {r["id"]: r["status"] for r in db.list_entries(conn)}
    assert rows[ev] == "CLOSED"
    assert rows[an] == "OPEN"


def test_close_entry_and_errors(conn):
    an = db.add_entry(conn, "ANOMALY", "CRITICAL", "wheel fault")
    db.close_entry(conn, an)
    assert db.list_entries(conn, "OPEN") == []
    with pytest.raises(ValueError):
        db.close_entry(conn, an)  # already closed
    with pytest.raises(ValueError):
        db.close_entry(conn, 999)  # missing


def test_bad_input_rejected(conn):
    with pytest.raises(ValueError):
        db.add_entry(conn, "EVENT", "LOUD", "x")
    with pytest.raises(ValueError):
        db.add_entry(conn, "EVENT", "INFO", "   ")
    with pytest.raises(ValueError):
        db.add_entry(conn, "EVENT", "INFO", "x", ts_utc="yesterday")


def test_sql_injection_text_is_stored_literally(conn):
    nasty = "x'); DROP TABLE entries; --"
    db.add_entry(conn, "EVENT", "INFO", nasty)
    assert db.list_entries(conn)[0]["action"] == nasty


def test_handover_window_and_open_issues(conn):
    now = datetime(2026, 1, 10, 12, 0, tzinfo=timezone.utc)
    old = to_text(now - timedelta(hours=30))
    recent = to_text(now - timedelta(hours=2))
    db.add_entry(conn, "EVENT", "INFO", "old event", old)
    db.add_entry(conn, "EVENT", "INFO", "recent event", recent)
    db.add_entry(conn, "ANOMALY", "WARNING", "old but open", old)
    open_issues, events = db.handover_data(conn, 24, now)
    assert [r["action"] for r in open_issues] == ["old but open"]
    assert [r["action"] for r in events] == ["recent event"]


def test_ist_conversion():
    assert utc_text_to_ist("2026-01-10 12:00:00") == "2026-01-10 17:30:00"
