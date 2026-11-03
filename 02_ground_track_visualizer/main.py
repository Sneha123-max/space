"""CLI entry point: python main.py plot --tle data/iss.tle --hours 3 ..."""
import argparse
import sys
from datetime import datetime, timezone

from src.plot import save_plot
from src.track import compute_track, load_satellite, split_at_dateline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Ground track visualizer (Skyfield + matplotlib, offline).")
    sub = parser.add_subparsers(dest="command")
    p = sub.add_parser("plot", help="compute a ground track and save it as a PNG")
    p.add_argument("--tle", default="data/iss.tle", help="TLE file (default: data/iss.tle)")
    p.add_argument("--hours", type=float, default=3.0, help="how long to simulate (default 3)")
    p.add_argument("--step-seconds", type=float, default=60.0, help="time between points (default 60)")
    p.add_argument("--station", type=float, nargs=2, metavar=("LAT", "LON"), default=[12.97, 77.59],
                   help="ground station lat lon (default Bangalore 12.97 77.59)")
    p.add_argument("--start", help="start time in UTC, e.g. 2024-01-01T12:00:00 (default: TLE epoch)")
    p.add_argument("--out", default="output/ground_track.png", help="output PNG path")
    return parser


def run_plot(args) -> None:
    lat, lon = args.station
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        raise ValueError("--station needs LAT in -90..90 and LON in -180..180")
    start = None
    if args.start:
        try:
            # All internal times are UTC, so we treat the given time as UTC.
            start = datetime.fromisoformat(args.start).replace(tzinfo=timezone.utc)
        except ValueError:
            raise ValueError(f"--start must look like 2024-01-01T12:00:00, got: {args.start}") from None
    sat, ts = load_satellite(args.tle)
    lats, lons, times = compute_track(sat, ts, args.hours, args.step_seconds, start)
    segments = split_at_dateline(lats, lons)
    save_plot(segments, (lat, lon), sat.name, args.hours, args.out)
    print(f"Satellite: {sat.name}")
    print(f"Start (UTC): {times[0].utc_strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Points: {len(lats)}  Segments (after dateline split): {len(segments)}")
    print(f"Saved: {args.out}")


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        return 0
    try:
        run_plot(args)
    except ValueError as err:  # user mistakes: one-line message, no stack trace
        print(f"Error: {err}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
