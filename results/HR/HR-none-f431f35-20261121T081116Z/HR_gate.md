# Revised H-R gate (prereg/HR_revised.md, frozen at 7725c5b)

- **Source of every number:** `results/HR_gate.json` (run_id `HR-none-f431f35-20261121T081116Z`). Per-task R outputs are in `results/HR/HR-none-f431f35-20261121T081116Z/`.
- **Seed:** 20261121 for every bootstrap, permutation and split.
- **Data:** existing S3b rows (fp32 GPU runs of 2026-11-21); no new model runs.
- **Counts:** EXACT only (Pythia `v4_piletrain_llama`, OLMo-2 `v4_olmo-mix-1124_llama`); each model fitted separately.

## Decision (frozen rule): **NO-GO**

| hypothesis | pass |
|---|---|
| H1 | False |
| H2_raw | False |
| H2_controlled | False |
| H3 | True |

Cross-family pairs that count: pythia-1.4b vs OLMo-2 and pythia-2.8b vs OLMo-2. The pythia-1.4b vs pythia-2.8b pair is reported but does not count.

## Gate table: pairs (H2)

| pair | counts | n rel | raw ρ [95% CI] | perm p (1-sided / 2-sided) | partial ρ [95% CI] | covariate-only ρ | raw − cov-only | split-half r_SB (A / B) | disattenuated ρ (undefined splits as 0) | H2 raw | H2 controlled |
|---|---|---|---|---|---|---|---|---|---|---|---|
| pythia-1.4b vs pythia-2.8b | no | 26 | 0.832 [0.662, 0.916] | 1.00e-04 / 1.00e-04 | 0.819 [0.392, 0.945] | 0.731 | 0.101 | 0.929 / 0.897 | 0.911 (0.996) | PASS | FAIL |
| pythia-1.4b vs OLMo-2-1124-7B | yes | 26 | 0.519 [0.157, 0.783] | 0.0028 / 0.0070 | 0.569 [0.042, 0.832] | 0.278 | 0.241 | 0.929 / 0.943 | 0.555 (0.556) | FAIL | FAIL |
| pythia-2.8b vs OLMo-2-1124-7B | yes | 26 | 0.597 [0.257, 0.812] | 0.0011 / 0.0017 | 0.601 [0.076, 0.854] | 0.571 | 0.025 | 0.897 / 0.943 | 0.649 (0.708) | FAIL | FAIL |

Thresholds: raw ρ ≥ 0.7 with 1-sided p < 0.01 (10000 permutations); partial ρ ≥ 0.5 with CI lower bound > 0.2; raw − cov-only ≥ 0.15.
Bootstrap CIs use 2000 resamples of relations. n = 26 relations.
Split-half: 200 random 25/25 fact splits per relation, H1 fit on each half, Spearman of the two halves' relation BLUPs, then Spearman-Brown. A split whose fit puts σ²_relation at 0 has constant BLUPs and an undefined Spearman. The prereg does not specify this case; such splits are counted, excluded from the mean, and also scored as r = 0 in a conservative variant. The human asked for no change in prereg/, so this is recorded here, not in prereg/DEVIATIONS.md.

## Gate table: models (H1, H3)

| model | N rows | ICC_rel [95% CI] | bootstrap failures (ICC) | H1 | H3 ΔR² [95% CI] | H3 | correctness OR per log1p cooc [95% CI] | split-half r_SB mean [2.5, 97.5 pct] | undefined splits | r_SB, undefined as 0 |
|---|---|---|---|---|---|---|---|---|---|---|
| pythia-1.4b | 3900 | 0.040 [0.000, 0.119] | 0/2000 | FAIL | -2.81e-04 [-0.0032, 0.0037] | PASS | 1.384 [1.276, 1.466] | 0.929 [0.880, 0.964] | 1/200 | 0.924 |
| pythia-2.8b | 3900 | 0.013 [0.000, 0.075] | 0/2000 | FAIL | 0.0012 [-0.0012, 0.0084] | PASS | 1.433 [1.320, 1.560] | 0.897 [0.814, 0.950] | 32/200 | 0.754 |
| OLMo-2-1124-7B | 3900 | 0.060 [2.92e-10, 0.123] | 0/2000 | FAIL | 0.0016 [-3.82e-04, 0.0104] | PASS | 1.283 [1.209, 1.370] | 0.943 [0.895, 0.976] | 0/200 | 0.943 |

Thresholds: ICC_rel ≥ 0.3 with CI lower bound ≥ 0.15; ΔR² CI upper bound < 0.02.
ICC_rel = σ²_relation / (σ²_relation + σ²_relation:template + σ²_subject + σ²_residual), from the REML H1 fit with 5 fact covariates.

### Variance components (H1 fit, REML)

