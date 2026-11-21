# EXPLORATORY (post hoc, not preregistered) — E-depthvar report

- **Source of every number:** `e_depthvar.json` in the run directory named in the ledger entry "EXPLORATORY (post hoc, not preregistered) E-depthvar B3-B7 run".
- **Settings:** seed 20261121; cluster bootstrap 1000 resamples of facts within relation; shuffled-fact null 1000 permutations; planted recovery 50 simulations per condition (200 bootstrap resamples per simulation for coverage).
- **Data:** S3b fp32 rows, 1300 facts × 3 templates per model, 26 relations. Plan: `EXPLORATORY_post-hoc_not-preregistered__PLAN.md`, committed before any statistic.
- **Scope:** numbers, CIs and limitations only. No headline claims.

## EXPLORATORY (post hoc, not preregistered): B2 inclusion and censoring

| EXPLORATORY (post hoc, not preregistered) model | L | facts correct 3/3 | 2/3 | 1/3 | 0/3 | correct cells | D2 censored (correct cells) | D3 censored (correct cells) |
|---|---|---|---|---|---|---|---|---|
| pythia-1.4b | 24 | 84 | 150 | 168 | 898 | 720 | 92/720 (0.128) | 0/720 |
| pythia-2.8b | 32 | 107 | 154 | 175 | 864 | 804 | 82/804 (0.102) | 0/804 |
| OLMo-2-1124-7B | 32 | 254 | 226 | 200 | 620 | 1414 | 60/1414 (0.042) | 0/1414 |

## EXPLORATORY (post hoc, not preregistered): B3/B4 variance shares, set (i): all correct cells (lme4 REML; 95% CI from the cluster bootstrap)

