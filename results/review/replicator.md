# Replication of revised H-R gate numbers (results/review/claimed_numbers.json, run_id HR-none-f431f35-20261121T081116Z)

Scripts and outputs: /home/user/depth-law/scratch/replicate/ (build.py, fit_lib.R, point.R, boot.R, h2.py, h2_sharedrng.py, split_mc.R, compare.py; outputs point.json, boot.json, h2.json, h2_sharedrng.json, boot_*.csv, split_*.csv, compare_out.md). Inputs used: the 3 S3b depth.parquet files, data/facts_g1cpu.parquet, data/facts.parquet, data/amend2_inputs.parquet, cache/hr/prior_<model>.parquet, and offline tokenizers. No project analysis code or reports were read. cache/hr/tab_*.csv (project-derived tables) were not used.

Setup: R 4.3.3, lme4 1.1-35.1, 2000 relation-cluster bootstrap resamples (R set.seed(20261121)), 200 split-half splits per model, 10000 permutations and 2000 H2 bootstraps (numpy default_rng(20261121), reseeded per pair). Bootstrap fit failures: 0 of 2000 for ICC, ΔR² and OR in every model.

## FAILs (6 of 116 rows)

All 6 come from the split-half r_SB Monte Carlo. Every deterministic point estimate, bootstrap CI, permutation p, boolean, hypothesis and the decision PASS.

| field | claimed | yours | abs diff | tol |
|---|---|---|---|---|
| pythia-2.8b split_half_r_sb_undefined_as_0 | 0.753790 | 0.712599 | 0.0412 | 0.03 |
| pythia-1.4b vs pythia-2.8b disattenuated_rho_undefined_as_0 | 0.996479 | 1.026182 | 0.0297 | 0.002 |
| pythia-1.4b vs OLMo-2 disattenuated_rho | 0.554885 | 0.557624 | 0.00274 | 0.002 |
| pythia-1.4b vs OLMo-2 disattenuated_rho_undefined_as_0 | 0.556277 | 0.559024 | 0.00275 | 0.002 |
| pythia-2.8b vs OLMo-2 disattenuated_rho | 0.648584 | 0.651325 | 0.00274 | 0.002 |
| pythia-2.8b vs OLMo-2 disattenuated_rho_undefined_as_0 | 0.707663 | 0.730490 | 0.0228 | 0.002 |

Supporting facts:
- Recomputing the claimed disattenuated ρ from the claimed ρ and claimed r_SB means gives exactly the claimed values (diff 0.0 for all 6 disattenuated fields). The claimed rho_minus_cov_only equals the claimed rho minus the claimed cov_only_rho exactly.
- Undefined splits for pythia-2.8b: 41/200 in my run vs 32/200 claimed. An extra run of 1000 splits (seed 1) gave 191/1000 undefined (19.1%). Its five blocks of 200 had 38, 35, 39, 44 and 35 undefined, with undefined_as_0 means of 0.727, 0.740, 0.719, 0.703 and 0.739, and mean_defined from 0.894 to 0.902.
- In all 191 undefined splits, one half's fit had every relation BLUP exactly 0 (σ²_rel = 0).
- The disattenuated ρ tolerance (0.002) is smaller than the Monte Carlo spread of r_SB propagated through ρ/sqrt(r_SB,A · r_SB,B).

## Full table

Lists and the vc dict are expanded to one row per element. That makes 111 rows for the 87 claimed fields, plus 4 hypothesis rows and the decision.
Count rule used for split_half_n_undefined: PASS if both are 0, or the yours/claimed ratio is within [0.1, 10], or both are < 10.

