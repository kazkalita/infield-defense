from pybaseball import statcast
import pandas as pd
from pathlib import Path

def pull_season(year: int) -> pd.DataFrame:
    start = f"{year}-03-01"
    end = f"{year}-11-30"
    df = statcast(start_dt=start, end_dt=end)
    df["season"] = year
    return df

if __name__ == "__main__":
    out_dir = Path("data/raw")
    out_dir.mkdir(parents=True, exist_ok=True)

    seasons = [2023, 2024, 2025]
    frames = []

    for y in seasons:
        print(f"Pulling Statcast for {y}...")
        df_y = pull_season(y)
        print(f"{y}: rows={len(df_y):,} cols={df_y.shape[1]}")
        frames.append(df_y)

    data = pd.concat(frames, ignore_index=True)
    out_path = out_dir / "statcast_2023_2025.parquet"
    data.to_parquet(out_path, index=False)

    print(f"Saved: {out_path}")
    print(f"Total: rows={len(data):,} cols={data.shape[1]}")
