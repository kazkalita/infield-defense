"""
calibrate_field_transform.py

Goal
- Create a reusable mapping from Statcast spray coordinates (hc_x, hc_y)
  to pixel coordinates on a baseball field diagram image.

Why we need this
- Statcast uses its own coordinate system for where the ball was hit (hc_x, hc_y).
- Your background image is in pixel coordinates (u, v) measured in pixels.
- To overlay points onto the diagram, we estimate an affine transform that converts:
      (hc_x, hc_y)  ->  (pixel_x, pixel_y)

How it works (high level)
1) You click 4 known landmarks on the image (home, 1B, 2B, 3B) in a fixed order.
2) We pair those clicked pixel points with reasonable "targets" in Statcast space.
3) We solve a least-squares affine transform that best maps the Statcast targets
   to the clicked pixels.
4) We save the transform to assets/field_transform.json so plotting scripts can reuse it.

Notes
- Affine transforms can scale, translate, rotate, shear. They do NOT model curvature.
- 4 points is enough to solve an affine transform robustly (and least squares helps).
"""

import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from pathlib import Path

# Background image you will click on (pixel coordinate system)
IMG_PATH = Path("assets/field_diagram.png")

# Output file containing the estimated transform and metadata
OUT_PATH = Path("assets/field_transform.json")

# These are "anchor points" in Statcast hc_x/hc_y space for home, 1B, 2B, 3B.
# They don't have to be perfect, but they must be consistent with the way
# hc_x/hc_y is oriented and scaled in your project.
#
# If the overlay looks shifted or stretched, you usually fix it by:
# - re-clicking more accurately, or
# - updating these TARGETS to better match your hc_x/hc_y centering.
TARGETS = {
    "home":   (125.0,  25.0),
    "first":  (165.0,  85.0),
    "second": (125.0, 138.0),
    "third":  ( 85.0,  85.0),
}


def fit_affine(src_xy: np.ndarray, dst_xy: np.ndarray) -> np.ndarray:
    """
    Fit an affine transform from src_xy -> dst_xy.

    We want:
        [u, v]^T = A * [x, y, 1]^T

    Where:
    - (x, y) are Statcast coordinates (hc_x, hc_y)
    - (u, v) are pixel coordinates on the image
    - A is a 2x3 matrix

    Inputs
    - src_xy: shape (n, 2), Statcast coords
    - dst_xy: shape (n, 2), pixel coords

    Output
    - A: shape (2, 3)
    """
    n = src_xy.shape[0]

    # Build design matrix with a constant 1 column to allow translation
    # X is (n, 3): [x, y, 1]
    X = np.hstack([src_xy, np.ones((n, 1))])

    # Y is (n, 2): [u, v]
    Y = dst_xy

    # Solve X * B = Y in least squares sense, where B is (3, 2)
    # Then A is B^T -> shape (2, 3)
    B, _, _, _ = np.linalg.lstsq(X, Y, rcond=None)
    return B.T


def main() -> None:
    # Load the field diagram image
    img = mpimg.imread(IMG_PATH)

    # Show it so you can click landmark points
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.imshow(img)
    ax.set_title("Click: home, 1B, 2B, 3B (in that order)")
    ax.axis("off")

    # IMPORTANT: You must click in this exact order
    labels = ["home", "first", "second", "third"]

    # ginput(4) collects 4 mouse clicks. timeout=0 means "wait forever".
    # It returns a list of (x, y) pixel coordinates.
    clicks = plt.ginput(4, timeout=0)
    plt.close(fig)

    # dst = clicked points in pixel space (u, v)
    dst = np.array(clicks, dtype=float)

    # src = the known targets in Statcast space (hc_x, hc_y) in the same order
    src = np.array([TARGETS[k] for k in labels], dtype=float)

    # Estimate the affine transform matrix
    A = fit_affine(src, dst)

    # Save everything needed to reproduce and debug later
    payload = {
        "image_path": str(IMG_PATH),
        "labels_order": labels,

        # The Statcast anchors you assumed
        "statcast_targets": {k: list(TARGETS[k]) for k in labels},

        # The pixel points you actually clicked
        "pixel_clicks": {
            k: [float(dst[i, 0]), float(dst[i, 1])]
            for i, k in enumerate(labels)
        },

        # The mapping matrix you will apply later:
        #   [u, v]^T = A * [x, y, 1]^T
        "affine_A_2x3": A.tolist(),
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(payload, indent=2))
    print(f"Saved transform to: {OUT_PATH}")


if __name__ == "__main__":
    main()
