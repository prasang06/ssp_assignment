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

## Which version of the code these guides describe

The guides match the code and reports **after the review fixes** (the physics and numerical-safety
reviews, PR #3). That version is what gets presented: `test_phonon.py` runs **7** checks and
`test_fermi.py` runs **9**, and both reports quote those numbers. If you remember an older
figure (5/6 checks, a Boltzmann "error" of 1.3e-4, a zone-folding error of 1.4e-4), it is out of
date; don't quote it.

What changed, in one line each, so nobody is surprised in the viva:
- **Q3 `phonon.py`:** per-bond spring constants, input validation, an error for unstable
  lattices (negative ω²) instead of silently clipping, overflow-safe `√m_j·√m_k`, relative gap
  tolerance, `is_folded`, and `modes()` now also says when two branches are degenerate.
- **Q3 app:** "folded acoustic" labels for equal masses, a degenerate-mode warning, frequency
  axis labelled "input units", bounded inputs.
- **Q5 `fermi.py`:** a more accurate `F_{1/2}` (good to ~1e-15 for any η), a root bracket built
  from the two closed-form limits, per-valley `k_F`/`v_F` for Si and Ge, errors for T=0 or n=0.
- **Q5 app:** warnings when μ nears the valence band, when donors would freeze out, and above
  1e19 cm⁻³; non-degenerate threshold is η < −3; n slider stops at 1e20.

## Things in the repo to know about (honest flags)

1. **Interface screenshots** in both reports were taken before the review fixes, so small
   details (the Q3 frequency-axis label, the Q5 banner wording) differ from the live app. The
   numbers shown are unchanged. If asked, say so.
2. **Q5 is a single-band, fixed-n model.** It has no holes and no donor levels. The app now
   *warns* when that matters (μ below the valence band, freeze-out at low T) rather than
   modelling it. Know this as the main limitation, and the fix: solve `n − p = N_D⁺`.

Check counts versus table rows: Q3 has 7 test functions and the report table has 8 rows
(monatomic and zone-folding are one function). Q5 has 9 functions; the table has 9 rows because
`F_{1/2}` gets two rows, and the input-guard check is mentioned in the caption instead.

## Commands (from the repo root)

```bash
cd question_3 && ../.venv/bin/python test_phonon.py    # 7/7 pass
cd question_5 && ../.venv/bin/python test_fermi.py     # 9/9 pass
.venv/bin/streamlit run streamlit_app.py               # both apps in one UI
```
