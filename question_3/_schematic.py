"""Lattice schematic figure. Imported by make_figures.py."""

import numpy as np
import matplotlib.pyplot as plt

import style

ATOM_COLORS = [style.ACOUSTIC, style.OPTICAL[0], style.OPTICAL[1], style.OPTICAL[2]]


def radius(m, mref=1.0):
    """Circle radius for a mass; shared so springs can stop at the atom edge."""
    return 0.085 * (m / mref) ** (1 / 3)


def spring(ax, x0, x1, y=0.0, coils=4, amp=0.05, color="0.25", lw=1.3, zorder=1,
           r0=0.0, r1=0.0):
    """Zigzag between two atoms, drawn edge to edge rather than centre to centre."""
    x0, x1 = x0 + r0, x1 - r1
    lead = 0.18 * (x1 - x0)
    xz = np.linspace(x0 + lead, x1 - lead, 2 * coils + 1)
    yz = y + amp * np.array([0] + [(-1) ** k for k in range(2 * coils - 1)] + [0])
    ax.plot([x0, x0 + lead], [y, y], color=color, lw=lw, zorder=zorder, solid_capstyle="round")
    ax.plot(xz, yz, color=color, lw=lw, zorder=zorder, solid_capstyle="round")
    ax.plot([x1 - lead, x1], [y, y], color=color, lw=lw, zorder=zorder, solid_capstyle="round")


def atom(ax, x, m, color, y=0.0, label=None, mref=1.0, dashed=False):
    """Circle with radius set by mass, so heavier atoms read bigger."""
    r = radius(m, mref)
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
    disp = 0.085  # keeps the displaced atom clear of its neighbour

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
                            arrowprops=dict(arrowstyle="-|>", color="0.15", lw=1.6,
                                            mutation_scale=14))
                ax.text(x + disp / 2 + 0.05, 0.285, r"$u_2^{\,n}$", ha="left",
                        va="bottom", fontsize=11)
                ax.text(x, -0.24, r"$m_2$", ha="center", va="top", fontsize=11)
            else:
                atom(ax, x, masses[j], ATOM_COLORS[j], label=rf"$m_{{{j+1}}}$")

    # springs, including the two that run off the edges
    xs = [n * a + (j + 0.5) * dx for n in range(ncell) for j in range(p)]
    rs = [radius(masses[i % p]) for i in range(len(xs))]
    spring(ax, xs[0] - dx, xs[0], r1=rs[0])
    for i in range(len(xs) - 1):
        spring(ax, xs[i], xs[i + 1], r0=rs[i], r1=rs[i + 1])
    spring(ax, xs[-1], xs[-1] + dx, r0=rs[-1])
    ax.text(-0.30, 0, r"$\cdots$", ha="center", va="center", fontsize=13)
    ax.text(ncell * a + 0.30, 0, r"$\cdots$", ha="center", va="center", fontsize=13)

    # one spring labelled, not all of them
    ax.text(xs[1] + dx / 2, 0.13, r"$K$", ha="center", va="bottom", fontsize=11)

    for n in range(ncell + 1):
        ax.plot([n * a, n * a], [-0.34, 0.44], color="0.75", lw=0.9,
                linestyle=(0, (4, 3)), zorder=0)
    for n, name in enumerate([r"cell $n-1$", r"cell $n$", r"cell $n+1$"]):
        ax.text((n + 0.5) * a, 0.52, name, ha="center", va="center", fontsize=10.5)

    # dimension line for the cell length
    ax.annotate("", xy=(2 * a, -0.42), xytext=(a, -0.42),
                arrowprops=dict(arrowstyle="<|-|>", color="0.15", lw=1.2))
    ax.text(1.5 * a, -0.55, r"$a$  (full cell length)", ha="center", va="top", fontsize=11)

    ax.set_xlim(-0.5, ncell * a + 0.5)
    ax.set_ylim(-0.70, 0.62)


def panel_two(ax):
    """(b) p=2: the two bonds that share matrix element D_12."""
    p, ncell, a = 2, 2, 1.0
    masses = [1.0, 2.5]
    dx = a / p

    xs = [n * a + (j + 0.5) * dx for n in range(ncell) for j in range(p)]
    rs = [radius(masses[i % p]) for i in range(len(xs))]
    spring(ax, xs[0] - dx, xs[0], r1=rs[0])
    spring(ax, xs[0], xs[1], color=style.ACOUSTIC, lw=2.0, r0=rs[0], r1=rs[1])   # intra
    spring(ax, xs[1], xs[2], color=style.OPTICAL[0], lw=2.0, r0=rs[1], r1=rs[2])  # inter
    spring(ax, xs[2], xs[3], r0=rs[2], r1=rs[3])
    spring(ax, xs[3], xs[3] + dx, r0=rs[3])
    ax.text(-0.42, 0, r"$\cdots$", ha="center", va="center", fontsize=13)
    ax.text(ncell * a + 0.42, 0, r"$\cdots$", ha="center", va="center", fontsize=13)

    for i, x in enumerate(xs):
        j = i % p
        atom(ax, x, masses[j], ATOM_COLORS[j], label=rf"$m_{{{j+1}}}$")

    ax.plot([a, a], [-0.34, 0.72], color="0.75", lw=0.9,
            linestyle=(0, (4, 3)), zorder=0)
    ax.text(0.5 * a, 0.80, r"cell $n$", ha="center", fontsize=10.5)
    ax.text(1.5 * a, 0.80, r"cell $n+1$", ha="center", fontsize=10.5)

    for x0, x1, c, lab, yb in [(xs[0], xs[1], style.ACOUSTIC, "intra-cell $K$", 0.26),
                               (xs[1], xs[2], style.OPTICAL[0], "inter-cell $K$", 0.52)]:
        ax.annotate("", xy=(x1, yb), xytext=(x0, yb),
                    arrowprops=dict(arrowstyle="<|-|>", color=c, lw=1.3))
        ax.text(0.5 * (x0 + x1), yb + 0.045, lab, ha="center", va="bottom",
                fontsize=10, color=c)

    ax.text(a, -0.50,
            r"Both bonds join the same pair $m_1\!-\!m_2$: one inside cell $n$, one across the"
            "\n" r"boundary. Both land in the same element $D_{12}$, so the implementation must"
            "\n" r"$\it{accumulate}$ their contributions rather than overwrite one with the other.",
            ha="center", va="top", fontsize=9.5, linespacing=1.5)

    ax.set_xlim(-0.6, ncell * a + 0.6)
    ax.set_ylim(-1.05, 0.95)


def make(path):
    fig, axes = plt.subplots(2, 1, figsize=(7.6, 5.1),
                             gridspec_kw=dict(height_ratios=[1.0, 1.05], hspace=0.30))
    panel_general(axes[0])
    panel_two(axes[1])
    for ax, t in zip(axes, [r"(a)  General chain ($p$ atoms per unit cell)",
                            r"(b)  $p=2$: the two bonds that share $D_{12}$"]):
        ax.set_title(t, loc="left", fontsize=11.5)
        ax.set_aspect("equal")
        ax.axis("off")
    fig.savefig(path)
    plt.close(fig)
