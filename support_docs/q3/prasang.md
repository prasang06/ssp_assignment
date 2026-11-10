# Prasang: Q3 Interface and Results

**Your part:** `app.py`, `_shots.py`, UI screenshots, report §Interface. Also `make_figures.py`,
`_schematic.py`, Cases A/B/C, spring-constant sweep, DOS, eigenfrequencies and their
significance (report §Results).

Back to [README](../README.md) · other-question primer is there too.

## 1. What you must be able to say in 30 seconds

> The app takes the number of atoms `p`, their masses, `K` and `a`, builds the p×p dynamical
> matrix at every q, diagonalises it, and plots the p branches. It shades gaps, tabulates
> branch limits and eigenfrequencies at q=0 and q=π/a, and draws the DOS and the mode
> displacement patterns. Results: mass contrast opens the gap, K only scales everything by
> √K, and flat branches give van Hove peaks.

## 2. The interface (`app.py`), top to bottom

| Section | What it does |
|---|---|
| Sidebar | Preset (Custom / Case A / B / C), `p` slider (1–5, fixed by a preset), one mass field per atom, `K`, `a`, q-points, toggles for DOS, modes, analytic overlay. Masses and K are bounded (≤1e4), a ≤ 1e3 |
| Solve | `ph.dispersion` → `(q, w)`, cached; bad input shows an error and stops instead of crashing; `ph.band_gaps(w)`; `ph.branch_limits(w)`; `ph.is_folded` |
| Dispersion plot | Gaps shaded with `axhspan` and labelled with width; acoustic vs optical in different colours; optional analytic overlay for p≤2; CSV download. y-axis says "input units" (see §5) |
| Tables | Branch limits, bandgaps, analytic sound velocity (`ph.sound_velocity`) |
| Eigenfrequencies | `ph.frequencies_at` at q=0 and q=π/a directly |
| DOS | `ph.dos`, histogram of ω over a dense q mesh; caption says read peak positions, not heights |
| Mode displacements | `ph.modes` gives eigenvectors; draws `Re[u_j e^{iqna}]` as arrows over 4 cells; warns if the branch is degenerate at that q |

Design points to be able to explain:
- **The key on the mass inputs includes the preset** (`key=f"m_{preset}_{j}"`). Streamlit widgets
  ignore `value=` once they exist, so without this, switching preset would keep the old masses.
- **Presets fix `p`**, so the slider is hidden rather than allowed to disagree.
- Every change recomputes everything: it's cheap (n_q diagonalisations of tiny matrices).
- Arrows show **physical** displacements `u_j = e_j/√m_j`, not the mass-weighted `e_j`. That's
  why the light atom moves more in the optical mode.
- **Equal masses → "Folded acoustic", not "Optical".** With all masses equal the real period is
  a/p, so the upper branches are the acoustic branch folded back into the smaller zone. The app
  labels them that way and explains why. With p=1 it says there's a single branch, so no gap.
- **Degenerate modes.** Equal masses at q=π/a give two equal frequencies; any mix of the two
  patterns is valid and the solver picks one arbitrarily. The app warns rather than presenting
  the picture as unique.
- Figures are `matplotlib.figure.Figure` objects (not pyplot), so a failed rerun can't leak
  them, and `sys.path` is only extended once, not on every rerun.

## 3. Results you must know cold

All in units of √(K/m₁), K=1, a=1.

| Case | Masses | Acoustic max | Optical range | Gap | v_s |
|---|---|---|---|---|---|
| A | (1, 4) | 0.7071 | 1.4142–1.5811 | 0.7071 | 0.3162 |
| B | (1, 1.1) | 1.3484 | 1.4142–1.9540 | 0.0658 | 0.4880 |
| C | (1, 2, 3) | 0.6180 | 0.8165–1.1101 and 1.5602–1.6180 | 0.1985, 0.4501 | 0.2357 |

Eigenfrequencies (q=0 → q=π/a):
- A: acoustic 0 → 0.7071; optical 1.5811 → 1.4142
- B: acoustic 0 → 1.3484; optical 1.9540 → 1.4142
- C: acoustic 0 → 0.6180; optical 1 1.1101 → 0.8165; optical 2 1.5602 → 1.6180

**The story in three sentences**
1. Case A: at the zone edge the two sublattices decouple. Acoustic mode = only heavy atoms move
   (ω=√(2K/m₂)); optical = only light atoms (ω=√(2K/m₁)). Gap = √(2K/m₁) − √(2K/m₂).
