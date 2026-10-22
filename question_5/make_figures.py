"""Regenerates every figure in figures/. Run: python make_figures.py"""

import os
import sys

import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "common"))
import style
import fermi as f

FIG = os.path.join(os.path.dirname(__file__), "figures")

# GaAs-like reference material, energies measured from the valence-band edge
EG = 1.42 * f.EV
M = 0.067 * f.M_E
CM3 = 1e6
N_REF = 1e17 * CM3
T_REF = 300.0


def ev(E):
    return E / f.EV


# ---- band diagram with f(E) alongside ----

def fig_bands():
    mu = f.solve_mu(N_REF, T_REF, M, EG)
    E = np.linspace(-0.4 * f.EV, EG + 0.6 * f.EV, 2000)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.5, 4.0), sharey=True,
                                   gridspec_kw=dict(width_ratios=[1.0, 1.3]))

    # left: the bands themselves
    ax1.axhspan(ev(EG), ev(E[-1]), color=style.ACOUSTIC, alpha=0.18, lw=0)
    ax1.axhspan(ev(E[0]), 0.0, color=style.OPTICAL[0], alpha=0.18, lw=0)
    ax1.axhline(ev(EG), color=style.ACOUSTIC, lw=2)
    ax1.axhline(0.0, color=style.OPTICAL[0], lw=2)
    ax1.axhline(ev(mu), color=style.EXACT, lw=1.8, ls="--")
    ax1.text(0.5, ev(EG) + 0.06, r"conduction band  $E_c$", ha="center", fontsize=9,
             color=style.ACOUSTIC)
    ax1.text(0.5, -0.16, r"valence band  $E_v$", ha="center", fontsize=9,
             color=style.OPTICAL[0])
    ax1.text(0.5, ev(mu) + 0.04, r"$\mu$", ha="center", fontsize=10)
    ax1.annotate("", xy=(0.12, ev(EG)), xytext=(0.12, 0.0),
                 arrowprops=dict(arrowstyle="<|-|>", color="0.3", lw=1.2))
    ax1.text(0.17, ev(EG) / 2, rf"$E_g = {EG/f.EV:.2f}$ eV", fontsize=9, va="center")
    ax1.set_xticks([])
    ax1.set_ylabel("Energy  (eV)")
    ax1.set_title("Band edges and Fermi level")

    # right: occupation on the same energy axis
    ax2.plot(f.fermi_dirac(E, mu, T_REF), ev(E), color=style.ACOUSTIC, lw=2)
    ax2.axhline(ev(mu), color=style.EXACT, lw=1.2, ls="--")
    ax2.axvline(0.5, color="0.8", lw=0.8)
    ax2.plot([0.5], [ev(mu)], marker="o", ms=6, color=style.EXACT, zorder=4)
    ax2.annotate(r"$f(\mu)=1/2$", xy=(0.5, ev(mu)), xytext=(0.62, ev(mu) - 0.28),
                 fontsize=9, arrowprops=dict(arrowstyle="->", lw=0.8))
    ax2.set_xlabel(r"Occupation  $f(E)$")
    ax2.set_xlim(-0.03, 1.03)
    ax2.set_title(rf"Fermi--Dirac occupation at $T={T_REF:.0f}$ K")

    fig.suptitle(rf"$n = 10^{{17}}$ cm$^{{-3}}$,  $m^*={M/f.M_E:.3f}\,m_e$", y=1.01)
    fig.savefig(f"{FIG}/bands.png")
    plt.close(fig)


# ---- f(E) sharpening as T falls ----

def fig_occupation():
    mu = f.solve_mu(1e19 * CM3, T_REF, M, EG)
    E = np.linspace(mu - 0.35 * f.EV, mu + 0.35 * f.EV, 2000)

    fig, ax = plt.subplots(figsize=(5.4, 3.6))
    cols = plt.cm.Blues(np.linspace(0.45, 1.0, 4))
    for T, c in zip([10.0, 100.0, 300.0, 600.0], cols):
        ax.plot(ev(E - mu), f.fermi_dirac(E, mu, T), color=c, label=f"$T={T:.0f}$ K")
    ax.axvline(0.0, color="0.8", lw=0.8)
    ax.axhline(0.5, color="0.8", lw=0.8)
    ax.set_xlabel(r"$E-\mu$  (eV)")
    ax.set_ylabel(r"$f(E)$")
    ax.set_title("The step softens over a width $\\sim k_BT$")
    ax.legend()
    fig.savefig(f"{FIG}/occupation.png")
    plt.close(fig)


# ---- D(E), f(E) and the occupied DOS ----

def dos_per_ev_cm3(E, m_eff, Ec):
    """DOS in the conventional semiconductor units: states eV^-1 cm^-3."""
    return f.dos(E, m_eff, Ec) * f.EV * 1e-6


