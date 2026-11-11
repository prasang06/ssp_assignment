# Abhilash: Q3 Report Generation (`report/report.tex`)

**Your part:** `question_3/report/report.tex`: how the Q3 report is put together and built, its
section structure, references, and the conclusions it draws.

Back to [README](../README.md) · read [THEORY.md](THEORY.md): the report's Theory section is
that material, and you are the person who can walk an examiner through the whole document.

Because the report touches every file, you need the **big picture of Q3** best of anyone in the
group. Skim the whole PDF once, and know where each thing lives.

## 1. 30-second version

> The report is a RevTeX paper in Physical Review B style. It derives the p-atom dispersion,
> explains the numerical method, validates it against the closed forms, shows the interface, and
> presents the three cases, the K-sweep, the DOS and the eigenfrequencies. Every figure comes
> from `make_figures.py`. The source-code appendix is pulled straight from the `.py` files with
> `\lstinputlisting`, so it can't drift from the code. One command, `latexmk -pdf report.tex`,
> builds the 20-page PDF.

## 2. How the report is built

```bash
cd question_3/report
latexmk -pdf report.tex        # runs pdflatex (and BibTeX) as many times as needed
```

| Piece | How it works |
|---|---|
| Document class | `revtex4-2` with `aps, prb, reprint, nofootinbib`: two-column Phys. Rev. B layout |
| Packages | `amsmath, amssymb` (maths), `graphicx` (figures), `booktabs` (tables), `listings` + `xcolor` (code), `hyperref` (links) |
| Figures | `\graphicspath{{../figures/}}`, so `\includegraphics{comparison.png}` finds `question_3/figures/comparison.png` |
| Code in the text | One `lstlisting` block in §Numerical method: the p≥2 core of `dynamical_matrix`, matching `phonon.py` |
| Appendix | `\lstinputlisting{../phonon.py}` etc.: **the real files**, included at build time |
| References | An inline `thebibliography` block at the end. `reportNotes.bib` only holds RevTeX control entries; don't call it the bibliography |
| Build outputs | `.aux, .bbl, .blg, .fls, .fdb_latexmk, .log, .out` are generated; `report.pdf` is the result (20 pages) |

**The `\lstset` block** (near the top) styles all code: blue keywords, green strings, grey
italic comments, line numbers, line breaking. Its `literate=` list maps Unicode characters
that appear in the Python comments (ω, π, μ, −, ⁵, ħ, …) to LaTeX maths. Without it,
`listings` can't print them and the build fails or drops characters.

**`\onecolumngrid` / `\twocolumngrid`** switch the appendix to a single column so long code
lines fit, then switch back for the references.

**Authors:** all ten group members are listed with roll numbers, with the affiliation
"Department of Engineering Physics" (both reports have the same author list).

## 3. Section map: what is where

| § | Section | Content | Figures/tables |
|---|---|---|---|
| I | Introduction | Phonons, why the 1D chain, acoustic vs optical | — |
| II | Theory | EOM → Bloch ansatz → D(q); conventions (`a` = full cell); the p=2 `+=` caution; branch structure; closed forms | `schematic.png` |
| III | Numerical method | Five steps; code listing; **Validation** subsection (7 checks) | validation table, `validation.png` |
| IV | The interactive interface | What the app takes and shows; folded-acoustic and degeneracy flags | `ui_case_a_top.png`, `ui_case_c_top.png` |
| V | Results | Cases A, B, C; K-sweep; DOS; eigenfrequencies and their significance | `comparison.png`, `gap_vs_ratio.png`, `spring_sweep.png`, `dos.png`, `modes.png`; cases and eigenfrequency tables |
| VI | Conclusions | Four results + limitations | — |
| — | Reproducing this work | The commands | — |
| App. A | Complete source code | `phonon.py`, `test_phonon.py`, `common/style.py`, `make_figures.py`, `app.py` | — |
| — | References | 7 entries | — |

How the report maps onto the assignment's seven requirements: (1) derive EOM and dispersion →
§II; (2) interface → §IV; (3) plot, acoustic/optical, frequency limits → §V cases table;
(4) bandgap marked → shaded spans + table; (5) eigenfrequencies and significance → §V last
subsection; (6) three mass/spring combinations → Cases A/B/C + K-sweep; (7) commented code,
procedure, references → §III, Appendix, references.

## 4. Conclusions (§VI): four bullets to know

