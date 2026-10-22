"""Regenerates every figure in figures/. Run: python make_figures.py"""

import os
import sys

import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "common"))
import style
import phonon as ph
import _schematic

FIG = os.path.join(os.path.dirname(__file__), "figures")

# the three required combinations, plus labels used in the report
CASES = [
    ("case_a", [1.0, 4.0], 1.0, "Case A: diatomic, $m=(1,4)$"),
    ("case_b", [1.0, 1.1], 1.0, "Case B: diatomic, $m=(1,1.1)$"),
    ("case_c", [1.0, 2.0, 3.0], 1.0, "Case C: triatomic, $m=(1,2,3)$"),
]


# ---- dispersion with gaps shaded ----

def plot_dispersion(ax, m, K, a=1.0, nq=801, annotate_gaps=True, ymax=None):
    q, w = ph.dispersion(m, K, a, nq=nq)
    colors = style.branch_colors(len(m))

    # gap labels sit left of centre; the legend takes the upper right
    for gap in ph.band_gaps(w):
        _, bottom, top, width = gap
        ax.axhspan(bottom, top, color=style.GAP_FILL, alpha=0.3, zorder=0)
        if annotate_gaps:
            ax.annotate(f"gap = {width:.3f}", xy=(-0.5, 0.5 * (bottom + top)),
                        ha="center", va="center", fontsize=8.5,
                        bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="none", alpha=0.85))

    for i in range(w.shape[1]):
        label = "Acoustic" if i == 0 else f"Optical {i}"
        ax.plot(q / np.pi, w[:, i], color=colors[i], label=label)

    ax.set_xlabel(r"Wavevector $q$  ($\pi/a$)")
    ax.set_ylabel(r"Frequency $\omega$  ($\sqrt{K/m_1}$)")
    ax.set_xlim(-1, 1)
    # headroom so the legend never lands on a curve
    ax.set_ylim(0, (ymax if ymax else w.max()) * 1.32)
    return q, w


def _common_ymax():
    return max(ph.dispersion(m, K, nq=401)[1].max() for _, m, K, _ in CASES)


def fig_cases():
    for name, m, K, title in CASES:
        fig, ax = plt.subplots(figsize=(5.2, 3.6))
        plot_dispersion(ax, m, K)
        ax.set_title(title)
        ax.legend(loc="upper right")
        fig.savefig(f"{FIG}/{name}.png")
        plt.close(fig)


def fig_comparison():
    """All three cases side by side — the gap is the thing that changes."""
    fig, axes = plt.subplots(1, 3, figsize=(11, 3.4), sharey=True)
    ymax = _common_ymax()
    for ax, (_, m, K, title) in zip(axes, CASES):
        plot_dispersion(ax, m, K, ymax=ymax)
        ax.set_title(title, fontsize=9.5)
        ax.legend(loc="upper right", fontsize=8)
    for ax in axes[1:]:
        ax.set_ylabel("")
    fig.suptitle("Effect of mass contrast and atom count on the phonon spectrum", y=1.02)
    fig.savefig(f"{FIG}/comparison.png")
    plt.close(fig)


# ---- spring-constant sweep: omega scales as sqrt(K), gap ratios do not move ----

def fig_spring_sweep():
    m = [1.0, 4.0]
    Ks = [0.5, 1.0, 2.0, 4.0]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 3.6))

    # K is ordered, so a single-hue light->dark ramp, not a categorical set
    greys = plt.cm.Blues(np.linspace(0.42, 1.0, len(Ks)))
    for K, c in zip(Ks, greys):
        q, w = ph.dispersion(m, K, nq=601)
        ax1.plot(q / np.pi, w[:, 0], color=c, label=f"$K={K}$")
        ax1.plot(q / np.pi, w[:, 1], color=c)
    ax1.set_xlabel(r"Wavevector $q$  ($\pi/a$)")
    ax1.set_ylabel(r"Frequency $\omega$")
    ax1.set_xlim(-1, 1)
    ax1.set_ylim(0, 4.1)  # headroom so the legend clears the K=4 curve
    ax1.set_title("Both branches scale as $\\sqrt{K}$")
    ax1.legend(loc="upper left", fontsize=9, ncol=2)

    # rescaling by sqrt(K) collapses every curve onto one
    for K, c in zip(Ks, greys):
        q, w = ph.dispersion(m, K, nq=601)
        ax2.plot(q / np.pi, w[:, 0] / np.sqrt(K), color=c, lw=3.2)
        ax2.plot(q / np.pi, w[:, 1] / np.sqrt(K), color=c, lw=3.2)
    ax2.set_xlabel(r"Wavevector $q$  ($\pi/a$)")
    ax2.set_ylabel(r"$\omega/\sqrt{K}$")
    ax2.set_xlim(-1, 1)
    ax2.set_ylim(bottom=0)
    ax2.set_title("Rescaled: the curves collapse")
    # no legend here: all four curves lie on top of each other, which is the point
    ax2.annotate("all four $K$ superimposed", xy=(0.0, 1.05), ha="center", fontsize=9.5,
                 bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="0.7"))

    fig.savefig(f"{FIG}/spring_sweep.png")
    plt.close(fig)


# ---- gap width vs mass ratio ----

