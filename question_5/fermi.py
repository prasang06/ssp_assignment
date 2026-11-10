"""Fermi-Dirac statistics for a parabolic-band semiconductor.

Single conduction band in the effective-mass approximation, 3D. Energies are
handled in joules internally; `EV` converts to and from electronvolts.

Carrier density is evaluated through the dimensionless Fermi-Dirac integral

    n = N_c (2/sqrt(pi)) F_{1/2}(eta),   eta = (mu - E_c) / kT

which keeps the units in one place and makes the integration cutoff a multiple
of kT rather than a fixed energy.
"""

import numpy as np
from scipy import integrate, optimize
from scipy.special import expit

# ---- constants (SI) ----
HBAR = 1.054571817e-34
M_E = 9.1093837015e-31
K_B = 1.380649e-23
EV = 1.602176634e-19          # joules per electronvolt


# ---- occupation ----

def _check_positive(**kw):
    for name, v in kw.items():
        if not np.isfinite(v) or v <= 0:
            raise ValueError(f"{name} must be finite and positive, got {v!r}")


def fermi_dirac(E, mu, T):
    """f(E) = 1/(exp((E-mu)/kT) + 1), written to not overflow. Needs T > 0."""
    _check_positive(T=T)
    # expit(x) = 1/(1+exp(-x)), so f = expit(-(E-mu)/kT) with no large exp
    return expit(-(np.asarray(E, dtype=float) - mu) / (K_B * T))


# ---- density of states ----

def dos(E, m_eff, Ec=0.0):
    """Conduction-band DOS per unit volume per unit energy; zero below Ec."""
    E = np.asarray(E, dtype=float)
    out = np.zeros_like(E)
    above = E > Ec
    out[above] = (1.0 / (2 * np.pi**2)) * (2 * m_eff / HBAR**2) ** 1.5 \
        * np.sqrt(E[above] - Ec)
    return out


def n_c(m_eff, T):
    """Effective conduction-band density of states N_c."""
    _check_positive(m_eff=m_eff, T=T)
    return 2.0 * (m_eff * K_B * T / (2 * np.pi * HBAR**2)) ** 1.5


# ---- carrier density ----

def _quad(fn, a, b):
    """quad with a purely relative tolerance; fails loudly if it cannot meet it.

    The default epsabs (~1.5e-8) is an absolute floor, which for a tiny
    integral silently becomes a large relative error.
    """
    if b <= a:
        return 0.0
    val, err = integrate.quad(fn, a, b, epsabs=0.0, epsrel=1e-12, limit=400)
    if err > 1e-9 * abs(val):
        raise RuntimeError(f"Fermi integral did not converge (rel. err {err / abs(val):.1e})")
    return val


def fermi_integral_half(eta):
    """F_{1/2}(eta) = int_0^inf sqrt(x)/(1+exp(x-eta)) dx.

    eta < 0: the factor e^eta is taken outside, so the quadrature works on an
    O(1) integrand and the relative accuracy holds however small F is.
    eta >= 0: the range is split at x = eta, where the occupation steps from
    1 to 0, and again 60 below it, so the step is resolved even when eta is
    huge. The integrand decays like exp(-(x-eta)), so eta + 60 is far past
    negligible.
    """
    eta = float(eta)
    if eta < 0.0:
        # sqrt(x) expit(eta - x) = e^eta * sqrt(x) e^{-x} / (1 + e^{eta - x})
        g = lambda x: np.sqrt(x) * np.exp(-x) / (1.0 + np.exp(eta - x))
        return np.exp(eta) * _quad(g, 0.0, 60.0)
    h = lambda x: np.sqrt(x) * expit(eta - x)
    split = max(eta - 60.0, 0.0)
    # below `split` the occupation is 1 to within e^-60, so that piece is
    # exactly (2/3) split^{3/2} minus a negligible correction
    return (2.0 / 3.0) * split**1.5 + _quad(h, split, eta) + _quad(h, eta, eta + 60.0)


def carrier_density(mu, T, m_eff, Ec=0.0):
    """n = int D(E) f(E) dE, via the dimensionless integral."""
    eta = (mu - Ec) / (K_B * T)
    return n_c(m_eff, T) * (2.0 / np.sqrt(np.pi)) * fermi_integral_half(eta)