| field | claimed | yours | abs diff | tolerance | result |
|---|---|---|---|---|---|
| models.EleutherAI/pythia-1.4b.n_rows | 3900 | 3900 | 0 | 0 | PASS |
| models.EleutherAI/pythia-1.4b.icc_rel | 0.0399805 | 0.0399805 | 6.772e-10 | 0.002 | PASS |
| models.EleutherAI/pythia-1.4b.icc_ci[0] | 0 | 0 | 0 | 0.03 | PASS |
| models.EleutherAI/pythia-1.4b.icc_ci[1] | 0.118786 | 0.122296 | 0.00351071 | 0.03 | PASS |
| models.EleutherAI/pythia-1.4b.dr2 | -2.811e-04 | -2.811e-04 | 1.547e-10 | 0.002 | PASS |
| models.EleutherAI/pythia-1.4b.dr2_ci[0] | -0.00315574 | -0.00303464 | 1.211e-04 | 0.03 | PASS |
| models.EleutherAI/pythia-1.4b.dr2_ci[1] | 0.0037236 | 0.00361366 | 1.099e-04 | 0.03 | PASS |
| models.EleutherAI/pythia-1.4b.or_per_log1p_cooc | 1.38368 | 1.38368 | 4.441e-16 | 0.002 | PASS |
| models.EleutherAI/pythia-1.4b.or_ci[0] | 1.27557 | 1.27397 | 0.00160805 | 0.03 | PASS |
| models.EleutherAI/pythia-1.4b.or_ci[1] | 1.46596 | 1.47053 | 0.00457013 | 0.03 | PASS |
| models.EleutherAI/pythia-1.4b.vc.subject | 0.00684968 | 0.00684968 | 2.999e-12 | 0.002 | PASS |
| models.EleutherAI/pythia-1.4b.vc.rt | 0.00629475 | 0.00629475 | 1.389e-12 | 0.002 | PASS |
| models.EleutherAI/pythia-1.4b.vc.relation | 8.738e-04 | 8.738e-04 | 1.538e-11 | 0.002 | PASS |
| models.EleutherAI/pythia-1.4b.vc.Residual | 0.00783774 | 0.00783774 | 7.229e-13 | 0.002 | PASS |
| models.EleutherAI/pythia-1.4b.r2m_without_cooc_ML | 0.408317 | 0.408317 | 1.265e-10 | 0.002 | PASS |
| models.EleutherAI/pythia-1.4b.r2m_with_cooc_ML | 0.408036 | 0.408036 | 2.819e-11 | 0.002 | PASS |
| models.EleutherAI/pythia-1.4b.split_half_r_sb_mean_defined | 0.929015 | 0.926648 | 0.00236687 | 0.03 | PASS |
| models.EleutherAI/pythia-1.4b.split_half_n_undefined | 1 | 1 | 0 | same order | PASS |
| models.EleutherAI/pythia-1.4b.split_half_r_sb_undefined_as_0 | 0.92437 | 0.922015 | 0.00235503 | 0.03 | PASS |
| models.EleutherAI/pythia-1.4b.h1_pass | False | False |  | rule | PASS |
| models.EleutherAI/pythia-1.4b.h3_pass | True | True |  | rule | PASS |
| models.EleutherAI/pythia-2.8b.n_rows | 3900 | 3900 | 0 | 0 | PASS |
| models.EleutherAI/pythia-2.8b.icc_rel | 0.0125924 | 0.0125924 | 1.506e-09 | 0.002 | PASS |
| models.EleutherAI/pythia-2.8b.icc_ci[0] | 0 | 0 | 0 | 0.03 | PASS |
| models.EleutherAI/pythia-2.8b.icc_ci[1] | 0.0748402 | 0.074173 | 6.672e-04 | 0.03 | PASS |
| models.EleutherAI/pythia-2.8b.dr2 | 0.00123328 | 0.00124124 | 7.960e-06 | 0.002 | PASS |
| models.EleutherAI/pythia-2.8b.dr2_ci[0] | -0.00122718 | -0.0012116 | 1.559e-05 | 0.03 | PASS |
| models.EleutherAI/pythia-2.8b.dr2_ci[1] | 0.00835136 | 0.00886192 | 5.106e-04 | 0.03 | PASS |
| models.EleutherAI/pythia-2.8b.or_per_log1p_cooc | 1.43309 | 1.43309 | 2.887e-15 | 0.002 | PASS |
| models.EleutherAI/pythia-2.8b.or_ci[0] | 1.31991 | 1.31821 | 0.00170158 | 0.03 | PASS |
| models.EleutherAI/pythia-2.8b.or_ci[1] | 1.56016 | 1.56379 | 0.0036297 | 0.03 | PASS |
| models.EleutherAI/pythia-2.8b.vc.subject | 0.0075205 | 0.0075205 | 8.762e-12 | 0.002 | PASS |
| models.EleutherAI/pythia-2.8b.vc.rt | 0.00610471 | 0.00610471 | 1.183e-12 | 0.002 | PASS |
| models.EleutherAI/pythia-2.8b.vc.relation | 2.634e-04 | 2.634e-04 | 3.180e-11 | 0.002 | PASS |
| models.EleutherAI/pythia-2.8b.vc.Residual | 0.00703062 | 0.00703062 | 2.040e-12 | 0.002 | PASS |
| models.EleutherAI/pythia-2.8b.r2m_without_cooc_ML | 0.336372 | 0.336364 | 7.960e-06 | 0.002 | PASS |
| models.EleutherAI/pythia-2.8b.r2m_with_cooc_ML | 0.337605 | 0.337605 | 2.396e-10 | 0.002 | PASS |
| models.EleutherAI/pythia-2.8b.split_half_r_sb_mean_defined | 0.897369 | 0.896351 | 0.0010175 | 0.03 | PASS |
| models.EleutherAI/pythia-2.8b.split_half_n_undefined | 32 | 41 | 9 | same order | PASS |
| models.EleutherAI/pythia-2.8b.split_half_r_sb_undefined_as_0 | 0.75379 | 0.712599 | 0.0411905 | 0.03 | FAIL |
| models.EleutherAI/pythia-2.8b.h1_pass | False | False |  | rule | PASS |
| models.EleutherAI/pythia-2.8b.h3_pass | True | True |  | rule | PASS |
| models.allenai/OLMo-2-1124-7B.n_rows | 3900 | 3900 | 0 | 0 | PASS |
| models.allenai/OLMo-2-1124-7B.icc_rel | 0.0595668 | 0.0595668 | 0 | 0.002 | PASS |
| models.allenai/OLMo-2-1124-7B.icc_ci[0] | 2.920e-10 | 2.941e-10 | 2.059e-12 | 0.03 | PASS |
| models.allenai/OLMo-2-1124-7B.icc_ci[1] | 0.123387 | 0.12448 | 0.00109322 | 0.03 | PASS |
| models.allenai/OLMo-2-1124-7B.dr2 | 0.0016048 | 0.0016048 | 0 | 0.002 | PASS |
| models.allenai/OLMo-2-1124-7B.dr2_ci[0] | -3.823e-04 | -4.056e-04 | 2.334e-05 | 0.03 | PASS |
| models.allenai/OLMo-2-1124-7B.dr2_ci[1] | 0.0104448 | 0.0109619 | 5.171e-04 | 0.03 | PASS |
| models.allenai/OLMo-2-1124-7B.or_per_log1p_cooc | 1.28328 | 1.28328 | 3.553e-15 | 0.002 | PASS |
| models.allenai/OLMo-2-1124-7B.or_ci[0] | 1.20851 | 1.20929 | 7.806e-04 | 0.03 | PASS |
| models.allenai/OLMo-2-1124-7B.or_ci[1] | 1.36988 | 1.37128 | 0.00139173 | 0.03 | PASS |
| models.allenai/OLMo-2-1124-7B.vc.subject | 0.00700913 | 0.00700913 | 0 | 0.002 | PASS |
| models.allenai/OLMo-2-1124-7B.vc.rt | 0.00632519 | 0.00632519 | 0 | 0.002 | PASS |
| models.allenai/OLMo-2-1124-7B.vc.relation | 0.0012534 | 0.0012534 | 0 | 0.002 | PASS |
| models.allenai/OLMo-2-1124-7B.vc.Residual | 0.00645413 | 0.00645413 | 0 | 0.002 | PASS |
| models.allenai/OLMo-2-1124-7B.r2m_without_cooc_ML | 0.290835 | 0.290835 | 0 | 0.002 | PASS |
| models.allenai/OLMo-2-1124-7B.r2m_with_cooc_ML | 0.29244 | 0.29244 | 0 | 0.002 | PASS |
| models.allenai/OLMo-2-1124-7B.split_half_r_sb_mean_defined | 0.942834 | 0.935978 | 0.00685649 | 0.03 | PASS |
| models.allenai/OLMo-2-1124-7B.split_half_n_undefined | 0 | 0 | 0 | same order | PASS |
| models.allenai/OLMo-2-1124-7B.split_half_r_sb_undefined_as_0 | 0.942834 | 0.935978 | 0.00685649 | 0.03 | PASS |
| models.allenai/OLMo-2-1124-7B.h1_pass | False | False |  | rule | PASS |
| models.allenai/OLMo-2-1124-7B.h3_pass | True | True |  | rule | PASS |
| pairs.pythia-1.4b vs pythia-2.8b.n_relations | 26 | 26 | 0 | 0 | PASS |
| pairs.pythia-1.4b vs pythia-2.8b.rho | 0.831795 | 0.831795 | 0 | 0.002 | PASS |
| pairs.pythia-1.4b vs pythia-2.8b.rho_ci[0] | 0.661627 | 0.661627 | 0 | 0.03 | PASS |
| pairs.pythia-1.4b vs pythia-2.8b.rho_ci[1] | 0.91553 | 0.91553 | 0 | 0.03 | PASS |
| pairs.pythia-1.4b vs pythia-2.8b.perm_p_one_sided | 9.999e-05 | 9.999e-05 | 0 | 0.003 | PASS |
| pairs.pythia-1.4b vs pythia-2.8b.perm_p_two_sided | 9.999e-05 | 9.999e-05 | 0 | 0.003 | PASS |
| pairs.pythia-1.4b vs pythia-2.8b.partial_rho | 0.819487 | 0.819487 | 0 | 0.002 | PASS |
| pairs.pythia-1.4b vs pythia-2.8b.partial_rho_ci[0] | 0.392262 | 0.392262 | 0 | 0.03 | PASS |
| pairs.pythia-1.4b vs pythia-2.8b.partial_rho_ci[1] | 0.945093 | 0.945093 | 0 | 0.03 | PASS |
| pairs.pythia-1.4b vs pythia-2.8b.cov_only_rho | 0.730598 | 0.730598 | 0 | 0.002 | PASS |
| pairs.pythia-1.4b vs pythia-2.8b.rho_minus_cov_only | 0.101197 | 0.101197 | 0 | 0.002 | PASS |
| pairs.pythia-1.4b vs pythia-2.8b.disattenuated_rho | 0.911002 | 0.912682 | 0.00168029 | 0.002 | PASS |
| pairs.pythia-1.4b vs pythia-2.8b.disattenuated_rho_undefined_as_0 | 0.996479 | 1.02618 | 0.0297033 | 0.002 | FAIL |
| pairs.pythia-1.4b vs pythia-2.8b.h2_raw_pass | True | True |  | rule | PASS |
| pairs.pythia-1.4b vs pythia-2.8b.h2_controlled_pass | False | False |  | rule | PASS |
| pairs.pythia-1.4b vs pythia-2.8b.counts_for_decision | False | False |  | rule | PASS |
| pairs.pythia-1.4b vs OLMo-2-1124-7B.n_relations | 26 | 26 | 0 | 0 | PASS |
| pairs.pythia-1.4b vs OLMo-2-1124-7B.rho | 0.519316 | 0.519316 | 0 | 0.002 | PASS |
| pairs.pythia-1.4b vs OLMo-2-1124-7B.rho_ci[0] | 0.156608 | 0.149696 | 0.00691163 | 0.03 | PASS |
| pairs.pythia-1.4b vs OLMo-2-1124-7B.rho_ci[1] | 0.78311 | 0.78027 | 0.00284031 | 0.03 | PASS |
| pairs.pythia-1.4b vs OLMo-2-1124-7B.perm_p_one_sided | 0.00279972 | 0.00459954 | 0.00179982 | 0.003 | PASS |
| pairs.pythia-1.4b vs OLMo-2-1124-7B.perm_p_two_sided | 0.0069993 | 0.00829917 | 0.00129987 | 0.003 | PASS |
| pairs.pythia-1.4b vs OLMo-2-1124-7B.partial_rho | 0.569231 | 0.569231 | 0 | 0.002 | PASS |
| pairs.pythia-1.4b vs OLMo-2-1124-7B.partial_rho_ci[0] | 0.0417958 | 0.034287 | 0.00750879 | 0.03 | PASS |
| pairs.pythia-1.4b vs OLMo-2-1124-7B.partial_rho_ci[1] | 0.832193 | 0.845298 | 0.0131053 | 0.03 | PASS |
| pairs.pythia-1.4b vs OLMo-2-1124-7B.cov_only_rho | 0.277949 | 0.277949 | 0 | 0.002 | PASS |
| pairs.pythia-1.4b vs OLMo-2-1124-7B.rho_minus_cov_only | 0.241368 | 0.241368 | 0 | 0.002 | PASS |
| pairs.pythia-1.4b vs OLMo-2-1124-7B.disattenuated_rho | 0.554885 | 0.557624 | 0.00273948 | 0.002 | FAIL |
| pairs.pythia-1.4b vs OLMo-2-1124-7B.disattenuated_rho_undefined_as_0 | 0.556277 | 0.559024 | 0.00274635 | 0.002 | FAIL |
| pairs.pythia-1.4b vs OLMo-2-1124-7B.h2_raw_pass | False | False |  | rule | PASS |
| pairs.pythia-1.4b vs OLMo-2-1124-7B.h2_controlled_pass | False | False |  | rule | PASS |
| pairs.pythia-1.4b vs OLMo-2-1124-7B.counts_for_decision | True | True |  | rule | PASS |
| pairs.pythia-2.8b vs OLMo-2-1124-7B.n_relations | 26 | 26 | 0 | 0 | PASS |
| pairs.pythia-2.8b vs OLMo-2-1124-7B.rho | 0.596581 | 0.596581 | 0 | 0.002 | PASS |
| pairs.pythia-2.8b vs OLMo-2-1124-7B.rho_ci[0] | 0.257132 | 0.250484 | 0.00664811 | 0.03 | PASS |
| pairs.pythia-2.8b vs OLMo-2-1124-7B.rho_ci[1] | 0.811762 | 0.81113 | 6.322e-04 | 0.03 | PASS |
| pairs.pythia-2.8b vs OLMo-2-1124-7B.perm_p_one_sided | 0.00109989 | 9.999e-04 | 9.999e-05 | 0.003 | PASS |
| pairs.pythia-2.8b vs OLMo-2-1124-7B.perm_p_two_sided | 0.00169983 | 0.0019998 | 3.000e-04 | 0.003 | PASS |
| pairs.pythia-2.8b vs OLMo-2-1124-7B.partial_rho | 0.600684 | 0.600684 | 0 | 0.002 | PASS |
| pairs.pythia-2.8b vs OLMo-2-1124-7B.partial_rho_ci[0] | 0.0758245 | 0.0910903 | 0.0152658 | 0.03 | PASS |
| pairs.pythia-2.8b vs OLMo-2-1124-7B.partial_rho_ci[1] | 0.85389 | 0.857465 | 0.00357457 | 0.03 | PASS |
| pairs.pythia-2.8b vs OLMo-2-1124-7B.cov_only_rho | 0.571282 | 0.571282 | 0 | 0.002 | PASS |
| pairs.pythia-2.8b vs OLMo-2-1124-7B.rho_minus_cov_only | 0.0252991 | 0.0252991 | 0 | 0.002 | PASS |
| pairs.pythia-2.8b vs OLMo-2-1124-7B.disattenuated_rho | 0.648584 | 0.651325 | 0.00274063 | 0.002 | FAIL |
| pairs.pythia-2.8b vs OLMo-2-1124-7B.disattenuated_rho_undefined_as_0 | 0.707663 | 0.73049 | 0.0228263 | 0.002 | FAIL |
| pairs.pythia-2.8b vs OLMo-2-1124-7B.h2_raw_pass | False | False |  | rule | PASS |
| pairs.pythia-2.8b vs OLMo-2-1124-7B.h2_controlled_pass | False | False |  | rule | PASS |
| pairs.pythia-2.8b vs OLMo-2-1124-7B.counts_for_decision | True | True |  | rule | PASS |
| hypotheses.H1 | False | False |  | rule | PASS |
| hypotheses.H2_raw | False | False |  | rule | PASS |
| hypotheses.H2_controlled | False | False |  | rule | PASS |
| hypotheses.H3 | True | True |  | rule | PASS |
| decision | NO-GO | NO-GO |  | rule | PASS |

