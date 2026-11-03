from src.detector import classify, detect
from src.simulator import generate


def rows_from(voltages):
    """Build rows with healthy temperature and the given battery voltages."""
    return [
        {"timestamp_utc": f"2026-01-01T00:00:{i:02d}Z", "battery_v": v, "temp_c": 25.0}
        for i, v in enumerate(voltages)
    ]


def test_classify_limits():
    assert classify("battery_v", 7.5) == "NORMAL"
    assert classify("battery_v", 7.0) == "WARNING"
    assert classify("battery_v", 6.5) == "CRITICAL"
    assert classify("temp_c", 40.0) == "WARNING"
    assert classify("temp_c", 50.0) == "CRITICAL"


def test_single_glitch_is_ignored():
    # One bad sample must not raise an alert (debounce).
    assert detect(rows_from([8.0, 8.0, 6.5, 8.0, 8.0, 8.0])) == []


def test_alert_fires_on_third_sample_then_clears_after_three_normal():
    alerts = detect(rows_from([8.0, 7.0, 7.0, 7.0, 8.0, 8.0, 8.0]))
    assert len(alerts) == 2
    assert "WARNING" in alerts[0] and "00:00:03Z" in alerts[0]
    assert "CLEARED" in alerts[1] and "00:00:06Z" in alerts[1]


def test_every_alert_line_is_labelled_and_simulation_is_deterministic():
    rows = generate(300, 42)
    assert rows == generate(300, 42)
    alerts = detect(rows)
    assert alerts and all(a.startswith("[SIMULATED]") for a in alerts)
