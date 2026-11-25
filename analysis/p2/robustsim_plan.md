# P2 robustness simulation: plan

Written and committed 2026-11-25, before the run, as prereg/P2_prompt_vs_fact.md section 4 requires ("Its code is written and committed before it runs"). Human instruction 2026-11-25 (GO G2): run it on CPU in the background and report it next to the results.

**Status: non-selecting.** It cannot change the CI method, any decision in `results/P2analysis/correct/p2_decision.json`, or the licensed sentence. It is preregistered as a robustness check, so it is not EXPLORATORY; it is not gating.

## What the prereg fixes
Parametric `bootMer` 95% coverage of ICC(1) and diff, fitting the frozen formula (four covariates and the carrier fixed effect), with:
- D1 discretised to (l\*+1)/L, L = 24 and 36;
- missingness tied to correctness (cells more likely missing when the latent depth is late);
- nc = 2 and nc = 3, with a carrier shift;
- true values near the boundaries: ICC(1) 0.4–0.5 and diff ≈ 0.

## Choices made here (the prereg does not fix them)
| item | value |
|---|---|
| code | `analysis/p2/p2_robustsim.R` (reuses the frozen `p2_formula`, `p2_prep`, `p2_shares`, `p2_truth` from `analysis/p2/p2_model.R`) |
| model | `p2_formula("y", COV, subject = FALSE, carrier = TRUE)`, REML, `calc.derivs = FALSE` (as in the CI-method simulations; affects warnings only) |
| design | the 300 facts / 20 relations of `materials/facts_v1.jsonl`, 10 frames, nc carriers |
| conditions | 2 truths × L ∈ {24, 36} × nc ∈ {3, 2} = 8 |
| truth A (latent variances) | relation 0.0004, frame 0.0002, rt 0.0005, fact 0.0014, ft 0.0007, fc 0.0001, e 0.0003 → ICC(1) 0.477 (nc 3) / 0.467 (nc 2), diff 0 |
| truth B | relation 0.0004, frame 0.0002, rt 0.0004, fact 0.0012, ft 0.0006, fc 0.0003, e 0.0015 → ICC(1) 0.400 (nc 3) / 0.364 (nc 2), diff 0 |
| scale | latent variances of the same order as the real D1 fits (`results/P2analysis/correct/fit_*_D1.json`) |
| covariates | 4 fact-level N(0, 1) covariates, effects 0.009, −0.005, −0.007, −0.015 (order of the real fixed effects), z-scored over carrier-level rows as upstream |
| carrier shift | fixed offsets 0, +0.005, −0.006 (first nc used) |
| discretisation | D1 = ceiling(y\* L)/L, clipped to [1/L, 1] |
| missingness | a (fact, template) cell is dropped (all carriers) with probability plogis(0.38 + 1.0 z), z = standardised latent cell depth without carrier-level terms; realised rate ≈ 0.58 (real: 0.59 Llama, 0.55 OLMo) |
| simulations | 100 per condition (800 in all) |
| bootstrap | 300 parametric resamples per simulation (the analysis used 1000; more resamples only reduce Monte Carlo error in the interval ends; 300 keeps the run near 7 h on 4 cores) |
| seeds | base 20261125; simulation seed = base + 1000·i + condition index; bootstrap seed = simulation seed + 7 |
| truth for coverage | latent-scale shares (`p2_truth(comp, nc)`), before discretisation and selection |

## Reported (descriptive; no threshold, no decision)
Per condition, with N simulations and Monte Carlo SE:
- 95% coverage of ICC(1), diff and wording;
- bias (mean point − truth) of ICC(1) and diff;
- one-sided misses (truth below the lower bound; above the upper bound) for ICC(1) and diff;
- rate of diff lower bound > 0 (the H1 single-measure condition passing when the true diff is 0);
- rate of ICC(1) lower bound ≥ 0.4 (the H1-alt CI condition);
- realised missingness, singular-fit rate, failed refits, errors.

Report: `analysis/p2/p2_robustsim_report.py` → `reports/p2/P2_robustsim_report.md`, quoted in `reports/p2/RESULTS.md` (section 9) with this status.

## Run
`scripts/p2_robustsim_run.sh`: one `scripts/log_run.py` call (status CONFIRMATORY with tag "non-selecting robustness simulation"), `nice -n 10 prlimit --as=1800000000`, 4 cores, checkpointed per simulation to `results/P2robust/p2_robustsim.json.jobs/` (resumes after a restart). It is the only heavy job while it runs. S5 (dead since the container restart of 2026-11-25 ~07:55 UTC) is relaunched after it under the standing authorization, by the same script, and the relaunch is logged in the ledger.

Smoke test before commit (scratchpad, not a result): 1 simulation per condition, 20 resamples, 21 s; all 8 conditions ran without error.
