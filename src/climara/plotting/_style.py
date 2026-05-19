from __future__ import annotations

import matplotlib.pyplot as plt


def ncl_style():
    plt.rcParams.update(
        {
            "figure.dpi": 120,
            "savefig.dpi": 300,
            "font.size": 10,
            "axes.titlesize": 11,
            "axes.labelsize": 10,
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
            "lines.linewidth": 1.0,
            "axes.linewidth": 0.8,
            "contour.negative_linestyle": "solid",
            "figure.facecolor": "white",
            "axes.facecolor": "white",
        }
    )
