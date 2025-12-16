"""
Pull raw MLB Statcast data for multiple seasons and save to disk.

Purpose:
- Create a reproducible raw data layer
- Pull complete pitch-level Statcast data for selected seasons
- Save once, then build all downstream analysis from this file

This script intentionally performs NO filtering or modeling.
That separation is deliberate and important.
"""

from pybaseball import statcast
import pandas as pd
from pathlib import Path


def pull_season(year: int) -> pd.DataFrame:
    """
    Pull Statcast data for a single MLB season.

    Parameters
    ----------
    year : int
        MLB season year (e.g. 2023)

    Returns
    -------
    pd.DataFrame
        Raw Statcast pitch-level data with a season column added
    """

    # Use a wide date range to ensure full season coverage.
    # Over-including dates is safer than missing late or early games.
    start = f"{year}-03-01"
    end = f"{year}-11-30"

    # Pull raw Statcast data from pybaseball.
    # This returns one row per pitch.
    df = statcast(start_dt=start, end_dt=end)

    # Explicitly tag each row with the season year.
    # This is critical once multiple seasons are combined.
    df["season"] = year

    return df


if __name__ == "__main__":
    """
    Script entry point.

    This block only runs when the file is executed directly.
    It allows the functions above to be imported elsewhere
    without automatically pulling Statcast data.
    """

    # Define output directory for raw data
    out_dir = Path("data/raw")

    # Create the directory if it does not exist
    out_dir.mkdir(parents=True, exist_ok=True)

    # Seasons to pull
    seasons = [2023, 2024, 2025]

    # List to store season-level DataFrames
    frames = []

    # Pull data season by season
    for y in seasons:
        print(f"Pulling Statcast for {y}...")

        df_y = pull_season(y)

        # Print basic sanity check information
        print(f"{y}: rows={len(df_y):,} cols={df_y.shape[1]}")

        frames.append(df_y)

    # Combine all seasons into a single DataFrame
    # ignore_index=True prevents duplicate indices
    data = pd.concat(frames, ignore_index=True)

    # Save raw data in Parquet format
    # Parquet is fast, compact, and preserves data types
    out_path = out_dir / "statcast_2023_2025.parquet"
    data.to_parquet(out_path, index=False)

    # Final confirmation logs
    print(f"Saved: {out_path}")
    print(f"Total: rows={len(data):,} cols={data.shape[1]}")
