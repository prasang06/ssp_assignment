"""Validation checks from PLAN.md. Run: python test_fermi.py"""

import numpy as np
import fermi as f

M = 0.067 * f.M_E          # GaAs-like effective mass
CM3 = 1e6                  # cm^-3 -> m^-3


def check(name, ok, detail=""):
    """Print one PASS/FAIL line and return the boolean. Shared by every test below."""
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f"  {detail}" if detail else ""))
    return ok


# ---- 1. non-degenerate limit matches the Boltzmann closed form ----

# Compared in eta = (mu - Ec)/kT, which does not depend on where the energy
# zero sits (a relative error in mu would). Fermi-Dirac and Boltzmann are not
# meant to agree exactly: n = N_c (e^eta - e^{2 eta}/2^{3/2} + ...), so the
# solved eta must exceed ln(n/N_c) by e^eta/(2 sqrt 2) to leading order. The
# check is that the numerics reproduce that correction, not just a small gap.

def test_boltzmann():
    """Low density: solve_mu matches the Boltzmann closed form (including the first FD correction)."""
    worst_gap = worst_corr = 0.0
    T = 300.0
    for n_cm3 in (1e12, 1e14, 1e15):
        n = n_cm3 * CM3
        eta = f.degeneracy(f.solve_mu(n, T, M), T)
        eta_b = f.degeneracy(f.boltzmann_mu(n, T, M), T)
        corr = np.exp(eta_b) / (2 * np.sqrt(2))
        worst_gap = max(worst_gap, abs(eta - eta_b))
        worst_corr = max(worst_corr, abs((eta - eta_b) / corr - 1))
    return check("non-degenerate vs Boltzmann, in eta", worst_gap < 1e-3,
                 f"max |d eta| {worst_gap:.2e}") and \
        check("eta - eta_Boltzmann equals the leading FD correction e^eta/2^1.5",
              worst_corr < 1e-4, f"max rel dev {worst_corr:.2e}")


# ---- 2. degenerate limit: mu -> E_F as T -> 0 ----

def test_degenerate():
    """High density, T=1 K: mu agrees with the T=0 value E_F (relative error < 1e-4)."""
    n = 1e19 * CM3
    E_F = f.fermi_quantities(n, M)["E_F"]
    mu = f.solve_mu(n, 1.0, M)          # 1 K is deep in the degenerate regime
    err = abs(mu - E_F) / E_F
    return check("degenerate T->0 vs E_F", err < 1e-4, f"rel err {err:.2e}")


# ---- 3. round trip: the solved mu reproduces n ----

def test_round_trip():
    """solve_mu then carrier_density returns the original n across many (n, T)."""
    worst = 0.0
    for n_cm3 in (1e14, 1e16, 1e18, 1e20):
        for T in (50.0, 300.0, 600.0):
            n = n_cm3 * CM3
            back = f.carrier_density(f.solve_mu(n, T, M), T, M)
            worst = max(worst, abs(back - n) / n)
    return check("carrier-density round trip", worst < 1e-8, f"max rel err {worst:.2e}")


# ---- 4. f(mu) = 1/2 at any temperature ----

def test_half_occupancy():
    """f(mu) = 1/2 at every temperature."""
    worst = max(abs(f.fermi_dirac(0.3 * f.EV, 0.3 * f.EV, T) - 0.5)
                for T in (1.0, 77.0, 300.0, 1000.0))
    return check("f(mu) = 1/2", worst < 1e-15, f"max dev {worst:.2e}")


# ---- 5. Sommerfeld expansion in the degenerate regime ----

def test_sommerfeld():
    """Strongly degenerate gas: solve_mu follows the Sommerfeld T^2 expansion."""
    n = 1e20 * CM3                       # strongly degenerate, E_F ~ 1 eV
    worst = 0.0
    for T in (20.0, 50.0, 100.0):
        num = f.solve_mu(n, T, M)
        som = f.sommerfeld_mu(n, T, M)
        worst = max(worst, abs(num - som) / abs(som))
    return check("degenerate mu(T) vs Sommerfeld", worst < 1e-4,
                 f"max rel err {worst:.2e}")


# ---- 6. DOS is zero in the gap and matches the analytic form above Ec ----

