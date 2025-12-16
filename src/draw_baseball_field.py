"""
draw_baseball_field.py

Goal
- Draw a simplified, schematic infield directly in Statcast coordinate space.

Why this exists
- Before using a background image, we need a quick, reproducible way
  to visualize spray data relative to the infield.
- This function draws an "idealized" baseball infield using geometry,
  not an image.
- It is mainly useful for:
    * debugging
    * early exploration
    * sanity-checking coordinate orientation

Important distinction
- This is NOT a photo-realistic field.
- Everything here is drawn in hc_x / hc_y space.
- Later, we switch to drawing points on top of an image using
  an affine transform (calibrate_field_transform.py).
"""

import matplotlib.pyplot as plt
import numpy as np


def draw_infield(ax):
    """
    Draw a simplified infield diagram onto an existing Matplotlib Axes.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axes to draw on. This lets us overlay the field on top of
        scatter plots without creating a new figure.

    Coordinate system
    -----------------
    - Uses approximate Statcast spray coordinates (hc_x, hc_y)
    - Home plate is near (125, 40)
    - Second base is near (125, 120)
    """

    # ------------------------------------------------------------
    # Bases (home -> 1B -> 2B -> 3B -> home)
    # These values are approximate but internally consistent.
    # ------------------------------------------------------------
    bases_x = [125, 155, 125, 95, 125]
    bases_y = [40,  80,  120, 80, 40]

    # Draw base paths (the infield diamond)
    ax.plot(bases_x, bases_y, linewidth=2)

    # ------------------------------------------------------------
    # Infield arc (grass/dirt boundary)
    # ------------------------------------------------------------
    # theta controls the angle of the arc
    # pi/4 to 3*pi/4 roughly spans from 1B side to 3B side
    theta = np.linspace(np.pi / 4, 3 * np.pi / 4, 200)

    # Radius of the arc in Statcast units
    r = 95

    # Arc center is roughly at home plate (125, 40)
    arc_x = 125 + r * np.cos(theta)
    arc_y = 40 + r * np.sin(theta)

    ax.plot(arc_x, arc_y, linewidth=2)

    # ------------------------------------------------------------
    # Pitcher’s mound (small circle)
    # ------------------------------------------------------------
    # Centered roughly halfway between home and second
    mound_center = (125, 75)

    # Radius chosen for visual clarity, not measurement accuracy
    circle = plt.Circle(
        mound_center,
        radius=5,
        fill=False,
        linewidth=1.5
    )

    ax.add_patch(circle)
