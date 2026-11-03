"""Satellite Pass Predictor: CLI entry point."""
import argparse
import sys
from datetime import datetime, timezone

from src.passes import find_passes, format_table
from src.tle import InputError, epoch_warning, load_satellite, utc_now


def parse_start(text: str) -> datetime:
    """Parse e.g. 2026-11-01T00:00:00Z into a UTC datetime."""
    try:
        dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        raise InputError(f"bad --start '{text}', use e.g. 2026-11-01T00:00:00Z")
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)  # assume UTC if no zone given
    return dt.astimezone(timezone.utc)


def check_args(args: argparse.Namespace) -> None:
    """Reject values that make no physical sense."""
    if not -90 <= args.lat <= 90:
        raise InputError("--lat must be between -90 and 90")
    if not -180 <= args.lon <= 180:
        raise InputError("--lon must be between -180 and 180")
    if not 0 <= args.min_elev < 90:
        raise InputError("--min-elev must be from 0 up to (but not including) 90")
    if not 0 < args.hours <= 24 * 30:
        raise InputError("--hours must be greater than 0 and at most 720")


def predict(args: argparse.Namespace) -> None:
    check_args(args)
    sat = load_satellite(args.tle)
    start = parse_start(args.start) if args.start else utc_now()
    warning = epoch_warning(sat, utc_now())
    if warning:
        print(warning, file=sys.stderr)  # stderr so it never mixes into the table
    print(f"Satellite: {sat.name}  Observer: {args.lat}, {args.lon}  "
          f"Min elevation: {args.min_elev} deg")
    print(f"Window: {start:%Y-%m-%d %H:%M} UTC for {args.hours} h")
    passes = find_passes(sat, args.lat, args.lon, start, args.hours, args.min_elev)
    if passes:
        print(format_table(passes))
    else:
        print("No passes found in this window.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Predict satellite passes from a TLE file (offline).")
    sub = parser.add_subparsers(dest="command")
    p = sub.add_parser("predict", help="list passes over an observer")
    p.add_argument("--tle", required=True, help="path to TLE file")
    p.add_argument("--lat", type=float, default=12.97, help="latitude, default 12.97 (Bangalore)")
    p.add_argument("--lon", type=float, default=77.59, help="longitude, default 77.59 (Bangalore)")
    p.add_argument("--start", help="start time, UTC, e.g. 2026-11-01T00:00:00Z (default: now)")
    p.add_argument("--hours", type=float, default=24, help="window length in hours, default 24")
    p.add_argument("--min-elev", type=float, default=10, help="minimum elevation in degrees, default 10")
    p.set_defaults(func=predict)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return 0
    try:
        args.func(args)
    except InputError as err:
        print(f"error: {err}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
