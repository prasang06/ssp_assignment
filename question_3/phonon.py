"""Phonon dispersion of a 1D lattice with p atoms per unit cell.

Convention: `a` is the FULL unit-cell length, so the Brillouin zone is
q in [-pi/a, pi/a] and the diatomic case has cos(q*a/2) where texts that
set `a` to the nearest-neighbour spacing write cos(q*a).

Spring constants: K is either one number (every bond equal) or a list of p
per-bond values, K[j] joining atom j to atom j+1 and K[p-1] joining the last
atom of a cell to the first atom of the next one.
"""

import numpy as np

EPS = np.finfo(float).eps


# ---- input handling ----

def _masses(m):
    """Validate and normalise the mass list. Every public function in this file
    runs its input through here, so bad masses fail early with a clear message."""
    m = np.atleast_1d(np.asarray(m, dtype=float))
    if m.ndim != 1 or m.size == 0:
        raise ValueError("masses must be a non-empty 1D list")
    if not np.all(np.isfinite(m)) or np.any(m <= 0):
        raise ValueError("masses must be finite and positive")
    return m


def _springs(K, p):
    """Per-bond spring constants as an array of length p.

    Lets callers pass one K (all bonds equal) or one K per bond; validates the
    values so a non-positive spring can never reach the eigen-solver."""
    K = np.atleast_1d(np.asarray(K, dtype=float))
    if K.size == 1:
        K = np.full(p, K[0])
    if K.size != p:
        raise ValueError(f"K must be a scalar or have one entry per bond ({p})")
    if not np.all(np.isfinite(K)) or np.any(K <= 0):
        # K <= 0 is not a lattice: the 'frequencies' would be imaginary
        raise ValueError("spring constants must be finite and positive")
    return K


# ---- dynamical matrix ----

def dynamical_matrix(q, m, K, a):
    """Mass-weighted dynamical matrix D(q) for masses m and springs K.

    Atom j couples to j+1 inside the cell; atom p couples back to atom 1 of
    the next cell, which is the only q-dependent term.

    Role: the physics core. Everything else (dispersion, gaps, DOS, modes, the
    app and every figure) is built on the eigenvalues of this matrix.
    """
    m = _masses(m)
    p = m.size
    K = _springs(K, p)
    sm = np.sqrt(m)            # sqrt(m_j)*sqrt(m_k), not sqrt(m_j*m_k): no overflow
    D = np.zeros((p, p), dtype=complex)

    if p == 1:
        # the single atom bonds to both neighbouring cells: 2K/m - 2K/m*cos(qa)
        D[0, 0] = 2.0 * K[0] / m[0] * (1.0 - np.cos(q * a))
        return D

    # each atom sits between the bond on its left and the one on its right
    np.fill_diagonal(D, (np.roll(K, 1) + K) / m)

    # intra-cell bonds
    for j in range(p - 1):
        c = -K[j] / (sm[j] * sm[j + 1])
        D[j, j + 1] = c
        D[j + 1, j] = c

    # inter-cell bond, carries all the q-dependence
    # += not =: at p=2 this bond shares the slot with the intra-cell one
    c = -K[-1] * np.exp(-1j * q * a) / (sm[0] * sm[-1])
    D[0, -1] += c
    D[-1, 0] += np.conj(c)
    return D


def _frequencies(w2, D):
    """sqrt of eigenvalues, clipping only round-off-sized negatives.

    Role: turns omega^2 from the eigen-solver into omega, and is where an
    unstable lattice (genuinely negative omega^2) is rejected."""
    floor = -100.0 * EPS * max(np.abs(D).max(), 1e-300)
    if np.any(w2 < floor):
        raise ValueError("negative omega^2: the lattice is mechanically unstable")
    return np.sqrt(np.clip(w2, 0.0, None))


def frequencies_at(q, m, K=1.0, a=1.0):
    """Branch frequencies at a single wavevector, ascending.

    Role: the one-q building block. dispersion() calls it for every q, and the
    app uses it directly for the q=0 and q=pi/a eigenfrequency tables."""
    D = dynamical_matrix(q, m, K, a)
    if not np.all(np.isfinite(D)):
        raise ValueError("dynamical matrix is not finite; inputs out of range")
    return _frequencies(np.linalg.eigvalsh(D), D)


def dispersion(m, K=1.0, a=1.0, nq=401, full_zone=True):
    """Frequencies omega(q) on a q grid. Returns (q, omega) with omega shape (nq, p).

    D(q) is Hermitian, so eigvalsh gives real, ascending eigenvalues: branch 0
    is acoustic, branches 1.. are optical. In a nearest-neighbour chain the
    branch extrema sit at q = 0 and q = pi/a, so the full-zone grid is forced
    to contain q = 0 (nq rounded up to odd); otherwise branch limits and gap
    edges would be read off points that miss the extrema.

    Role: the main entry point. The app's dispersion plot, the DOS and every
    results figure start from the (q, omega) arrays returned here.
    """
    m = _masses(m)
    qmax = np.pi / a
    if full_zone and nq % 2 == 0:
        nq += 1
    q = np.linspace(-qmax if full_zone else 0.0, qmax, nq)
    w = np.array([frequencies_at(qi, m, K, a) for qi in q])
    return q, w


# ---- derived quantities ----

def branch_limits(w):
    """(min, max) frequency of each branch.

    Role: feeds the "branch limits" table in the app and the report's cases table."""
    return list(zip(w.min(axis=0), w.max(axis=0)))


