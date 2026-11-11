"""Validation checks from SCOPE.md. Run: python test_phonon.py"""

import numpy as np
import phonon as ph


def check(name, ok, detail=""):
    """Print one PASS/FAIL line and return the boolean. Shared by every test below."""
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f"  {detail}" if detail else ""))
    return ok


# ---- 1. diatomic matches the closed form ----

def test_diatomic():
    """p=2 numerics against the textbook two-branch closed form."""
    m1, m2, K, a = 1.0, 4.0, 1.0, 1.0
    q, w = ph.dispersion([m1, m2], K, a, nq=401)
    ac, op = ph.diatomic_exact(q, m1, m2, K, a)
    err = max(np.abs(w[:, 0] - ac).max(), np.abs(w[:, 1] - op).max())
    return check("diatomic vs closed form", err < 1e-10, f"max err {err:.2e}")


# ---- 2. monatomic limit, including a folded cell of equal masses ----

def test_monatomic():
    """p=1 against 2*sqrt(K/m)*|sin(qa/2)|, plus zone folding (equal masses, p=2)."""
    K, a = 1.0, 1.0
    q, w = ph.dispersion([1.0], K, a, nq=401)
    err = np.abs(w[:, 0] - ph.monatomic_exact(q, 1.0, K, a)).max()
    ok = check("monatomic vs closed form", err < 1e-10, f"max err {err:.2e}")

    # three equal masses in a cell of length 3a must be the monatomic branch
    # folded into the smaller zone: at each q the three frequencies are the
    # monatomic ones at q + 2*pi*n/(3a), n = -1, 0, 1. Compared at matched q,
    # so this pins the frequency-to-wavevector map, not just the frequency set.
    q3, w3 = ph.dispersion([1.0, 1.0, 1.0], K, 3 * a, nq=301)
    folded = np.sort(np.stack([ph.monatomic_exact(q3 + 2 * np.pi * n / (3 * a), 1.0, K, a)
                               for n in (-1, 0, 1)], axis=1), axis=1)
    err = np.abs(w3 - folded).max()
    return ok and check("equal-mass cell folds onto monatomic branch at matched q",
                        err < 1e-10, f"max err {err:.2e}")


# ---- 3. acoustic slope at q->0 equals the analytic sound velocity ----

def test_sound_velocity():
    """Numerical acoustic slope at q->0 equals the analytic sound velocity."""
    worst = 0.0
    for m in ([1.0, 4.0], [1.0, 2.0, 3.0], [2.0]):
        a = 1.0
        q, w = ph.dispersion(m, 1.0, a, nq=20001, full_zone=False)
        n = 5  # slope from the first few points, where omega is still linear
        v_num = np.polyfit(q[:n], w[:n, 0], 1)[0]
        v_ana = ph.sound_velocity(m, 1.0, a)
        worst = max(worst, abs(v_num - v_ana) / v_ana)
    return check("acoustic sound velocity", worst < 1e-3, f"max rel err {worst:.2e}")


# ---- 4. acoustic branch vanishes at q=0 ----

def test_acoustic_zero():
    """omega=0 at q=0 for the acoustic branch; this is what caught the `=` vs `+=` bug."""
    worst = 0.0
    for m in ([1.0, 4.0], [1.0, 2.0, 3.0], [1.0, 1.0, 2.0, 5.0]):
        w = ph.frequencies_at(0.0, m, 1.0, 1.0)
        worst = max(worst, w[0])
    return check("omega_acoustic(q=0) = 0", worst < 1e-8, f"max {worst:.2e}")


# ---- 5. equal masses close the gap ----

def test_gap_closure():
    """Equal masses give no gap; unequal masses do."""
    _, w_eq = ph.dispersion([1.0, 1.0], nq=801)
    _, w_un = ph.dispersion([1.0, 4.0], nq=801)
    return check("equal masses -> no gap", len(ph.band_gaps(w_eq)) == 0) and \
           check("unequal masses -> gap", len(ph.band_gaps(w_un)) == 1)


# ---- 6. per-bond springs: invariance and series sound velocity ----

