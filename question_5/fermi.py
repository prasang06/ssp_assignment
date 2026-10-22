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

def fermi_dirac(E, mu, T):
    """f(E) = 1/(exp((E-mu)/kT) + 1), written to not overflow."""
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
    return 2.0 * (m_eff * K_B * T / (2 * np.pi * HBAR**2)) ** 1.5


# ---- carrier density ----

def fermi_integral_half(eta):
    """F_{1/2}(eta) = int_0^inf sqrt(x)/(1+exp(x-eta)) dx."""
    # integrand decays like exp(-(x-eta)), so eta + 60 is far past negligible
    upper = max(eta, 0.0) + 60.0
    val, _ = integrate.quad(lambda x: np.sqrt(x) * expit(eta - x), 0.0, upper,
                            limit=200)
    return val


def carrier_density(mu, T, m_eff, Ec=0.0):
    """n = int D(E) f(E) dE, via the dimensionless integral."""
    eta = (mu - Ec) / (K_B * T)
    return n_c(m_eff, T) * (2.0 / np.sqrt(np.pi)) * fermi_integral_half(eta)


def solve_mu(n, T, m_eff, Ec=0.0):
    """Chemical potential mu(T) from charge neutrality, by root-finding on eta.

    At low T the integral is nearly a step in eta, so the bracket is widened
    geometrically until it straddles the root instead of being fixed.
    """
    target = float(n)

    def residual(eta):
        return n_c(m_eff, T) * (2.0 / np.sqrt(np.pi)) * fermi_integral_half(eta) - target

    lo, hi = -5.0, 5.0
    for _ in range(80):
        if residual(lo) < 0 < residual(hi):
            break
        lo *= 2.0 if residual(lo) >= 0 else 1.0
        hi *= 2.0 if residual(hi) <= 0 else 1.0
        if lo > -1e-6:
            lo = -5.0
        if abs(lo) > 1e12 or abs(hi) > 1e12:
            raise RuntimeError("could not bracket the chemical potential")
    else:
        raise RuntimeError("could not bracket the chemical potential")

    eta = optimize.brentq(residual, lo, hi, xtol=1e-12, rtol=1e-14)
    return Ec + eta * K_B * T


def boltzmann_mu(n, T, m_eff, Ec=0.0):
    """Non-degenerate closed form: n = N_c exp((mu-Ec)/kT). For validation."""
    return Ec + K_B * T * np.log(n / n_c(m_eff, T))


# ---- degenerate-gas quantities ----

def fermi_quantities(n, m_eff):
    """E_F (above Ec), k_F, v_F, T_F for a filled Fermi sphere of density n.

    These describe a degenerate gas. For a non-degenerate semiconductor they
    are formal numbers; `degeneracy` below says which regime applies.
    """
    k_F = (3 * np.pi**2 * n) ** (1 / 3)
    E_F = HBAR**2 * k_F**2 / (2 * m_eff)
    return {"E_F": E_F, "k_F": k_F, "v_F": HBAR * k_F / m_eff, "T_F": E_F / K_B}


def degeneracy(mu, T, Ec=0.0):
    """eta = (mu - Ec)/kT.  eta >> 1 degenerate, eta << -1 non-degenerate."""
    return (mu - Ec) / (K_B * T)


def sommerfeld_mu(n, T, m_eff, Ec=0.0):
    """Degenerate low-T expansion: mu ~ E_F[1 - (pi^2/12)(kT/E_F)^2]."""
    E_F = fermi_quantities(n, m_eff)["E_F"]
    return Ec + E_F * (1.0 - (np.pi**2 / 12.0) * (K_B * T / E_F) ** 2)
