# Solid State Physics — Assignment 1

Coursework for SSP Assignment-1. Six questions were set; each group submits two.
Ours are **Question 3** and **Question 5**, both interactive Python interfaces.

## Scope

**[Question 3](question_3/) — Phonon dispersion in a 1D multi-atomic lattice.**
Interactive interface taking the number of atoms per unit cell, their masses and the spring
constant, solving the equations of motion for the dispersion relation ω(q). Separates the
acoustic and optical branches, reports the frequency limits of each, and finds and marks the
bandgap between them.

**[Question 5](question_5/) — Fermi–Dirac statistics in a semiconductor crystal.**
Interactive interface taking temperature, carrier concentration, effective mass and band gap.
Computes E_F, k_F, v_F and T_F, plots the occupation probability f(E), the density of states
D(E) and the occupied DOS, and tracks how the Fermi level moves with temperature and with
carrier concentration.

Each folder carries its own `SCOPE.md` (what is required, and the physics conventions used)
and `PROGRESS.md` (what is done so far).

## Layout

```
common/style.py      shared matplotlib defaults
question_3/          phonon.py  app.py  make_figures.py  test_phonon.py  figures/  report/
question_5/          same shape, different physics
```

Each question folder runs on its own. One virtual environment at the root serves both.

## Status

Scaffolding and scope only — no implementation yet. Question 3 is the current focus.

## Team

Group of 10. Contributions per section are listed in each question's report.

| Roll number | Name |
|---|---|
| EP24BTECH11011 | Guhan Dhanasekharan |
| EP24BTECH11015 | Kumud Jalori |
| EP24BTECH11016 | Naman Verma |
| EP24BTECH11017 | Nazakar Abhilash |
| EP24BTECH11018 | Nithin Surya S |
| EP24BTECH11019 | Panduru Sri Abish |
| EP24BTECH11020 | Prasang Das |
| EP24BTECH11021 | Praveen Kumar |
| EP24BTECH11022 | S Haresh |
| EP24BTECH11023 | S Kshiteesh |
