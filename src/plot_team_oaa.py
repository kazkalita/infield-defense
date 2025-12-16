"""
plot_team_oaa.py

Goal
- Produce season-level team leaderboards for infield Outs Above Average (OAA),
  expressed as OAA per 100 opportunities.

What this figure represents
- For a given season, each team has:
    * opportunities: number of infield balls in play included in the model
    * oaa: actual outs minus expected outs (sum over those opportunities)
    * oaa_per_100: oaa scaled to a rate per 100 opportunities for comparability

Why we plot OAA per 100
- Raw OAA is volume-dependent: teams with more opportunities will tend to have
  larger magnitude totals.
- Rate scaling (per 100) makes cross-team comparisons more interpretable.

Plot design choice
- Show only top 10 and bottom 10 to keep the chart readable and “story-first.”
- Include opportunities in the label to prevent over-interpreting tiny samples.
"""

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# SQLite DB that contains the final summary table built by the SQL pipeline
DB = Path("data/db/infield_range.sqlite")

# Directory for output figures
OUT_DIR = Path("figures")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def plot_season(season: int) -> None:
    """
    Create and save a top-10 / bottom-10 bar chart of team OAA per 100
    for a single season.

    Parameters
    ----------
    season : int
        Season year (e.g. 2023)
    """

    # --------------------------------------------------
    # Load season-level team results from SQLite
    # --------------------------------------------------
    conn = sqlite3.connect(DB)

    # We use a parameterized query (WHERE season = ?)
    # to avoid string formatting and keep the query safe and clean.
    df = pd.read_sql_query(
        """
        SELECT
          season,
          inf_group_id AS team,
          opportunities,
          oaa,
          oaa_per_100
        FROM infield_oaa_summary
        WHERE season = ?
        """,
        conn,
        params=(season,)
    )

    conn.close()

    # --------------------------------------------------
    # Choose what to plot
    # --------------------------------------------------
    # Sort teams by rate metric so top and bottom teams are clear
    df = df.sort_values("oaa_per_100", ascending=False)

    # Take top 10 and bottom 10 to keep the visualization compact
    top = df.head(10).copy()
    bot = df.tail(10).copy()

    # Combine into one plotting DataFrame
    plot_df = pd.concat([top, bot], ignore_index=True)

    # Create a label that includes team and opportunity count.
    # This helps the reader interpret context and sample size quickly.
    plot_df["label"] = (
        plot_df["team"]
        + " ("
        + plot_df["opportunities"].astype(int).astype(str)
        + ")"
    )

    # For a horizontal bar plot, sort ascending so smallest appears at bottom
    # and largest at top (reads naturally).
    plot_df = plot_df.sort_values("oaa_per_100")

    # --------------------------------------------------
    # Plot
    # --------------------------------------------------
    plt.figure(figsize=(10, 6))

    # Horizontal bar chart:
    # - y axis: team labels (with opportunities)
    # - x axis: OAA per 100
    plt.barh(plot_df["label"], plot_df["oaa_per_100"])

    # Vertical reference line at 0 makes above/below average obvious
    plt.axvline(0, linewidth=1)

    plt.title(f"Team Infield OAA per 100 Opportunities ({season})")
    plt.xlabel("OAA per 100 opportunities")
    plt.ylabel("Team (opportunities)")

    plt.tight_layout()

    # Save the plot and close figure to avoid memory build-up in loops
    out = OUT_DIR / f"team_infield_oaa_per100_{season}.png"
    plt.savefig(out, dpi=200)
    plt.close()

    print(f"Saved: {out}")


if __name__ == "__main__":
    # Generate one figure per season in the project scope
    for season in [2023, 2024, 2025]:
        plot_season(season)
