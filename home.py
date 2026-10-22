"""Landing page for the combined app."""

import streamlit as st

st.title("Solid State Physics — Assignment 1")
st.caption("Interactive interfaces for Questions 3 and 5. Pick one from the sidebar.")

c1, c2 = st.columns(2)

with c1:
    st.subheader("Q3 · Phonon dispersion")
    st.markdown(
        "A 1D chain of unit cells holding $p$ atoms of arbitrary mass, joined by "
        "nearest-neighbour springs. A Bloch ansatz reduces the equations of motion to a "
        "$p\\times p$ Hermitian eigenvalue problem, giving one acoustic and $p-1$ optical "
        "branches."
    )
    st.markdown(
        "- dispersion with bandgaps shaded and measured\n"
        "- per-branch frequency limits and eigenfrequencies\n"
        "- phonon density of states\n"
        "- mode displacement patterns"
    )

with c2:
    st.subheader("Q5 · Fermi–Dirac statistics")
    st.markdown(
        "A parabolic conduction band in the effective-mass approximation. The carrier-density "
        "integral $n=\\int D(E)f(E)\\,dE$ is solved numerically for the chemical potential, "
        "with no Boltzmann approximation anywhere."
    )
    st.markdown(
        "- band edges, Fermi level and occupation $f(E)$\n"
        "- density of states and its occupied part\n"
        "- $E_F$, $k_F$, $v_F$, $T_F$ with a degeneracy flag\n"
        "- Fermi level against temperature and carrier concentration"
    )

st.divider()
st.markdown(
    "Both cores are validated against closed-form limits before any number is reported: "
    "the monatomic and diatomic chains for Q3, and the Boltzmann, degenerate and Sommerfeld "
    "limits for Q5. Source and reports are in the "
    "[repository](https://github.com/prasang06/ssp_assignment)."
)
