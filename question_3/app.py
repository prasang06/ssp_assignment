"""Streamlit interface for 1D multi-atomic phonon dispersion.

Run:  streamlit run app.py
"""

import os
import sys

import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

_HERE = os.path.dirname(os.path.abspath(__file__))
# when run as a page of streamlit_app.py the entry script's directory is on
# sys.path, not this one, so add both explicitly
sys.path.insert(0, os.path.join(_HERE, "..", "common"))
sys.path.insert(0, _HERE)
import style
import phonon as ph

style.apply()
# only the entry script may configure the page; harmless no-op when this
# module runs as a page of streamlit_app.py
try:
    st.set_page_config(page_title="Phonon Dispersion — 1D Multi-atomic Lattice", layout="wide")
except Exception:
    pass
st.title("Phonon Dispersion in a 1D Multi-atomic Lattice")
st.caption(r"Solves $D(q)\,e = \omega^2 e$ for a chain of $p$ atoms per unit cell.")

# ---- inputs ----

with st.sidebar:
    st.header("Lattice parameters")
    st.subheader("Masses")
    preset = st.selectbox("Preset", ["Custom", "Case A: (1, 4)", "Case B: (1, 1.1)",
                                     "Case C: (1, 2, 3)"])
    defaults = {"Case A: (1, 4)": [1.0, 4.0],
                "Case B: (1, 1.1)": [1.0, 1.1],
                "Case C: (1, 2, 3)": [1.0, 2.0, 3.0]}

    # a preset fixes p, so show it rather than a slider that would disagree with it
    if preset in defaults:
        base = defaults[preset]
        p = len(base)
        st.caption(f"Atoms per unit cell: $p = {p}$  (set by preset)")
    else:
        p = st.slider("Number of atoms per unit cell, $p$", 1, 5, 2)
        base = [1.0 + i for i in range(p)]

    # the key carries the preset: a keyed widget ignores `value` once it exists,
    # so without this, switching preset would leave the old masses in place
    masses = [st.number_input(f"$m_{{{j+1}}}$", min_value=0.01, value=float(base[j]),
                              step=0.1, key=f"m_{preset}_{j}") for j in range(p)]

    st.subheader("Interaction")
    K = st.number_input("Spring constant $K$", min_value=0.01, value=1.0, step=0.1)
    a = st.number_input("Lattice constant $a$ (full cell)", min_value=0.01, value=1.0, step=0.1)
    nq = st.select_slider("q-points", [201, 401, 801, 1601], value=801)
    show_dos = st.checkbox("Show density of states", value=True)
    show_modes = st.checkbox("Show mode displacements", value=True)
    show_exact = st.checkbox("Overlay analytic solution", value=False,
                             help="Available for p = 1 and p = 2.")

# ---- solve ----

q, w = ph.dispersion(masses, K, a, nq=nq)
gaps = ph.band_gaps(w)
limits = ph.branch_limits(w)
colors = style.branch_colors(p)

# ---- dispersion plot ----

left, right = st.columns([3, 2])

with left:
    st.subheader("Dispersion relation")
    fig, ax = plt.subplots(figsize=(7, 4.6))

    for _, bottom, top, width in gaps:
        ax.axhspan(bottom, top, color=style.GAP_FILL, alpha=0.3, zorder=0)
        ax.annotate(f"gap = {width:.4f}", xy=(-0.5, 0.5 * (bottom + top)),
                    ha="center", va="center", fontsize=9,
                    bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="none", alpha=0.85))

    for i in range(p):
        ax.plot(q / np.pi, w[:, i], color=colors[i],
                label="Acoustic" if i == 0 else f"Optical {i}")

    if show_exact and p <= 2:
        if p == 1:
            ax.plot(q / np.pi, ph.monatomic_exact(q, masses[0], K, a),
                    color=style.EXACT, lw=3.0, alpha=0.3, zorder=0, label="Analytic")
        else:
            ac, op = ph.diatomic_exact(q, masses[0], masses[1], K, a)
            ax.plot(q / np.pi, ac, color=style.EXACT, lw=3.0, alpha=0.3, zorder=0,
                    label="Analytic")
            ax.plot(q / np.pi, op, color=style.EXACT, lw=3.0, alpha=0.3, zorder=0)
    elif show_exact:
        st.caption("No closed form for $p > 2$; the overlay is shown only for $p \\le 2$.")

    ax.set_xlabel(r"Wavevector $q$  ($\pi/a$)")
    ax.set_ylabel(r"Frequency $\omega$  ($\sqrt{K/m_1}$)")
    ax.set_xlim(-1, 1)
    ax.set_ylim(0, w.max() * 1.3)
    ax.legend(loc="upper right")
    st.pyplot(fig)
    plt.close(fig)

    csv = "q," + ",".join(["acoustic"] + [f"optical_{i}" for i in range(1, p)]) + "\n"
    csv += "\n".join(",".join(f"{v:.6g}" for v in row) for row in np.column_stack([q, w]))
    st.download_button("Download dispersion as CSV", csv, "dispersion.csv", "text/csv")

with right:
    st.subheader("Branch limits")
    st.dataframe(pd.DataFrame({
        "Branch": ["Acoustic"] + [f"Optical {i}" for i in range(1, p)],
        "ω min": [f"{lo:.4f}" for lo, _ in limits],
        "ω max": [f"{hi:.4f}" for _, hi in limits],
    }), hide_index=True, use_container_width=True)

    st.subheader("Bandgaps")
    if gaps:
        st.dataframe(pd.DataFrame({
            "Between": [f"branch {i} and {i+1}" for i, _, _, _ in gaps],
            "From": [f"{b:.4f}" for _, b, _, _ in gaps],
            "To": [f"{t:.4f}" for _, _, t, _ in gaps],
            "Width": [f"{wd:.4f}" for _, _, _, wd in gaps],
        }), hide_index=True, use_container_width=True)
    else:
        st.info("No gap: the branches touch. Equal masses leave the spectrum unsplit.")

    st.subheader("Sound velocity")
    st.metric("v (q→0, analytic)", f"{ph.sound_velocity(masses, K, a):.4f}")

