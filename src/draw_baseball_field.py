import matplotlib.pyplot as plt
import numpy as np

def draw_infield(ax):
    # Bases (approximate Statcast space)
    bases_x = [125, 155, 125, 95, 125]
    bases_y = [40, 80, 120, 80, 40]

    # Base paths
    ax.plot(bases_x, bases_y, linewidth=2)

    # Infield arc
    theta = np.linspace(np.pi / 4, 3 * np.pi / 4, 200)
    r = 95
    ax.plot(125 + r * np.cos(theta), 40 + r * np.sin(theta), linewidth=2)

    # Pitcher mound
    circle = plt.Circle((125, 75), 5, fill=False, linewidth=1.5)
    ax.add_patch(circle)
