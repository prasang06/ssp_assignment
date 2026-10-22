"""Phonon dispersion of a 1D lattice with p atoms per unit cell.

Convention: `a` is the FULL unit-cell length, so the Brillouin zone is
q in [-pi/a, pi/a] and the diatomic case has cos(q*a/2) where texts that
set `a` to the nearest-neighbour spacing write cos(q*a).
"""

import numpy as np


# ---- dynamical matrix ----

def dynamical_matrix(q, m, K, a):
    """Mass-weighted dynamical matrix D(q) for masses m, spring constant K.

    Atom j couples to j+1 inside the cell; atom p couples back to atom 1 of
    the next cell, which is the only q-dependent term.
    """
    m = np.atleast_1d(np.asarray(m, dtype=float))
    p = m.size
    D = np.zeros((p, p), dtype=complex)

    np.fill_diagonal(D, 2.0 * K / m)

    # intra-cell bonds
    for j in range(p - 1):
        c = -K / np.sqrt(m[j] * m[j + 1])
        D[j, j + 1] = c
        D[j + 1, j] = c

    # inter-cell bond, carries all the q-dependence
    if p == 1:
        # the single atom bonds to both neighbouring cells: 2K/m - 2K/m*cos(qa)
        D[0, 0] = 2.0 * K / m[0] * (1.0 - np.cos(q * a))
    else:
        # += not =: at p=2 this bond shares the slot with the intra-cell one
        c = -K * np.exp(-1j * q * a) / np.sqrt(m[0] * m[-1])
        D[0, -1] += c
        D[-1, 0] += np.conj(c)

    return D


def dispersion(m, K=1.0, a=1.0, nq=401, full_zone=True):
    """Frequencies omega(q) on a q grid. Returns (q, omega) with omega shape (nq, p).

    D(q) is Hermitian, so eigvalsh gives real, ascending eigenvalues: branch 0
    is acoustic, branches 1.. are optical.
    """
    m = np.atleast_1d(np.asarray(m, dtype=float))
    qmax = np.pi / a
    q = np.linspace(-qmax if full_zone else 0.0, qmax, nq)

    w2 = np.array([np.linalg.eigvalsh(dynamical_matrix(qi, m, K, a)) for qi in q])
    return q, np.sqrt(np.clip(w2, 0.0, None))  # clip: tiny negatives at q=0 are roundoff


# ---- derived quantities ----

def branch_limits(w):
    """(min, max) frequency of each branch."""
    return list(zip(w.min(axis=0), w.max(axis=0)))


def band_gaps(w, tol=1e-9):
    """Gaps between consecutive branches as (index, bottom, top, width).

    Branch i and i+1 are separated only if the whole of i lies below the whole
    of i+1 over the zone.
    """
    gaps = []
    for i in range(w.shape[1] - 1):
        bottom, top = w[:, i].max(), w[:, i + 1].min()
        if top - bottom > tol:
            gaps.append((i, bottom, top, top - bottom))
    return gaps


def sound_velocity(m, K=1.0, a=1.0):
    """Analytic acoustic slope at q->0: v = a*sqrt(K/(p*sum(m)))."""
    m = np.atleast_1d(np.asarray(m, dtype=float))
    return a * np.sqrt(K / (m.size * m.sum()))


def dos(m, K=1.0, a=1.0, nq=4001, nbins=200):
    """Phonon density of states by histogramming omega over a dense q mesh."""
    _, w = dispersion(m, K, a, nq=nq)
    counts, edges = np.histogram(w.ravel(), bins=nbins, density=True)
    return 0.5 * (edges[:-1] + edges[1:]), counts


# ---- closed forms, for validation ----

def monatomic_exact(q, m=1.0, K=1.0, a=1.0):
    """omega = 2*sqrt(K/m)*|sin(qa/2)|."""
    return 2.0 * np.sqrt(K / m) * np.abs(np.sin(q * a / 2.0))


def diatomic_exact(q, m1, m2, K=1.0, a=1.0):
    """Textbook two-branch solution. Returns (acoustic, optical)."""
    s = 1.0 / m1 + 1.0 / m2
    root = np.sqrt(s**2 - 4.0 * np.sin(q * a / 2.0) ** 2 / (m1 * m2))
    return np.sqrt(K * (s - root)), np.sqrt(K * (s + root))


# ---- eigenvectors ----

def modes(q, m, K=1.0, a=1.0):
    """Frequencies and real-space displacement patterns at one q.

    eigh returns the mass-weighted eigenvectors e; the physical displacement
    amplitude is u_j = e_j / sqrt(m_j), which is what gets drawn.
    """
    m = np.atleast_1d(np.asarray(m, dtype=float))
    w2, e = np.linalg.eigh(dynamical_matrix(q, m, K, a))
    u = e / np.sqrt(m)[:, None]
    u = u / np.abs(u).max(axis=0)  # normalise each mode for plotting
    return np.sqrt(np.clip(w2, 0.0, None)), u