def test_dos():
    """D(E) is zero below E_c and scales as sqrt(E-E_c) above it."""
    Ec = 1.42 * f.EV
    below = f.dos(np.linspace(0.0, Ec, 50), M, Ec)
    E = Ec + np.array([0.01, 0.1, 0.5]) * f.EV
    ana = (1 / (2 * np.pi**2)) * (2 * M / f.HBAR**2) ** 1.5 * np.sqrt(E - Ec)
    return check("DOS zero in the gap", np.all(below == 0)) and \
        check("DOS matches analytic form",
              np.allclose(f.dos(E, M, Ec), ana, rtol=1e-12))


# ---- 7. F_{1/2} itself, against independent closed forms at both extremes ----

def test_fermi_integral():
    """F_1/2 against its convergent series (eta<0) and asymptotic form (eta>>1)."""
    # eta < 0: convergent series (sqrt(pi)/2) sum (-1)^{k+1} e^{k eta} / k^{3/2}
    k = np.arange(1, 400)
    worst_neg = max(abs(f.fermi_integral_half(eta) /
                        (np.sqrt(np.pi) / 2 * np.sum((-1) ** (k + 1) * np.exp(k * eta) / k**1.5))
                        - 1) for eta in (-40.0, -20.0, -15.0, -5.0, -0.5))
    # eta >> 1: Sommerfeld asymptotic series, truncation ~ eta^-6
    asym = lambda e: 2 / 3 * e**1.5 * (1 + np.pi**2 / (8 * e**2) + 7 * np.pi**4 / (640 * e**4))
    worst_pos = max(abs(f.fermi_integral_half(eta) / asym(eta) - 1)
                    for eta in (1e3, 1e5, 1e7))
    return check("F_1/2 vs series, eta in [-40, -0.5]", worst_neg < 1e-12,
                 f"max rel err {worst_neg:.2e}") and \
        check("F_1/2 vs asymptotic series, eta in [1e3, 1e7]", worst_pos < 1e-12,
              f"max rel err {worst_pos:.2e}")


# ---- 8. multi-valley Fermi quantities ----

def test_multivalley():
    """Si/Ge ellipsoidal valleys: E_F equals the single-sphere value for the DOS mass."""
    # Si: 6 X valleys, m_l = 0.98, m_t = 0.19 -> m_de = 6^{2/3}(m_l m_t^2)^{1/3}
    Mc, ml, mt = 6, 0.98 * f.M_E, 0.19 * f.M_E
    m_de = Mc ** (2 / 3) * (ml * mt**2) ** (1 / 3)
    n = 1e20 * CM3
    one = f.fermi_quantities(n, m_de)
    many = f.fermi_quantities(n, m_de, valleys=(Mc, ml, mt))
    # E_F must agree with the equivalent sphere; k_F must not, by Mc^{1/3}
    ok_E = abs(many["E_F"] / one["E_F"] - 1) < 1e-12
    ok_k = abs(one["k_F"] / many["k_F"] - Mc ** (1 / 3)) < 1e-12
    # the ellipsoid's volume must hold n/Mc electrons: k_l k_t^2 = 3 pi^2 n/Mc
    ok_v = abs(many["k_F_l"] * many["k_F_t"] ** 2 / (3 * np.pi**2 * n / Mc) - 1) < 1e-12
    return check("multi-valley: E_F as one sphere, k_F smaller by M_c^1/3, "
                 "ellipsoid holds n/M_c", ok_E and ok_k and ok_v)


# ---- 9. unphysical input is rejected, not turned into nan / inf ----

def test_guards():
    """Invalid inputs (T=0, n<=0) raise ValueError rather than returning garbage."""
    bad = [lambda: f.fermi_dirac(0.0, 0.0, 0.0), lambda: f.solve_mu(1e20, 0.0, M),
           lambda: f.solve_mu(0.0, 300.0, M), lambda: f.boltzmann_mu(0.0, 300.0, M),
           lambda: f.sommerfeld_mu(0.0, 300.0, M)]
    raised = 0
    for call in bad:
        try:
            call()
        except ValueError:
            raised += 1
    return check("T = 0 and n = 0 raise ValueError", raised == len(bad),
                 f"{raised}/{len(bad)}")


if __name__ == "__main__":
    results = [test_boltzmann(), test_degenerate(), test_round_trip(),
               test_half_occupancy(), test_sommerfeld(), test_dos(),
               test_fermi_integral(), test_multivalley(), test_guards()]
    print(f"\n{sum(results)}/{len(results)} checks passed")
    raise SystemExit(0 if all(results) else 1)
