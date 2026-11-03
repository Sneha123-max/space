"""Scan log files for ERROR and MISSED lines."""
from pathlib import Path


def scan_file(log_file: Path) -> dict:
    """Return the ERROR and MISSED lines found in one log file."""
    errors, missed = [], []
    for line in log_file.read_text(encoding="utf-8").splitlines():
        # The level is the 3rd word: "DATE TIME LEVEL message"
        parts = line.split()
        level = parts[2] if len(parts) >= 3 else ""
        if level == "ERROR":
            errors.append(line)
        elif level == "MISSED":
            missed.append(line)
    return {"name": log_file.name, "errors": errors, "missed": missed}


def scan_dir(log_dir: Path) -> list[dict]:
    """Scan every *.log file in a folder. Raises ValueError if none found."""
    if not log_dir.is_dir():
        raise ValueError(f"log directory not found: {log_dir}")
    files = sorted(log_dir.glob("*.log"))
    if not files:
        raise ValueError(f"no .log files in: {log_dir}")
    return [scan_file(f) for f in files]


def format_summary(results: list[dict]) -> str:
    """Make the printed report: counts per file, then the offending lines."""
    out = []
    for r in results:
        out.append(f"{r['name']}: {len(r['errors'])} ERROR, {len(r['missed'])} MISSED")
        for line in r["errors"] + r["missed"]:
            out.append(f"    {line}")
    total_e = sum(len(r["errors"]) for r in results)
    total_m = sum(len(r["missed"]) for r in results)
    out.append(f"TOTAL: {total_e} ERROR, {total_m} MISSED in {len(results)} files")
    return "\n".join(out)