| EXPLORATORY (post hoc, not preregistered) model | def | N cells / facts | fact+subject | template main | residual | relation | (tmpl+resid) − (fact+subj) | ICC(1) | n′ (Φ≥0.8) | Φ(3) / G(3) | bootstrap fails |
|---|---|---|---|---|---|---|---|---|---|---|---|
| pythia-1.4b | D1 | 720 / 402 | 0.465 [0.338, 0.539] | 0.213 [0.122, 0.354] | 0.229 [0.128, 0.310] | 0.094 [0.009, 0.227] | -0.023 [-0.189, 0.210] | 0.513 [0.383, 0.612] | 4.0 [3, 7] | 0.759 / 0.859 | 0/1000 |
| pythia-1.4b | D4 | 720 / 402 | 0.484 [0.357, 0.522] | 0.151 [0.102, 0.235] | 0.133 [0.083, 0.162] | 0.233 [0.175, 0.388] | -0.200 [-0.278, -0.040] | 0.630 [0.526, 0.688] | 3.0 [2, 4] | 0.837 / 0.916 | 0/1000 |
| pythia-1.4b | D2 | 628 / 338 | 0.365 [0.231, 0.425] | 0.322 [0.143, 0.561] | 0.184 [0.089, 0.218] | 0.129 [0.000, 0.368] | 0.141 [-0.067, 0.416] | 0.419 [0.272, 0.552] | 6.0 [4, 11] | 0.684 / 0.856 | 0/1000 |
| pythia-1.4b | D2_cens_as_Lp1 | 720 / 402 | 0.295 [0.207, 0.332] | 0.399 [0.344, 0.530] | 0.083 [0.049, 0.103] | 0.223 [0.123, 0.330] | 0.187 [0.120, 0.374] | 0.380 [0.273, 0.420] | 7.0 [6, 11] | 0.648 / 0.914 | 0/1000 |
| pythia-1.4b | D3 | 720 / 402 | 0.443 [0.310, 0.514] | 0.240 [0.215, 0.387] | 0.317 [0.210, 0.368] | 0.000 [0.000, 0.046] | 0.115 [-0.028, 0.374] | 0.443 [0.312, 0.514] | 6.0 [4, 9] | 0.704 / 0.807 | 0/1000 |
| pythia-2.8b | D1 | 804 / 436 | 0.379 [0.285, 0.431] | 0.051 [0.043, 0.100] | 0.243 [0.162, 0.301] | 0.327 [0.278, 0.420] | -0.085 [-0.197, 0.073] | 0.563 [0.444, 0.650] | 4.0 [3, 6] | 0.795 / 0.824 | 0/1000 |
| pythia-2.8b | D4 | 804 / 436 | 0.430 [0.333, 0.477] | 0.072 [0.061, 0.130] | 0.173 [0.111, 0.212] | 0.325 [0.261, 0.438] | -0.186 [-0.261, -0.041] | 0.638 [0.533, 0.698] | 3.0 [2, 4] | 0.841 / 0.882 | 0/1000 |
| pythia-2.8b | D2 | 722 / 384 | 0.434 [0.258, 0.522] | 0.119 [0.077, 0.303] | 0.212 [0.110, 0.271] | 0.235 [0.108, 0.445] | -0.104 [-0.260, 0.176] | 0.568 [0.386, 0.669] | 4.0 [2, 7] | 0.798 / 0.860 | 0/1000 |
| pythia-2.8b | D2_cens_as_Lp1 | 804 / 436 | 0.317 [0.200, 0.378] | 0.317 [0.235, 0.453] | 0.125 [0.064, 0.172] | 0.241 [0.133, 0.383] | 0.125 [0.018, 0.326] | 0.417 [0.288, 0.486] | 6.0 [5, 10] | 0.682 / 0.883 | 0/1000 |
| pythia-2.8b | D3 | 804 / 436 | 0.467 [0.349, 0.531] | 0.141 [0.093, 0.272] | 0.275 [0.175, 0.325] | 0.117 [0.069, 0.214] | -0.051 [-0.197, 0.156] | 0.529 [0.410, 0.615] | 4.0 [3, 6] | 0.771 / 0.836 | 0/1000 |
| OLMo-2-1124-7B | D1 | 1414 / 680 | 0.306 [0.251, 0.345] | 0.332 [0.234, 0.455] | 0.173 [0.129, 0.189] | 0.189 [0.107, 0.303] | 0.199 [0.078, 0.341] | 0.377 [0.305, 0.448] | 7.0 [5, 10] | 0.645 / 0.841 | 0/1000 |
| OLMo-2-1124-7B | D4 | 1414 / 680 | 0.287 [0.237, 0.321] | 0.366 [0.267, 0.460] | 0.124 [0.096, 0.136] | 0.222 [0.153, 0.333] | 0.203 [0.091, 0.315] | 0.369 [0.306, 0.434] | 7.0 [6, 10] | 0.637 / 0.874 | 0/1000 |
| OLMo-2-1124-7B | D2 | 1354 / 647 | 0.364 [0.285, 0.406] | 0.253 [0.194, 0.376] | 0.209 [0.140, 0.238] | 0.175 [0.094, 0.286] | 0.098 [-0.006, 0.258] | 0.440 [0.347, 0.504] | 6.0 [4, 8] | 0.703 / 0.839 | 0/1000 |
| OLMo-2-1124-7B | D2_cens_as_Lp1 | 1414 / 680 | 0.391 [0.301, 0.440] | 0.235 [0.186, 0.345] | 0.202 [0.135, 0.235] | 0.171 [0.105, 0.280] | 0.046 [-0.056, 0.216] | 0.472 [0.371, 0.535] | 5.0 [4, 7] | 0.728 / 0.853 | 0/1000 |
| OLMo-2-1124-7B | D3 | 1414 / 680 | 0.395 [0.310, 0.440] | 0.270 [0.192, 0.405] | 0.230 [0.156, 0.268] | 0.105 [0.058, 0.184] | 0.105 [-0.014, 0.276] | 0.441 [0.350, 0.508] | 6.0 [4, 8] | 0.703 / 0.838 | 0/1000 |

## EXPLORATORY (post hoc, not preregistered): B3/B4 variance shares, set (ii): facts correct under all 3 templates (lme4 REML; 95% CI from the cluster bootstrap)

