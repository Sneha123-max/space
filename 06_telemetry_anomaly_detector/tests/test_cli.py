import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def run(*args):
    return subprocess.run([sys.executable, str(ROOT / "main.py"), *args],
                          capture_output=True, text=True, cwd=ROOT)


def test_simulate_then_detect_writes_log(tmp_path):
    csv_path, log_path = tmp_path / "t.csv", tmp_path / "out" / "a.log"
    assert run("simulate", "--samples", "300", "--seed", "42", "--out", str(csv_path)).returncode == 0
    result = run("detect", "--telemetry", str(csv_path), "--alerts", str(log_path))
    assert result.returncode == 0
    assert log_path.read_text(encoding="utf-8").splitlines() == result.stdout.splitlines()
    assert all(line.startswith("[SIMULATED]") for line in result.stdout.splitlines())


def test_missing_file_gives_clean_error():
    result = run("detect", "--telemetry", "nope.csv")
    assert result.returncode == 1
    assert "Traceback" not in result.stderr and "not found" in result.stderr
