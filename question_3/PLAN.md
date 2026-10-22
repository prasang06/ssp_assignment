# Question 3 — Implementation Plan

Status: **for review, nothing built yet.** Physics conventions are fixed in `SCOPE.md`.

## Using AI_STUDY.md

The study was written as a *course-design* document — a 6-week, 40–60 hour project brief with its
own invented rubric. Our assignment is 10 marks with a fixed 7-point requirement list. Treat it
as a source, not as the plan.

**Take from it:**
- The analytic validation formulas (monatomic and diatomic). Already in `SCOPE.md`.
- Phonon **DOS by histogramming** ω over a dense BZ mesh, with van Hove peaks at branch edges.
  Cheap once the dispersion exists, and it makes the branch limits visible. Bonus item.
- Reproducibility checklist: pinned library versions, recorded parameters, one command to
  regenerate every figure.
- References: Kittel, Ashcroft & Mermin, Tong's lecture notes.
- Mass-defect localized mode as an extension, if time allows.

**Drop, and why:**

| In the study | Why it goes |
|---|---|
| 2D honeycomb / graphene case | The question says *one-dimensional* multi-atomic lattice. A 2D case is a week of work on something not asked. |
| phonopy + ASE | Our dynamical matrix is a p×p numpy array written in ~10 lines. phonopy means force constants by finite differences, a supercell, and a dependency that obscures the physics we are being marked on. |
| Jupyter notebook workflow | The PDF requires source "in .py format" and screenshots of an interactive interface. A notebook is neither. |
| Interactive widgets as an "extension idea" | It is requirement 2, the core of the question. The study has this inverted. |
| Its 3 test cases (mono / diatomic / 2D) | Requirement 6 wants three combinations of **masses and spring constants**, i.e. varying m and K within one model — not three different dimensionalities. |
| 6-week timeline, rubric, weightings | Written for an instructor designing a course. Not our grading. |

**Trap it exposes.** The study's diatomic formula uses `a` as the *nearest-neighbour distance*
(lattice constant 2a), so its `cos²(ka)` is our `cos²(qa/2)`. Our `SCOPE.md` defines `a` as the
full unit-cell length. Both forms are correct; mixing them is a silent factor-of-2 in every plot.
The convention is stated once at the top of `phonon.py` and the validation test is written in
*our* convention.

## Architecture

Four files, each with one job. The core knows no UI.

```
question_3/
  phonon.py          dynamical matrix, dispersion, branch limits, gaps, DOS
  test_phonon.py     the five checks in SCOPE.md
  app.py             Streamlit interface
  make_figures.py    regenerates everything in figures/
  figures/           output, git-tracked
  report/            theory.md, methodology.md, results.md, references.md
```

Dependencies: numpy, scipy, matplotlib, streamlit. Nothing else.

## Phases

**1 — Environment.** `uv venv --python 3.12` at the repo root, install the four packages,
freeze versions into `requirements.txt`. System python3 is 3.8 and empty.

**2 — `phonon.py`.** The physics, pure numpy:
- `dynamical_matrix(q, m, K, a)` → p×p Hermitian array
- `dispersion(m, K, a, nq)` → q grid and (nq, p) frequencies via `eigvalsh`
- `branch_limits(w)` → min and max per branch (requirement 3)
- `band_gaps(w)` → positive gaps between consecutive branches (requirement 4)
- `dos(m, K, a, nq, nbins)` → histogram (bonus)

**3 — `test_phonon.py`.** All five checks from `SCOPE.md`: diatomic closed form, monatomic limit,
sound speed from the q→0 slope, ω₁(0)=0, gap closure at equal masses. This phase gates the
rest — no number reaches the report before these pass.

**4 — `app.py`.** Sidebar: atom count p, p mass inputs, K, a. Main panel: dispersion with the
acoustic branch distinguished from the optical ones, gaps shaded and annotated with their widths,
and a table of eigenfrequencies at q=0 and q=π/a alongside each branch's limits.

**5 — `make_figures.py`.** The three cases from `SCOPE.md` (m=(1,4); m=(1,1.1); m=(1,2,3)),
plus a K-sweep showing every frequency scaling as √K while the gap *ratios* hold still. That
sweep is what turns requirement 6 from description into evidence.

**6 — `report/`.** Derivation longhand, numerical method, each figure interpreted, references.

**7 — Screenshots.** Three runs of the interface at different inputs, into `figures/`.

## Deliverables

Mapped to the seven numbered requirements in the PDF:

| # | Requirement | Deliverable | Where |
|---|---|---|---|
| 1 | Derive equations of motion, obtain dispersion relation | Longhand derivation: EOM → Bloch ansatz → D(q)e = ω²e | `report/theory.md` |
| 2 | Interface for atom count, masses, spring constant → branches | Running Streamlit app + 3 screenshots | `app.py`, `figures/` |
| 3 | Plot dispersion, distinguish acoustic/optical, give frequency limits | Labelled plot + limits table | `phonon.py`, `app.py` |
| 4 | Compute bandgap, mark it on the plot | `band_gaps()` + shaded annotated span | `phonon.py`, `app.py` |
| 5 | Eigenfrequencies + physical significance | Table at q=0 and q=π/a; in-phase vs out-of-phase motion explained | `app.py`, `report/results.md` |
| 6 | Three mass/spring combinations compared and discussed | Cases A/B/C + K-sweep, each interpreted | `make_figures.py`, `report/results.md` |
| 7 | Commented code, numerical procedure, references | All source + method section + reference list | `report/` |

Plus, not required by the PDF: passing `test_phonon.py`, phonon DOS, `requirements.txt`.

Every figure carries axis labels with units, a legend and a title, and every figure gets at least
one sentence of interpretation in the report. Both are stated grading criteria.

## Work split (proposal — 10 members)

The PDF requires naming who did what.

| Area | People |
|---|---|
| Derivation and `report/theory.md` | 2 |
| `phonon.py` core | 2 |
| `test_phonon.py` and validation | 1 |
| `app.py` interface | 2 |
| Figures, cases, `report/results.md` | 2 |
| Report assembly, references, presentation | 1 |

## Risks

- **The `a` convention** — see above. Single most likely source of a wrong plot.
- **Inter-cell bond sign.** `D[0,-1] = -K·exp(-iqa)/√(m₁m_p)`; getting the sign of the exponent
  wrong still gives a plausible-looking plot. The monatomic-limit test catches it.
- **p=1 edge case.** With one atom per cell the inter-cell term wraps onto the diagonal. Handle
  explicitly rather than letting numpy silently do the wrong thing.
- **Streamlit on Python 3.12** — fine, but pin the version so the screenshots stay reproducible.