| EXPLORATORY (post hoc, not preregistered) model | def | N cells / facts | fact+subject | template main | residual | relation | (tmpl+resid) − (fact+subj) | ICC(1) | n′ (Φ≥0.8) | Φ(3) / G(3) | bootstrap fails |
|---|---|---|---|---|---|---|---|---|---|---|---|
| pythia-1.4b | D1 | 252 / 84 | 0.439 [0.260, 0.499] | 0.379 [0.258, 0.564] | 0.182 [0.087, 0.218] | 0.000 [0.000, 0.198] | 0.121 [-0.043, 0.410] | 0.439 [0.280, 0.524] | 6.0 [4, 11] | 0.702 / 0.879 | 0/1000 |
| pythia-1.4b | D4 | 252 / 84 | 0.407 [0.209, 0.466] | 0.357 [0.266, 0.539] | 0.236 [0.133, 0.291] | 0.000 [0.000, 0.216] | 0.186 [0.009, 0.527] | 0.407 [0.230, 0.496] | 6.0 [5, 14] | 0.673 / 0.838 | 0/1000 |
| pythia-1.4b | D2 | 241 / 84 | 0.075 [0.038, 0.115] | 0.450 [0.128, 0.580] | 0.077 [0.047, 0.100] | 0.398 [0.297, 0.703] | 0.452 [0.126, 0.583] | 0.124 [0.063, 0.313] | 29.0 [9, 31] | 0.299 / 0.745 | 0/1000 |
| pythia-1.4b | D2_cens_as_Lp1 | 252 / 84 | 0.037 [0.018, 0.049] | 0.907 [0.844, 0.939] | 0.056 [0.033, 0.068] | 0.000 [0.000, 0.069] | 0.926 [0.864, 0.961] | 0.037 [0.018, 0.049] | >30 [31, 31] | 0.103 / 0.666 | 0/1000 |
| pythia-1.4b | D3 | 252 / 84 | 0.189 [0.081, 0.268] | 0.512 [0.467, 0.661] | 0.299 [0.177, 0.376] | 0.000 [0.000, 0.002] | 0.623 [0.463, 0.836] | 0.189 [0.081, 0.268] | 18.0 [11, 31] | 0.411 / 0.654 | 0/1000 |
| pythia-2.8b | D1 | 321 / 107 | 0.302 [0.165, 0.377] | 0.036 [0.026, 0.091] | 0.230 [0.140, 0.287] | 0.433 [0.372, 0.565] | -0.036 [-0.178, 0.155] | 0.532 [0.339, 0.661] | 4.0 [3, 8] | 0.773 / 0.797 | 0/1000 |
| pythia-2.8b | D4 | 321 / 107 | 0.339 [0.209, 0.404] | 0.069 [0.057, 0.129] | 0.229 [0.139, 0.288] | 0.364 [0.271, 0.522] | -0.042 [-0.153, 0.133] | 0.533 [0.387, 0.624] | 4.0 [3, 7] | 0.774 / 0.816 | 0/1000 |
| pythia-2.8b | D2 | 311 / 107 | 0.202 [0.087, 0.320] | 0.458 [0.161, 0.665] | 0.340 [0.173, 0.515] | 0.000 [0.000, 0.208] | 0.596 [0.251, 0.801] | 0.202 [0.091, 0.357] | 16.0 [8, 31] | 0.432 / 0.641 | 0/1000 |
| pythia-2.8b | D2_cens_as_Lp1 | 321 / 107 | 0.070 [0.030, 0.106] | 0.799 [0.728, 0.881] | 0.131 [0.069, 0.186] | 0.000 [0.000, 0.000] | 0.859 [0.787, 0.941] | 0.070 [0.030, 0.106] | >30 [31, 31] | 0.185 / 0.618 | 0/1000 |
| pythia-2.8b | D3 | 321 / 107 | 0.275 [0.143, 0.340] | 0.127 [0.075, 0.265] | 0.250 [0.156, 0.305] | 0.347 [0.251, 0.484] | 0.102 [-0.038, 0.327] | 0.422 [0.242, 0.533] | 6.0 [4, 13] | 0.687 / 0.768 | 0/1000 |
| OLMo-2-1124-7B | D1 | 762 / 254 | 0.278 [0.200, 0.316] | 0.411 [0.302, 0.577] | 0.159 [0.118, 0.166] | 0.152 [0.027, 0.308] | 0.292 [0.169, 0.484] | 0.328 [0.231, 0.388] | 9.0 [7, 14] | 0.594 / 0.840 | 0/1000 |
| OLMo-2-1124-7B | D4 | 762 / 254 | 0.301 [0.225, 0.340] | 0.391 [0.299, 0.533] | 0.119 [0.094, 0.127] | 0.189 [0.065, 0.321] | 0.209 [0.110, 0.377] | 0.371 [0.284, 0.425] | 7.0 [6, 11] | 0.639 / 0.883 | 0/1000 |
| OLMo-2-1124-7B | D2 | 750 / 254 | 0.326 [0.233, 0.372] | 0.434 [0.362, 0.569] | 0.194 [0.125, 0.227] | 0.046 [0.000, 0.162] | 0.302 [0.195, 0.495] | 0.342 [0.247, 0.394] | 8.0 [7, 13] | 0.609 / 0.835 | 0/1000 |
| OLMo-2-1124-7B | D2_cens_as_Lp1 | 762 / 254 | 0.281 [0.195, 0.325] | 0.426 [0.359, 0.573] | 0.251 [0.163, 0.283] | 0.041 [0.000, 0.160] | 0.397 [0.289, 0.576] | 0.293 [0.206, 0.343] | 10.0 [8, 16] | 0.554 / 0.770 | 0/1000 |
| OLMo-2-1124-7B | D3 | 762 / 254 | 0.276 [0.200, 0.314] | 0.393 [0.321, 0.555] | 0.244 [0.170, 0.275] | 0.088 [0.000, 0.181] | 0.360 [0.257, 0.547] | 0.302 [0.216, 0.349] | 10.0 [8, 15] | 0.565 / 0.772 | 0/1000 |

