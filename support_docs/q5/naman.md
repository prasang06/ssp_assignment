# Naman: Q5 Report Generation (`report/report.tex`)

**Your part:** `question_5/report/report.tex`: how the Q5 report is put together and built, its
section structure, references, and the conclusions and limitations it states.

Back to [README](../README.md) · read [THEORY.md](THEORY.md): the report's Theory section is
that material, and you are the person who can walk an examiner through the whole document.

Because the report touches every file, you need the **big picture of Q5** best of anyone in the
group. Skim the whole PDF once, and know where each thing lives.

## 1. 30-second version

> The report is a RevTeX paper in Physical Review B style. It explains Fermi–Dirac statistics and
> derives the density of states, then sets up the carrier-density integral that fixes μ. It
> describes the numerical solution and validates it against the Boltzmann, degenerate and
> Sommerfeld limits. It then shows the interface and the results: the three doping regimes,
> μ against T and against n, and three materials. Results figures come from `make_figures.py`,
> and the code appendix is pulled from the `.py` files with `\lstinputlisting`. One command,
> `latexmk -pdf report.tex`, builds the 18-page PDF.

## 2. How the report is built

```bash
cd question_5/report
latexmk -pdf report.tex        # runs pdflatex (and BibTeX) as many times as needed
```

| Piece | How it works |
|---|---|
| Document class | `revtex4-2` with `aps, prb, reprint, nofootinbib`: two-column Phys. Rev. B layout |
| Packages | `amsmath, amssymb` (maths), `graphicx` (figures), `booktabs` (tables), `listings` + `xcolor` (code), `hyperref` (links) |
| Figures | `\graphicspath{{../figures/}}`, so `\includegraphics{mu_vs_T.png}` finds `question_5/figures/mu_vs_T.png` |
| Appendix | `\lstinputlisting{../fermi.py}`, `../test_fermi.py`, `../make_figures.py`, `../app.py`: **the real files**, included at build time |
| References | An inline `thebibliography` block at the end. `reportNotes.bib` only holds RevTeX control entries |
| Build outputs | `.aux, .bbl, .blg, .fls, .fdb_latexmk, .log, .out` are generated; `report.pdf` is the result (18 pages) |

**The `\lstset` block** styles all code (blue keywords, green strings, grey italic comments,
line numbers). Its `literate=` list maps Unicode characters in the Python comments (ω, π, μ,
η, ħ, Γ, ⁻, ³, …) to LaTeX maths. Q5's code uses more of these than Q3's (`ħ`, `Γ`, `η`), which
is why the list is longer. Without it, `listings` can't print them.

**`\onecolumngrid` / `\twocolumngrid`** switch the appendix to one column so code lines fit.

**Authors:** all ten group members with roll numbers, same list as the Q3 report.

## 3. Section map: what is where

| § | Section | Content | Figures/tables |
|---|---|---|---|
| I | Introduction | Fermions, degenerate vs classical gas, why doping moves a semiconductor between them | — |
| II | Theory | FD statistics; DOS from k-space counting; `n = ∫Df dE` and `F_{1/2}(η)`; the two limits; **multi-valley materials**; the two points of care (E_F ≠ μ(T); k_F, v_F, T_F need degeneracy) | `kspace_dos.png` |
| III | Numerical method | Quadrature of `F_{1/2}`, bracket from the two limits, Brent; **Validation** subsection (9 checks) | validation table |
| IV | The interactive interface | Inputs, outputs, regime banner (η>2, η<−3), the validity warnings (valence band, freeze-out, heavy doping) | `ui_gaas_top.png` |
| V | Results | Bands and occupation; three regimes; μ vs T; μ vs n; materials | `bands.png`, `occupation.png`, `dos_occupied.png`, `mu_vs_T.png`, `mu_vs_n.png`; regimes and materials tables |
| VI | Conclusions | Five results + limitations | — |
| — | Reproducing this work | The commands | — |
| App. A | Complete source code | `fermi.py`, `test_fermi.py`, `make_figures.py`, `app.py` | — |
| — | References | 7 entries | — |

How the report maps onto the assignment's eight requirements: (1) explain FD statistics, E_F,
DOS → §II; (2) interface → §IV; (3) E_F, k_F, v_F, T_F with equations → §II eqs + §IV;
(4) bands, Fermi level, f(E) → `bands.png`; (5) D(E) and D(E)f(E) → `dos_occupied.png`;
(6) E_F vs T → μ vs T subsection; (7) E_F vs n → μ vs n subsection; (8) demonstration, code,
interpretation, references → §V, Appendix, references.

## 4. Conclusions (§VI): five bullets to know

1. The classical/degenerate boundary is near `n ~ N_c` (4.35e17 cm⁻³ for GaAs at 300 K);
   equivalently, degeneracy needs `T ≪ T_F`.
