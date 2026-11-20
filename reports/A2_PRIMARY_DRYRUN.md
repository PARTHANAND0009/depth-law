# Amendment 2 primary test (DRY RUN, not a gate result)

Source of every number: `results/A2/A2dry-none-3bd6894-20261120T165531Z/a2.json` (run_id `A2dry-none-3bd6894-20261120T165531Z`). Pre-registration: `configs/prereg_amendment_2026-11-20.yaml`.

## Decision
Rule: Same thresholds as g1: per model PASS = partial R^2 >= 0.10 and slope < 0; WEAK = partial R^2 >= 0.05 and slope < 0; else FAIL. Outcome GO if >= 2 of {pythia-1.4b, pythia-2.8b, olmo-2-1124-7b} PASS; WEAK if PASS + WEAK >= 2; else NO-GO.

| model | index (label) | N rows / facts / relations | partial R² [95% CI] | slope cooc_within [95% CI] | p | p (Holm) | outcome |
|---|---|---|---|---|---|---|---|
| EleutherAI/pythia-70m | piletrain (EXACT) | 900 / 300 / 26 | 0.0010 [-0.0532, 0.0666] | 0.0073 [0.0017, 0.0155] | 0.0680 | 0.0680 | FAIL |

Gate models not run: pythia-1.4b, pythia-2.8b, olmo-2-1124-7b. **Outcome: UNDECIDED (gate models missing)**

Bootstrap: relation clusters, 20 resamples (failures listed in the json).

## Descriptives (half_prob_depth, fit rows)

| model | correct@1 | median depth correct / wrong | Spearman raw log cooc | Spearman within relation | Spearman obj logprob | share final > carrier alone |
|---|---|---|---|---|---|---|
| EleutherAI/pythia-70m | 0.003 | 0.722 / 0.611 | 0.037 | 0.123 | 0.361 | 0.880 |

## Sensitivities (not gating)

| model | variant | N | partial R² | slope | p |
|---|---|---|---|---|---|
| EleutherAI/pythia-70m | drop_final_not_above_carrier_alone | 792 | -0.0211 | 0.0114 | 0.0049 |
| EleutherAI/pythia-70m | plus_margin | 900 | -0.0345 | 0.0073 | 0.0651 |
| EleutherAI/pythia-70m | plus_template_subject_intercepts | 900 | 0.0025 | 0.0074 | 0.0773 |
| EleutherAI/pythia-70m | original_prereg_controls_unsplit | 900 | -0.0182 | 0.0049 | 0.2677 |
| EleutherAI/pythia-70m | correct_rows_only | | MISSING: too few correct rows | | |
| EleutherAI/pythia-70m | secondary_causal_final | | MISSING: 3 resolved rows | | |
| EleutherAI/pythia-70m | secondary_logit_lens_depth | | MISSING: 3 resolved rows | | |

## Runs

- EleutherAI/pythia-70m @ main: depth rows 900, errors 0, layers 6, depth runs S3bdry-pythia-70m-3bd6894-20261120T165137Z