- **n′ in the bootstrap:** a resample with no k ≤ 30 reaching 0.8 is coded as 31.
- **D2:** uses uncensored cells only. D2_cens_as_Lp1 scores censored carriers as (L+1)/L. D3 has no censored correct cells.
- **B4:** which of template main and residual is larger can be read directly from the two columns above.

## EXPLORATORY (post hoc, not preregistered): B3 ANOVA (method-of-moments) cross-check, balanced sets (fact = fact+subject)

| EXPLORATORY (post hoc, not preregistered) model | def | set | N facts | relations | fact | template main | residual | relation |
|---|---|---|---|---|---|---|---|---|
| pythia-1.4b | D1 | all_cells | 1300 | 26 | 0.480 | 0.098 | 0.269 | 0.153 |
| pythia-1.4b | D1 | all3 | 84 | 8 | 0.473 | 0.268 | 0.194 | 0.065 |
| pythia-1.4b | D4 | all_cells | 1300 | 26 | 0.477 | 0.155 | 0.208 | 0.160 |
| pythia-1.4b | D4 | all3 | 84 | 8 | 0.431 | 0.270 | 0.250 | 0.049 |
| pythia-2.8b | D1 | all_cells | 1300 | 26 | 0.515 | 0.121 | 0.262 | 0.102 |
| pythia-2.8b | D1 | all3 | 107 | 9 | 0.296 | 0.046 | 0.233 | 0.425 |
| pythia-2.8b | D4 | all_cells | 1300 | 26 | 0.531 | 0.142 | 0.206 | 0.122 |
| pythia-2.8b | D4 | all3 | 107 | 9 | 0.335 | 0.099 | 0.230 | 0.336 |
| OLMo-2-1124-7B | D1 | all_cells | 1300 | 26 | 0.489 | 0.153 | 0.283 | 0.076 |
| OLMo-2-1124-7B | D1 | all3 | 254 | 18 | 0.325 | 0.158 | 0.184 | 0.333 |
| OLMo-2-1124-7B | D4 | all_cells | 1300 | 26 | 0.519 | 0.185 | 0.239 | 0.056 |
| OLMo-2-1124-7B | D4 | all3 | 254 | 18 | 0.363 | 0.167 | 0.143 | 0.327 |

## EXPLORATORY (post hoc, not preregistered): B7a shuffled-fact null (fact IDs permuted within relation × template; ANOVA fact share)

