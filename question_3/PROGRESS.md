# Question 3 — Progress

**Status:** planning complete, implementation not started.

## Log
- **2026-10-22** — Repo scaffolded (CLAUDE.md, SCOPE.md, PROGRESS.md, .gitignore).
  Physics formulation fixed in `SCOPE.md`: mass-weighted Hermitian dynamical matrix,
  `eigvalsh` per q-point. Environment surveyed: system python3 is 3.8 with no packages;
  `uv` and python3.12 are available, so the venv will be built with those.

## Awaiting review
`PLAN.md` written and ready for review. Work starts once it is approved.

Source note: `AI_STUDY.md` (gitignored, supplied by the user) was assessed against the PDF.
Kept its validation formulas, DOS histogram idea and references; dropped the 2D honeycomb case,
phonopy/ASE and the notebook workflow as off-requirement. It also uses a different convention for
`a` than `SCOPE.md` — see the trap noted in `PLAN.md`.

## Next up
1. `uv venv --python 3.12` + install numpy/scipy/matplotlib/streamlit.
2. `phonon.py` — dynamical matrix, branch sorting, band limits, gap finder.
3. `test_phonon.py` — the five validation checks in `SCOPE.md`.
4. `app.py` — Streamlit interface.
5. `make_figures.py` — the three demonstration cases.
6. `report/` — theory, methodology, results, references.

## Decided (not yet built)
- **No shared codebase with Q5.** Two self-contained folders, one root venv, one shared
  `common/style.py`. Overlap between the questions is convention, not logic — see `CLAUDE.md`.
- **Reuse worth setting up now:** the core/UI/figures/test module split and the plot style, so
  Q5 inherits the shape rather than starting over.
- **Optional bonus item:** phonon DOS as a histogram over the BZ eigenfrequencies. Not in the
  PDF, cheap given the dispersion is already computed, and it pairs with the D(E) work in Q5.

## Open questions
- None blocking. Per-bond spring constants ($K_1 \dots K_p$) are treated as an optional extra
  beyond the PDF's single-$K$ wording; the UI defaults to a single $K$.

## Done
- **Environment** — `.venv` on Python 3.12 (uv); numpy, scipy, matplotlib, streamlit, pandas
  pinned in `requirements.txt`.
- **`phonon.py`** — dynamical matrix, dispersion, branch limits, gaps, DOS, sound velocity,
  and the two closed forms used for validation.
- **`test_phonon.py`** — all five SCOPE.md checks pass. Diatomic to 4.5e-14, monatomic to
  1.6e-15, sound velocity to 1.6e-8, omega_acoustic(0) = 0 exactly, gap closure confirmed.
- **`app.py`** — Streamlit interface; verified serving HTTP 200 with no runtime errors.
- **`common/style.py`** — shared palette, CVD-validated (worst adjacent pair dE 11.0 deutan).
- **`make_figures.py`** — 8 figures regenerated from scratch by one command.
- **`report/report.tex`** — 9 pages, compiles clean with latexmk. Prasang Das listed first.

### Bug found and fixed by the tests
For p=2 the intra-cell and inter-cell bonds share matrix element D[0,1]: atom 1 bonds to atom 2
both inside the cell and across the boundary. The first implementation overwrote instead of
accumulating, which broke translational invariance — omega_acoustic(0) came out at 0.59 instead
of 0. Four of the five checks caught it. Documented in the report as a caution, since it is an
easy error to repeat.
