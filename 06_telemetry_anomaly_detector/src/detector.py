"""Limit checking plus debounce. Pure logic, no printing or files."""
from datetime import datetime, timedelta

from src import config

NORMAL, WARNING, CRITICAL = "NORMAL", "WARNING", "CRITICAL"


def classify(channel: str, value: float) -> str:
    """Raw level of ONE sample against the limits (no debounce yet)."""
    limits = config.LIMITS[channel]
    if limits["direction"] == "low":
        if value < limits["critical"]:
            return CRITICAL
        if value < limits["warning"]:
            return WARNING
    else:
        if value > limits["critical"]:
            return CRITICAL
        if value > limits["warning"]:
            return WARNING
    return NORMAL


def to_ist(utc_text: str) -> str:
    """Convert a UTC timestamp text to IST (UTC+05:30) for display only."""
    utc = datetime.strptime(utc_text, "%Y-%m-%dT%H:%M:%SZ")
    return (utc + timedelta(hours=5, minutes=30)).strftime("%H:%M:%S IST")


def detect(rows: list[dict], n: int = config.DEBOUNCE_N) -> list[str]:
    """Walk through the samples and return alert lines.

    Debounce rule: the confirmed state only changes after the SAME new raw
    level is seen n samples in a row. This applies to raising an alert
    and to clearing it, so one noisy sample cannot make the alert flap.
    """
    alerts = []  # (timestamp, line) pairs so we can sort by time later
    for channel, limits in config.LIMITS.items():
        state = NORMAL      # confirmed (debounced) state
        pending = NORMAL    # raw level we are currently counting
        count = 0           # how many samples in a row showed `pending`
        for row in rows:
            value = row[channel]
            raw = classify(channel, value)
            if raw == state:
                count = 0   # sample agrees with confirmed state: nothing pending
                continue
            if raw == pending:
                count += 1
            else:
                pending, count = raw, 1   # new candidate level: start counting
            if count >= n:
                state, count = raw, 0     # held long enough: confirm the change
                stamp = row["timestamp_utc"]
                when = f"{stamp} ({to_ist(stamp)})"
                if state == NORMAL:
                    text = f"CLEARED  {channel} back to normal ({value}{limits['unit']})"
                else:
                    text = f"{state:<8} {channel} = {value}{limits['unit']}"
                alerts.append((stamp, f"{config.LABEL} {when} {text}"))
    # Sort by timestamp so both channels read in time order.
    alerts.sort(key=lambda pair: pair[0])
    return [line for _, line in alerts]
