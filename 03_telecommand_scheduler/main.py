"""Telecommand scheduler CLI. Run with --help to see usage."""

import argparse
import sys

from src import loader, output, scheduler


def run_build(args: argparse.Namespace) -> int:
    requests = loader.load_requests(args.requests)
    warnings = scheduler.find_warnings(requests)

    if args.report_only:
        # User only wants the warning list, no command list.
        output.print_warnings(warnings)
        return 0

    commands = scheduler.build_schedule(requests)
    if args.out:
        output.write_csv(commands, args.out)
        print(f"Wrote {len(commands)} commands to {args.out}")
    else:
        output.print_table(commands)
    print()
    output.print_warnings(warnings)
    return 0


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Expand imaging requests into a timed telecommand list.")
    sub = parser.add_subparsers(dest="command")
    build = sub.add_parser("build", help="build the timed command list")
    build.add_argument("--requests", required=True, help="requests CSV (request_id,start_utc,duration_s,target)")
    build.add_argument("--out", help="write commands to this CSV instead of printing a table")
    build.add_argument("--report-only", action="store_true", help="only print the overlap warnings")
    build.set_defaults(func=run_build)
    return parser


def main() -> int:
    parser = make_parser()
    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return 0
    try:
        return args.func(args)
    except (ValueError, OSError) as err:  # user mistakes -> one clean line
        print(f"error: {err}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
