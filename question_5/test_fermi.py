"""Validation checks from PLAN.md. Run: python test_fermi.py"""

import numpy as np
import fermi as f

M = 0.067 * f.M_E          # GaAs-like effective mass
CM3 = 1e6                  # cm^-3 -> m^-3


def check(name, ok, detail=""):
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f"  {detail}" if detail else ""))
    return ok


# ---- 1. non-degenerate limit matches the Boltzmann closed form ----

def test_boltzmann():
    worst = 0.0
    for n_cm3 in (1e12, 1e14, 1e15):
        n = n_cm3 * CM3
        num = f.solve_mu(n, 300.0, M)
        ana = f.boltzmann_mu(n, 300.0, M)
        worst = max(worst, abs(num - ana) / abs(ana))
    return check("non-degenerate vs Boltzmann", worst < 2e-3, f"max rel err {worst:.2e}")


# ---- 2. degenerate limit: mu -> E_F as T -> 0 ----

def test_degenerate():
    n = 1e19 * CM3
    E_F = f.fermi_quantities(n, M)["E_F"]
    mu = f.solve_mu(n, 1.0, M)          # 1 K is deep in the degenerate regime
    err = abs(mu - E_F) / E_F
    return check("degenerate T->0 vs E_F", err < 1e-4, f"rel err {err:.2e}")


# ---- 3. round trip: the solved mu reproduces n ----

def test_round_trip():
    worst = 0.0
    for n_cm3 in (1e14, 1e16, 1e18, 1e20):
        for T in (50.0, 300.0, 600.0):
            n = n_cm3 * CM3
            back = f.carrier_density(f.solve_mu(n, T, M), T, M)
            worst = max(worst, abs(back - n) / n)
    return check("carrier-density round trip", worst < 1e-8, f"max rel err {worst:.2e}")


# ---- 4. f(mu) = 1/2 at any temperature ----

def test_half_occupancy():
    worst = max(abs(f.fermi_dirac(0.3 * f.EV, 0.3 * f.EV, T) - 0.5)
                for T in (1.0, 77.0, 300.0, 1000.0))
    return check("f(mu) = 1/2", worst < 1e-15, f"max dev {worst:.2e}")


# ---- 5. Sommerfeld expansion in the degenerate regime ----

def test_sommerfeld():
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
    Ec = 1.42 * f.EV
    below = f.dos(np.linspace(0.0, Ec, 50), M, Ec)
    E = Ec + np.array([0.01, 0.1, 0.5]) * f.EV
    ana = (1 / (2 * np.pi**2)) * (2 * M / f.HBAR**2) ** 1.5 * np.sqrt(E - Ec)
    return check("DOS zero in the gap", np.all(below == 0)) and \
        check("DOS matches analytic form",
              np.allclose(f.dos(E, M, Ec), ana, rtol=1e-12))


if __name__ == "__main__":
    results = [test_boltzmann(), test_degenerate(), test_round_trip(),
               test_half_occupancy(), test_sommerfeld(), test_dos()]
    print(f"\n{sum(results)}/{len(results)} checks passed")
    raise SystemExit(0 if all(results) else 1)