| EXPLORATORY (post hoc, not preregistered) model | def | set | observed fact share | null mean | null 95th | null 99th | p |
|---|---|---|---|---|---|---|---|
| pythia-1.4b | D1 | all_cells | 0.480 | 0.005 | 0.020 | 0.030 | 0.0010 |
| pythia-1.4b | D1 | all3 | 0.473 | 0.021 | 0.092 | 0.128 | 0.0010 |
| pythia-1.4b | D4 | all_cells | 0.477 | 0.005 | 0.019 | 0.029 | 0.0010 |
| pythia-1.4b | D4 | all3 | 0.431 | 0.022 | 0.097 | 0.133 | 0.0010 |
| pythia-2.8b | D1 | all_cells | 0.515 | 0.006 | 0.023 | 0.033 | 0.0010 |
| pythia-2.8b | D1 | all3 | 0.296 | 0.016 | 0.071 | 0.111 | 0.0010 |
| pythia-2.8b | D4 | all_cells | 0.531 | 0.005 | 0.023 | 0.030 | 0.0010 |
| pythia-2.8b | D4 | all3 | 0.335 | 0.015 | 0.061 | 0.083 | 0.0010 |
| OLMo-2-1124-7B | D1 | all_cells | 0.489 | 0.006 | 0.024 | 0.034 | 0.0010 |
| OLMo-2-1124-7B | D1 | all3 | 0.325 | 0.009 | 0.035 | 0.047 | 0.0010 |
| OLMo-2-1124-7B | D4 | all_cells | 0.519 | 0.005 | 0.021 | 0.028 | 0.0010 |
| OLMo-2-1124-7B | D4 | all3 | 0.363 | 0.009 | 0.037 | 0.054 | 0.0010 |

## EXPLORATORY (post hoc, not preregistered): B7b planted-depth recovery

- **Bias arm:** lme4 on each model's exact correct-cell design.
- **Coverage arm:** ANOVA estimator with a within-relation fact bootstrap, on the balanced set-(ii) design.
- **Units:** planted shares are on the latent midpoint; D1 and D4 are nonlinear in it.