def solve_mu(n, T, m_eff, Ec=0.0):
    """Chemical potential mu(T) at fixed n, by root-finding on eta.

    The bracket comes from the two closed forms, which bound the root:
    Boltzmann overestimates n at a given eta (so the true eta is above
    ln(n/N_c)), and the T = 0 sphere underestimates it (so the true eta is
    below E_F/kT when that is positive). The bracket is then only widened if
    round-off makes those bounds touch the root.
    """
    _check_positive(n=n, T=T, m_eff=m_eff)
    target = float(n)
    pref = n_c(m_eff, T) * (2.0 / np.sqrt(np.pi))

    def residual(eta):
        # relative residual: same scale whatever n is
        return pref * fermi_integral_half(eta) / target - 1.0

    eta_b = np.log(target / n_c(m_eff, T))
    eta_d = fermi_quantities(target, m_eff)["E_F"] / (K_B * T)
    lo, hi = eta_b - 1.0, max(eta_d, eta_b) + 1.0
    r_lo, r_hi = residual(lo), residual(hi)
    for _ in range(60):
        if r_lo < 0.0 < r_hi:
            break
        if r_lo >= 0.0:
            lo -= max(10.0, abs(lo))
            r_lo = residual(lo)
        if r_hi <= 0.0:
            hi += max(10.0, abs(hi))
            r_hi = residual(hi)
    else:
        raise RuntimeError("could not bracket the chemical potential")

    eta = optimize.brentq(residual, lo, hi, xtol=1e-13, rtol=4 * np.finfo(float).eps)
    return Ec + eta * K_B * T


def boltzmann_mu(n, T, m_eff, Ec=0.0):
    """Non-degenerate closed form: n = N_c exp((mu-Ec)/kT). For validation."""
    _check_positive(n=n)
    return Ec + K_B * T * np.log(n / n_c(m_eff, T))


# ---- degenerate-gas quantities ----

def fermi_quantities(n, m_eff, valleys=None):
    """E_F (above Ec), k_F, v_F, T_F at T = 0 for carrier density n.

    Single isotropic valley (valleys=None): one Fermi sphere of mass m_eff.

    Multi-valley, valleys = (M_c, m_l, m_t) in kg: the carriers are shared
    between M_c equivalent ellipsoids, n/M_c each. E_F is the same as one
    sphere of density-of-states mass m_eff = M_c^{2/3} (m_l m_t^2)^{1/3}, but
    the Fermi surface is not: each valley has semi-axes k_l, k_t with
    hbar^2 k_i^2 / 2 m_i = E_F, and the velocity on it is hbar k_i / m_i
    along each principal direction. `k_F` is then the per-valley geometric
    mean radius (3 pi^2 n / M_c)^{1/3}; the directional values are k_F_l,
    k_F_t, v_F_l, v_F_t. `v_F` is sqrt(2 E_F / m_dv), a single-number summary
    only -- no electron on the surface need move at exactly that speed.

    These describe a degenerate gas. For a non-degenerate semiconductor they
    are formal numbers; `degeneracy` below says which regime applies.
    """
    _check_positive(n=n, m_eff=m_eff)
    if valleys is None:
        k_F = (3 * np.pi**2 * n) ** (1 / 3)
        E_F = HBAR**2 * k_F**2 / (2 * m_eff)
        return {"E_F": E_F, "k_F": k_F, "v_F": HBAR * k_F / m_eff, "T_F": E_F / K_B}

    M_c, m_l, m_t = valleys
    m_dv = (m_l * m_t**2) ** (1 / 3)         # density-of-states mass of ONE valley
    k_F = (3 * np.pi**2 * n / M_c) ** (1 / 3)
    E_F = HBAR**2 * k_F**2 / (2 * m_dv)
    k_l, k_t = (np.sqrt(2 * m * E_F) / HBAR for m in (m_l, m_t))
    return {"E_F": E_F, "k_F": k_F, "k_F_l": k_l, "k_F_t": k_t,
            "v_F_l": HBAR * k_l / m_l, "v_F_t": HBAR * k_t / m_t,
            "v_F": np.sqrt(2 * E_F / m_dv), "T_F": E_F / K_B}


def degeneracy(mu, T, Ec=0.0):
    """eta = (mu - Ec)/kT.  eta >> 1 degenerate, eta << -1 non-degenerate."""
    return (mu - Ec) / (K_B * T)


def sommerfeld_mu(n, T, m_eff, Ec=0.0):
    """Degenerate low-T expansion: mu ~ E_F[1 - (pi^2/12)(kT/E_F)^2]."""
    _check_positive(n=n, T=T)
    E_F = fermi_quantities(n, m_eff)["E_F"]
    return Ec + E_F * (1.0 - (np.pi**2 / 12.0) * (K_B * T / E_F) ** 2)