# ---- eigenfrequencies at the zone centre and edge ----

st.subheader("Eigenfrequencies")
st.caption("At $q=0$ the acoustic mode is a rigid translation of the whole cell "
           "($\\omega=0$); optical modes there are the atoms beating against each other.")

w_centre = np.sqrt(np.clip(np.linalg.eigvalsh(ph.dynamical_matrix(0.0, masses, K, a)), 0, None))
w_edge = np.sqrt(np.clip(np.linalg.eigvalsh(ph.dynamical_matrix(np.pi / a, masses, K, a)), 0, None))
st.dataframe(pd.DataFrame({
    "Branch": ["Acoustic"] + [f"Optical {i}" for i in range(1, p)],
    "ω at q = 0": [f"{v:.4f}" for v in w_centre],
    "ω at q = π/a": [f"{v:.4f}" for v in w_edge],
}), hide_index=True, use_container_width=True)

# ---- density of states ----

if show_dos:
    st.subheader("Density of states")
    centres, g = ph.dos(masses, K, a, nbins=160)
    fig, ax = plt.subplots(figsize=(7, 2.8))
    ax.fill_between(centres, g, color=style.ACOUSTIC, alpha=0.35, lw=0)
    ax.plot(centres, g, color=style.ACOUSTIC, lw=1.2)
    ax.set_xlabel(r"Frequency $\omega$")
    ax.set_ylabel(r"$g(\omega)$")
    st.pyplot(fig)
    plt.close(fig)
    st.caption("Normalised per unit cell, so the area under the curve is the number of "
               "branches p. Peaks are van Hove singularities, where a branch flattens "
               "and many q-states share one frequency.")

# ---- mode displacements ----

if show_modes:
    st.subheader("Mode displacements")
    st.caption("Arrows show the instantaneous displacement of each atom. "
               "Pick a branch and a wavevector to see how that mode actually moves.")

    c1, c2 = st.columns(2)
    with c1:
        branch = st.selectbox("Branch", ["Acoustic"] + [f"Optical {i}" for i in range(1, p)])
    with c2:
        q_frac = st.slider("q  (units of π/a)", 0.0, 1.0, 0.0, 0.05)

    b = 0 if branch == "Acoustic" else int(branch.split()[-1])
    q_sel = q_frac * np.pi / a
    w_sel, u_sel = ph.modes(q_sel, masses, K, a)

    ncells = 4
    y_atom, y_arrow = 0.0, 0.30 * a      # arrows sit on their own row above the chain
    atom_colors = [style.ACOUSTIC] + style.OPTICAL

    # real part of u_j * exp(iqna): the displacement at this instant. Collected
    # first so the arrow scale can be set from the largest one.
    disp = np.array([[np.real(u_sel[j, b] * np.exp(1j * q_sel * n * a))
                      for j in range(p)] for n in range(ncells)])
    dmax = np.abs(disp).max()
    # longest arrow reaches 70% of the atom spacing, whatever p and however u is normalised
    scale = 0.7 * (a / p) / dmax if dmax > 1e-9 else 0.0
    mmin = min(masses)

    fig, ax = plt.subplots(figsize=(8, 2.6))
    for n in range(ncells):
        for j in range(p):
            x = n * a + (j + 0.5) * a / p
            d = disp[n, j]
            # atoms always drawn, sized by mass, so stationary ones stay visible
            ax.plot([x], [y_atom], marker="o",
                    ms=min(16.0, 7.5 * (masses[j] / mmin) ** (1 / 3)),
                    color=atom_colors[j % len(atom_colors)],
                    markeredgecolor="0.15", markeredgewidth=0.8, zorder=3)
            if abs(d) > 1e-9:
                # head length scales with the arrow, so a short arrow is not
                # swallowed by a fixed-size head and amplitude ratios stay readable
                L = scale * d
                ax.arrow(x, y_arrow, L, 0, length_includes_head=True,
                         head_width=0.052 * a, head_length=min(0.05 * a, 0.34 * abs(L)),
                         lw=1.9, fc="0.15", ec="0.15", zorder=4)
                ax.plot([x, x], [y_atom + 0.09 * a, y_arrow], color="0.75", lw=0.7,
                        zorder=1)
    ax.axhline(y_atom, color="0.88", lw=0.8, zorder=0)
    for n in range(ncells + 1):
        ax.axvline(n * a, color="0.88", lw=0.8, linestyle=(0, (4, 3)), zorder=0)
    ax.set_xlim(-0.25 * a, (ncells + 0.25) * a)
    ax.set_ylim(-0.22 * a, 0.52 * a)
    ax.set_yticks([])
    ax.set_xticks([n * a for n in range(ncells + 1)])
    ax.set_xticklabels(range(ncells + 1))
    ax.set_xlabel("Position along the chain  ($a$)")
    ax.set_title(f"{branch} mode at $q = {q_frac:.2f}\\,\\pi/a$,  "
                 f"$\\omega = {w_sel[b]:.4f}$")
    st.pyplot(fig)
    plt.close(fig)

    if b == 0 and q_frac == 0.0:
        st.info("At $q=0$ the acoustic mode is a uniform translation — every atom moves "
                "together, no spring stretches, so $\\omega = 0$.")
    elif b > 0 and q_frac == 0.0:
        st.info("At $q=0$ an optical mode has the atoms inside each cell moving against "
                "one another, with the cell's centre of mass at rest.")