| EXPLORATORY (post hoc, not preregistered) model | planted fact | planted template | D1 recovered fact (bias) | D1 recovered template (bias) | D4 recovered fact (bias) | D4 recovered template (bias) | D1 coverage fact / template | D4 coverage fact / template |
|---|---|---|---|---|---|---|---|---|
| pythia-1.4b | 0.1 | 0.05 | 0.100 (-0.000) | 0.045 (-0.005) | 0.102 (0.002) | 0.049 (-0.001) | 0.86 / 0.72 | 0.90 / 0.68 |
| pythia-1.4b | 0.3 | 0.05 | 0.286 (-0.014) | 0.049 (-0.001) | 0.299 (-0.001) | 0.052 (0.002) | 0.86 / 0.68 | 0.90 / 0.70 |
| pythia-1.4b | 0.5 | 0.05 | 0.488 (-0.012) | 0.047 (-0.003) | 0.506 (0.006) | 0.049 (-0.001) | 0.84 / 0.76 | 0.92 / 0.72 |
| pythia-1.4b | 0.7 | 0.05 | 0.674 (-0.026) | 0.044 (-0.006) | 0.699 (-0.001) | 0.047 (-0.003) | 0.66 / 0.74 | 0.72 / 0.72 |
| pythia-1.4b | 0.1 | 0.2 | 0.095 (-0.005) | 0.185 (-0.015) | 0.097 (-0.003) | 0.193 (-0.007) | 0.92 / 0.86 | 0.96 / 0.82 |
| pythia-1.4b | 0.3 | 0.2 | 0.281 (-0.019) | 0.191 (-0.009) | 0.292 (-0.008) | 0.196 (-0.004) | 0.86 / 0.76 | 0.92 / 0.72 |
| pythia-1.4b | 0.5 | 0.2 | 0.487 (-0.013) | 0.175 (-0.025) | 0.504 (0.004) | 0.184 (-0.016) | 0.78 / 0.54 | 0.86 / 0.52 |
| pythia-1.4b | 0.7 | 0.2 | 0.672 (-0.028) | 0.193 (-0.007) | 0.694 (-0.006) | 0.202 (0.002) | 0.50 / 0.46 | 0.62 / 0.46 |
| pythia-1.4b | max abs bias 0.028 | pass (±0.05): True | coverage design: {'n_facts_balanced': 84, 'n_relations_with_facts': 8, 'L': 24} | | | | | |
| pythia-2.8b | 0.1 | 0.05 | 0.105 (0.005) | 0.046 (-0.004) | 0.106 (0.006) | 0.047 (-0.003) | 0.98 / 0.66 | 0.98 / 0.70 |
| pythia-2.8b | 0.3 | 0.05 | 0.299 (-0.001) | 0.052 (0.002) | 0.304 (0.004) | 0.052 (0.002) | 0.82 / 0.78 | 0.82 / 0.78 |
| pythia-2.8b | 0.5 | 0.05 | 0.494 (-0.006) | 0.050 (0.000) | 0.502 (0.002) | 0.050 (0.000) | 0.86 / 0.86 | 0.86 / 0.84 |
| pythia-2.8b | 0.7 | 0.05 | 0.689 (-0.011) | 0.046 (-0.004) | 0.698 (-0.002) | 0.046 (-0.004) | 0.80 / 0.74 | 0.84 / 0.80 |
| pythia-2.8b | 0.1 | 0.2 | 0.108 (0.008) | 0.197 (-0.003) | 0.108 (0.008) | 0.198 (-0.002) | 0.80 / 0.68 | 0.82 / 0.68 |
| pythia-2.8b | 0.3 | 0.2 | 0.293 (-0.007) | 0.192 (-0.008) | 0.297 (-0.003) | 0.194 (-0.006) | 0.82 / 0.68 | 0.88 / 0.70 |
| pythia-2.8b | 0.5 | 0.2 | 0.499 (-0.001) | 0.185 (-0.015) | 0.507 (0.007) | 0.187 (-0.013) | 0.76 / 0.50 | 0.78 / 0.52 |
| pythia-2.8b | 0.7 | 0.2 | 0.682 (-0.018) | 0.197 (-0.003) | 0.692 (-0.008) | 0.200 (-0.000) | 0.70 / 0.46 | 0.72 / 0.48 |
| pythia-2.8b | max abs bias 0.018 | pass (±0.05): True | coverage design: {'n_facts_balanced': 107, 'n_relations_with_facts': 9, 'L': 32} | | | | | |
| OLMo-2-1124-7B | 0.1 | 0.05 | 0.101 (0.001) | 0.046 (-0.004) | 0.102 (0.002) | 0.046 (-0.004) | 0.88 / 0.68 | 0.88 / 0.72 |
| OLMo-2-1124-7B | 0.3 | 0.05 | 0.294 (-0.006) | 0.048 (-0.002) | 0.296 (-0.004) | 0.049 (-0.001) | 0.86 / 0.68 | 0.88 / 0.70 |
| OLMo-2-1124-7B | 0.5 | 0.05 | 0.498 (-0.002) | 0.050 (0.000) | 0.504 (0.004) | 0.051 (0.001) | 0.88 / 0.74 | 0.90 / 0.72 |
| OLMo-2-1124-7B | 0.7 | 0.05 | 0.691 (-0.009) | 0.050 (-0.000) | 0.698 (-0.002) | 0.050 (-0.000) | 0.82 / 0.64 | 0.84 / 0.64 |
| OLMo-2-1124-7B | 0.1 | 0.2 | 0.095 (-0.005) | 0.208 (0.008) | 0.096 (-0.004) | 0.211 (0.011) | 0.90 / 0.62 | 0.88 / 0.62 |
| OLMo-2-1124-7B | 0.3 | 0.2 | 0.291 (-0.009) | 0.199 (-0.001) | 0.294 (-0.006) | 0.201 (0.001) | 0.78 / 0.70 | 0.76 / 0.72 |
| OLMo-2-1124-7B | 0.5 | 0.2 | 0.497 (-0.003) | 0.187 (-0.013) | 0.504 (0.004) | 0.189 (-0.011) | 0.70 / 0.64 | 0.70 / 0.64 |
| OLMo-2-1124-7B | 0.7 | 0.2 | 0.691 (-0.009) | 0.200 (-0.000) | 0.698 (-0.002) | 0.201 (0.001) | 0.66 / 0.50 | 0.68 / 0.50 |
| OLMo-2-1124-7B | max abs bias 0.013 | pass (±0.05): True | coverage design: {'n_facts_balanced': 254, 'n_relations_with_facts': 18, 'L': 32} | | | | | |

