# P2 CI-method simulation report

Source: `results/P2sim/p2_bootsim.json` (settings {"n_sim": "60", "n_boot": "100", "miss": "0.5", "cores": "3", "seed": "20261121"}). Written by `analysis/p2/p2_bootsim_report.py`.

| condition | quantity | truth | mean point | bias | coverage twoway | coverage param | width twoway | width param | N ok |
|---|---|---|---|---|---|---|---|---|---|
| edepthvar_like | icc1 | 0.372 | 0.379 | +0.008 | 0.767 | 0.900 | 0.155 | 0.115 | 60 |
| edepthvar_like | diff | 0.206 | 0.191 | -0.016 | 0.733 | 0.883 | 0.313 | 0.232 | 60 |
| edepthvar_like | wording | 0.578 | 0.570 | -0.008 | 0.733 | 0.883 | 0.158 | 0.117 | 60 |
| fact_dominant | icc1 | 0.709 | 0.711 | +0.002 | 0.917 | 0.950 | 0.107 | 0.095 | 60 |
| fact_dominant | diff | -0.461 | -0.465 | -0.005 | 0.900 | 0.933 | 0.209 | 0.185 | 60 |
| fact_dominant | wording | 0.248 | 0.246 | -0.002 | 0.867 | 0.933 | 0.103 | 0.091 | 60 |

| condition | N ok | N error | singular-fit rate |
|---|---|---|---|
| edepthvar_like | 60 | 0 | 0.000 |
| fact_dominant | 60 | 0 | 0.000 |

Monte Carlo SE of a coverage near 0.90 with N = 60 simulations: 0.039.

## Selection rule outcome

- |bias| <= 0.05 for icc1 and diff in both conditions: yes
- twoway coverage >= 0.90 for icc1 and diff in both conditions: NO
- param coverage >= 0.90 for icc1 and diff in both conditions: NO
- Failures: coverage twoway edepthvar_like/icc1 = 0.767; coverage twoway edepthvar_like/diff = 0.733; coverage param edepthvar_like/diff = 0.883
- **Chosen CI method: NONE: STOP (no method meets the rule; no rental)**
