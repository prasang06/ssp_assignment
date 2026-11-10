# Abish: Q3 Conclusions, References and Assembly

**Your part:** report §Conclusions, the references list, appendix source listings, final LaTeX
build.

Back to [README](../README.md).

Because your part spans the whole report, you need the **big picture of Q3** best of anyone in
the group. Read all of this and skim the whole report once.

## 1. 30-second version

> We derived the equations of motion for a p-atom chain, reduced them to a p×p Hermitian
> eigenvalue problem, implemented it in Python, validated it against closed forms, and used it
> to show that mass contrast opens the gap, K just scales all frequencies by √K, and flat
> branches give DOS peaks. Limitations: harmonic, nearest-neighbour, 1D.

## 2. Conclusions (report §Conclusions): four bullets to know

1. p atoms per cell → 1 acoustic + (p−1) optical branches, up to p−1 gaps.
2. The gap comes from mass contrast and closes continuously: 0.7071 at mass ratio 4, 0.0658 at
   1.1, 0 at 1.
3. K scales all frequencies as √K and changes nothing else about the spectrum.
4. Flat branches → van Hove peaks in the DOS and negligible group velocity.

**Limitations stated:** harmonic approximation (no thermal expansion or phonon lifetimes);
nearest-neighbour only; 1D.

## 3. The whole project in one table (so you can answer anything at overview level)

| Piece | File | Owner |
|---|---|---|
| Theory (EOM → Bloch → D(q)) | report §Theory | Haresh |
| Physics core | `phonon.py` | Abhilash |
| Validation | `test_phonon.py` | Kumud |
| Interface + figures + results | `app.py`, `make_figures.py` | Prasang |
| Conclusions, references, build | `report.tex` | You |

Key numbers to remember: Case A gap 0.7071; Case B 0.0658; Case C 0.1985 and 0.4501; ω₁(0)=0;
tests: 7 functions, all pass, exact-formula checks at ~1e-14.

## 4. References (the `thebibliography` block at the end of `report.tex`)

The references are typed inline in `report.tex`. `reportNotes.bib` only holds RevTeX control
entries, so don't call it the bibliography. The seven Q3 entries and where they're used:

| Key | Source | Used for |
|---|---|---|
| kittel | Kittel, *Introduction to Solid State Physics*, 8th ed., ch. 4 | Lattice vibrations, diatomic chain |
| ashcroft | Ashcroft & Mermin, *Solid State Physics*, ch. 22–23 | Harmonic crystal |
| dove | Dove, *Introduction to Lattice Dynamics* (CUP 1993) | Dynamical matrix formalism |
| tong | Tong, *Lectures on Solid State Physics* (Cambridge) | Lecture notes |
| numpy | Harris et al., *Nature* 585, 357 (2020) | `numpy.linalg.eigvalsh` |
| matplotlib | Hunter, *Comput. Sci. Eng.* 9, 90 (2007) | Plots |
| streamlit | Streamlit docs | Interface |

Be ready to answer "where did you get the diatomic formula?": Kittel ch. 4 (and it is
re-derived in the report from the 2×2 determinant).

## 5. Assembly: how the report is built

- RevTeX 4-2 (`aps, prb, reprint`), built with `latexmk -pdf report.tex` inside `report/`.
- Figures are included from the `figures/` PNGs (`\includegraphics`).
- The appendix source listings use `\lstinputlisting`, so they pull in the *actual* files
  (`phonon.py`, `test_phonon.py`, `common/style.py`, `make_figures.py`, `app.py`) and cannot
  drift from the code.
- References are an inline `thebibliography` block in `report.tex` (the `.bbl`/`.blg` files are
  build outputs from the RevTeX bibliography step).

**Report state after the review fixes (PR #3):**
1. The §Numerical method listing now matches `phonon.py` exactly (the p≥2 branch, with per-bond
   K); its caption says so. The p=1 case and the input checks are in the appendix listing.
2. The validation table is current: zone folding 3.5e-14, plus rows for per-bond springs and
   robustness ("Seven checks run").
3. Text corrections made: why the q=0 optical frequency is √(2K/μ) (two springs per atom, not
   "a shared spring"); the zone-edge eigenvectors are (0,1) and (1,0) only for m₁ ≠ m₂; the DOS
   panels share one bin width.
4. **Still open:** the interface screenshots predate the fixes (the app's axis label now reads
   "input units"). If asked, say the numbers are the same and the screenshots weren't retaken.

## 6. Likely questions

- **What's the main result of your project?** Mass contrast opens a bandgap; K is a pure scale.
- **What did validation show?** Agreement with analytic limits to ~1e-14; caught the `=` vs `+=`
  bug. A later review added regression checks for numerical edge cases (overflow, `nan`,
  unit-dependent gap detection, unstable input).
- **Limitations?** Harmonic, 1D, nearest-neighbour; no anharmonicity, no 3D polarisations.
- **How would you extend it?** Next-nearest-neighbour springs, a defect (mass impurity) for a
  localised mode, 2D/3D, thermal properties from the DOS.
- **How reproducible is it?** One command each: `test_phonon.py`, `make_figures.py`,
  `streamlit run app.py`; pinned `requirements.txt`; Python 3.12 via `uv`.
- **Why RevTeX?** Standard physics-paper format.
- **What is the relevance to real materials?** Optical phonons couple to infrared light in ionic
  crystals; phonon DOS enters heat capacity and thermal conductivity.

## 7. Run it yourself

```bash
cd question_3/report && latexmk -pdf report.tex     # needs a TeX install
cd .. && ../.venv/bin/python test_phonon.py
```
Also read the Introduction and Conclusions of the Q5 report so you can say how the two
questions connect (both end in a density of states; both gaps arise from a basis splitting a
band: mass contrast in Q3, periodic potential in Q5).
