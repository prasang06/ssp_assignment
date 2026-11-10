"""Streamlit interface for Fermi-Dirac statistics in a semiconductor.

Run:  streamlit run app.py
"""

import os
import sys

import numpy as np
import pandas as pd
import streamlit as st
from matplotlib.figure import Figure

_HERE = os.path.dirname(os.path.abspath(__file__))
# when run as a page of streamlit_app.py the entry script's directory is on
# sys.path, not this one, so add both explicitly. Streamlit re-runs this script
# on every widget change, so insert only once or the list grows without bound.
for _p in (os.path.normpath(os.path.join(_HERE, "..", "common")), _HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import style
import fermi as f

style.apply()
# only the entry script may configure the page; harmless no-op when this
# module runs as a page of streamlit_app.py
try:
    st.set_page_config(page_title="Fermi–Dirac Statistics in a Semiconductor", layout="wide")
except Exception:
    pass
st.title("Fermi\u2013Dirac Statistics in a Semiconductor Crystal")
st.caption(r"Solves $n=\int D(E)f(E)\,dE$ for the chemical potential $\mu(T)$.")

CM3 = 1e6


def ev(E):
    return E / f.EV



# ---- material data ----

# Eg (eV), density-of-states mass m_de/m_e, valleys (M_c, m_l, m_t) or None,
# shallow-donor ionisation energy E_d (eV), approximate Mott density (cm^-3).
# m_de already folds in the valley degeneracy (Si 6 X valleys, Ge 4 L), so N_c
# must not be multiplied by it again; m_de = M_c^{2/3} (m_l m_t^2)^{1/3}.
MATS = {
    "GaAs": dict(Eg=1.42, m=0.067, valleys=None, Ed=0.0058, mott=1e16),
    "Si":   dict(Eg=1.12, m=1.08, valleys=(6, 0.98, 0.19), Ed=0.045, mott=3.7e18),
    "Ge":   dict(Eg=0.66, m=0.56, valleys=(4, 1.64, 0.082), Ed=0.0127, mott=3e17),
}
# above this the single parabolic valley stops describing any of the presets
# (satellite valleys in GaAs, non-parabolicity, dopant solubility): report Sec. IV
N_VALID = 1e19
# GaAs L valley above Gamma: carriers start spilling into it once mu nears it
GAAS_L = 0.29

# ---- inputs ----

with st.sidebar:
    st.header("Material")
    preset = st.selectbox("Preset", ["Custom", "GaAs", "Si", "Ge"])
    mat = MATS.get(preset)
    eg_d, me_d = (mat["Eg"], mat["m"]) if mat else (1.42, 0.067)

    Eg = st.number_input("Band gap $E_g$ (eV)", 0.1, 6.0, float(eg_d), 0.01,
                         key=f"eg_{preset}")
    m_rel = st.number_input(r"Effective mass $m^*/m_e$", 0.01, 5.0, float(me_d),
                            0.001, format="%.3f", key=f"me_{preset}")

    st.header("Conditions")
    T = st.slider("Temperature $T$ (K)", 1, 1000, 300)
    log_n = st.slider(r"Carrier concentration  $\log_{10} n$ (cm$^{-3}$)",
                      12.0, 20.0, 17.0, 0.1,
                      help="The model is valid up to about 1e19 cm^-3; see the warning "
                           "shown beyond that.")
    span = st.slider("Energy range above/below the gap (eV)", 0.1, 2.0, 0.5, 0.1)

n = 10.0 ** log_n * CM3
m_eff = m_rel * f.M_E
Ec = Eg * f.EV
kT = f.K_B * T
# the valley structure belongs to the preset's mass; if the mass is edited the
# anisotropic masses no longer match it, so fall back to one isotropic valley
valleys = None
if mat and mat["valleys"] and abs(m_rel - mat["m"]) < 1e-9:
    Mc, ml, mt = mat["valleys"]
    valleys = (Mc, ml * f.M_E, mt * f.M_E)

# ---- solve ----


@st.cache_data(max_entries=256)
def mu_of(n, T, m_eff, Ec):
    return f.solve_mu(n, T, m_eff, Ec)


@st.cache_data(max_entries=64)
def mu_sweep_T(n, m_eff, Ec):
    Ts = np.linspace(5.0, 1000.0, 90)
    return Ts, np.array([f.solve_mu(n, t, m_eff, Ec) for t in Ts])


@st.cache_data(max_entries=64)
def mu_sweep_n(T, m_eff, Ec):
    ns = np.logspace(12, 20, 81)
    return ns, np.array([f.solve_mu(x * CM3, T, m_eff, Ec) for x in ns])


mu = mu_of(n, float(T), m_eff, Ec)
eta = f.degeneracy(mu, T, Ec)
q = f.fermi_quantities(n, m_eff, valleys=valleys)

# ---- computed quantities ----

st.subheader("Computed quantities")
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("μ − E_c  (meV)", f"{ev(mu - Ec)*1000:.1f}")
c2.metric("E_F above E_c  (meV)", f"{ev(q['E_F'])*1000:.1f}")
if valleys:
    c3.metric("k_F per valley  (nm⁻¹)", f"{q['k_F']/1e9:.3f}",
              help=f"Geometric-mean radius of each of the {valleys[0]} valleys; "
                   f"semi-axes k_l = {q['k_F_l']/1e9:.3f}, k_t = {q['k_F_t']/1e9:.3f} nm⁻¹.")
    c4.metric("v_F  l / t  (10⁵ m/s)", f"{q['v_F_l']/1e5:.2f} / {q['v_F_t']/1e5:.2f}",
              help="Fermi velocity along the long (l) and short (t) valley axes, "
                   "v_i = ħk_i/m_i. It is anisotropic, so no single value applies.")
else:
    c3.metric("k_F  (nm⁻¹)", f"{q['k_F']/1e9:.3f}")
    c4.metric("v_F  (10⁵ m/s)", f"{q['v_F']/1e5:.3f}")
c5.metric("T_F  (K)", f"{q['T_F']:.0f}")

if eta > 2:
    st.success(f"**Degenerate** (η = (μ−E_c)/k_BT = {eta:.2f}). The Fermi surface is "
               "well defined, so $k_F$, $v_F$ and $T_F$ describe real carriers.")
elif eta < -3:
    st.warning(f"**Non-degenerate** (η = {eta:.2f}). μ lies well below the band edge and "
               "Boltzmann statistics hold to better than 2 %. There is no Fermi surface, "
               "so $k_F$, $v_F$ and $T_F$ above are formal values, not physical ones.")
else:
    st.info(f"**Intermediate** (η = {eta:.2f}). Neither limit applies cleanly (Boltzmann "
            "would be off by more than 2 %); the full Fermi–Dirac integral is required, "
            "which is what is solved here.")

if mat and mat["valleys"] and not valleys:
    st.caption("The mass differs from the preset's, so the valley structure is dropped "
               "and $k_F$, $v_F$ are for a single isotropic valley.")

# ---- where the model stops applying ----

if mu < 3 * kT:
    st.error(f"**Outside the model.** μ is {ev(mu)*1000:.0f} meV from the valence-band "
             "edge, within 3 k_BT of it or below it. The model has no holes, so it cannot "
             "describe this state: in a real crystal the intrinsic density at this "
             "temperature exceeds the chosen n, and μ would be pinned near mid-gap.")
elif mu < 0.5 * Ec:
    st.warning("μ is below mid-gap, so the chosen n is roughly below the intrinsic density "
               "at this temperature. Holes, which this model omits, would then outnumber "
               "electrons.")

if n / CM3 > N_VALID:
    st.warning(f"**Beyond the model's range** (n > 10¹⁹ cm⁻³). A single parabolic valley "
               "no longer holds at this doping: satellite valleys fill, the band becomes "
               "non-parabolic and dopants stop being fully active. Treat the numbers as "
               "illustrative only.")
elif preset == "GaAs" and ev(mu - Ec) > GAAS_L - 3 * ev(kT):
    st.warning(f"μ is within a few k_BT of the GaAs L valley ({GAAS_L} eV above Γ), "
               "which would start to take carriers that this model does not count.")

if mat and n / CM3 < mat["mott"] and eta < 0:
    # fraction of donors ionised if n electrons came from donors at E_d below
    # E_c (non-degenerate, spin degeneracy 2): N_D+/N_D = 1/(1 + 2 (n/N_c) e^{E_d/kT})
    ion = 1.0 / (1.0 + 2.0 * n / f.n_c(m_eff, T) * np.exp(mat["Ed"] * f.EV / kT))
    ion_txt = "under 1 %" if ion < 0.01 else f"about {ion*100:.0f} %"
    if ion < 0.9:
        st.warning(f"**Freeze-out not modelled.** At {T} K only {ion_txt} of "
                   f"donors ({mat['Ed']*1000:.0f} meV below E_c) would be ionised. Here "
                   "n is held fixed, whereas a real crystal with fixed doping would lose "
                   "free electrons and μ would settle between the donor level and E_c.")
elif not mat and T < 100 and eta < 0:
    st.caption("At low temperature a real non-degenerate crystal freezes out (donors "
               "recapture electrons); this model holds n fixed and does not capture it.")

# ---- bands and occupation ----


def energy_grid(lo, hi, n_pts):
    """Uniform grid plus a dense patch around mu, so the Fermi step is resolved
    even when k_BT is far smaller than the uniform spacing."""
    patch = np.linspace(mu - 12 * kT, mu + 12 * kT, 600)
    E = np.concatenate([np.linspace(lo, hi, n_pts), patch[(patch > lo) & (patch < hi)]])
    return np.unique(E)


left, right = st.columns(2)
E = energy_grid(-span * f.EV, Ec + span * f.EV, 2000)

with left:
    st.subheader("Bands, Fermi level and occupation")
    fig = Figure(figsize=(7.2, 4.2))
    a1, a2 = fig.subplots(1, 2, sharey=True, gridspec_kw=dict(width_ratios=[1, 1.3]))
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

with right:
    st.subheader("Density of states and occupied DOS")
    lo = min(Ec - 0.02 * f.EV, mu - 4 * kT)
    hi = max(Ec + 0.3 * f.EV, mu + 8 * kT)
    Ed = energy_grid(lo, hi, 2500)
    D = f.dos(Ed, m_eff, Ec) * f.EV * 1e-6
    occ = D * f.fermi_dirac(Ed, mu, T)

    fig = Figure(figsize=(7.2, 4.2))
    ax = fig.subplots()
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
    st.caption("Area under $D(E)f(E)$ is the carrier concentration $n$.")

# ---- sweeps ----

st.subheader("Fermi level versus temperature and carrier concentration")
s1, s2 = st.columns(2)

with s1:
    Ts, mus = mu_sweep_T(n, m_eff, Ec)
    fig = Figure(figsize=(5.6, 3.4))
    ax = fig.subplots()
    ax.plot(Ts, ev(mus - Ec), color=style.ACOUSTIC, lw=2)
    ax.axhline(0.0, color="0.55", lw=1.0)
    ax.axhline(ev(q["E_F"]), color=style.EXACT, ls=":", lw=1.0)
    ax.plot([T], [ev(mu - Ec)], marker="o", ms=7, color=style.OPTICAL[0], zorder=4)
    ax.set_xlabel("Temperature (K)")
    ax.set_ylabel(r"$\mu-E_c$ (eV)")
    ax.set_title("dotted: $E_F=\\mu(0)$;  marker: current $T$", fontsize=9)
    st.pyplot(fig)
    st.caption("n is held fixed at every T, so the low-T end shows no donor freeze-out.")

with s2:
    ns, mun = mu_sweep_n(float(T), m_eff, Ec)
    fig = Figure(figsize=(5.6, 3.4))
    ax = fig.subplots()
    ax.axvspan(N_VALID, ns[-1], color=style.GAP_FILL, alpha=0.3, lw=0)
    ax.semilogx(ns, ev(mun - Ec), color=style.ACOUSTIC, lw=2)
    ax.axhline(0.0, color="0.55", lw=1.0)
    ax.plot([10.0 ** log_n], [ev(mu - Ec)], marker="o", ms=7,
            color=style.OPTICAL[0], zorder=4)
    ax.set_xlabel(r"$n$ (cm$^{-3}$)")
    ax.set_ylabel(r"$\mu-E_c$ (eV)")
    ax.set_title(r"above $E_c$ = degenerate;  shaded: beyond model", fontsize=9)
    st.pyplot(fig)

st.caption("Both sweeps are recomputed from the full Fermi–Dirac integral at every "
           "point; neither uses the Boltzmann approximation.")
