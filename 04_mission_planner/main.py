"""Mission Planner CLI. Example:
python main.py plan --requests data/requests.csv --visibility data/visibility.csv --battery-wh 500 --storage-mb 2000
"""
import argparse
import sys

from src.loader import InputError, load_requests, load_windows
from src.planner import plan
from src.report import print_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Greedy satellite imaging mission planner.")
    sub = parser.add_subparsers(dest="command")
    p = sub.add_parser("plan", help="accept/reject imaging requests")
    p.add_argument("--requests", default="data/requests.csv", help="requests CSV")
    p.add_argument("--visibility", default="data/visibility.csv", help="visibility windows CSV")
    p.add_argument("--battery-wh", type=float, default=500, help="battery budget in Wh")
    p.add_argument("--storage-mb", type=float, default=2000, help="storage budget in MB")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if args.command != "plan":
        parser.print_help()
        return 0
    if args.battery_wh < 0 or args.storage_mb < 0:
        print("error: budgets cannot be negative", file=sys.stderr)
        return 1
    try:
        requests = load_requests(args.requests)
        windows = load_windows(args.visibility)
    except InputError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    results = plan(requests, windows, args.battery_wh, args.storage_mb)
    print_report(results, args.battery_wh, args.storage_mb)
    return 0


if __name__ == "__main__":
    sys.exit(main())
