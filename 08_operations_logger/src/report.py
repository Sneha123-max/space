"""Turn database rows into plain text for the terminal."""
from .timeutil import utc_text_to_ist

ROW_HEAD = f"{'ID':>3}  {'UTC':<19}  {'IST':<19}  {'KIND':<7}  {'SEVERITY':<8}  {'STATUS':<6}  ACTION"


def format_row(row) -> str:
    return (f"{row['id']:>3}  {row['ts_utc']:<19}  {utc_text_to_ist(row['ts_utc']):<19}  "
            f"{row['kind']:<7}  {row['severity']:<8}  {row['status']:<6}  {row['action']}")


def format_list(rows) -> str:
    if not rows:
        return "No entries found."
    return "\n".join([ROW_HEAD] + [format_row(r) for r in rows])


def _section(rows) -> list[str]:
    """Header plus rows, or 'None.' when there is nothing to show."""
    if not rows:
        return ["None."]
    return [ROW_HEAD] + [format_row(r) for r in rows]


def format_handover(open_issues, recent, hours: int) -> str:
    lines = ["SHIFT HANDOVER REPORT (times shown in UTC and IST)", "",
             f"OPEN ISSUES ({len(open_issues)})"]
    lines += _section(open_issues)
    lines += ["", f"RECENT EVENTS, CLOSED, LAST {hours} HOURS ({len(recent)})"]
    lines += _section(recent)
    return "\n".join(lines)
