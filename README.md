# Solid State Physics — Assignment 1

Coursework for SSP Assignment-1. Six questions were set; each group submits two. Ours are
**Question 3** (phonon dispersion) and **Question 5** (Fermi–Dirac statistics), both interactive
Python interfaces with accompanying reports.

Both are complete: validated against analytic limits, figures regenerable from a single command,
and written up as RevTeX papers.

| | Question 3 | Question 5 |
|---|---|---|
| Topic | Phonon dispersion in a 1D multi-atomic lattice | Fermi–Dirac statistics in a semiconductor |
| Core problem | Hermitian eigenvalue problem, `eigvalsh` | Root-find for the chemical potential, `brentq` |
| Validation | 5 checks, all pass | 6 checks, all pass |
| Report | [report.pdf](question_3/report/report.pdf) — 17 pp. | [report.pdf](question_5/report/report.pdf) — 14 pp. |

## Question 3 — Phonon dispersion

A chain of unit cells of length `a`, each holding `p` atoms of arbitrary mass joined by
nearest-neighbour springs. The equations of motion reduce under a Bloch ansatz to a `p × p`
Hermitian eigenvalue problem, giving one acoustic and `p−1` optical branches with no change of
algorithm as `p` varies.

The interface takes `p`, the masses, the spring constant and the lattice constant, and reports
the dispersion with bandgaps shaded and annotated, per-branch frequency limits, eigenfrequencies
at the zone centre and edge, the phonon density of states, and the mode displacement patterns.

Key results: the bandgap is produced by mass contrast and closes continuously as the masses are
equalised; the spring constant scales every frequency as `√K` without changing the shape of the
spectrum; at the zone boundary the two sublattices decouple completely, with eigenvectors exactly
`(0,1)` and `(1,0)`.

## Question 5 — Fermi–Dirac statistics

A parabolic conduction band in the effective-mass approximation. The carrier-density integral
`n = ∫ D(E) f(E) dE` is solved numerically for the chemical potential, written through the
dimensionless Fermi–Dirac integral `F₁⁄₂(η)` so that all dimensional factors sit in one place.

The interface takes temperature, carrier concentration, effective mass and band gap, with presets
for GaAs, Si and Ge. It reports `E_F`, `k_F`, `v_F` and `T_F` together with a degeneracy flag, and
plots the band edges with `f(E)`, the density of states with its occupied part, and the Fermi
level against both temperature and carrier concentration.

Two points the report is careful about, because the usual phrasing obscures them: the quantity
that varies with temperature is the chemical potential `μ(T)`, not the Fermi energy `E_F = μ(0)`;
and `k_F`, `v_F`, `T_F` describe a filled Fermi sphere, so they are formal numbers rather than
physical ones unless the carrier gas is degenerate.

## Running it

One virtual environment at the root serves both questions. The system Python is 3.8 with no
packages, so build the venv with `uv` and Python 3.12:

```bash
uv venv --python 3.12 .venv
uv pip install -r requirements.txt
```

Then, in either `question_3/` or `question_5/`:

```bash
../.venv/bin/python test_phonon.py     # or test_fermi.py — validation checks
../.venv/bin/python make_figures.py    # regenerates every figure in figures/
../.venv/bin/streamlit run app.py      # the interactive interface
```

The interface opens at `http://localhost:8501`. Over SSH, forward the port rather than exposing
it: `ssh -L 8501:localhost:8501 <user>@<host>`.

Rebuild a report with `latexmk -pdf report.tex` inside its `report/` directory. The source
listings in each appendix are pulled in with `\lstinputlisting`, so they cannot drift from the
code that produced the results.

## Layout

```
common/style.py       shared matplotlib palette and defaults
question_3/           phonon.py  app.py  make_figures.py  test_phonon.py  figures/  report/
question_5/           fermi.py   app.py  make_figures.py  test_fermi.py   figures/  report/
requirements.txt      pinned versions
```

Each question folder runs on its own; the only shared code is the plotting style. Files prefixed
with an underscore (`_schematic.py`, `_shots.py`) are figure and screenshot helpers rather than
part of the physics.

## On the validation suites

Both question folders carry a test file that checks the general code against closed-form
solutions in limits where those exist — the monatomic and diatomic chains for Q3, the Boltzmann
and degenerate limits plus the Sommerfeld expansion for Q5. These are not decorative. The Q3
suite caught a bug in which the intra-cell and inter-cell spring contributions were overwriting
rather than accumulating in the same matrix element, which left the acoustic branch non-zero at
`q = 0` and so violated translational invariance while still producing a plausible-looking plot.

Run them before trusting any number in either report.

## Team

Group of 10, Department of Engineering Physics.

| Roll number | Name |
|---|---|
| EP24BTECH11011 | Guhan Dhanasekharan |
| EP24BTECH11015 | Kumud Jalori |
| EP24BTECH11016 | Naman Verma |
| EP24BTECH11017 | Nazakar Abhilash |
| EP24BTECH11018 | Nithin Surya S |
| EP24BTECH11019 | Panduru Sri Abish |
| EP24BTECH11020 | Prasang Das |
| EP24BTECH11021 | Praveen Kumar |
| EP24BTECH11022 | S Haresh |
| EP24BTECH11023 | S Kshiteesh |

Contributions per section are listed with the submission.
