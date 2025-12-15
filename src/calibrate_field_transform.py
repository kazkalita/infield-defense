import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from pathlib import Path

IMG_PATH = Path("assets/field_diagram.png")
OUT_PATH = Path("assets/field_transform.json")

# Enter approximate Statcast coordinate targets for these landmarks.
# These are reasonable defaults in hc_x/hc_y space.
TARGETS = {
    "home":  (125.0,  25.0),
    "first": (165.0,  85.0),
    "second":(125.0, 138.0),
    "third": ( 85.0,  85.0),
}

def fit_affine(src_xy, dst_xy):
    """
    Fit affine transform: [u v]^T = A*[x y 1]^T where A is 2x3
    src_xy: (n,2) in Statcast coords
    dst_xy: (n,2) in pixel coords
    """
    n = src_xy.shape[0]
    X = np.hstack([src_xy, np.ones((n, 1))])  # (n,3)
    Y = dst_xy  # (n,2)
    A, _, _, _ = np.linalg.lstsq(X, Y, rcond=None)  # (3,2)
    return A.T  # (2,3)

def main():
    img = mpimg.imread(IMG_PATH)
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.imshow(img)
    ax.set_title("Click: home, 1B, 2B, 3B (in that order)")
    ax.axis("off")

    # Click points in this exact order
    labels = ["home", "first", "second", "third"]
    clicks = plt.ginput(4, timeout=0)
    plt.close(fig)

    dst = np.array(clicks, dtype=float)  # pixel coords (x,y)

    src = np.array([TARGETS[k] for k in labels], dtype=float)  # Statcast coords

    A = fit_affine(src, dst)

    payload = {
        "image_path": str(IMG_PATH),
        "labels_order": labels,
        "statcast_targets": {k: list(TARGETS[k]) for k in labels},
        "pixel_clicks": {k: [float(dst[i,0]), float(dst[i,1])] for i,k in enumerate(labels)},
        "affine_A_2x3": A.tolist(),
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(payload, indent=2))
    print(f"Saved transform to: {OUT_PATH}")

if __name__ == "__main__":
    main()
