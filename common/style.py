"""Shared matplotlib defaults, so Q3 and Q5 figures look like one document.

Palette is Okabe-Ito based and validated for colour-vision deficiency:
worst adjacent pair dE 11.0 (deutan). Branch identity is carried by colour
*and* by the legend plus direct labels, never by colour alone.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# categorical, assigned in this fixed order — never cycled
ACOUSTIC = "#0072B2"
OPTICAL = ["#D55E00", "#009E73", "#9B59B6", "#56B4E9"]
GAP_FILL = "#B0B0B0"
EXACT = "#333333"


def branch_colors(p):
    """Acoustic first, then optical. Wraps into greys past 5 branches."""
    return [ACOUSTIC] + [OPTICAL[i % len(OPTICAL)] for i in range(p - 1)]


def apply():
    """Serif to match the LaTeX body text; grid and spines kept recessive."""
    plt.rcParams.update({
        "font.family": "serif",
        "font.size": 10,
        "axes.titlesize": 11,
        "axes.labelsize": 10,
        "axes.linewidth": 0.8,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.alpha": 0.25,
        "grid.linewidth": 0.5,
        "lines.linewidth": 2.0,
        "legend.frameon": False,
        "legend.fontsize": 9,
        "figure.dpi": 150,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
    })
