# Support docs: defend-your-part guides

One markdown per person, in `q3/` (phonon dispersion) and `q5/` (Fermi–Dirac statistics).
Each guide has: what your part is, the concepts you must be able to explain, a code
walk-through, figures to know, likely questions with short answers, and a "run it yourself"
checklist.

Figures are linked from the existing `figures/` folders, so view these files in a Markdown
previewer (VS Code, GitHub) from inside the repo.

## The split

| Q3: phonon dispersion | | Q5: Fermi–Dirac statistics | |
|---|---|---|---|
| [Prasang](q3/prasang.md) | Interface and Results | [Guhan](q5/guhan.md) | Theory |
| [Haresh](q3/haresh.md) | Theory | [Naman](q5/naman.md) | Numerical core (`fermi.py`) |
| [Abhilash](q3/abhilash.md) | Physics core (`phonon.py`) | [Nithin](q5/nithin.md) | Validation (`test_fermi.py`) |
| [Kumud](q3/kumud.md) | Validation (`test_phonon.py`) | [Praveen](q5/praveen.md) | Results and figures |
| [Abish](q3/abish.md) | Conclusions, references, assembly | [Kshiteesh](q5/kshiteesh.md) | Interface section and assembly |

## Ground rules from the class briefing

- The instructor wants you to **defend your stated contribution and explain how it works**.
  Group presentation polish does not matter.
- He will ask about the **other question too**. Read the primers below. Basic level is enough.
- He will ask whether your code is AI-written. AI use is accepted; not understanding it is not.
  The honest answer is: **"AI helped with the code and structure. I went through it and I can
  explain how it works."** Only say that if it is true, so read your files.
- For a question you didn't run into: *"I didn't hit that while working on it; I'll look into it
  after."* This is fine. Bluffing is not.

## Two-minute primer: the other question

### Q3 in plain words
A 1D chain of atoms joined by springs. Atoms are grouped in unit cells of `p` atoms. Assuming a
wave solution turns the infinitely many equations of motion into a small `p × p` eigenvalue
problem, `D(q) e = ω² e`, solved at each wavevector `q`. That gives `p` frequency branches: 1
**acoustic** (ω→0 as q→0) and `p−1` **optical**. If the masses differ, a **gap** opens between
branches: no wave exists at those frequencies. Stiffer springs scale all frequencies by √K.
Equal masses close the gap. The code builds the matrix, calls `numpy.linalg.eigvalsh`, and
plots.

### Q5 in plain words
Electrons in a semiconductor obey Fermi–Dirac statistics: `f(E) = 1/(e^{(E−μ)/kT}+1)`, the
probability a state at energy E is occupied. The number of available states is the density of
states `D(E) ∝ √(E−E_c)` above the conduction-band edge. The carrier density is
`n = ∫ D(E) f(E) dE`. Given `n` and `T`, we **numerically solve for the chemical potential μ**
(root-finding, `brentq`). At low doping and room temperature the gas is classical
(non-degenerate: μ is below the band edge). At high doping it is degenerate (μ well above the
edge, a Fermi sphere exists). `E_F` is `μ` at T=0; the thing that varies with T is `μ(T)`.

## Heads-up: the code has uncommitted changes

While these guides were being written, `phonon.py`, `fermi.py`, both test files, both `app.py`
files and `make_figures.py` were modified in the working tree (not by these guides), alongside
two new review files (`PHYSICS_REVIEW.md`, `NUMERICAL_SAFETY_REVIEW.md`). Consequences:

- The **committed code and the reports** have 5 phonon tests and 6 Fermi tests. The **working
  tree** now runs 7 and 9 tests, and `fermi.py` gained `_check_positive`, `_quad` and a
  `valleys` option; `phonon.py` gained per-bond `K`, input validation and `is_folded`.
- These guides describe the code as it stood when they were written and the 5/6 tests quoted in
  the reports. **Before the presentation, agree on one version**, then re-read the guides for
  your file: either commit the changes and update the reports, or revert to the committed code.
  Whoever presents a file must know the version that will actually be shown.

## Two things in the repo to know about (honest flags)

1. **Q3 report vs code.** The code listing in the Q3 report's "Numerical method" section is a
   *simplified* version (a single scalar `K`, no p=1 special case). The actual `phonon.py` also
   supports per-bond spring constants, a p=1 branch, input validation and an instability check.
   The report says "verbatim". If asked, say the listing shows the core idea and the full file
   is in the appendix.
2. **Q3 validation table is stale in one row.** The report table gives the zone-folding error
   as `1.4e-4`; the current test (which compares at matched q) gives about `3.5e-14`. The test
   passes either way. Don't quote the old number.

Both reports say "five checks": there are five test functions in `test_phonon.py`, and the
report table splits them into six rows (monatomic and zone-folding are one test function).

## Commands (from the repo root)

```bash
cd question_3 && ../.venv/bin/python test_phonon.py    # 5/5 pass
cd question_5 && ../.venv/bin/python test_fermi.py     # 6/6 pass
.venv/bin/streamlit run streamlit_app.py               # both apps in one UI
```
