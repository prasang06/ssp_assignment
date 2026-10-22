"""Validation checks from SCOPE.md. Run: python test_phonon.py"""

import numpy as np
import phonon as ph


def check(name, ok, detail=""):
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f"  {detail}" if detail else ""))
    return ok


# ---- 1. diatomic matches the closed form ----

def test_diatomic():
    m1, m2, K, a = 1.0, 4.0, 1.0, 1.0
    q, w = ph.dispersion([m1, m2], K, a, nq=401)
    ac, op = ph.diatomic_exact(q, m1, m2, K, a)
    err = max(np.abs(w[:, 0] - ac).max(), np.abs(w[:, 1] - op).max())
    return check("diatomic vs closed form", err < 1e-10, f"max err {err:.2e}")


# ---- 2. monatomic limit, including a folded cell of equal masses ----

def test_monatomic():
    K, a = 1.0, 1.0
    q, w = ph.dispersion([1.0], K, a, nq=401)
    err = np.abs(w[:, 0] - ph.monatomic_exact(q, 1.0, K, a)).max()
    ok = check("monatomic vs closed form", err < 1e-10, f"max err {err:.2e}")

    # three equal masses in a cell of length 3a must unfold onto the same curve:
    # the set of frequencies at each q is a subset of the monatomic branch
    _, w3 = ph.dispersion([1.0, 1.0, 1.0], K, 3 * a, nq=301)
    qq = np.linspace(-np.pi / a, np.pi / a, 20001)
    exact = ph.monatomic_exact(qq, 1.0, K, a)
    far = max(np.abs(exact - f).min() for f in w3.ravel())
    return ok and check("equal-mass cell unfolds onto monatomic branch",
                        far < 1e-3, f"max distance {far:.2e}")


# ---- 3. acoustic slope at q->0 equals the analytic sound velocity ----

def test_sound_velocity():
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
    worst = 0.0
    for m in ([1.0, 4.0], [1.0, 2.0, 3.0], [1.0, 1.0, 2.0, 5.0]):
        w = np.sqrt(np.clip(np.linalg.eigvalsh(ph.dynamical_matrix(0.0, m, 1.0, 1.0)), 0, None))
        worst = max(worst, w[0])
    return check("omega_acoustic(q=0) = 0", worst < 1e-8, f"max {worst:.2e}")


# ---- 5. equal masses close the gap ----

def test_gap_closure():
    _, w_eq = ph.dispersion([1.0, 1.0], nq=801)
    _, w_un = ph.dispersion([1.0, 4.0], nq=801)
    return check("equal masses -> no gap", len(ph.band_gaps(w_eq)) == 0) and \
           check("unequal masses -> gap", len(ph.band_gaps(w_un)) == 1)


if __name__ == "__main__":
    results = [test_diatomic(), test_monatomic(), test_sound_velocity(),
               test_acoustic_zero(), test_gap_closure()]
    print(f"\n{sum(results)}/{len(results)} checks passed")
    raise SystemExit(0 if all(results) else 1)