## EXPLORATORY (post hoc, not preregistered): B7c carrier facet (long per-carrier data, correct cells, REML shares)

| EXPLORATORY (post hoc, not preregistered) model | def | fact | subject | template main | relation | carrier | fact:carrier | template:carrier | residual | singular |
|---|---|---|---|---|---|---|---|---|---|---|
| pythia-1.4b | D1 | 0.349 | 0.141 | 0.196 | 0.079 | 0.010 | 0.000 | 0.014 | 0.210 | True |
| pythia-1.4b | D4 | 0.257 | 0.205 | 0.121 | 0.198 | 0.044 | 0.000 | 0.076 | 0.099 | True |
| pythia-2.8b | D1 | 0.153 | 0.272 | 0.055 | 0.300 | 0.009 | 0.000 | 0.012 | 0.200 | True |
| pythia-2.8b | D4 | 0.113 | 0.335 | 0.083 | 0.280 | 0.034 | 0.000 | 0.038 | 0.117 | True |
| OLMo-2-1124-7B | D1 | 0.153 | 0.156 | 0.316 | 0.155 | 0.005 | 0.000 | 0.030 | 0.186 | True |
| OLMo-2-1124-7B | D4 | 0.093 | 0.188 | 0.333 | 0.182 | 0.029 | 0.005 | 0.055 | 0.115 | False |

## EXPLORATORY (post hoc, not preregistered): B5 covariates (all six jointly; % change of each component vs B3, correct cells)

| EXPLORATORY (post hoc, not preregistered) model | def | fact | subject | fact+subject | template main | relation | residual |
|---|---|---|---|---|---|---|---|
| pythia-1.4b | D1 | 0.257 | -0.641 | share 0.465 → 0.459 | -0.304 | 0.789 | -0.013 |
| pythia-1.4b | D4 | 0.003 | -0.121 | share 0.484 → 0.418 | 0.102 | 0.470 | -0.027 |
| pythia-2.8b | D1 | 2.020 | -0.361 | share 0.379 → 0.335 | -0.660 | 0.462 | -0.008 |
| pythia-2.8b | D4 | 4.313 | -0.450 | share 0.430 → 0.385 | -0.180 | 0.307 | -0.008 |
| OLMo-2-1124-7B | D1 | 0.650 | -0.749 | share 0.306 → 0.302 | -0.304 | 0.216 | -0.059 |
| OLMo-2-1124-7B | D4 | 1.176 | -0.709 | share 0.287 → 0.282 | -0.357 | 0.050 | -0.019 |

- **One-at-a-time changes:** in `e_depthvar.json` → `covariates_B5`.
- **Fact vs subject split:** not interpretable (one fact per subject apart from a handful); only fact+subject is.

## EXPLORATORY (post hoc, not preregistered): B6 cross-model agreement of fact-level mean depth

