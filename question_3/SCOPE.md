# Question 3 — Scope

**Task.** Interactive Python interface that computes and visualises the phonon dispersion of a
**1D multi-atomic lattice** (p atoms per unit cell, arbitrary masses, nearest-neighbour springs)
by solving the equations of motion. 10 marks.

## Required deliverables (from the PDF, numbered as asked)

| # | Requirement | Where it lands |
|---|---|---|
| 1 | Derive equations of motion for a 1D multi-atomic lattice; obtain the dispersion relation | `report/theory.md` |
| 2 | Interactive interface: user inputs number of particles, masses, spring constant → acoustic + optical branches | `app.py` |
| 3 | Plot dispersion, distinguish acoustic vs optical, identify lower/upper frequency limits of each branch | `phonon.py` + `app.py` |
| 4 | Compute and display the frequency **bandgap**, mark it on the plot | `phonon.py` + `app.py` |
| 5 | Compute and display **eigenfrequencies**, explain their physical significance | `app.py` + `report/` |
| 6 | Three different (mass, spring) combinations compared and discussed | `figures/` + `report/results.md` |
| 7 | Complete commented code, numerical procedure explained, references | all |

## Physics, fixed here so it does not drift

Chain of identical cells of length $a$, each holding $p$ atoms of masses $m_1 \dots m_p$,
nearest neighbours joined by springs of constant $K$ (optionally a per-bond list $K_1 \dots K_p$).
Equation of motion for atom $j$ in cell $n$:

$$ m_j \ddot u_j^n = K\,(u_{j+1}^n - u_j^n) + K\,(u_{j-1}^n - u_j^n) $$

with the neighbours wrapping into the adjacent cells at $j=1$ and $j=p$.

Bloch ansatz $u_j^n = m_j^{-1/2} e_j \, e^{i(qna - \omega t)}$ turns this into the eigenproblem
$D(q)\,e = \omega^2 e$ with the **mass-weighted dynamical matrix**

- $D_{jj} = 2K/m_j$
- $D_{j,j+1} = D_{j+1,j} = -K/\sqrt{m_j m_{j+1}}$  for $j = 1 \dots p-1$
- $D_{1,p} = -K e^{-iqa}/\sqrt{m_1 m_p}$, and $D_{p,1}$ its conjugate (the inter-cell bond)

$D(q)$ is Hermitian, so `numpy.linalg.eigvalsh` gives $p$ real $\omega^2 \ge 0$ per $q$:
**1 acoustic branch** ($\omega \to 0$ as $q \to 0$) and **$p-1$ optical branches**.

Brillouin zone: $q \in [-\pi/a, \pi/a]$; plots use the full zone, tables use $[0, \pi/a]$.

Bandgaps: for sorted branches, gap $i$ = $\min_q \omega_{i+1}(q) - \max_q \omega_i(q)$,
reported only when positive.

## Validation checks (must pass before any number goes in the report)

1. **Diatomic limit** ($p=2$): numerical branches match the textbook closed form
   $\omega^2 = K\left(\tfrac{1}{m_1}+\tfrac{1}{m_2}\right) \pm K\sqrt{\left(\tfrac{1}{m_1}+\tfrac{1}{m_2}\right)^2 - \tfrac{4\sin^2(qa/2)}{m_1 m_2}}$.
2. **Monatomic limit** (all masses equal): single branch $\omega = 2\sqrt{K/m}\,|\sin(qa/2)|$,
   and the artificial zone-folding of a p-atom cell with equal masses must unfold onto it.
3. **Acoustic sound speed**: as $q \to 0$, $\omega_1 \approx v_s q$ with $v_s = a\sqrt{K/(p\sum_j m_j)}$.
4. **Acoustic gap**: $\omega_1(q{=}0) = 0$ to numerical tolerance.
5. **Degenerate-mass gap closure**: equal masses ⇒ no bandgap (branches touch at the zone edge).

## Demonstration cases for requirement 6
- **Case A** — diatomic, strong mass contrast ($m_1=1$, $m_2=4$, $K=1$): wide gap.
- **Case B** — diatomic, near-equal masses ($m_1=1$, $m_2=1.1$, $K=1$): gap nearly closed.
- **Case C** — triatomic ($m=1,2,3$, $K=1$): two optical branches, two gaps.
Plus a spring-constant sweep showing all frequencies scale as $\sqrt{K}$ with gap *ratios* unchanged.

## Out of scope
3D lattices, real materials / force constants from DFT, anharmonic effects, thermal properties.