def fig_gap_vs_ratio():
    ratios = np.linspace(1.0, 6.0, 120)
    widths = []
    for r in ratios:
        _, w = ph.dispersion([1.0, r], 1.0, nq=401)
        gaps = ph.band_gaps(w)
        widths.append(gaps[0][3] if gaps else 0.0)

    fig, ax = plt.subplots(figsize=(5.2, 3.4))
    ax.plot(ratios, widths, color=style.ACOUSTIC)
    ax.set_xlabel(r"Mass ratio $m_2/m_1$")
    ax.set_ylabel(r"Gap width  ($\sqrt{K/m_1}$)")
    ax.set_title("The gap opens only once the masses differ")
    ax.annotate("gap closes at $m_2=m_1$", xy=(1.0, 0.0), xytext=(2.0, 0.12),
                fontsize=8.5, arrowprops=dict(arrowstyle="->", lw=0.8))
    fig.savefig(f"{FIG}/gap_vs_ratio.png")
    plt.close(fig)


# ---- validation: numerics on top of the closed form ----

def fig_validation():
    m1, m2 = 1.0, 4.0
    q, w = ph.dispersion([m1, m2], 1.0, nq=201)
    ac, op = ph.diatomic_exact(q, m1, m2)

    fig, ax = plt.subplots(figsize=(5.2, 3.6))
    ax.plot(q / np.pi, ac, color=style.EXACT, lw=3.0, alpha=0.35, label="Analytic")
    ax.plot(q / np.pi, op, color=style.EXACT, lw=3.0, alpha=0.35)
    ax.plot(q[::4] / np.pi, w[::4, 0], ls="none", marker="o", ms=4,
            color=style.ACOUSTIC, label="Numerical (acoustic)")
    ax.plot(q[::4] / np.pi, w[::4, 1], ls="none", marker="s", ms=4,
            color=style.OPTICAL[0], label="Numerical (optical)")
    ax.set_xlabel(r"Wavevector $q$  ($\pi/a$)")
    ax.set_ylabel(r"Frequency $\omega$  ($\sqrt{K/m_1}$)")
    ax.set_xlim(-1, 1)
    ax.set_ylim(bottom=0)
    ax.set_title("Diatomic chain: eigensolver vs closed form")
    ax.legend(loc="center")
    fig.savefig(f"{FIG}/validation.png")
    plt.close(fig)


# ---- density of states ----

def fig_dos():
    fig, axes = plt.subplots(1, 3, figsize=(11, 3.2), sharey=True)
    for ax, (_, m, K, title) in zip(axes, CASES):
        # shared y-axis: the report compares peak heights across the three cases
        centres, g = ph.dos(m, K, nq=40001, nbins=200)
        ax.fill_between(centres, g, color=style.ACOUSTIC, alpha=0.35, lw=0)
        ax.plot(centres, g, color=style.ACOUSTIC, lw=1.2)
        ax.set_xlabel(r"Frequency $\omega$")
        ax.set_title(title, fontsize=9.5)
    axes[0].set_ylabel(r"DOS  $g(\omega)$")
    fig.suptitle("Phonon density of states: peaks mark the branch edges", y=1.03)
    fig.savefig(f"{FIG}/dos.png")
    plt.close(fig)


# ---- lattice schematic ----

def fig_schematic():
    _schematic.make(f"{FIG}/schematic.png")


# ---- mode displacements ----

def fig_modes():
    """Case A at the zone centre and edge: what each branch actually does."""
    m, K, a, ncell = [1.0, 4.0], 1.0, 1.0, 4
    p = len(m)
    colors = style.branch_colors(p)

    fig, axes = plt.subplots(2, 2, figsize=(10, 3.8))
    for row, (q_frac, qlab) in enumerate([(0.0, r"$q=0$"), (1.0, r"$q=\pi/a$")]):
        q = q_frac * np.pi / a
        w, u = ph.modes(q, m, K, a)
        for col, bname in enumerate(["Acoustic", "Optical"]):
            ax = axes[row, col]
            for n in range(ncell):
                for j in range(p):
                    x = n * a + (j + 0.5) * a / p
                    d = np.real(u[j, col] * np.exp(1j * q * n * a))
                    ax.plot([x], [0], marker="o", ms=7 + 4 * (j == 1),
                            color=colors[j], zorder=3)
                    if abs(d) > 1e-9:
                        ax.annotate("", xy=(x + 0.17 * d, 0), xytext=(x, 0),
                                    arrowprops=dict(arrowstyle="-|>", color="0.15", lw=1.6))
            ax.axhline(0, color="0.85", lw=0.8, zorder=0)
            for n in range(ncell + 1):
                ax.axvline(n * a, color="0.85", lw=0.8, linestyle=(0, (4, 3)), zorder=0)
            ax.set_title(f"{bname},  {qlab},  " + rf"$\omega={w[col]:.3f}$", fontsize=9.5)
            ax.set_xlim(-0.25, ncell * a + 0.25)
            ax.set_ylim(-0.4, 0.4)
            ax.set_yticks([])
            ax.set_xticks(range(ncell + 1))
            ax.set_xlabel("position  ($a$)", fontsize=9)

    fig.suptitle(r"Mode displacements for $m=(1,4)$: arrows show atomic motion", y=1.04)
    fig.tight_layout()
    fig.savefig(f"{FIG}/modes.png")
    plt.close(fig)


if __name__ == "__main__":
    style.apply()
    os.makedirs(FIG, exist_ok=True)
    fig_schematic()
    fig_cases()
    fig_modes()
    fig_comparison()
    fig_spring_sweep()
    fig_gap_vs_ratio()
    fig_validation()
    fig_dos()
    print("figures written to", os.path.abspath(FIG))