| EXPLORATORY (post hoc, not preregistered) def | facts | pair | N facts | relations | ρ [95% CI] | ρ within relation [CI] | G(3) a / b | disattenuated ρ [CI] |
|---|---|---|---|---|---|---|---|---|
| D1 | strict_all3 | pythia-1.4b vs pythia-2.8b | 50 | 7 | -0.173 [-0.422, 0.100] | 0.145 [-0.156, 0.407] | 0.879 / 0.797 | -0.206 [-0.504, 0.119] |
| D1 | strict_all3 | pythia-1.4b vs OLMo-2-1124-7B | 50 | 7 | 0.001 [-0.287, 0.301] | -0.021 [-0.266, 0.237] | 0.879 / 0.840 | 0.001 [-0.335, 0.351] |
| D1 | strict_all3 | pythia-2.8b vs OLMo-2-1124-7B | 50 | 7 | 0.411 [0.106, 0.638] | 0.288 [-0.029, 0.545] | 0.797 / 0.840 | 0.502 [0.129, 0.780] |
| D1 | any_correct | pythia-1.4b vs pythia-2.8b | 312 | 26 | 0.347 [0.247, 0.443] | 0.188 [0.067, 0.311] | 0.879 / 0.797 | 0.415 [0.295, 0.529] |
| D1 | any_correct | pythia-1.4b vs OLMo-2-1124-7B | 312 | 26 | 0.356 [0.252, 0.451] | 0.113 [-0.000, 0.222] | 0.879 / 0.840 | 0.414 [0.293, 0.525] |
| D1 | any_correct | pythia-2.8b vs OLMo-2-1124-7B | 312 | 26 | 0.527 [0.437, 0.608] | 0.271 [0.157, 0.384] | 0.797 / 0.840 | 0.644 [0.534, 0.744] |
| D4 | strict_all3 | pythia-1.4b vs pythia-2.8b | 50 | 7 | 0.182 [-0.100, 0.436] | 0.308 [0.019, 0.539] | 0.838 / 0.816 | 0.220 [-0.121, 0.527] |
| D4 | strict_all3 | pythia-1.4b vs OLMo-2-1124-7B | 50 | 7 | 0.319 [0.026, 0.562] | 0.130 [-0.148, 0.377] | 0.838 / 0.883 | 0.370 [0.030, 0.653] |
| D4 | strict_all3 | pythia-2.8b vs OLMo-2-1124-7B | 50 | 7 | 0.612 [0.382, 0.778] | 0.507 [0.223, 0.727] | 0.816 / 0.883 | 0.721 [0.450, 0.916] |
| D4 | any_correct | pythia-1.4b vs pythia-2.8b | 312 | 26 | 0.499 [0.407, 0.583] | 0.398 [0.291, 0.498] | 0.838 / 0.816 | 0.603 [0.492, 0.705] |
| D4 | any_correct | pythia-1.4b vs OLMo-2-1124-7B | 312 | 26 | 0.455 [0.358, 0.542] | 0.222 [0.105, 0.332] | 0.838 / 0.883 | 0.528 [0.417, 0.630] |
| D4 | any_correct | pythia-2.8b vs OLMo-2-1124-7B | 312 | 26 | 0.550 [0.460, 0.630] | 0.353 [0.247, 0.458] | 0.816 / 0.883 | 0.648 [0.542, 0.742] |

## EXPLORATORY (post hoc, not preregistered): limitations

1. **Not blind.** The D1 all-rows variance components were seen in the H-R gate before this plan (see the plan's disclosure).
2. **Interaction vs error.** One observation per fact × template cell, so the residual (fact × template interaction) cannot be separated from measurement error.
3. **Templates are nested in relations, 3 per relation.** The template-main component is estimated from 78 levels, and the D-study for k > 3 extrapolates assuming new templates come from the same population.
4. **Correctness filter.** Set (i) keeps only correct cells. The cells kept differ by model (720 / 804 / 1414), so facts and relations are unequally represented.
   - Set (ii) is small: 84 / 107 / 254 facts.
   - D2 and D3 are censored for incorrect cells by construction.
5. **Fact vs subject.** These are confounded; only their sum is reported as a share.
6. **Carrier.** 3 carriers, all neutral templates, which is too few levels to estimate a carrier main effect well.
7. **B6 uncertainty.** The B6 disattenuation holds G(3) at its point estimate (from the set-(ii) fit), so its CI ignores the uncertainty in G.
8. **Covariates.** Covariate effects are associations within these data, not causal decompositions.
9. **Exploratory.** Everything here is post hoc and not preregistered; no result here is confirmatory.
10. **CI coverage is below nominal in simulation.** Nominal 95% intervals (ANOVA estimator, within-relation fact bootstrap, balanced set-(ii) design) covered:
    - all components: 0.46–0.98, median 0.74;
    - fact share: 0.50–0.98 (median 0.84);
    - template-main share: 0.46–0.86 (median 0.69).
    - The lme4 cluster-bootstrap CIs used for the tables above were not themselves tested for coverage. Read every CI here as likely too narrow, most of all for template main (26 relations × 3 templates).
11. **Memory.** The largest single process peaked at 258 MB (`/usr/bin/time -v`, run.time in the run dir). The bootstrap used 3 R worker processes at once, roughly 3 × 0.26 GB.
