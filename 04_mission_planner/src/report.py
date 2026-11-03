"""Prints the accepted and rejected tables. Times are shown in IST."""
from datetime import datetime, timedelta, timezone

from .planner import Result

IST = timezone(timedelta(hours=5, minutes=30))  # display only; data stays UTC


def ist(t: datetime) -> str:
    return t.astimezone(IST).strftime("%H:%M")


def _table(headers: list[str], rows: list[list]) -> str:
    """Make a simple aligned text table."""
    widths = [max(len(str(x)) for x in col) for col in zip(headers, *rows)]

    def line(cells) -> str:
        return "  ".join(str(c).ljust(w) for c, w in zip(cells, widths)).rstrip()

    separator = "  ".join("-" * w for w in widths)
    return "\n".join([line(headers), separator] + [line(r) for r in rows])


def print_report(results: list[Result], battery_wh: float, storage_mb: float) -> None:
    acc = [r for r in results if r.accepted]
    rej = [r for r in results if not r.accepted]

    print("SIMULATED sample data. Times shown in IST (UTC+05:30)\n")
    print("ACCEPTED")
    rows = [[r.request.request_id, r.request.priority, ist(r.request.start), ist(r.request.end),
             f"{r.request.battery_wh:g}", f"{r.request.storage_mb:g}"] for r in acc]
    print(_table(["ID", "Pri", "Start", "End", "Wh", "MB"], rows) if rows else "(none)")

    print("\nREJECTED")
    rows = [[r.request.request_id, r.request.priority, ist(r.request.start), ist(r.request.end),
             r.reason] for r in rej]
    print(_table(["ID", "Pri", "Start", "End", "Reason"], rows) if rows else "(none)")

    used_wh = sum(r.request.battery_wh for r in acc)
    used_mb = sum(r.request.storage_mb for r in acc)
    print(f"\nTotals: {len(acc)} accepted, {len(rej)} rejected")
    print(f"Battery: {used_wh:g} / {battery_wh:g} Wh used")
    print(f"Storage: {used_mb:g} / {storage_mb:g} MB used")
