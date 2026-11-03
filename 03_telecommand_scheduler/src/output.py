"""Show or save the command list. IST is only used for display."""

import csv
from datetime import datetime, timedelta
from pathlib import Path

from . import config
from .models import Command


def to_ist(moment: datetime) -> datetime:
    return moment + timedelta(hours=config.IST_OFFSET_HOURS)


def print_table(commands: list[Command]) -> None:
    print(f"{'UTC TIME':<21}{'IST TIME':<21}{'REQUEST':<9}{'STEP':<9}TARGET")
    for c in commands:
        print(f"{c.time:%Y-%m-%d %H:%M:%S}  {to_ist(c.time):%Y-%m-%d %H:%M:%S}  "
              f"{c.request_id:<9}{c.step:<9}{c.target}")


def write_csv(commands: list[Command], path: str) -> None:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)  # create output/ if missing
    with out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["time_utc", "request_id", "step", "target"])
        for c in commands:
            writer.writerow([f"{c.time:%Y-%m-%dT%H:%M:%SZ}", c.request_id, c.step, c.target])


def print_warnings(warnings: list[str]) -> None:
    if not warnings:
        print("No overlaps or collisions found.")
        return
    print(f"WARNINGS ({len(warnings)}):")
    for w in warnings:
        print(f"  - {w}")
