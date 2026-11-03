"""Set up every project in the space/ folder in one go.

For each project folder this script:
  1. creates a local .venv (python -m venv .venv)
  2. installs that project's requirements.txt into the .venv
  3. runs seed.py inside the project, if the project has one

Nothing is installed globally. Only the .venv folders are touched.

Usage:
    python setup_all.py
"""

import subprocess
import sys
from pathlib import Path

# The 12 project folders, in order. Keep this list in sync with README.md.
PROJECTS = [
    "01_satellite_pass_predictor",
    "02_ground_track_visualizer",
    "03_telecommand_scheduler",
    "04_mission_planner",
    "05_ground_station_automation",
    "06_telemetry_anomaly_detector",
    "07_telemetry_dashboard",
    "08_operations_logger",
]

SPACE_DIR = Path(__file__).resolve().parent


def venv_python(project_dir: Path) -> Path:
    """Return the path to the python inside a project's .venv (Windows or Linux/macOS)."""
    if sys.platform == "win32":
        return project_dir / ".venv" / "Scripts" / "python.exe"
    return project_dir / ".venv" / "bin" / "python"


def run_step(label: str, command: list[str], cwd: Path) -> bool:
    """Run one command and report whether it worked."""
    print(f"  {label} ...", end=" ", flush=True)
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True)
    if result.returncode == 0:
        print("ok")
        return True
    print("FAILED")
    # Show the last few lines of the error so the user knows what went wrong.
    tail = (result.stderr or result.stdout).strip().splitlines()[-5:]
    for line in tail:
        print(f"      {line}")
    return False


def set_up_project(name: str) -> bool:
    """Create the venv, install requirements and seed one project. Return True on success."""
    project_dir = SPACE_DIR / name
    print(f"[{name}]")

    if not project_dir.is_dir():
        print("  folder missing - skipped")
        return False

    # Step 1: create the venv only if it is not already there.
    if not venv_python(project_dir).exists():
        if not run_step("create .venv", [sys.executable, "-m", "venv", ".venv"], project_dir):
            return False

    # Step 2: install this project's requirements into its own venv.
    python = str(venv_python(project_dir))
    if not run_step(
        "install requirements",
        [python, "-m", "pip", "install", "--quiet", "-r", "requirements.txt"],
        project_dir,
    ):
        return False

    # Step 3: seed the local SQLite data if the project has a seed script.
    if (project_dir / "seed.py").exists():
        if not run_step("seed data", [python, "seed.py"], project_dir):
            return False

    return True


def main() -> int:
    print(f"Setting up {len(PROJECTS)} projects in {SPACE_DIR}")
    failed = [name for name in PROJECTS if not set_up_project(name)]

    print()
    if failed:
        print(f"{len(failed)} project(s) failed setup:")
        for name in failed:
            print(f"  - {name}")
        return 1
    print("All projects set up.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
