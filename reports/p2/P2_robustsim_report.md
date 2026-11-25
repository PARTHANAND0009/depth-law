# P2 robustness simulation (non-selecting)

Source: `results/P2robust/p2_robustsim.json` (plan `analysis/p2/robustsim_plan.md`; code `analysis/p2/p2_robustsim.R`). Settings: 100 simulations per condition, 300 parametric bootMer resamples, seed base 20261125. Status: preregistered robustness check (prereg section 4), **non-selecting**: it cannot change the CI method or any decision. Truth = latent-scale shares before discretisation and selection.

| condition | N (errors) | true ICC(1) | true diff | coverage ICC(1) (MCSE) | coverage diff (MCSE) | coverage wording | bias ICC(1) | bias diff | truth below / above CI: ICC(1); diff | diff lower bound > 0 | ICC(1) lower bound ≥ 0.4 | missingness | singular | failed refits |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A_L24_nc3 | 100 (0) | 0.477 | 0.000 | 0.860 (0.035) | 0.940 (0.024) | 0.940 | -0.026 | +0.030 | 1 / 13; 5 / 1 | 0.050 | 0.320 | 0.577 | 0.010 | 0 |
| A_L24_nc2 | 100 (0) | 0.467 | 0.000 | 0.790 (0.041) | 0.910 (0.029) | 0.890 | -0.034 | +0.036 | 1 / 20; 8 / 1 | 0.080 | 0.190 | 0.577 | 0.010 | 0 |
| A_L36_nc3 | 100 (0) | 0.477 | 0.000 | 0.860 (0.035) | 0.880 (0.032) | 0.900 | -0.022 | +0.031 | 1 / 13; 9 / 3 | 0.090 | 0.380 | 0.579 | 0.010 | 0 |
| A_L36_nc2 | 100 (0) | 0.467 | 0.000 | 0.890 (0.031) | 0.920 (0.027) | 0.960 | -0.026 | +0.032 | 0 / 11; 8 / 0 | 0.080 | 0.280 | 0.580 | 0.000 | 0 |
| B_L24_nc3 | 100 (0) | 0.400 | 0.000 | 0.800 (0.040) | 0.870 (0.034) | 0.900 | -0.034 | +0.034 | 1 / 19; 12 / 1 | 0.120 | 0.010 | 0.578 | 0.000 | 0 |
| B_L24_nc2 | 100 (0) | 0.364 | 0.000 | 0.830 (0.038) | 0.950 (0.022) | 0.910 | -0.034 | +0.026 | 0 / 17; 5 / 0 | 0.050 | 0.000 | 0.577 | 0.000 | 0 |
| B_L36_nc3 | 100 (0) | 0.400 | 0.000 | 0.810 (0.039) | 0.900 (0.030) | 0.930 | -0.031 | +0.031 | 0 / 19; 10 / 0 | 0.100 | 0.000 | 0.577 | 0.010 | 0 |
| B_L36_nc2 | 100 (0) | 0.364 | 0.000 | 0.860 (0.035) | 0.920 (0.027) | 0.910 | -0.029 | +0.028 | 0 / 14; 6 / 2 | 0.060 | 0.000 | 0.578 | 0.000 | 0 |

Condition names: truth A/B, discretisation L, carriers nc. Nominal coverage 0.95. 'diff lower bound > 0' is the single-measure H1 CI condition passing when the true diff is 0 (nominal one-sided rate 0.025). Descriptive only.
