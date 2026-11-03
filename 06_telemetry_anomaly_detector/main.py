"""CLI for the SIMULATED telemetry anomaly detector."""
import argparse
import sys
from pathlib import Path

from src import config
from src.detector import detect
from src.simulator import generate
from src.telemetry_io import read_csv, write_csv


def cmd_simulate(args: argparse.Namespace) -> None:
    """Generate simulated telemetry and save it as CSV."""
    if args.samples < 1:
        raise ValueError("--samples must be at least 1")
    rows = generate(args.samples, args.seed)
    write_csv(rows, Path(args.out))
    print(f"{config.LABEL} wrote {len(rows)} simulated samples (seed {args.seed}) to {args.out}")


def cmd_detect(args: argparse.Namespace) -> None:
    """Read telemetry, find alerts, print them and save them to a file."""
    rows = read_csv(Path(args.telemetry))
    alerts = detect(rows)
    lines = [f"{config.LABEL} checked {len(rows)} simulated samples, debounce N={config.DEBOUNCE_N}"]
    lines += alerts
    lines.append(f"{config.LABEL} {len(alerts)} alert events")
    out = Path(args.alerts)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Telemetry anomaly detector (SIMULATED data only).")
    sub = parser.add_subparsers(dest="command")

    sim = sub.add_parser("simulate", help="generate simulated telemetry CSV")
    sim.add_argument("--samples", type=int, default=300, help="number of samples (default 300)")
    sim.add_argument("--seed", type=int, default=42, help="random seed (default 42)")
    sim.add_argument("--out", default="data/telemetry_sim.csv", help="output CSV path")
    sim.set_defaults(func=cmd_simulate)

    det = sub.add_parser("detect", help="check telemetry against limits")
    det.add_argument("--telemetry", default="data/telemetry_sim.csv", help="input CSV path")
    det.add_argument("--alerts", default="output/alerts.log", help="alert log path")
    det.set_defaults(func=cmd_detect)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return 0
    try:
        args.func(args)
    except (ValueError, OSError) as err:
        print(f"{config.LABEL} error: {err}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
