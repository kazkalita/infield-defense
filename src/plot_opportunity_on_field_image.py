import json
import sqlite3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from pathlib import Path

DB_PATH = Path("data/db/infield_range.sqlite")
TRANSFORM_PATH = Path("assets/field_transform.json")
OUT_PATH = Path("figures/infield_opportunity_map_on_field.png")

def apply_affine(A, x, y):
    # A is 2x3, points are (x,y,1)
    pts = np.column_stack([x, y, np.ones(len(x))])
    uv = pts @ A.T
    return uv[:, 0], uv[:, 1]

def main():
    cfg = json.loads(TRANSFORM_PATH.read_text())
    A = np.array(cfg["affine_A_2x3"], dtype=float)

    img = mpimg.imread(cfg["image_path"])

    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("""
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
    """, conn)
    conn.close()

    u, v = apply_affine(A, df["x"].values, df["y"].values)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.imshow(img)
    sc = ax.scatter(
        u, v,
        c=df["p_out"],
        s=df["n"] / 25,
        alpha=0.85
    )
    plt.colorbar(sc, ax=ax, label="Expected Out Probability")
    ax.set_title("Infield Opportunity Map (on field diagram, 2023–2025)")
    ax.axis("off")
    plt.tight_layout()
    plt.savefig(OUT_PATH, dpi=250)
    plt.show()

    print(f"Saved: {OUT_PATH}")

if __name__ == "__main__":
    main()
