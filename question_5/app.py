"""Streamlit interface for Fermi-Dirac statistics in a semiconductor.

Run:  streamlit run app.py
"""

import os
import sys

import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "common"))
import style
import fermi as f

style.apply()
st.set_page_config(page_title="Fermi\u2013Dirac Statistics in a Semiconductor",
                   layout="wide")
st.title("Fermi\u2013Dirac Statistics in a Semiconductor Crystal")
st.caption(r"Solves $n=\int D(E)f(E)\,dE$ for the chemical potential $\mu(T)$.")

CM3 = 1e6


def ev(E):
    return E / f.EV


# ---- inputs ----

with st.sidebar:
    st.header("Material")
    preset = st.selectbox("Preset", ["Custom", "GaAs", "Si", "Ge"])
    mats = {"GaAs": (1.42, 0.067), "Si": (1.12, 0.26), "Ge": (0.66, 0.12)}
    if preset in mats:
        eg_d, me_d = mats[preset]
    else:
        eg_d, me_d = 1.42, 0.067

    Eg = st.number_input("Band gap $E_g$ (eV)", 0.1, 6.0, float(eg_d), 0.01,
                         key=f"eg_{preset}")
    m_rel = st.number_input(r"Effective mass $m^*/m_e$", 0.01, 5.0, float(me_d),
                            0.001, format="%.3f", key=f"me_{preset}")

    st.header("Conditions")
    T = st.slider("Temperature $T$ (K)", 1, 1000, 300)
    log_n = st.slider(r"Carrier concentration  $\log_{10} n$ (cm$^{-3}$)",
                      12.0, 21.0, 17.0, 0.1)
    span = st.slider("Energy range above/below the gap (eV)", 0.1, 2.0, 0.5, 0.1)

n = 10.0 ** log_n * CM3
m_eff = m_rel * f.M_E
Ec = Eg * f.EV

# ---- solve ----

mu = f.solve_mu(n, T, m_eff, Ec)
eta = f.degeneracy(mu, T, Ec)
q = f.fermi_quantities(n, m_eff)

# ---- computed quantities ----

st.subheader("Computed quantities")
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("μ − E_c  (meV)", f"{ev(mu - Ec)*1000:.1f}")
c2.metric("E_F above E_c  (meV)", f"{ev(q['E_F'])*1000:.1f}")
c3.metric("k_F  (nm⁻¹)", f"{q['k_F']/1e9:.3f}")
c4.metric("v_F  (10⁵ m/s)", f"{q['v_F']/1e5:.3f}")
c5.metric("T_F  (K)", f"{q['T_F']:.0f}")

if eta > 2:
    st.success(f"**Degenerate** (η = (μ−E_c)/k_BT = {eta:.2f}). The Fermi sphere is "
               "well defined, so $k_F$, $v_F$ and $T_F$ are physically meaningful.")
elif eta < -2:
    st.warning(f"**Non-degenerate** (η = {eta:.2f}). μ lies below the band edge and "
               "Boltzmann statistics apply. There is no Fermi surface, so $k_F$, "
               "$v_F$ and $T_F$ above are formal values, not physical ones.")
else:
    st.info(f"**Intermediate** (η = {eta:.2f}). Neither limit applies cleanly; the "
            "full Fermi–Dirac integral is required, which is what is solved here.")

# ---- bands and occupation ----

left, right = st.columns(2)
E = np.linspace(-span * f.EV, Ec + span * f.EV, 2000)

with left:
    st.subheader("Bands, Fermi level and occupation")
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.2, 4.2), sharey=True,
                                 gridspec_kw=dict(width_ratios=[1, 1.3]))
    a1.axhspan(ev(Ec), ev(E[-1]), color=style.ACOUSTIC, alpha=0.18, lw=0)
    a1.axhspan(ev(E[0]), 0.0, color=style.OPTICAL[0], alpha=0.18, lw=0)
    a1.axhline(ev(Ec), color=style.ACOUSTIC, lw=2)
    a1.axhline(0.0, color=style.OPTICAL[0], lw=2)
    a1.axhline(ev(mu), color=style.EXACT, lw=1.8, ls="--")
    a1.text(0.12, ev(Ec) + 0.04, "$E_c$", fontsize=9, color=style.ACOUSTIC)
    a1.text(0.12, -0.1, "$E_v$", fontsize=9, color=style.OPTICAL[0])
    # mu can sit within a few meV of Ec, so label it on the opposite side
    a1.text(0.78, ev(mu) - 0.085, r"$\mu$", fontsize=10)
    a1.set_xticks([])
    a1.set_ylabel("Energy (eV)")

    a2.plot(f.fermi_dirac(E, mu, T), ev(E), color=style.ACOUSTIC, lw=2)
    a2.axhline(ev(mu), color=style.EXACT, lw=1.0, ls="--")
    a2.set_xlabel("$f(E)$")
    a2.set_xlim(-0.03, 1.03)
    st.pyplot(fig)
    plt.close(fig)