def test_per_bond_springs():
    """A scalar K equals a list of identical per-bond K; with unequal bonds omega_1(0)=0 and the slope follows the series-spring sound velocity."""
    m = [1.0, 2.0, 3.0]
    _, w_scalar = ph.dispersion(m, 1.7, nq=201)
    _, w_list = ph.dispersion(m, [1.7, 1.7, 1.7], nq=201)
    ok = check("per-bond K list equal to scalar K", np.abs(w_scalar - w_list).max() < 1e-14)

    # unequal bonds: omega_1(0) must still vanish and the slope must follow
    # the series-spring formula K_eff = 1/sum(1/K_j)
    K = [1.0, 3.0, 0.5]
    # omega = sqrt(eigenvalue), so round-off of ~eps*|D| in the eigenvalue
    # shows up as ~sqrt(eps*|D|) ~ 1e-8 in omega
    w0 = ph.frequencies_at(0.0, m, K)[0]
    q, w = ph.dispersion(m, K, nq=20001, full_zone=False)
    v_num = np.polyfit(q[:5], w[:5, 0], 1)[0]
    rel = abs(v_num - ph.sound_velocity(m, K)) / ph.sound_velocity(m, K)
    return ok and check("unequal bonds: omega_1(0)=0 and series sound velocity",
                        w0 < 1e-7 and rel < 1e-3, f"omega_1(0) {w0:.1e}, v rel err {rel:.1e}")


# ---- 7. robustness: units, round-off and unphysical input ----

def test_robustness():
    """Edge cases: finite closed forms, unit-independent gap detection, no overflow, q=0 sampled, degeneracy flagged, negative K rejected."""
    # closed form stays finite for equal masses (rounding used to give NaN)
    # and keeps full accuracy at extreme mass ratio (no cancellation)
    q = np.linspace(-np.pi, np.pi, 2001)
    ok = check("diatomic_exact finite for equal masses",
               all(np.all(np.isfinite(ph.diatomic_exact(q, mm, mm)[0])) for mm in (0.09, 0.7, 1.0)))
    qs = np.array([1e-4])
    ac, _ = ph.diatomic_exact(qs, 1.0, 1e9)
    w_ref = qs * ph.sound_velocity([1.0, 1e9])
    ok &= check("diatomic_exact free of cancellation at mass ratio 1e9",
                abs(ac[0] - w_ref[0]) / w_ref[0] < 1e-6)

    # gap detection must not depend on the unit of K
    _, w_big = ph.dispersion([1.0, 1.0, 1.0], 1e14, nq=301)
    _, w_tiny = ph.dispersion([1.0, 4.0], 1e-20, nq=301)
    ok &= check("gap detection independent of units",
                len(ph.band_gaps(w_big)) == 0 and len(ph.band_gaps(w_tiny)) == 1)

    # huge masses no longer overflow the coupling into zero
    _, w_huge = ph.dispersion([1e160, 4e160], 1e160, nq=101)
    _, w_unit = ph.dispersion([1.0, 4.0], 1.0, nq=101)
    ok &= check("no overflow for masses ~1e160", np.allclose(w_huge, w_unit, rtol=1e-12))

    # an even nq must still put a grid point at q = 0
    _, w_even = ph.dispersion([1.0, 4.0], nq=400)
    ok &= check("even nq still samples q = 0", w_even[:, 0].min() == 0.0)

    # degenerate branches are flagged (their drawn pattern is an arbitrary mix)
    ok &= check("degeneracy flagged: equal masses at q = pi/a, not unequal",
                ph.modes(np.pi, [0.7, 0.7])[2].all() and not ph.modes(np.pi, [1.0, 4.0])[2].any())

    try:
        ph.dispersion([1.0, 4.0], -1.0)
        raised = False
    except ValueError:
        raised = True
    return ok and check("negative K rejected, not clipped to omega = 0", raised)


if __name__ == "__main__":
    results = [test_diatomic(), test_monatomic(), test_sound_velocity(),
               test_acoustic_zero(), test_gap_closure(), test_per_bond_springs(),
               test_robustness()]
    print(f"\n{sum(results)}/{len(results)} checks passed")
    raise SystemExit(0 if all(results) else 1)