| model | relation | relation:template | subject | residual | marginal R² (fixed, ML, without / with cooc) |
|---|---|---|---|---|---|
| pythia-1.4b | 8.74e-04 | 0.00629 | 0.00685 | 0.00784 | 0.408 / 0.408 |
| pythia-2.8b | 2.63e-04 | 0.00610 | 0.00752 | 0.00703 | 0.336 / 0.338 |
| OLMo-2-1124-7B | 0.00125 | 0.00633 | 0.00701 | 0.00645 | 0.291 / 0.292 |

## Robustness and secondary outcomes (non-gating; point estimates)

| variant | model | N rows | n rel | ICC_rel | H3 ΔR² |
|---|---|---|---|---|---|
| correct_only | pythia-1.4b | 720 | 26 | 0.139 | 3.89e-04 |
| correct_only | pythia-2.8b | 804 | 26 | 0.371 | 0.0082 |
| correct_only | OLMo-2-1124-7B | 1414 | 26 | 0.178 | -6.38e-04 |
| incorrect_only | pythia-1.4b | 3180 | 26 | 0.061 | 5.89e-04 |
| incorrect_only | pythia-2.8b | 3096 | 26 | 0.025 | 0.0019 |
| incorrect_only | OLMo-2-1124-7B | 2486 | 26 | 0.121 | 0.0061 |
| collapse_le_25 | pythia-1.4b | 3900 | 26 | 0.040 | -2.81e-04 |
| collapse_le_25 | pythia-2.8b | 3900 | 26 | 0.013 | 0.0012 |
| collapse_le_25 | OLMo-2-1124-7B | 3900 | 26 | 0.060 | 0.0016 |
| whole_word_object | pythia-1.4b | 3270 | 26 | 0.042 | -1.64e-04 |
| whole_word_object | pythia-2.8b | 3270 | 26 | 0.000 | 0.0014 |
| whole_word_object | OLMo-2-1124-7B | 3618 | 26 | 0.063 | 0.0028 |
| frac_0.25 | pythia-1.4b | 3900 | 26 | 0.087 | 3.01e-06 |
| frac_0.25 | pythia-2.8b | 3900 | 26 | 0.050 | 0.0014 |
| frac_0.25 | OLMo-2-1124-7B | 3900 | 26 | 0.084 | 0.0010 |
| frac_0.75 | pythia-1.4b | 3900 | 26 | 0.000 | -0.0015 |
| frac_0.75 | pythia-2.8b | 3900 | 26 | 0.000 | 0.0030 |
| frac_0.75 | OLMo-2-1124-7B | 3900 | 26 | 0.084 | 6.03e-04 |
| template_0 | pythia-1.4b | 1300 | 26 | 0.135 | -0.0014 |
| template_0 | pythia-2.8b | 1300 | 26 | 0.134 | -0.0011 |
| template_0 | OLMo-2-1124-7B | 1300 | 26 | 0.173 | -4.72e-04 |
| template_1 | pythia-1.4b | 1300 | 26 | 0.397 | -0.0012 |
| template_1 | pythia-2.8b | 1300 | 26 | 0.504 | -0.0010 |
| template_1 | OLMo-2-1124-7B | 1300 | 26 | 0.542 | 4.09e-04 |
| template_2 | pythia-1.4b | 1300 | 26 | 0.444 | -0.0018 |
| template_2 | pythia-2.8b | 1300 | 26 | 0.313 | -0.0029 |
| template_2 | OLMo-2-1124-7B | 1300 | 26 | 0.319 | -3.46e-04 |
| carrier_0 | pythia-1.4b | 3900 | 26 | 0.036 | -4.25e-04 |
| carrier_0 | pythia-2.8b | 3900 | 26 | 0.008 | 8.08e-05 |
| carrier_0 | OLMo-2-1124-7B | 3900 | 26 | 0.051 | 6.15e-04 |
| carrier_1 | pythia-1.4b | 3900 | 26 | 0.043 | -0.0020 |
| carrier_1 | pythia-2.8b | 3900 | 26 | 0.022 | -0.0010 |
| carrier_1 | OLMo-2-1124-7B | 3900 | 26 | 0.085 | 2.68e-05 |
| carrier_2 | pythia-1.4b | 3900 | 26 | 0.001 | -0.0019 |
| carrier_2 | pythia-2.8b | 3900 | 26 | 0.006 | 1.08e-04 |
| carrier_2 | OLMo-2-1124-7B | 3900 | 26 | 0.041 | 0.0040 |
| secondary_p01_onset | pythia-1.4b | 761 | 25 | 0.121 | 4.06e-04 |
| secondary_p01_onset | pythia-2.8b | 886 | 26 | 0.100 | 0.0051 |
| secondary_p01_onset | OLMo-2-1124-7B | 1591 | 26 | 0.136 | 2.50e-04 |
| secondary_rank1_onset | pythia-1.4b | 720 | 26 | 0.343 | 0.0023 |
| secondary_rank1_onset | pythia-2.8b | 804 | 26 | 0.255 | 0.0094 |
| secondary_rank1_onset | OLMo-2-1124-7B | 1414 | 26 | 0.137 | 0.0020 |

