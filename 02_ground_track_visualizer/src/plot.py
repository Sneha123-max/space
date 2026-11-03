"""Draw the ground track on a plain lat/lon grid (matplotlib only, no map data)."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # file-only backend: no window needed
import matplotlib.pyplot as plt  # noqa: E402  (must come after use())


def save_plot(segments, station, sat_name, hours, out_path: str) -> None:
    """Plot each track segment, mark the ground station and save a PNG."""
    fig, ax = plt.subplots(figsize=(12, 6))
    for lats, lons in segments:
        ax.plot(lons, lats, color="tab:blue", linewidth=1.5)
    # Mark start and end of the track so the direction of travel is clear.
    ax.plot(segments[0][1][0], segments[0][0][0], "go", label="Start")
    ax.plot(segments[-1][1][-1], segments[-1][0][-1], "rs", label="End")
    ax.plot(station[1], station[0], "k*", markersize=16,
            label=f"Ground station ({station[0]}, {station[1]})")
    ax.set_xlim(-180, 180)
    ax.set_ylim(-90, 90)
    ax.set_xticks(range(-180, 181, 30))
    ax.set_yticks(range(-90, 91, 30))
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.set_xlabel("Longitude (deg)")
    ax.set_ylabel("Latitude (deg)")
    ax.set_title(f"{sat_name} ground track, {hours:g} h (Skyfield + bundled sample TLE, not live data)")
    ax.legend(loc="lower left")
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)  # create output/ if missing
    fig.savefig(out_path, dpi=120, bbox_inches="tight")
    plt.close(fig)