1. p atoms per cell → 1 acoustic + (p−1) optical branches, up to p−1 gaps.
2. The gap comes from mass contrast and closes continuously: 0.7071 at mass ratio 4, 0.0658 at
   1.1, 0 at 1.
3. K scales all frequencies as √K and changes nothing else about the spectrum.
4. Flat branches → van Hove peaks in the DOS and negligible group velocity.

**Limitations stated:** harmonic approximation (no thermal expansion or phonon lifetimes);
nearest-neighbour only; 1D.

Key numbers: Case A gap 0.7071; Case B 0.0658; Case C 0.1985 and 0.4501; ω₁(0)=0; the code
reproduces the closed forms to ~4e-14 (abstract) / within 1e-13 (conclusions); 7 validation
checks, all pass.

## 5. References (the `thebibliography` block)

| Key | Source | Used for |
|---|---|---|
| kittel | Kittel, *Introduction to Solid State Physics*, 8th ed., ch. 4 | Lattice vibrations, diatomic chain |
| ashcroft | Ashcroft & Mermin, *Solid State Physics*, ch. 22–23 | Harmonic crystal |
| dove | Dove, *Introduction to Lattice Dynamics* (CUP 1993) | Dynamical matrix formalism |
| tong | Tong, *Lectures on Solid State Physics* (Cambridge) | Lecture notes |
| numpy | Harris et al., *Nature* 585, 357 (2020) | `numpy.linalg.eigvalsh` |
| matplotlib | Hunter, *Comput. Sci. Eng.* 9, 90 (2007) | Plots |
| streamlit | Streamlit docs | Interface |

"Where did you get the diatomic formula?": Kittel ch. 4, and it is re-derived in §II from the
2×2 determinant.

## 6. The project in one table

| Piece | File | Owner |
|---|---|---|
| Interface, combined app, screenshots | `app.py`, `_shots.py`, `streamlit_app.py`, `home.py`, `common/style.py` | Prasang |
| Results and figures | `make_figures.py`, `_schematic.py` | Haresh |
| Physics core | `phonon.py` | Abish |
| Validation | `test_phonon.py` | Kumud |
| Report | `report/report.tex` | You |

## 7. Honest flags about the current report

- **Screenshots predate the review fixes.** The live app's y-axis now says "input units" and
  equal masses show "Folded acoustic". The numbers in the screenshots are unchanged. If asked,
  say the screenshots weren't retaken.
- **The `_top` screenshots are manual crops.** No script in the repo makes them.
- **Not every file is in the appendix.** `_schematic.py` and `_shots.py` are helpers and are
  left out; the appendix has the five files that produce the physics, figures and interface.
- **The validation table has 8 rows for 7 checks,** because monatomic and zone-folding are one
  test function but two rows.

## 8. Likely questions

- **Why RevTeX?** It's the standard physics-journal format (APS); it gives the two-column paper
  layout and handles authors, affiliations and references.
- **How do you make sure the code in the report is the code you ran?** The appendix uses
  `\lstinputlisting`, which reads the `.py` files at build time.
- **How are figures kept in sync?** `make_figures.py` writes them all into `figures/`; the report
  includes them from there. Rerun the script, rebuild, done.
- **What's the main result?** Mass contrast opens a bandgap; K is a pure scale.
- **What did validation show?** Agreement with analytic limits to ~1e-14, and it caught the
  `=` vs `+=` bug that left the acoustic branch non-zero at q=0.
- **Limitations?** Harmonic, 1D, nearest-neighbour; no anharmonicity, no 3D polarisations.
- **How would you extend it?** Next-nearest-neighbour springs, a mass defect (localised mode),
  2D/3D, heat capacity from the DOS.
- **How reproducible is it?** `test_phonon.py`, `make_figures.py`, `streamlit run app.py`,
  `latexmk -pdf report.tex`; pinned `requirements.txt`; Python 3.12 via `uv`.
- **Why `literate` in `\lstset`?** To print the Unicode characters in the code comments.

## 9. Run it yourself

```bash
cd question_3 && ../.venv/bin/python make_figures.py   # fresh figures
cd report && latexmk -pdf report.tex                   # rebuild the PDF (20 pages)
latexmk -c                                             # clean auxiliary files, keep the PDF
```
Open the PDF next to this guide and find each item in the section map. Read the Q5 report's
Introduction and Conclusions too, so you can say how the questions connect: both end in a density
of states, and both gaps come from a basis splitting one band (mass contrast in Q3, the periodic
potential in Q5).
