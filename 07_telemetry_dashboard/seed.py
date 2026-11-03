"""Create data/telemetry.db and fill it with 500 SIMULATED samples (safe to run twice)."""
from pathlib import Path

from src import db
from src.simulate import make_samples

DB_PATH = str(Path(__file__).parent / "data" / "telemetry.db")


def main() -> None:
    samples = make_samples(500, seed=42)
    conn = db.reset_db(DB_PATH)  # drop + recreate, so a second run gives the same result
    db.insert_samples(conn, samples)
    conn.close()
    print(f"SIMULATED data: inserted {len(samples)} samples into data/telemetry.db")
    print(f"First: {samples[0]}")
    print(f"Last:  {samples[-1]}")


if __name__ == "__main__":
    main()