def fig_dos():
    """D(E) and D(E)f(E) across three doping regimes.

    Log y: at n = 1e16 the occupied fraction is ~1e-7 of D(E), so on a linear
    axis the occupied curve would be a flat zero and show nothing.
    """
    fig, axes = plt.subplots(1, 3, figsize=(11, 3.5))

    for ax, (n_cm3, lab) in zip(axes, [(1e16, "non-degenerate"),
                                       (1e18, "intermediate"),
                                       (1e19, "degenerate")]):
        n = n_cm3 * CM3
        mu = f.solve_mu(n, T_REF, M, EG)
        # window follows mu, so the occupied region is bounded by physics
        # window must contain mu, which lies BELOW Ec when non-degenerate
        lo = min(EG - 0.02 * f.EV, mu - 4 * f.K_B * T_REF)
        hi = max(EG + 0.3 * f.EV, mu + 8 * f.K_B * T_REF)
        E = np.linspace(lo, hi, 3000)

        D = dos_per_ev_cm3(E, M, EG)
        occ = D * f.fermi_dirac(E, mu, T_REF)

        ax.semilogy(ev(E), D, color=style.ACOUSTIC, lw=1.8, label=r"$D(E)$")
        ax.semilogy(ev(E), np.maximum(occ, 1e10), color=style.OPTICAL[0], lw=1.8,
                    label=r"$D(E)\,f(E)$")
        ax.fill_between(ev(E), np.maximum(occ, 1e10), 1e10,
                        color=style.OPTICAL[0], alpha=0.25, lw=0)
        ax.axvline(ev(mu), color=style.EXACT, ls="--", lw=1.2)
        ax.annotate(r"$\mu$", xy=(ev(mu), 3e21), fontsize=10, ha="center")
        ax.set_ylim(1e12, 1e23)
        ax.set_xlim(ev(E[0]), ev(E[-1]))
        ax.set_xlabel("Energy  (eV)")
        ax.set_title(rf"$n=10^{{{int(np.log10(n_cm3))}}}$ cm$^{{-3}}$ ({lab})",
                     fontsize=9.5)
        ax.legend(fontsize=8, loc="lower left")

    axes[0].set_ylabel(r"states  eV$^{-1}$ cm$^{-3}$")
    fig.suptitle(rf"Density of states and its occupied part at $T={T_REF:.0f}$ K"
                 r"  (area under $D f$ is $n$)", y=1.03)
    fig.tight_layout()
    fig.savefig(f"{FIG}/dos_occupied.png")
    plt.close(fig)


# ---- mu versus temperature ----

def fig_mu_vs_T():
    """Two panels: the crossover below E_c, and the degenerate T^2 law."""
    T = np.linspace(10.0, 700.0, 160)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 3.9))

    # (a) moderate doping -- mu drops below the band edge as T rises
    for n_cm3, c in zip([1e16, 1e18, 1e19],
                        [style.ACOUSTIC, style.OPTICAL[0], style.OPTICAL[1]]):
        n = n_cm3 * CM3
        mu = np.array([f.solve_mu(n, t, M, EG) for t in T])
        ax1.plot(T, ev(mu - EG), color=c,
                 label=rf"$n=10^{{{int(np.log10(n_cm3))}}}$ cm$^{{-3}}$")
        ax1.axhline(ev(f.fermi_quantities(n, M)["E_F"]), color=c, lw=0.8, ls=":")

    ax1.axhline(0.0, color="0.55", lw=1.0)
    ax1.text(695, 0.012, r"$E_c$", ha="right", fontsize=9, color="0.4")
    ax1.text(20, -0.33, r"dotted: $E_F=\mu(0)$", fontsize=8.5, color="0.35")
    ax1.set_xlabel("Temperature  (K)")
    ax1.set_ylabel(r"$\mu - E_c$  (eV)")
    ax1.set_title("(a) Fermi level falls as $T$ rises")
    ax1.legend(loc="lower left", fontsize=9)

    # (b) strongly degenerate -- the numerical mu follows the Sommerfeld law
    n = 1e19 * CM3
    E_F = f.fermi_quantities(n, M)["E_F"]
    Td = np.linspace(10.0, 700.0, 120)
    mu_num = np.array([f.solve_mu(n, t, M, EG) for t in Td])
    mu_som = np.array([f.sommerfeld_mu(n, t, M, EG) for t in Td])

    ax2.plot(Td, (mu_som - EG) / E_F, color=style.EXACT, lw=3.0, alpha=0.35,
             label=r"Sommerfeld $1-\frac{\pi^2}{12}(k_BT/E_F)^2$")
    ax2.plot(Td[::4], (mu_num[::4] - EG) / E_F, ls="none", marker="o", ms=4,
             color=style.ACOUSTIC, label="numerical")
    ax2.set_xlabel("Temperature  (K)")
    ax2.set_ylabel(r"$\mu / E_F$")
    ax2.set_title(rf"(b) Degenerate case, $n=10^{{19}}$ cm$^{{-3}}$")
    ax2.legend(loc="lower left", fontsize=8.5)

    fig.tight_layout()
    fig.savefig(f"{FIG}/mu_vs_T.png")
    plt.close(fig)


# ---- mu versus carrier concentration ----

def fig_mu_vs_n():
    n_cm3 = np.logspace(13, 21, 200)
    fig, ax = plt.subplots(figsize=(5.8, 4.0))

    for T, c in zip([77.0, 300.0, 600.0], [style.ACOUSTIC, style.OPTICAL[0],
                                           style.OPTICAL[1]]):
        mu = np.array([f.solve_mu(x * CM3, T, M, EG) for x in n_cm3])
        ax.semilogx(n_cm3, ev(mu - EG), color=c, label=f"$T={T:.0f}$ K")

    ax.axhline(0.0, color="0.6", lw=1.0)
    ax.text(1.2e13, 0.02, r"$E_c$  (degenerate above this line)", fontsize=8.5,
            color="0.4")
    ax.set_xlabel(r"Carrier concentration  (cm$^{-3}$)")
    ax.set_ylabel(r"$\mu - E_c$  (eV)")
    ax.set_title("Doping pushes the Fermi level into the band")
    ax.legend(loc="upper left", fontsize=9)
    fig.savefig(f"{FIG}/mu_vs_n.png")
    plt.close(fig)


if __name__ == "__main__":
    style.apply()
    os.makedirs(FIG, exist_ok=True)
    fig_bands()
    fig_occupation()
    fig_dos()
    fig_mu_vs_T()
    fig_mu_vs_n()
    print("figures written to", os.path.abspath(FIG))