with right:
    st.subheader("Density of states and occupied DOS")
    lo = min(Ec - 0.02 * f.EV, mu - 4 * f.K_B * T)
    hi = max(Ec + 0.3 * f.EV, mu + 8 * f.K_B * T)
    Ed = np.linspace(lo, hi, 2500)
    D = f.dos(Ed, m_eff, Ec) * f.EV * 1e-6
    occ = D * f.fermi_dirac(Ed, mu, T)

    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    ax.semilogy(ev(Ed), np.maximum(D, 1e10), color=style.ACOUSTIC, lw=1.8,
                label="$D(E)$")
    ax.semilogy(ev(Ed), np.maximum(occ, 1e10), color=style.OPTICAL[0], lw=1.8,
                label="$D(E)f(E)$")
    ax.fill_between(ev(Ed), np.maximum(occ, 1e10), 1e10, color=style.OPTICAL[0],
                    alpha=0.25, lw=0)
    ax.axvline(ev(mu), color=style.EXACT, ls="--", lw=1.2)
    ax.set_ylim(1e12, 1e23)
    ax.set_xlabel("Energy (eV)")
    ax.set_ylabel(r"states eV$^{-1}$ cm$^{-3}$")
    ax.legend(loc="lower left", fontsize=8)
    st.pyplot(fig)
    plt.close(fig)
    st.caption("Area under $D(E)f(E)$ is the carrier concentration $n$.")

# ---- sweeps ----

st.subheader("Fermi level versus temperature and carrier concentration")
s1, s2 = st.columns(2)

with s1:
    Ts = np.linspace(5.0, 1000.0, 90)
    mus = np.array([f.solve_mu(n, t, m_eff, Ec) for t in Ts])
    fig, ax = plt.subplots(figsize=(5.6, 3.4))
    ax.plot(Ts, ev(mus - Ec), color=style.ACOUSTIC, lw=2)
    ax.axhline(0.0, color="0.55", lw=1.0)
    ax.axhline(ev(q["E_F"]), color=style.EXACT, ls=":", lw=1.0)
    ax.plot([T], [ev(mu - Ec)], marker="o", ms=7, color=style.OPTICAL[0], zorder=4)
    ax.set_xlabel("Temperature (K)")
    ax.set_ylabel(r"$\mu-E_c$ (eV)")
    ax.set_title("dotted: $E_F=\\mu(0)$;  marker: current $T$", fontsize=9)
    st.pyplot(fig)
    plt.close(fig)

with s2:
    ns = np.logspace(12, 21, 90)
    mun = np.array([f.solve_mu(x * CM3, T, m_eff, Ec) for x in ns])
    fig, ax = plt.subplots(figsize=(5.6, 3.4))
    ax.semilogx(ns, ev(mun - Ec), color=style.ACOUSTIC, lw=2)
    ax.axhline(0.0, color="0.55", lw=1.0)
    ax.plot([10.0 ** log_n], [ev(mu - Ec)], marker="o", ms=7,
            color=style.OPTICAL[0], zorder=4)
    ax.set_xlabel(r"$n$ (cm$^{-3}$)")
    ax.set_ylabel(r"$\mu-E_c$ (eV)")
    ax.set_title(r"above $E_c$ = degenerate;  marker: current $n$", fontsize=9)
    st.pyplot(fig)
    plt.close(fig)

st.caption("Both sweeps are recomputed from the full Fermi–Dirac integral at every "
           "point; neither uses the Boltzmann approximation.")
