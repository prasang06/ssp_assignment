# Abhilash: Q3 Physics Core (`phonon.py`)

**Your part:** `phonon.py` and the report §Numerical method.

Back to [README](../README.md).

> **Version note:** the working tree's `phonon.py` has uncommitted changes (per-bond K, validation, `is_folded`). The committed version, which the report describes, uses a scalar K only. See the README heads-up and know which version you are presenting.

## 1. 30-second version

> `phonon.py` builds the mass-weighted dynamical matrix `D(q)` for any number of atoms, calls
> `numpy.linalg.eigvalsh` on it for each q on a grid, and takes square roots to get the p branch
> frequencies. Helper functions extract branch limits, gaps, the sound velocity and a DOS
> histogram. There is no iteration: it is a direct diagonalisation.

## 2. File map

| Function | Job |
|---|---|
| `_masses`, `_springs` | Validate input (positive, finite, right length); a scalar K is broadcast to p bonds |
| `dynamical_matrix(q, m, K, a)` | Builds the p×p complex Hermitian matrix |
| `_frequencies(w2, D)` | √ of eigenvalues; clips only *round-off-sized* negatives, raises if the lattice is unstable |
| `frequencies_at(q, ...)` | Branch frequencies at one q |
| `dispersion(m, K, a, nq, full_zone)` | `(q, ω)`, ω shape (nq, p); forces the grid to contain q=0 (nq made odd) |
| `branch_limits(w)` | (min, max) per branch |
| `band_gaps(w, tol)` | Gaps between consecutive branches |
| `sound_velocity(m, K, a)` | Analytic slope `a√(K_eff/Σm)` |
| `is_folded(m, K)` | True when all masses and springs are equal (p>1): "optical" is just the folded acoustic branch |
| `dos(...)` | Histogram of ω over a dense mesh, normalised to integrate to p |
| `monatomic_exact`, `diatomic_exact` | Closed forms used only for validation |
| `modes(q, ...)` | Frequencies and displacement patterns `u_j = e_j/√m_j` |

## 3. `dynamical_matrix` line by line

```python
sm = np.sqrt(m)                       # √m_j; products √m_j·√m_k avoid overflow vs √(m_j m_k)
D = np.zeros((p, p), dtype=complex)
if p == 1:
    D[0,0] = 2K/m * (1 - cos(qa))     # the one atom bonds to both neighbouring cells
    return D
np.fill_diagonal(D, (np.roll(K,1) + K) / m)   # each atom: bond on its left + bond on its right
for j in range(p-1):                  # intra-cell bonds, symmetric
    c = -K[j]/(sm[j]*sm[j+1]);  D[j,j+1] = c;  D[j+1,j] = c
c = -K[-1]*exp(-1j*q*a)/(sm[0]*sm[-1])        # inter-cell bond: the only q-dependence
D[0,-1] += c;  D[-1,0] += conj(c)             # += not = (p=2: shares a slot with intra bond)
```

Why each piece:
- **`+=` on the inter-cell bond.** At p=2, `D[0,1]` already holds the intra-cell bond.
  Overwriting would drop it and break the acoustic branch at q=0.
- **p=1 special case.** With one atom the "intra" and "inter" bonds both land on the diagonal:
  `2K/m − 2K/m cos(qa) = 4K/m sin²(qa/2)`, matching the monatomic closed form.
- **`np.roll(K, 1)`.** Spring `K[j]` joins atom j to j+1 (and `K[p−1]` joins the last atom to the
  next cell's first). Atom j's two springs are therefore `K[j−1]` and `K[j]`.
- **Conjugate for the lower triangle.** Makes D exactly Hermitian.

## 4. Other design decisions you should know

- **`eigvalsh`** exploits Hermiticity: real eigenvalues, ascending order, so branch 0 is
  acoustic and no sort is needed.
- **Clipping before √.** At q=0 the acoustic eigenvalue is 0 up to round-off and can come out as
  −1e-17, whose √ is `nan`. `_frequencies` clips values above `−100·eps·max|D|` but *raises* for
  anything genuinely negative (an unstable lattice).
- **Grid contains q=0.** For nearest-neighbour chains, branch extrema sit at q=0 and q=π/a, so
  the grid is forced to include them; otherwise limits and gap edges would be read off the wrong
  points.
- **Gap rule.** Gap between branches i and i+1 exists if `max_q ω_i < min_q ω_{i+1}`, with a
  relative tolerance so the answer is unit-independent.
- **DOS.** Histogram `ω` over 4001 q-points, drop the q=+π/a endpoint (same state as −π/a),
  normalise so the integral is p.
- **Diatomic closed form written stably.** `ω₋²` is computed as `4K sin²/(m₁m₂(s+root))` to avoid
  cancellation between two nearly equal terms.

## 5. Report §Numerical method: five steps to recite

1. Grid of n_q wavevectors across the Brillouin zone.
2. Build `D(q)` at each q (accumulating the inter-cell bond).
3. `eigvalsh` → real ascending ω².
4. √ after clipping tiny negatives.
5. Per-branch min/max; gap wherever `min ω_{i+1} > max ω_i`.

Cost: n_q diagonalisations of p×p matrices, negligible, so the app recomputes on every slider
move.

> **Heads-up:** the code listing printed in the report is the *simplified* version (scalar K).
> The real file above also supports per-bond K, p=1, and validation. If asked, say the listing
> shows the core assembly and the full file is in the appendix.

## 6. Likely questions

- **Why `eigvalsh` and not `eig`?** Hermitian → real, ordered, numerically stable.
- **What is `D`'s size and why complex?** p×p; the Bloch phase `e^{−iqa}` is complex.
- **What happens at q=0?** `D(0)` is real, with a zero eigenvalue (rigid translation).
- **Why clip?** Round-off → tiny negative → `nan` after √.
- **What if masses are huge or tiny?** Using `√m_j · √m_k` instead of `√(m_j m_k)` avoids overflow
  in the product.
- **Why is the DOS a histogram, and what's its weakness?** Simple and cheap; peak heights at van
  Hove singularities depend on bin width (the true divergence can't be captured).
- **What does `is_folded` flag?** Equal masses and springs in a p>1 cell, where "optical" branches
  are just the acoustic branch folded back (true period a/p).
- **Complexity?** O(n_q · p³).

## 7. Run it yourself

```bash
cd question_3
../.venv/bin/python -c "
import phonon as ph, numpy as np
q, w = ph.dispersion([1,4]); print(w.shape, ph.band_gaps(w)); print(ph.sound_velocity([1,4]))
print(ph.dynamical_matrix(0.0,[1,4],1.0,1.0))   # note D[0,1] = -2/√4 = -1, from BOTH bonds
"
```
Then change `+=` to `=` in `phonon.py` temporarily, rerun `test_phonon.py`, and see it fail (undo
after!). That is the best way to understand the bug the report talks about.
