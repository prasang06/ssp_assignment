# Naman: Q5 Numerical Core (`fermi.py`)

**Your part:** `fermi.py` and the report §Numerical method.

Back to [README](../README.md).

> **Version note:** the working-tree `fermi.py` has changes since this guide was written (`_check_positive`, `_quad`, a `valleys` option). The function list below is the committed core. Re-read the file before presenting. See the README heads-up.

## 1. 30-second version

> `fermi.py` evaluates the dimensionless Fermi–Dirac integral `F_{1/2}(η)` by quadrature, wraps
> it in a function giving carrier density `n(μ,T)`, and finds the chemical potential for a
> target `n` with Brent's root finder, after widening a bracket until it straddles the root.
> It also provides the DOS, an overflow-safe `f(E)`, and the degenerate-gas quantities.

## 2. File map

| Function | Job |
|---|---|
| constants | `HBAR, M_E, K_B, EV` in SI |
| `fermi_dirac(E, mu, T)` | `f(E)` via `scipy.special.expit(-(E−μ)/kT)`: no overflow |
| `dos(E, m_eff, Ec)` | `D(E)`, exactly zero for `E ≤ Ec` |
| `n_c(m_eff, T)` | `N_c = 2(m*kT/2πħ²)^{3/2}` |
| `fermi_integral_half(eta)` | `F_{1/2}(η)` by `scipy.integrate.quad` on `[0, max(η,0)+60]` |
| `carrier_density(mu, T, m_eff, Ec)` | `n = N_c (2/√π) F_{1/2}(η)` |
| `solve_mu(n, T, m_eff, Ec)` | bracket + `brentq` on η, returns `μ = E_c + η kT` |
| `boltzmann_mu` | closed-form non-degenerate μ, for validation |
| `fermi_quantities(n, m_eff)` | `E_F, k_F, v_F, T_F` |
| `degeneracy(mu, T, Ec)` | `η = (μ−E_c)/kT` |
| `sommerfeld_mu` | `E_F[1 − (π²/12)(kT/E_F)²]`, for validation |

## 3. The method, four steps (report §Numerical method)

1. Evaluate `F_{1/2}(η)` by quadrature; upper limit `max(η,0)+60` (the integrand decays like
   `e^{−(x−η)}`, so +60 is far past negligible).
2. Solve `n(η) = n_target` for η with Brent's method.
3. **Bracket** by widening geometrically until the residual changes sign. A fixed bracket fails at
   low T where `n(η)` is nearly a step.
4. Return `μ = E_c + η k_BT`.

## 4. Design decisions to be able to defend

- **Solve for η, not μ.** η is dimensionless and O(1–10), so the root finder doesn't deal with
  joules (~1e-19). Units sit in one place (`N_c`).
- **Cutoff scales with η.** A fixed energy cutoff would silently lose carriers in the degenerate
  case, where the integrand extends far above the band edge.
- **`expit` instead of `1/(exp(x)+1)`.** For large positive `x`, `exp(x)` overflows to `inf`.
  `expit(x)=1/(1+e^{−x})` is stable for all x.
- **`solve_mu` bracket logic.** Start at `[−5, 5]`. While the residual isn't negative at lo and
  positive at hi, double the end that's still on the wrong side. Raises `RuntimeError` if it
  can't bracket (limit 1e12).
- **`brentq` tolerances:** `xtol=1e-12`, `rtol=1e-14`. Brent combines bisection (guaranteed) with
  secant/inverse-quadratic steps (fast).
- **DOS zero in the gap.** `dos` returns 0 where `E ≤ Ec` using a mask.
- **Units.** Everything is SI internally (joules, m⁻³). The UI converts to eV and cm⁻³
  (`1 cm⁻³ = 1e6 m⁻³`).

## 5. Maths behind `carrier_density`

`n = ∫ D f dE`. With `x=(E−E_c)/kT`: `D dE = (1/2π²)(2m*/ħ²)^{3/2}(kT)^{3/2}√x dx`, and pulling
constants out yields `N_c (2/√π) F_{1/2}(η)`. Check: for η→−∞, `F_{1/2} → (√π/2) e^η`, so
`n → N_c e^η`: the Boltzmann result.

## 6. Likely questions

- **Why Brent's method?** Robust (bracketed, always converges) and fast (superlinear); we don't need
  derivatives.
- **What if it fails to converge?** Bracketing error is raised explicitly rather than returning a
  wrong number.
- **Why does low T make bracketing hard?** `n(η)` becomes nearly a step (it jumps when μ crosses
  E_c), so any fixed starting interval may not contain the sign change.
- **What does `quad` do?** Adaptive Gauss–Kronrod quadrature; `limit=200` subdivisions.
- **Why not use an approximation for F_{1/2}?** The point is to span both regimes with one code
  path; approximations (like Blakemore's, cited in the report) are only accurate in limits.
- **How is accuracy checked?** Four validation tests (Nithin's part), including a round trip with
  error 5e-14.
- **Why is `T_F` computed even when non-degenerate?** The question asks for it; the app flags it as
  formal via η.
- **Complexity?** Each `solve_mu` is ~10–30 `quad` calls; the app's sweeps (90 points) are
  recomputed each interaction.

## 7. Run it yourself

```bash
cd question_5
../.venv/bin/python -c "
import fermi as f
M=0.067*f.M_E; n=1e17*1e6
mu=f.solve_mu(n,300,M,1.42*f.EV)
print((mu-1.42*f.EV)/f.EV*1000,'meV  eta=',f.degeneracy(mu,300,1.42*f.EV))
print(f.fermi_quantities(n,M))
"
```
Expect μ−E_c ≈ −35.9 meV and η ≈ −1.39, matching the report's GaAs materials table.
Try `n=1e19` and `T=1` to watch μ → E_F.