def band_gaps(w, tol=1e-9):
    """Gaps between consecutive branches as (index, bottom, top, width).

    Branch i and i+1 are separated only if the whole of i lies below the whole
    of i+1 over the zone. `tol` is relative to the highest frequency, so the
    answer does not depend on the units of K and m.

    Role: finds the forbidden-frequency bands that the app shades and labels, and
    that the report quotes (gap 0.7071 for Case A, 0.0658 for Case B, ...).
    """
    thresh = tol * max(w.max(), 1e-300)
    gaps = []
    for i in range(w.shape[1] - 1):
        bottom, top = w[:, i].max(), w[:, i + 1].min()
        if top - bottom > thresh:
            gaps.append((i, bottom, top, top - bottom))
    return gaps


def sound_velocity(m, K=1.0, a=1.0):
    """Analytic acoustic slope at q->0.

    The p springs of a cell act in series, K_eff = 1/sum(1/K_j), and the whole
    cell mass moves: v = a*sqrt(K_eff/sum(m)). With equal springs this is
    a*sqrt(K/(p*sum(m))).

    Role: closed-form cross-check of the acoustic slope; shown in the app and
    compared with the numerical slope in test_phonon.py.
    """
    m = _masses(m)
    K = _springs(K, m.size)
    return a * np.sqrt(1.0 / np.sum(1.0 / K) / m.sum())


def is_folded(m, K=1.0, rtol=1e-9):
    """True if every mass and every spring in the cell is equal (p > 1).

    The true period is then a/p and the 'optical' branches are the acoustic
    branch folded back into the smaller zone, not genuine optical modes.

    Role: lets the app label such branches "Folded acoustic" instead of "Optical".
    """
    m = _masses(m)
    K = _springs(K, m.size)
    return m.size > 1 and np.ptp(m) <= rtol * m.max() and np.ptp(K) <= rtol * K.max()


def dos(m, K=1.0, a=1.0, nq=4001, nbins=200, bins=None):
    """Phonon DOS per unit cell by histogramming omega over a dense q mesh.

    Normalised so that the integral of g over all frequencies equals p, the
    number of branches: density=True gives unit area, so scale by p. The
    q = +pi/a endpoint is dropped because it is the same state as -pi/a.
    Pass explicit bin edges via `bins` to compare several lattices at one bin
    width; peak heights at a van Hove singularity depend on the bin width.

    Role: supplies the DOS panel in the app and dos.png in the report.
    """
    _, w = dispersion(m, K, a, nq=nq)
    w = w[:-1]
    counts, edges = np.histogram(w.ravel(), bins=nbins if bins is None else bins,
                                 density=True)
    # density=True normalises over the binned range; correct for any modes
    # that fall outside explicit edges (none do when edges span the spectrum)
    inside = np.mean((w.ravel() >= edges[0]) & (w.ravel() <= edges[-1]))
    return 0.5 * (edges[:-1] + edges[1:]), w.shape[1] * inside * counts


# ---- closed forms, for validation ----

def monatomic_exact(q, m=1.0, K=1.0, a=1.0):
    """omega = 2*sqrt(K/m)*|sin(qa/2)|.

    Role: independent closed form for p=1, used only to validate the numerics
    (test_phonon.py) and for the app's analytic overlay. Not used in the solve."""
    return 2.0 * np.sqrt(K / m) * np.abs(np.sin(q * a / 2.0))


def diatomic_exact(q, m1, m2, K=1.0, a=1.0):
    """Textbook two-branch solution. Returns (acoustic, optical).

    omega_-^2 is written as 4K sin^2/(m1 m2 (s + root)) rather than K(s - root),
    which avoids cancellation when the two terms are nearly equal; the square
    root argument is clipped because rounding can push it just below zero at
    the zone edge for equal masses.

    Role: independent closed form for p=2, used to validate the numerics
    (test_phonon.py, validation.png) and for the app's analytic overlay.
    """
    s = 1.0 / m1 + 1.0 / m2
    sin2 = np.sin(q * a / 2.0) ** 2
    root = np.sqrt(np.clip(s**2 - 4.0 * sin2 / (m1 * m2), 0.0, None))
    w_minus2 = 4.0 * K * sin2 / (m1 * m2 * (s + root))
    return np.sqrt(w_minus2), np.sqrt(K * (s + root))


# ---- eigenvectors ----

def modes(q, m, K=1.0, a=1.0, rtol=1e-6):
    """Frequencies, real-space displacement patterns and degeneracy flags at one q.

    eigh returns the mass-weighted eigenvectors e; the physical displacement
    amplitude is u_j = e_j / sqrt(m_j), which is what gets drawn.

    `degenerate[b]` is True when branch b shares its frequency with another
    branch at this q. eigh then returns an arbitrary basis of the degenerate
    subspace, so the drawn pattern for that branch is not unique.

    Role: gives the app's "Mode displacements" arrows and modes.png; the
    degeneracy flag lets the app warn instead of drawing an arbitrary pattern.
    """
    m = _masses(m)
    D = dynamical_matrix(q, m, K, a)
    w2, e = np.linalg.eigh(D)
    w = _frequencies(w2, D)
    u = e / np.sqrt(m)[:, None]

    # eigh fixes each column only up to a global phase, which at the zone edge
    # can be a pure i -- taking Re() then gives zero. Rotate so the largest
    # component of each mode is real and positive.
    lead = np.argmax(np.abs(u), axis=0)
    u = u * np.exp(-1j * np.angle(u[lead, np.arange(u.shape[1])]))
    u = u / np.abs(u).max(axis=0)  # normalise each mode for plotting

    tol = rtol * max(w2.max(), 1e-300)
    if w2.size == 1:
        return w, u, np.array([False])
    sep = np.abs(w2[:, None] - w2[None, :])
    np.fill_diagonal(sep, np.inf)          # a branch is not degenerate with itself
    return w, u, sep.min(axis=1) < tol