| variant | pair | n rel | raw ρ | perm p (1-sided) | partial ρ | covariate-only ρ |
|---|---|---|---|---|---|---|
| correct_only | pythia-1.4b vs pythia-2.8b | 26 | 0.567 | 0.0013 | 0.512 | 0.876 |
| incorrect_only | pythia-1.4b vs pythia-2.8b | 26 | 0.817 | 1.00e-04 | 0.820 | 0.728 |
| collapse_le_25 | pythia-1.4b vs pythia-2.8b | 26 | 0.832 | 1.00e-04 | 0.819 | 0.731 |
| whole_word_object | pythia-1.4b vs pythia-2.8b | 26 | undefined (σ²_relation = 0 in a model) | – | – | – |
| frac_0.25 | pythia-1.4b vs pythia-2.8b | 26 | 0.865 | 1.00e-04 | 0.903 | 0.864 |
| frac_0.75 | pythia-1.4b vs pythia-2.8b | 26 | undefined (σ²_relation = 0 in a model) | – | – | – |
| template_0 | pythia-1.4b vs pythia-2.8b | 26 | 0.759 | 1.00e-04 | 0.702 | 0.852 |
| template_1 | pythia-1.4b vs pythia-2.8b | 26 | 0.807 | 1.00e-04 | 0.882 | 0.896 |
| template_2 | pythia-1.4b vs pythia-2.8b | 26 | 0.881 | 1.00e-04 | 0.906 | 0.845 |
| carrier_0 | pythia-1.4b vs pythia-2.8b | 26 | 0.803 | 1.00e-04 | 0.781 | 0.869 |
| carrier_1 | pythia-1.4b vs pythia-2.8b | 26 | 0.790 | 1.00e-04 | 0.773 | 0.647 |
| carrier_2 | pythia-1.4b vs pythia-2.8b | 26 | 0.787 | 1.00e-04 | 0.751 | 0.627 |
| secondary_p01_onset | pythia-1.4b vs pythia-2.8b | 25 | 0.335 | 0.0486 | 0.325 | 0.713 |
| secondary_rank1_onset | pythia-1.4b vs pythia-2.8b | 26 | 0.667 | 1.00e-04 | 0.616 | 0.837 |
| survival_frailty | pythia-1.4b vs pythia-2.8b | 26 | 0.623 | 7.00e-04 | 0.549 | 0.855 |
| correct_only | pythia-1.4b vs OLMo-2-1124-7B | 26 | 0.403 | 0.0215 | 0.525 | 0.758 |
| incorrect_only | pythia-1.4b vs OLMo-2-1124-7B | 26 | 0.495 | 0.0056 | 0.525 | 0.519 |
| collapse_le_25 | pythia-1.4b vs OLMo-2-1124-7B | 26 | 0.519 | 0.0046 | 0.569 | 0.278 |
| whole_word_object | pythia-1.4b vs OLMo-2-1124-7B | 26 | 0.428 | 0.0156 | 0.435 | 0.521 |
| frac_0.25 | pythia-1.4b vs OLMo-2-1124-7B | 26 | 0.507 | 0.0051 | 0.534 | 0.374 |
| frac_0.75 | pythia-1.4b vs OLMo-2-1124-7B | 26 | undefined (σ²_relation = 0 in a model) | – | – | – |
| template_0 | pythia-1.4b vs OLMo-2-1124-7B | 26 | 0.536 | 0.0037 | 0.446 | 0.626 |
| template_1 | pythia-1.4b vs OLMo-2-1124-7B | 26 | 0.724 | 1.00e-04 | 0.652 | 0.728 |
| template_2 | pythia-1.4b vs OLMo-2-1124-7B | 26 | 0.591 | 0.0011 | 0.504 | 0.574 |
| carrier_0 | pythia-1.4b vs OLMo-2-1124-7B | 26 | 0.523 | 0.0032 | 0.643 | 0.375 |
| carrier_1 | pythia-1.4b vs OLMo-2-1124-7B | 26 | 0.498 | 0.0054 | 0.382 | 0.417 |
| carrier_2 | pythia-1.4b vs OLMo-2-1124-7B | 26 | 0.408 | 0.0191 | 0.507 | 0.256 |
| secondary_p01_onset | pythia-1.4b vs OLMo-2-1124-7B | 25 | 0.392 | 0.0253 | 0.404 | 0.305 |
| secondary_rank1_onset | pythia-1.4b vs OLMo-2-1124-7B | 26 | 0.635 | 4.00e-04 | 0.655 | 0.612 |
| survival_frailty | pythia-1.4b vs OLMo-2-1124-7B | 26 | 0.605 | 0.0013 | 0.489 | 0.729 |
| correct_only | pythia-2.8b vs OLMo-2-1124-7B | 26 | 0.608 | 5.00e-04 | 0.722 | 0.579 |
| incorrect_only | pythia-2.8b vs OLMo-2-1124-7B | 26 | 0.577 | 0.0013 | 0.536 | 0.702 |
| collapse_le_25 | pythia-2.8b vs OLMo-2-1124-7B | 26 | 0.597 | 8.00e-04 | 0.601 | 0.571 |
| whole_word_object | pythia-2.8b vs OLMo-2-1124-7B | 26 | undefined (σ²_relation = 0 in a model) | – | – | – |
| frac_0.25 | pythia-2.8b vs OLMo-2-1124-7B | 26 | 0.598 | 0.0013 | 0.530 | 0.538 |
| frac_0.75 | pythia-2.8b vs OLMo-2-1124-7B | 26 | undefined (σ²_relation = 0 in a model) | – | – | – |
| template_0 | pythia-2.8b vs OLMo-2-1124-7B | 26 | 0.581 | 8.00e-04 | 0.512 | 0.596 |
| template_1 | pythia-2.8b vs OLMo-2-1124-7B | 26 | 0.730 | 1.00e-04 | 0.631 | 0.726 |
| template_2 | pythia-2.8b vs OLMo-2-1124-7B | 26 | 0.517 | 0.0046 | 0.323 | 0.793 |
| carrier_0 | pythia-2.8b vs OLMo-2-1124-7B | 26 | 0.642 | 1.00e-04 | 0.693 | 0.520 |
| carrier_1 | pythia-2.8b vs OLMo-2-1124-7B | 26 | 0.450 | 0.0115 | 0.301 | 0.629 |
| carrier_2 | pythia-2.8b vs OLMo-2-1124-7B | 26 | 0.594 | 0.0015 | 0.610 | 0.712 |
| secondary_p01_onset | pythia-2.8b vs OLMo-2-1124-7B | 26 | 0.194 | 0.1749 | 0.238 | 0.640 |
| secondary_rank1_onset | pythia-2.8b vs OLMo-2-1124-7B | 26 | 0.653 | 2.00e-04 | 0.727 | 0.473 |
| survival_frailty | pythia-2.8b vs OLMo-2-1124-7B | 26 | 0.668 | 1.00e-04 | 0.526 | 0.906 |