Extra (not claimed): split-half r_SB 2.5/97.5 percentiles over defined splits were pythia-1.4b [0.875, 0.966], pythia-2.8b [0.809, 0.953] and OLMo-2 [0.893, 0.970].

## Ambiguities in definitions that let a different value arise

1. Undefined split-halves. B6 does not say what to do when a half's H1 fit is singular in σ²_rel, which makes all 26 BLUPs 0 and the Spearman undefined. It defines only "the per-model mean r_SB".
   - The claim reports two variants: the mean over defined splits, and the mean with undefined set to 0. B6 does not specify either.
   - The disattenuated ρ therefore has two values. For pythia-1.4b vs 2.8b the claimed values are 0.911 vs 0.996, and mine are 0.913 vs 1.026.
   - I counted a split as undefined when the Spearman was NA. All such cases were an all-zero BLUP half.
2. The disattenuated ρ is listed under deterministic tolerance (0.002) but depends on the Monte Carlo r_SB. Given the claimed r_SB it reproduces exactly; given mine it differs by 0.0017-0.030.
3. Permutation p and RNG stream. B5/B10 give one seed but not how the RNG is consumed across pairs.
   - With numpy default_rng(20261121) reseeded per pair, pair 1 (pythia-1.4b vs 2.8b) reproduces the claimed rho_ci, partial_rho_ci and p to full float precision. Pairs 2 and 3 do not.
   - Pair 2 one-sided p: 0.00460 (reseeded per pair), 0.00360 (one shared stream across pairs), 0.00280 (claimed). All are < 0.01.
