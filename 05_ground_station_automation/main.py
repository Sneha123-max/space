"""Ground station automation: build a contact schedule and check logs."""
import argparse
import sys
from datetime import date
from pathlib import Path

from src.logcheck import format_summary, scan_dir
from src.schedule import build_schedule


def cmd_schedule(args: argparse.Namespace) -> int:
    try:
        day = date.fromisoformat(args.date)
    except ValueError:
        print("error: --date must look like 2026-11-02", file=sys.stderr)
        return 2
    out_file = build_schedule(day, Path(args.pass_file), Path(args.out_dir))
    print(f"Wrote {out_file}")
    return 0


def cmd_check_logs(args: argparse.Namespace) -> int:
    results = scan_dir(Path(args.log_dir))
    print(format_summary(results))
    # Only fail on MISSED when asked, so the plain command is safe to explore.
    if args.fail_on_missed and any(r["missed"] for r in results):
        return 1
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Ground station automation tools.")
    sub = parser.add_subparsers(dest="command")

    p = sub.add_parser("schedule", help="build the daily contact schedule file")
    p.add_argument("--date", required=True, help="UTC day, e.g. 2026-11-02")
    p.add_argument("--pass-file", default="data/pass_times.csv", help="CSV of pass times")
    p.add_argument("--out-dir", default="output", help="where to write the schedule")
    p.set_defaults(func=cmd_schedule)

    p = sub.add_parser("check-logs", help="scan logs for ERROR and MISSED lines")
    p.add_argument("--log-dir", default="logs", help="folder with *.log files")
    p.add_argument("--fail-on-missed", action="store_true",
                   help="exit with code 1 if any MISSED line is found")
    p.set_defaults(func=cmd_check_logs)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return 0
    try:
        return args.func(args)
    except ValueError as err:
        # User mistakes (bad file, bad data) get one clear line, no stack trace.
        print(f"error: {err}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