2. μ falls with T because `D(E) ∝ √(E−E_c)` offers more states above μ than below.
3. In the degenerate regime that fall is the `T²` Sommerfeld correction.
4. μ rises logarithmically with n while non-degenerate, and as `n^{2/3}` once degenerate.
5. Effective mass, not band gap, controls how readily a material becomes degenerate.

Accuracy claims in the Conclusions: the Boltzmann limit is recovered *including* the leading FD
correction, to 3e-5; the degenerate limit reaches E_F to 1e-7, which is the size of the physical
Sommerfeld offset at 1 K.

**Limitations stated (know these, they are the most likely hard questions):**
- Parabolic valleys. DOS masses make N_c and E_F right; k_F and v_F are given per valley for
  Si/Ge.
- GaAs L and X valleys sit 0.29 and 0.48 eV above Γ, which caps the doping range at 1e19.
- Band non-parabolicity is ignored.
- There is no valence band and no donor statistics, and n is an input rather than solved
  for. Two consequences, both flagged by the app:
  - μ can fall below E_v at low n and high T.
  - There is no freeze-out as T→0. For Si at 1e16 and 5 K the model puts μ 0.75 meV below E_c;
    reality is about 20 meV.
- E_g is fixed at its 300 K value, so Varshni narrowing (~0.24 eV for Si between 300 and
  1000 K) is ignored.
- The fix is to solve charge neutrality, `n − p = N_D⁺`, with a valence band and a donor level.

## 5. References (the `thebibliography` block)

| Key | Source | Used for |
|---|---|---|
| kittel | Kittel, *Intro to Solid State Physics*, 8th ed., ch. 6 | Free-electron Fermi gas |
| ashcroft | Ashcroft & Mermin, ch. 2 and ch. 28 | Sommerfeld theory, semiconductors |
| sze | Sze & Ng, *Physics of Semiconductor Devices*, ch. 1 | Carrier statistics |
| blakemore | Blakemore, *Solid-State Electronics* 25, 1067 (1982) | Fermi–Dirac integral approximations |
| scipy | Virtanen et al., *Nature Methods* 17, 261 (2020) | `quad`, `brentq` |
| numpy | Harris et al., *Nature* 585, 357 (2020) | Arrays |
| streamlit | Streamlit docs | Interface |

## 6. The project in one table

| Piece | File | Owner |
|---|---|---|
| Physics core | `fermi.py` | Kshiteesh |
| Validation (9 checks) | `test_fermi.py` | Nithin |
| Results and figures | `make_figures.py` | Guhan |
| Interface and screenshots | `app.py`, `_shots.py` | Praveen |
| Report | `report/report.tex` | You |

## 7. Honest flags about the current report

- **Screenshots predate the review fixes.** The banner wording and the Si/Ge k_F/v_F tiles look
  slightly different in the live app; the GaAs numbers are the same.
- **`kspace_dos.png` is not generated by `make_figures.py`.** It's a separately made diagram.
- **`ui_gaas_top.png` is a manual crop** of the `_shots.py` screenshot.
- **The validation table lists 9 rows for 9 checks, but not one-to-one.** `F_{1/2}` gets two rows,
  and the input-guard check is only mentioned in the caption.

## 8. Likely questions

- **Why RevTeX?** The standard APS physics-paper format.
- **How do you make sure the code in the report is the code you ran?** `\lstinputlisting` reads
  the `.py` files at build time.
- **The question says "Fermi energy vs temperature". Why does the report plot μ?** E_F = μ(T=0)
  depends only on n. The thing that changes with T is μ(T). The report says this explicitly
  (§II, "Two points of care").
- **Why does the doping range stop at 1e19?** Above that, E_F reaches the GaAs L/X valleys and the
  single-valley model stops describing the material.
- **What's the main result?** The classical–degenerate crossover sits at n ~ N_c, and the
  effective mass, not the gap, sets it.
- **Main limitation?** Conduction band only, with n fixed: no holes, no donor levels.
- **How reproducible is it?** `test_fermi.py`, `make_figures.py`, `streamlit run app.py`,
  `latexmk -pdf report.tex`; pinned `requirements.txt`.

## 9. Run it yourself

```bash
cd question_5 && ../.venv/bin/python make_figures.py   # fresh figures
cd report && latexmk -pdf report.tex                   # rebuild the PDF (18 pages)
latexmk -c                                             # clean auxiliary files, keep the PDF
```
Open the PDF next to this guide and find each item in the section map. Read the Q3 report's
Introduction and Conclusions too, so you can say how the questions connect: both end in a density
of states, and both gaps come from a basis splitting one band (mass contrast in Q3, the periodic
potential in Q5).
