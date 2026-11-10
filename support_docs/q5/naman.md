# Naman: Q5 Numerical Core (`fermi.py`)

**Your part:** `fermi.py` and the report §Numerical method.

Back to [README](../README.md).

## 1. 30-second version

> `fermi.py` evaluates the dimensionless Fermi–Dirac integral `F_{1/2}(η)` by quadrature, wraps
> it in a function giving carrier density `n(μ,T)`, and finds the chemical potential for a
> target `n` with Brent's root finder, inside a bracket built from the two closed-form limits.
> It also provides the DOS, an overflow-safe `f(E)`, and the degenerate-gas quantities,
> including per-valley values for multi-valley materials.

## 2. File map

| Function | Job |
|---|---|
| constants | `HBAR, M_E, K_B, EV` in SI |
| `_check_positive(**kw)` | Raises `ValueError` for T, n or m* that is ≤ 0 or not finite |
| `fermi_dirac(E, mu, T)` | `f(E)` via `scipy.special.expit(-(E−μ)/kT)`: no overflow |
| `dos(E, m_eff, Ec)` | `D(E)`, exactly zero for `E ≤ Ec` |
| `n_c(m_eff, T)` | `N_c = 2(m*kT/2πħ²)^{3/2}` |
| `_quad(fn, a, b)` | `scipy.integrate.quad` with a purely relative tolerance (1e-12); raises if it isn't met |
| `fermi_integral_half(eta)` | `F_{1/2}(η)`: factors out `e^η` for η<0; splits at x=η for η≥0 (see §4) |
| `carrier_density(mu, T, m_eff, Ec)` | `n = N_c (2/√π) F_{1/2}(η)` |
| `solve_mu(n, T, m_eff, Ec)` | bracket from the limits + `brentq` on η, returns `μ = E_c + η kT` |
| `boltzmann_mu` | closed-form non-degenerate μ, for validation |
| `fermi_quantities(n, m_eff, valleys=None)` | `E_F, k_F, v_F, T_F`; with `valleys=(M_c, m_l, m_t)` also per-valley `k_F_l, k_F_t, v_F_l, v_F_t` |
| `degeneracy(mu, T, Ec)` | `η = (μ−E_c)/kT` |
| `sommerfeld_mu` | `E_F[1 − (π²/12)(kT/E_F)²]`, for validation |

## 3. The method, four steps (report §Numerical method)

1. Evaluate `F_{1/2}(η)` by quadrature with a relative tolerance of 1e-12; upper limit
   `max(η,0)+60` (the integrand decays like `e^{−(x−η)}`, so +60 is far past negligible).
2. Solve `n(η) = n_target` for η with Brent's method.
3. **Bracket** between the two closed forms: the root always lies between `ln(n/N_c)` (Boltzmann)
   and `E_F/kT` (T=0 sphere). A fixed bracket fails at low T, where η can be 1e4 or more.
4. Return `μ = E_c + η k_BT`.

## 4. Design decisions to be able to defend

- **Solve for η, not μ.** η is dimensionless and O(1–10), so the root finder doesn't deal with
  joules (~1e-19). Units sit in one place (`N_c`).
- **Cutoff scales with η.** A fixed energy cutoff would silently lose carriers in the degenerate
  case, where the integrand extends far above the band edge.
- **Relative tolerance only (`epsabs=0`).** `quad`'s default absolute tolerance (~1.5e-8)
  becomes a ~1e-3 *relative* error once `F_{1/2}` is tiny (η ≲ −20). Using only a relative
  tolerance, and checking the returned error estimate, removes that silent floor.
- **Factor out `e^η` for η < 0.** `√x·expit(η−x) = e^η · √x e^{−x}/(1+e^{η−x})`, so quad
  integrates an O(1) function however negative η is.
- **Split at x = η for η ≥ 0.** The occupation steps from 1 to 0 at x = η. Splitting there lets
  quad resolve the step even at η ~ 1e5. Below `η − 60` the occupation is 1 to within `e^{−60}`,
  so that piece is just `(2/3)x^{3/2}`.
- **`expit` instead of `1/(exp(x)+1)`.** For large positive `x`, `exp(x)` overflows to `inf`.
  `expit(x)=1/(1+e^{−x})` is stable for all x.
- **`solve_mu` bracket logic.** Two facts bound the root. Boltzmann *overestimates* n at a given
  η: dropping the +1 makes every state look fuller, `e^{−(x−η)} > 1/(1+e^{x−η})`. So the
  Boltzmann η for a given n is too low, and the true η is **above** `η_B = ln(n/N_c)`. The T=0 sphere
  *underestimates* n (`F_{1/2}(η) > (2/3)η^{3/2}`), so the true η is **below** `η_d = E_F/kT`.
  The bracket is `[η_B − 1, max(η_d, η_B) + 1]`, widened only if round-off makes it touch the
  root; residuals are stored, not recomputed. Raises `RuntimeError` if it still can't bracket.
- **Relative residual.** The function handed to `brentq` is `n(η)/n_target − 1`, so it is O(1)
  whatever n is.
- **`brentq` tolerances:** `xtol=1e-13`, `rtol=4·eps`. Brent combines bisection (guaranteed)
  with secant/inverse-quadratic steps (fast).
- **Multi-valley (Si, Ge).** `m_de = M_c^{2/3}(m_l m_t²)^{1/3}` gives the right `N_c` and `E_F`, but
  each valley holds only `n/M_c`, so the mean `k_F` is `(3π²n/M_c)^{1/3}` (smaller by `M_c^{1/3}`,
  1.82 for Si) and `v_F` differs along the long and short valley axes: `v_i = ħk_i/m_i`.
- **Input guards.** T = 0, n = 0 or m* = 0 raise `ValueError` instead of producing `nan`.
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
- **What does `quad` do?** Adaptive Gauss–Kronrod quadrature; here `limit=400` subdivisions,
  `epsabs=0`, `epsrel=1e-12`.
- **How accurate is `F_{1/2}`?** ~1e-15 relative against the exact series for η between −40 and
  −0.5, and against the asymptotic series for η up to 1e7 (Nithin's test 7).
- **Why not use an approximation for F_{1/2}?** The point is to span both regimes with one code
  path; approximations (like Blakemore's, cited in the report) are only accurate in limits.
- **How is accuracy checked?** Nine validation checks (Nithin's part), including a round trip
  with error 7e-15 and direct checks of `F_{1/2}`.
- **Why is `T_F` computed even when non-degenerate?** The question asks for it; the app flags it as
  formal via η.
- **Complexity?** Each `solve_mu` is ~10–30 `quad` calls. The app's sweeps (90 T points, 81 n
  points) take well under a second and are cached, so they are only recomputed when an input
  that affects them changes.

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
Try `n=1e19` and `T=1` to watch μ → E_F. For Si, compare
`f.fermi_quantities(1e26, 1.08*f.M_E)` with
`f.fermi_quantities(1e26, 1.08*f.M_E, valleys=(6, 0.98*f.M_E, 0.19*f.M_E))`: `E_F` agrees
(72.7 vs 72.5 meV; the valley masses give m_de = 1.084, not exactly 1.08), but `k_F` drops from
1.44 to 0.79 nm⁻¹.