2. Case B: a 10% mass difference leaves a tiny gap; it closes continuously as m₂→m₁. The gap
   comes from the two-atom basis, not from any threshold.
3. Case C: p=3 gives 1 acoustic + 2 optical branches and 2 gaps. The top optical branch is
   nearly flat, so group velocity ≈ 0 and the DOS has a sharp peak.

**K-sweep:** `D ∝ K`, so ω ∝ √K. Dividing by √K collapses all curves. Masses set the *structure*,
K sets the *scale*.

**DOS:** `g(ω)` counts modes per unit frequency, normalised so ∫g dω = p. It is zero in gaps. Peaks
(van Hove singularities) occur where a branch has zero slope (q=0, q=π/a, flat branches).
Histogram peak heights depend on bin width, so the height isn't a physical number. The report
figure uses **one common bin width** (8.1e-3) for all three panels, so heights can at least be
compared across cases. The bin-independent statement: Case C's top branch spans only
1.5602–1.6180 (width 0.058), about 3× narrower than the next-narrowest branch (Case A optical,
0.167), so its states pile up into the tallest peak.

## 4. Figures (know what each shows)

![comparison](../../question_3/figures/comparison.png)
*Three cases on a common scale. Shaded = forbidden frequencies.*

![spring sweep](../../question_3/figures/spring_sweep.png)
*Left: Case A at four K. Right: divided by √K, all collapse.*

![dos](../../question_3/figures/dos.png)
*DOS per case, common bins; empty regions are the gaps.*

![modes](../../question_3/figures/modes.png)
*Mode patterns for m=(1,4). At q=0 the acoustic mode is a uniform translation; the optical mode
has atoms moving against each other. At q=π/a the eigenvectors are exactly (0,1) and (1,0);
that needs m₁ ≠ m₂. With equal masses the two zone-edge frequencies coincide and the pattern is
not unique.*

![gap vs ratio](../../question_3/figures/gap_vs_ratio.png)
*Gap grows monotonically from 0 at m₂=m₁.*

![UI case A](../../question_3/figures/ui_case_a_top.png)
*Taken before the review fixes: the live app's y-axis now reads "input units". Numbers are the
same.*

## 5. Likely questions

- **Why does the acoustic branch start at zero?** A uniform shift of all atoms stretches no
  spring, so it costs no energy. Mathematically `D(0)` has the null vector `e_j ∝ √m_j`.
- **What is the gap physically?** A frequency range where no travelling wave exists at any q.
  A wave driven in that range decays (is reflected).
- **Why does the gap close for equal masses?** The two-atom basis becomes trivial; the cell is
  really a monatomic chain of period a/2 and the "optical" branch is the acoustic one folded
  back.
- **Why does the light atom swing four times further in the optical mode at q=0?** The
  centre of mass must stay at rest: m₁u₁ + m₂u₂ = 0, so u₁/u₂ = m₂/m₁ = 4.
- **Why is the optical frequency at q=0 √(2K/μ), and not √(K/μ) like two masses on one spring?**
  Each atom sits between *two* springs, and in this mode both stretch by the same amount, so the
  restoring force doubles. (μ is the reduced mass; Case A: √(2·1/0.8) = 1.5811.)
- **What does the DOS tell you that the dispersion doesn't?** How many modes sit at each
  frequency. Flat branches pile up many modes at one frequency.
- **How do you know the app is right?** The same `phonon.py` is checked against the monatomic
  and diatomic closed forms to 1e-14 (Kumud's part), and the app's analytic overlay can be
  switched on for p ≤ 2.
- **Why `eigvalsh`, not `eig`?** D is Hermitian. `eigvalsh` returns real eigenvalues in
  ascending order, which is exactly the branch ordering.
- **Why units of √(K/m₁)?** So results don't depend on the chosen numerical values of K and m₁.
  All report results use K = m₁ = 1, so the numbers *are* in those units. The app plots raw
  √(K/m) values for whatever you type, so its axis says "input units"; it would be wrong to
  label them √(K/m₁) when, say, m₁ = 4.
- **Did you write this with AI?** See the README ground rules. Answer honestly, then show you
  understand the code in section 2.

## 6. Run it yourself

```bash
cd question_3
../.venv/bin/streamlit run app.py     # try Case A → Case C, move the q slider in Mode displacements
../.venv/bin/python make_figures.py   # regenerates everything in figures/
```
Try: set masses (1, 1) and watch the gap vanish and the branches become "Folded acoustic";
move the mode q slider to 1.0 and see the degeneracy warning; double K and watch frequencies
× 1.414.
