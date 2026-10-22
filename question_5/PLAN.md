# Question 5 — Implementation Plan

Status: **for review, nothing built yet.** Requirements are listed in `SCOPE.md`.

## The physics, fixed here so it does not drift

Single parabolic conduction band in the effective-mass approximation, 3D, with band edge $E_c$
and a valence band edge $E_v = E_c - E_g$. Energies are measured from $E_v = 0$, so $E_c = E_g$.

**Density of states** (conduction band, per unit volume per unit energy):
$$ D(E) = \frac{1}{2\pi^2}\left(\frac{2m^*}{\hbar^2}\right)^{3/2}\sqrt{E - E_c}, \qquad E \ge E_c $$

**Occupation**: $f(E) = \left[\exp\!\big((E-\mu)/k_BT\big) + 1\right]^{-1}$.

**Carrier density** ties the two together and defines the chemical potential $\mu$:
$$ n = \int_{E_c}^{\infty} D(E)\, f(E)\, dE $$
Given $n$, $T$ and $m^*$, this is one equation in one unknown $\mu$, solved numerically.

### The naming trap, resolved once

The question asks for "the Fermi energy $E_F$", but the quantity that actually varies with
temperature in requirement 6 is the **chemical potential** $\mu(T)$. They coincide only at
$T=0$. We use:

- $E_F \equiv \mu(T{=}0) = \dfrac{\hbar^2}{2m^*}\left(3\pi^2 n\right)^{2/3}$ — a function of $n$ alone.
- $\mu(T)$ — solved from the integral above; this is what requirements 6 and 7 plot.

Both are reported, and the report says plainly that "Fermi level versus temperature" means
$\mu(T)$. Conflating them is the single most common error in this topic.

### A second trap worth stating, not hiding

$k_F$, $v_F$ and $T_F$ are **degenerate-gas** quantities. They describe a filled Fermi sphere:
$$ k_F = (3\pi^2 n)^{1/3}, \qquad v_F = \hbar k_F/m^*, \qquad T_F = E_F/k_B $$
For a typical doped semiconductor at room temperature ($n \sim 10^{16}\,$cm$^{-3}$) the gas is
**non-degenerate**: $\mu$ sits below $E_c$, there is no Fermi surface, and $k_F$ and $v_F$ are
formal numbers rather than physical ones. The interface will compute them as asked **and**
display the degeneracy ratio $(\mu - E_c)/k_BT$ next to them, flagging which regime the user is
in. Demonstrating both regimes is the point of requirement 8, not a caveat to bury.

## Architecture

Mirrors question 3. Four files, core knows no UI.

```
question_5/
  fermi.py           DOS, f(E), carrier integral, mu solver, E_F/k_F/v_F/T_F
  test_fermi.py      validation checks (below)
  app.py             Streamlit interface
  make_figures.py    regenerates figures/
  figures/           output, git-tracked
  report/            report.tex, built with revtex4-2 like Q3
```

Units: SI internally, eV and cm$^{-3}$ at the interface. One conversion layer, not scattered
factors — the most likely source of a silently wrong number in this question.

## Phases

**1 — `fermi.py`.**
- `dos(E, m_eff, Ec)` → $D(E)$, zero below the band edge
- `fermi_dirac(E, mu, T)` → $f(E)$, written to avoid `exp` overflow at large $|E-\mu|/k_BT$
- `carrier_density(mu, T, m_eff, Ec)` → the integral, via `scipy.integrate.quad`
- `solve_mu(n, T, m_eff, Ec)` → `brentq`, with a bracket that widens until it straddles the root
- `fermi_quantities(n, m_eff)` → $E_F$, $k_F$, $v_F$, $T_F$
- `boltzmann_mu(n, T, m_eff, Ec)` → the closed-form non-degenerate result, for validation

