"""Operations Logger CLI: log events and anomalies, close issues, print a handover."""
import argparse
import sqlite3
import sys
from pathlib import Path

from src import db, report

DEFAULT_DB = Path(__file__).parent / "data" / "ops_log.db"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Operations Logger (stored in UTC, shown in UTC and IST)")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB, help="path to the SQLite file")
    sub = parser.add_subparsers(dest="command")

    add = sub.add_parser("add", help="add an event or anomaly")
    add.add_argument("--kind", required=True, choices=db.KINDS, type=str.upper)
    add.add_argument("--severity", required=True, choices=db.SEVERITIES, type=str.upper)
    add.add_argument("--action", required=True, help="what happened / what was done")
    add.add_argument("--ts", help="UTC time 'YYYY-MM-DD HH:MM:SS' (default: now)")

    lst = sub.add_parser("list", help="list entries")
    lst.add_argument("--status", choices=("OPEN", "CLOSED"), type=str.upper)

    close = sub.add_parser("close", help="close an open issue")
    close.add_argument("id", type=int)

    hand = sub.add_parser("handover", help="print the shift handover report")
    hand.add_argument("--hours", type=int, default=24, help="how far back to show events")
    return parser


def run(args) -> None:
    conn = db.connect(args.db)
    try:
        if args.command == "add":
            new_id = db.add_entry(conn, args.kind, args.severity, args.action, args.ts)
            print(f"Added entry {new_id}")
        elif args.command == "list":
            print(report.format_list(db.list_entries(conn, args.status)))
        elif args.command == "close":
            db.close_entry(conn, args.id)
            print(f"Closed entry {args.id}")
        elif args.command == "handover":
            open_issues, recent = db.handover_data(conn, args.hours)
            print(report.format_handover(open_issues, recent, args.hours))
    finally:
        conn.close()


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        return 0
    try:
        run(args)
    except (ValueError, sqlite3.Error) as err:  # user mistakes -> one clean line
        print(f"error: {err}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
