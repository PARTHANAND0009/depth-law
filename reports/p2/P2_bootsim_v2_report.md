# P2 CI-method simulation v2 report (second look after a near-miss)

Source: `results/P2sim_v2/p2_bootsim_v2.json` (settings {"n_sim": "120", "n_boot": "500", "miss": "0.5", "cores": "3", "seed": "20261122"}). Plan: `analysis/p2/bootsim_v2_plan.md`. Written by `analysis/p2/p2_bootsim_v2_report.py`. v1 (`reports/p2/P2_bootsim_report.md`) stays on record.

| condition | quantity | truth | mean point | bias (MCSE) | coverage 95% (MCSE) | coverage 97.5% (MCSE) | width 95% | width 97.5% | N |
|---|---|---|---|---|---|---|---|---|---|
| edepthvar_like | icc1 | 0.372 | 0.375 | +0.003 (0.003) | 0.958 (0.018) | 0.975 (0.014) | 0.123 | 0.139 | 120 |
| edepthvar_like | diff | 0.206 | 0.200 | -0.006 (0.006) | 0.950 (0.020) | 0.975 (0.014) | 0.248 | 0.281 | 120 |
| edepthvar_like | wording | 0.578 | 0.575 | -0.003 (0.003) | 0.950 (0.020) | 0.975 (0.014) | 0.126 | 0.143 | 120 |
| fact_dominant | icc1 | 0.709 | 0.710 | +0.001 (0.002) | 0.925 (0.024) | 0.967 (0.016) | 0.100 | 0.115 | 120 |
| fact_dominant | diff | -0.461 | -0.462 | -0.002 (0.005) | 0.933 (0.023) | 0.975 (0.014) | 0.195 | 0.225 | 120 |
| fact_dominant | wording | 0.248 | 0.247 | -0.001 (0.002) | 0.925 (0.024) | 0.967 (0.016) | 0.096 | 0.110 | 120 |

| condition | N ok | N error | failed bootstrap refits | singular-fit rate |
|---|---|---|---|---|
| edepthvar_like | 120 | 0 | 0 | 0.000 |
| fact_dominant | 120 | 0 | 0 | 0.008 |

## Prespecified rule outcome

- |bias| <= 0.05 for icc1 and diff in both conditions: yes
- (a) nominal 95%: coverage >= 0.90 for icc1 and diff in both conditions: yes
- (b) nominal 97.5%: coverage >= 0.90 for icc1 and diff in both conditions: yes
- Failures: none
- **Outcome: parametric bootMer, 95% percentile**