**2 — `test_fermi.py`.** Gates everything downstream:
1. **Non-degenerate limit** — at low $n$, `solve_mu` matches $n = N_c\exp[-(E_c-\mu)/k_BT]$ with
   $N_c = 2(m^*k_BT/2\pi\hbar^2)^{3/2}$.
2. **Degenerate limit** — as $T \to 0$, $\mu \to E_F = \hbar^2(3\pi^2n)^{2/3}/2m^*$.
3. **Round trip** — `carrier_density(solve_mu(n, ...), ...)` returns $n$ to solver tolerance.
4. **Half occupancy** — $f(\mu) = 1/2$ exactly, at every $T$.
5. **Sommerfeld expansion** — in the degenerate regime,
   $\mu \approx E_F\left[1 - \frac{\pi^2}{12}(k_BT/E_F)^2\right]$, giving a *quantitative*
   check on the temperature dependence rather than just its sign.

**3 — `app.py`.** Sidebar: $T$, $n$, $m^*/m_e$, $E_g$, energy range. Main panel: band diagram
with $E_c$, $E_v$, $\mu$ and $f(E)$ on a shared energy axis; $D(E)$ and $D(E)f(E)$; the computed
quantities with the degeneracy flag; and the two sweeps below.

**4 — `make_figures.py`.** Band diagram, $f(E)$ at several temperatures, $D(E)$ and $D(E)f(E)$,
$\mu$ versus $T$, $\mu$ versus $n$, and one figure contrasting a non-degenerate with a
degenerate case.

**5 — `report/report.tex`.** Same RevTeX setup as Q3 — `aps,prb,reprint`, listings appendix,
black cross-reference links.

## Deliverables

| # | Requirement | Deliverable | Where |
|---|---|---|---|
| 1 | Explain FD statistics, $E_F$, DOS and their significance | Theory section with the derivation of $D(E)$ from $k$-space counting | `report/` |
| 2 | Interface for $T$, $n$, $m^*$, $E_g$, energy range | Streamlit app + screenshots | `app.py`, `figures/` |
| 3 | Compute $E_F$, $k_F$, $v_F$, $T_F$ with equations stated | `fermi_quantities()` + displayed panel with degeneracy flag | `fermi.py`, `app.py` |
| 4 | Plot conduction band, valence band, Fermi level, $f(E)$ | Band diagram on a shared energy axis | `make_figures.py` |
| 5 | Compute and plot $D(E)$ and $D(E)f(E)$ | Two-panel figure, interpreted | `fermi.py`, `report/` |
| 6 | $\mu$ versus $T$, numerically, explained | Sweep figure + Sommerfeld comparison | `make_figures.py` |
| 7 | $\mu$ versus $n$, with discussion | Sweep across the non-degenerate/degenerate crossover | `make_figures.py` |
| 8 | Demonstration, commented code, interpretation, references | Full report + appendix listings | `report/` |

Beyond the PDF: passing `test_fermi.py`, and the degeneracy flag that makes requirement 3
honest.

## Risks

- **Root-find bracketing.** At low $T$ the carrier integral is nearly a step in $\mu$; a fixed
  bracket fails. The bracket widens geometrically until it straddles the root, and the test
  suite covers $T$ down to a few kelvin.
- **`exp` overflow** in $f(E)$ for $|E-\mu| \gg k_BT$. Evaluate piecewise on the sign of the
  exponent rather than letting `numpy` produce `inf`.
- **Unit confusion** between eV, joules and cm$^{-3}$ vs m$^{-3}$. One conversion layer; the
  tests assert against values in SI.
- **Integration cutoff.** $\int_{E_c}^{\infty}$ is truncated in practice; the upper limit must
  scale with $\max(\mu, E_c) + \text{many}\times k_BT$, not be a fixed constant, or the
  degenerate case silently loses carriers.

## Reuse from question 3

`common/style.py` as-is. Conventions inherited: core/UI/figures/test split, validate against a
closed form before trusting the general code, figures regenerated by one command, screenshots
captured headlessly with `_shots.py` (copy and adjust the preset labels).
