from draw_baseball_field import draw_infield

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

DB_PATH = Path("data/db/infield_range.sqlite")
OUT_PATH = Path("figures/infield_opportunity_map_league.png")

def main():
    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql_query(
        """
        SELECT
          f.zone_id,
          AVG(s.p_out) AS p_out,
          COUNT(*) AS n,
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

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    # -------- PLOTTING SECTION (must be indented) --------
    fig, ax = plt.subplots(figsize=(8, 6))

    sc = ax.scatter(
        df["x"], df["y"],
        c=df["p_out"],
        s=df["n"] / 20,
        alpha=0.85
    )

    draw_infield(ax)

    plt.colorbar(sc, ax=ax, label="Expected Out Probability")
    ax.set_title("Infield Opportunity Map (League Average, 2023–2025)")
    ax.set_xlabel("Spray X (hc_x)")
    ax.set_ylabel("Spray Y (hc_y)")
    ax.invert_yaxis()
    plt.tight_layout()
    plt.savefig(OUT_PATH, dpi=200)
    plt.show()

    print(f"Saved figure to: {OUT_PATH}")


if __name__ == "__main__":
    main()
