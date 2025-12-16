"""
make_opportunity_map.py

Goal
- Create the league-average infield opportunity map.

What this figure represents
- Each point is a spatial zone on the infield.
- Color encodes the expected probability that a ball hit to that zone
  becomes an out (league average).
- Size encodes how frequently balls are hit to that zone.
- The field diagram provides baseball-context orientation.

Key idea
- This plot visualizes OPPORTUNITY, not performance.
- No teams, no players, no credit/blame yet.
"""

from draw_baseball_field import draw_infield

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# SQLite database produced by SQL pipeline
DB_PATH = Path("data/db/infield_range.sqlite")

# Output figure path
OUT_PATH = Path("figures/infield_opportunity_map_league.png")


def main() -> None:
    """
    Load league-average opportunity data from SQLite
    and generate the infield opportunity map figure.
    """

    # --------------------------------------------------
    # Load aggregated opportunity data from SQLite
    # --------------------------------------------------
    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql_query(
        """
        SELECT
          f.zone_id,

          -- League-average probability an infield BIP
          -- in this zone becomes an out
          AVG(s.p_out) AS p_out,

          -- Number of balls hit to this zone
          COUNT(*) AS n,

          -- Mean spray coordinates of the zone
          AVG(f.hit_x) AS x,
          AVG(f.hit_y) AS y

        FROM bip_features f
        JOIN bip_scored s
          ON f.bip_id = s.bip_id

        GROUP BY f.zone_id
        """,
        conn
    )

    conn.close()

    # Ensure output directory exists
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    # --------------------------------------------------
    # Plotting section
    # --------------------------------------------------
    fig, ax = plt.subplots(figsize=(8, 6))

    # Scatter plot:
    # - position: average location of each zone
    # - color: expected out probability
    # - size: number of balls hit to that zone
    sc = ax.scatter(
        df["x"],
        df["y"],
        c=df["p_out"],
        s=df["n"] / 20,   # scale size for readability
        alpha=0.85
    )

    # Draw schematic infield geometry underneath points
    draw_infield(ax)

    # Colorbar explains expected out probability scale
    plt.colorbar(sc, ax=ax, label="Expected Out Probability")

    # Axes labels and title
    ax.set_title("Infield Opportunity Map (League Average, 2023–2025)")
    ax.set_xlabel("Spray X (hc_x)")
    ax.set_ylabel("Spray Y (hc_y)")

    # Invert Y-axis so the field orientation matches baseball convention
    ax.invert_yaxis()

    # Improve spacing and save output
    plt.tight_layout()
    plt.savefig(OUT_PATH, dpi=200)
    plt.show()

    print(f"Saved figure to: {OUT_PATH}")


if __name__ == "__main__":
    main()
