"""Lattice schematic figure. Imported by make_figures.py."""

import numpy as np
import matplotlib.pyplot as plt

import style

ATOM_COLORS = [style.ACOUSTIC, style.OPTICAL[0], style.OPTICAL[1], style.OPTICAL[2]]


def spring(ax, x0, x1, y=0.0, coils=6, amp=0.055, color="0.25", lw=1.3, zorder=1):
    """Zigzag between two points, with straight lead-ins at each end."""
    lead = 0.16 * (x1 - x0)
    xz = np.linspace(x0 + lead, x1 - lead, 2 * coils + 1)
    yz = y + amp * np.array([0] + [(-1) ** k for k in range(2 * coils - 1)] + [0])
    ax.plot([x0, x0 + lead], [y, y], color=color, lw=lw, zorder=zorder, solid_capstyle="round")
    ax.plot(xz, yz, color=color, lw=lw, zorder=zorder, solid_capstyle="round")
    ax.plot([x1 - lead, x1], [y, y], color=color, lw=lw, zorder=zorder, solid_capstyle="round")


def atom(ax, x, m, color, y=0.0, label=None, mref=1.0, dashed=False):
    """Circle with radius set by mass, so heavier atoms read bigger."""
    r = 0.085 * (m / mref) ** (1 / 3)
    kw = dict(zorder=3, linewidth=1.4)
    if dashed:
        c = plt.Circle((x, y), r, facecolor="none", edgecolor="0.45",
                       linestyle=(0, (2, 2)), **kw)
    else:
        c = plt.Circle((x, y), r, facecolor=color, edgecolor="0.15", **kw)
    ax.add_patch(c)
    if label:
        ax.text(x, y - r - 0.11, label, ha="center", va="top", fontsize=11)
    return r


def panel_general(ax):
    """(a) Three cells of a p-atom chain, with a, K and u_j^n defined."""
    p, ncell, a = 3, 3, 1.0
    masses = [1.0, 2.0, 3.0]
    dx = a / p
    disp = 0.09  # displacement drawn for the marked atom

    for n in range(ncell):
        for j in range(p):
            x = n * a + (j + 0.5) * dx
            marked = (n == 1 and j == 1)  # mid-cell: room to show the offset
            if marked:
                atom(ax, x, masses[j], None, dashed=True)       # equilibrium site
                atom(ax, x + disp, masses[j], ATOM_COLORS[j])   # displaced
                for xg in (x, x + disp):
                    ax.plot([xg, xg], [0.14, 0.25], color="0.5", lw=0.8,
                            linestyle=(0, (2, 2)), zorder=1)
                ax.annotate("", xy=(x + disp, 0.25), xytext=(x, 0.25),
                            arrowprops=dict(arrowstyle="-|>", color="0.15", lw=1.4))
                ax.text(x + disp / 2 + 0.05, 0.285, r"$u_2^{\,n}$", ha="left",
                        va="bottom", fontsize=11)
                ax.text(x, -0.24, r"$m_2$", ha="center", va="top", fontsize=11)
            else:
                atom(ax, x, masses[j], ATOM_COLORS[j], label=rf"$m_{{{j+1}}}$")

    # springs, including the two that run off the edges
    xs = [n * a + (j + 0.5) * dx for n in range(ncell) for j in range(p)]
    spring(ax, xs[0] - dx, xs[0])
    for i in range(len(xs) - 1):
        spring(ax, xs[i], xs[i + 1])
    spring(ax, xs[-1], xs[-1] + dx)
    ax.text(-0.30, 0, r"$\cdots$", ha="center", va="center", fontsize=13)
    ax.text(ncell * a + 0.30, 0, r"$\cdots$", ha="center", va="center", fontsize=13)

    # one spring labelled, not all of them
    ax.text(xs[1] + dx / 2, 0.13, r"$K$", ha="center", va="bottom", fontsize=11)

    for n in range(ncell + 1):
        ax.axvline(n * a, color="0.75", lw=0.9, linestyle=(0, (4, 3)), zorder=0)
    for n, name in enumerate([r"cell $n-1$", r"cell $n$", r"cell $n+1$"]):
        ax.text((n + 0.5) * a, 0.52, name, ha="center", va="center", fontsize=10.5)

    # dimension line for the cell length
    ax.annotate("", xy=(2 * a, -0.42), xytext=(a, -0.42),
                arrowprops=dict(arrowstyle="<|-|>", color="0.15", lw=1.2))
    ax.text(1.5 * a, -0.55, r"$a$  (full cell length)", ha="center", va="top", fontsize=11)

    ax.set_xlim(-0.5, ncell * a + 0.5)
    ax.set_ylim(-0.80, 0.66)


def panel_two(ax):
    """(b) p=2: the two bonds that share matrix element D_12."""
    p, ncell, a = 2, 2, 1.0
    masses = [1.0, 2.5]
    dx = a / p

    xs = [n * a + (j + 0.5) * dx for n in range(ncell) for j in range(p)]
    spring(ax, xs[0] - dx, xs[0])
    spring(ax, xs[0], xs[1], color=style.ACOUSTIC, lw=2.0)        # intra-cell
    spring(ax, xs[1], xs[2], color=style.OPTICAL[0], lw=2.0)      # inter-cell
    spring(ax, xs[2], xs[3])
    spring(ax, xs[3], xs[3] + dx)
    ax.text(-0.42, 0, r"$\cdots$", ha="center", va="center", fontsize=13)
    ax.text(ncell * a + 0.42, 0, r"$\cdots$", ha="center", va="center", fontsize=13)

    for i, x in enumerate(xs):
        j = i % p
        atom(ax, x, masses[j], ATOM_COLORS[j], label=rf"$m_{{{j+1}}}$")

    ax.axvline(a, color="0.75", lw=0.9, linestyle=(0, (4, 3)), zorder=0)
    ax.text(0.5 * a, 0.80, r"cell $n$", ha="center", fontsize=10.5)
    ax.text(1.5 * a, 0.80, r"cell $n+1$", ha="center", fontsize=10.5)

    for x0, x1, c, lab, yb in [(xs[0], xs[1], style.ACOUSTIC, "intra-cell $K$", 0.26),
                               (xs[1], xs[2], style.OPTICAL[0], "inter-cell $K$", 0.52)]:
        ax.annotate("", xy=(x1, yb), xytext=(x0, yb),
                    arrowprops=dict(arrowstyle="<|-|>", color=c, lw=1.3))
        ax.text(0.5 * (x0 + x1), yb + 0.045, lab, ha="center", va="bottom",
                fontsize=10, color=c)

    ax.text(a, -0.52,
            r"both bonds join the same pair $m_1\!-\!m_2$, so both land in $D_{12}$",
            ha="center", va="top", fontsize=10.5)

    ax.set_xlim(-0.6, ncell * a + 0.6)
    ax.set_ylim(-0.80, 0.98)


def make(path):
    fig, axes = plt.subplots(2, 1, figsize=(7.2, 5.8),
                             gridspec_kw=dict(height_ratios=[1.15, 1.0], hspace=0.38))
    panel_general(axes[0])
    panel_two(axes[1])
    for ax, t in zip(axes, [r"(a)  General chain ($p$ atoms per unit cell)",
                            r"(b)  $p=2$: the two bonds that share $D_{12}$"]):
        ax.set_title(t, loc="left", fontsize=11.5)
        ax.set_aspect("equal")
        ax.axis("off")
    fig.savefig(path)
    plt.close(fig)
