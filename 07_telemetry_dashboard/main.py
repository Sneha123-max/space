"""CLI entry point for the SIMULATED telemetry dashboard."""
import argparse
import sys

from src.dashboard import run_live


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="SIMULATED telemetry dashboard (terminal).")
    sub = parser.add_subparsers(dest="command")
    live = sub.add_parser("live", help="show the live-updating dashboard")
    live.add_argument("--db", default="data/telemetry.db", help="path to the SQLite file")
    live.add_argument("--refresh", type=float, default=1.0, help="seconds between redraws")
    live.add_argument("--max-seconds", type=float, default=None,
                      help="exit after this many seconds (default: run until Ctrl+C)")
    live.add_argument("--feed", action="store_true",
                      help="also append one new SIMULATED row per refresh so the data moves")
    return parser


def main() -> int:
    # Block characters need UTF-8; Windows consoles/pipes often default to cp1252.
    sys.stdout.reconfigure(encoding="utf-8")
    parser = build_parser()
    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        return 0
    if args.refresh <= 0:
        print("error: --refresh must be greater than 0", file=sys.stderr)
        return 2
    try:
        run_live(args.db, args.refresh, args.max_seconds, args.feed)
    except FileNotFoundError as err:
        print(f"error: {err}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
