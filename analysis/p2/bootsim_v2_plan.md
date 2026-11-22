# P2 CI-method simulation v2: plan (second look, proposed after a near-miss)

Written and committed 2026-11-22 before any v2 simulation is run. Decided by the human (2026-11-22, option 2 with a prespecified fallback).

## Why a second look

- The v1 simulation (`results/P2sim/p2_bootsim.json`, report `reports/p2/P2_bootsim_report.md`) failed the rule. Two-way coverage was 0.733–0.767 in the edepthvar_like condition. The parametric method failed by one simulation (diff, edepthvar_like: 0.883, 53/60).
- This v2 run was proposed *after* seeing that near-miss. It is a second look and is labelled so in the ledger, the report and the prereg.
- v1 stays on record unchanged. v2 does not replace it; both are cited.

## Design (fixed)

| item | v2 | v1 (for reference) |
|---|---|---|
| methods | parametric `lme4::bootMer(type = "parametric", use.u = FALSE)` only | two-way cluster bootstrap and parametric |
| simulations per condition | 120 | 60 |
| bootstrap replicates per simulation | 500 | 100 |
| conditions | edepthvar_like, fact_dominant (same variance components as v1) | same |
| design | materials/facts_v1.jsonl (300 facts, 20 relations), 10 frames, 3 carriers, missingness 0.5 | same |
| model | `p2_formula("y", subject = FALSE)`, REML (as v1) | same |
| seeds | base 20261122, so the simulated datasets are new and independent of v1 (base 20261121) | 20261121 |
| intervals | percentile, from the same bootstrap replicates: (a) nominal 95% [0.025, 0.975]; (b) nominal 97.5% [0.0125, 0.9875] | 95% only |

- Code: `analysis/p2/p2_bootsim_v2.R`, output `results/P2sim_v2/p2_bootsim_v2.json`.
- Run through `scripts/log_run.py` under nice and prlimit, 3 cores.
- Each job is checkpointed to `results/P2sim_v2/p2_bootsim_v2.json.jobs/`, so a restart resumes. A scheduled check-in relaunches the run if it has died.
- Report: `analysis/p2/p2_bootsim_v2_report.py` writes `reports/p2/P2_bootsim_v2_report.md` and `.json`.

## Thresholds (unchanged from v1)

- Coverage ≥ 0.90 for ICC1 and diff in both conditions.
- |bias| ≤ 0.05 for ICC1 and diff in both conditions.
- Bias is a property of the point estimator: mean point estimate minus truth, over the 120 simulations.

## Decision rule (fixed before launch)

1. If (a) passes, the prereg uses **parametric bootMer, 95% percentile intervals**.
2. Else, if (b) passes, the prereg uses **parametric bootMer, 97.5% percentile intervals**, and says why: the nominal 95% interval under-covered in simulation, and the wider interval is the smallest prespecified one that met the rule.
3. Else, **STOP**. Nothing is written into the prereg and there is no rental; the human is told.

- A method "passes" only if coverage and bias pass in all four (quantity × condition) cells.
- Nothing else is evaluated for selection. wording coverage and interval widths are reported but do not affect the choice.

## Reporting

- Every coverage figure carries its Monte Carlo SE, sqrt(c(1 − c)/N), with N the number of successful simulations in that condition.
- Bias carries its Monte Carlo SE, sd(point)/sqrt(N).
- The report also gives: N errors, N failed bootstrap refits, singular-fit rate, and mean interval widths.
- Runtime estimate: about 6 h on 3 cores, scaled from v1 (1 h 09 min for 120 jobs × 200 refits; v2 is 240 jobs × 500 refits). Peak RSS is expected to be about 300 MB, as in v1.

## Order after v2 (human, 2026-11-22)

1. GPU-script dry run on pythia-70m.
2. End-to-end synthetic test.
3. One heavy job at a time; S5 is not touched.