### Discrete-time survival with relation frailty (cloglog, event = half-probability layer)

| model | person-periods | frailty SD | HR per log1p cooc_within [95% CI] | p | warnings |
|---|---|---|---|---|---|
| pythia-1.4b | 54701 | 0.359 | 0.934 [0.917, 0.952] | 8.32e-13 | 0 |
| pythia-2.8b | 65037 | 0.392 | 0.936 [0.919, 0.954] | 5.40e-12 | 0 |
| OLMo-2-1124-7B | 73001 | 0.410 | 0.966 [0.953, 0.979] | 3.28e-07 | 0 |

### Secondary outcomes

- `p01_onset` and `rank1_onset`: rows `secondary_*` in the tables above. They are defined only on the subset where the final p ≥ 0.1, or on correct@1 rows.
- `logitdiff_onset`: PENDING: distractor logits not stored; GPU job scripts/hr_logitdiff_gpu.sh (not run)

## Prior covariate (log_prior)

| model | source | hub commit | seconds | bytes read |
|---|---|---|---|---|
| pythia-1.4b | local_cache | fedc38a16e | 26.3 | None |
| pythia-2.8b | hub_range | 2a259cdd96 | 322.2 | 5293046184 |
| OLMo-2-1124-7B | hub_range | 7df9a82518 | 600.8 | 27550752976 |

Streamed forward validated against a standard fp32 forward: pythia-70m max abs log-prob difference 3.7e-4, on values down to −850 (`tests/test_hr_prior.py`); a random tiny OLMo-2 agrees to < 1e-4.

Correction 2026-11-21T08:31:30Z: perm p set to null where rho is NaN (was 1/10001 because NaN comparisons are false); no refit, no new random draws. Rows: pythia-1.4b vs pythia-2.8b / whole_word_object; pythia-1.4b vs pythia-2.8b / frac_0.75; pythia-1.4b vs OLMo-2-1124-7B / frac_0.75; pythia-2.8b vs OLMo-2-1124-7B / whole_word_object; pythia-2.8b vs OLMo-2-1124-7B / frac_0.75.
