# Nithin: Q5 Validation (`test_fermi.py`)

**Your part:** `test_fermi.py` and the report §Validation.

Back to [README](../README.md).

> **Version note:** the working-tree `test_fermi.py` has 9 checks (extra series/asymptotic and multi-valley tests); the committed version and the report have 6. See the README heads-up.

## 1. 30-second version

> `fermi_integral_half` and `solve_mu` are general numerical code, so we test them where the
> answer is known: the Boltzmann limit, the T→0 limit, an exact round trip, `f(μ)=1/2`, and the
> Sommerfeld expansion for μ(T). All six checks pass, the strongest being the Sommerfeld
> comparison at 3.6e-9, which tests the temperature dependence quantitatively.

## 2. The checks (current run: **6/6 pass**)

| # | Test | Idea | Result |
|---|---|---|---|
| 1 | `test_boltzmann` | n = 1e12, 1e14, 1e15 cm⁻³ at 300 K: `solve_mu` vs `μ = E_c + kT ln(n/N_c)` | 1.3e-4 |
| 2 | `test_degenerate` | n=1e19 at **T=1 K**: μ → `E_F = ħ²(3π²n)^{2/3}/2m*` | 9.6e-8 |
| 3 | `test_round_trip` | `carrier_density(solve_mu(n)) = n` for n = 1e14–1e20, T = 50, 300, 600 K | 4.9e-14 |
| 4 | `test_half_occupancy` | `f(μ) = 1/2` at T = 1, 77, 300, 1000 K | 0 |
| 5 | `test_sommerfeld` | n=1e20, T = 20, 50, 100 K: `μ ≈ E_F[1 − (π²/12)(kT/E_F)²]` | 3.6e-9 |
| 6 | `test_dos` | `D=0` for `E ≤ E_c`; matches the analytic formula above | exact |

(Test 6 prints two PASS lines: "DOS zero in the gap" and "DOS matches analytic form".)

## 3. Why each is meaningful

1. **Boltzmann.** Tests the dilute limit, the regime of real doped semiconductors. 1e-4 error, not
   1e-14, because the closed form itself drops the small `+1` correction; the tolerance is 2e-3.
2. **T→0 degenerate.** Tests the other limit and the bracketing at very low T (the hard case).
3. **Round trip.** Internal consistency across 6 decades of n and 3 temperatures; catches any
   mismatch between the solver and the integral.
4. **`f(μ)=1/2`.** Tests the overflow-safe `expit` implementation at both low and high T.
5. **Sommerfeld.** *The strongest.* In the degenerate regime μ drops as `T²` with a specific
   coefficient `π²/12`. Matching it to 9 digits tests the temperature dependence quantitatively,
   not just the sign. (n=1e20 with E_F ~ 1 eV keeps `kT/E_F` small.)
6. **DOS.** Basic correctness of the √ form and the band-edge cutoff.

![mu vs T with Sommerfeld](../../question_5/figures/mu_vs_T.png)
*Panel (b) is the Sommerfeld check: numerical points follow the analytic curve and depart by
~0.5% only by 700 K, where `kT/E_F` ≈ 0.24 and the asymptotic series fails, as expected.*

## 4. Tolerances you should be able to justify

| Check | Tolerance | Actual | Why this tolerance |
|---|---|---|---|
| Boltzmann | 2e-3 | 1.3e-4 | closed form neglects the +1 |
| Degenerate | 1e-4 | 9.6e-8 | 1 K isn't exactly 0 K |
| Round trip | 1e-8 | 4.9e-14 | solver tolerance |
| `f(μ)` | 1e-15 | 0 | exact in floating point |
| Sommerfeld | 1e-4 | 3.6e-9 | next term is O(T⁴) |

## 5. Likely questions

- **Why does the Boltzmann test have a loose tolerance?** The analytic formula is itself an
  approximation; the residual error is the physics being neglected.
- **Why test at 1 K?** The nearly-step integral is the numerically hard case; it checks the
  bracketing.
- **Why is the Sommerfeld test the "strongest"?** It's an independent analytic prediction of
  *how* μ changes with T, not just the end values.
- **What does the round trip not prove?** That `carrier_density` is right (both directions could
  share an error). The limits tests cover that.
- **Where does the Sommerfeld expansion come from?** Expanding `∫ g(E) f(E) dE` around the step
  using `f'(E)` being peaked at μ. The first correction is `(π²/6)(kT)² g'(μ)`, giving the `π²/12`
  coefficient for √E.
- **Would the suite catch a unit mix-up (cm⁻³ vs m⁻³)?** Yes: test 2 compares to an SI
  closed form, so a factor 1e6 would blow every limit check.
- **What failure would each test catch?** (1) wrong `N_c` or η sign; (2) bad bracketing/cutoff;
  (3) solver/integral mismatch; (4) overflow handling; (5) wrong T-dependence; (6) DOS prefactor.

## 6. Run it yourself

```bash
cd question_5
../.venv/bin/python test_fermi.py        # expect 6/6 passed
```
Try editing the cutoff in `fermi_integral_half` (`+60` → `+2`) in a scratch copy and see which
tests fail first (the degenerate ones).