4. Two-sided permutation p is "also reported" in B5 without a formula. I used (1 + #{|ρ_perm| >= |ρ_obs|}) / 10001.
5. Bootstrap relabelling of subjects. Four subject strings occur in two relations each.
   - I kept original labels for the first draw of a relation and suffixed the relation, relation:template and subject labels for repeat draws.
   - B4 does not say whether the first copy keeps its labels, or whether a subject shared across relations stays crossed. I did not test the alternative.
6. Marginal R². B7 says var(fixed-part predictions) without stating the denominator. I used R var() (n-1).
   - pythia-2.8b r2m_without_cooc_ML and dr2 differ from the claims by 8.0e-6 (PASS); the other two models match to ≤3e-10.
   - The source of the 8e-6 difference is not identified (n vs n-1 alone would change all models). I used lmerControl(calc.derivs = FALSE) with default optimizers.
7. Scaling (B2) says "continuous fact covariates are z-scored". It is unspecified whether integer counts (token counts, subj_final_dist) count as continuous, and whether to re-z-score inside each bootstrap resample. I z-scored all 5 on the full data once. ICC, BLUPs, R² and the cooc OR are invariant to this; cooc_within was left unscaled.
8. Field count. The claim says 87 fields. That count is reached only when icc_ci, dr2_ci, or_ci, rho_ci, partial_rho_ci and vc each count as one field.
