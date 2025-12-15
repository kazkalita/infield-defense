import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

DB = Path("data/db/infield_range.sqlite")
OUT_DIR = Path("figures")
OUT_DIR.mkdir(parents=True, exist_ok=True)

def plot_season(season: int):
    conn = sqlite3.connect(DB)
    df = pd.read_sql_query(
        """
        SELECT season, inf_group_id AS team, opportunities, oaa, oaa_per_100
        FROM infield_oaa_summary
        WHERE season = ?
        """,
        conn,
        params=(season,)
    )
    conn.close()

    df = df.sort_values("oaa_per_100", ascending=False)
    top = df.head(10).copy()
    bot = df.tail(10).copy()

    plot_df = pd.concat([top, bot], ignore_index=True)
    plot_df["label"] = plot_df["team"] + " (" + plot_df["opportunities"].astype(int).astype(str) + ")"
    plot_df = plot_df.sort_values("oaa_per_100")

    plt.figure(figsize=(10, 6))
    plt.barh(plot_df["label"], plot_df["oaa_per_100"])
    plt.axvline(0, linewidth=1)
    plt.title(f"Team Infield OAA per 100 Opportunities ({season})")
    plt.xlabel("OAA per 100 opportunities")
    plt.ylabel("Team (opportunities)")
    plt.tight_layout()

    out = OUT_DIR / f"team_infield_oaa_per100_{season}.png"
    plt.savefig(out, dpi=200)
    plt.close()
    print(f"Saved: {out}")

if __name__ == "__main__":
    for season in [2023, 2024, 2025]:
        plot_season(season)
