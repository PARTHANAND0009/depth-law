# EXPLORATORY (post hoc, not preregistered) — independent replication of E-depthvar B3 shares and B6 cross-model rho

Claims: reports/gates/G1/EXPLORATORY_post-hoc_not-preregistered__claimed_numbers.json (source run EXPLORATORY_E-depthvar-none-321939b-20261121T153451Z).
Inputs: the three S3b depth.parquet files (S3b-pythia-1.4b-a7dfeb5-20261121T063528Z, S3b-pythia-2.8b-a7dfeb5-20261121T064110Z, S3b-OLMo-2-1124-7B-923945f-20261121T061237Z) and data/facts_g1cpu.parquet.
Scripts: /home/user/depth-law/scratch/replicate_edv/rep2.py (D1/D4, ANOVA, B6, MixedLM), compare.py, sim_anova.py, write_report.py. Outputs: scratch/replicate_edv/{stage1.json, ml.json, cells.parquet}.

## FAILs

None. 72 numbers checked (48 B3 shares, 24 B6 rho); 0 FAIL. Max |diff|: B3 0.00016, B6 0.0e+00.

## Pre-checks

- D1 recomputed from final_logprob_curves equals stored half_prob_depth for all 3900 rows in each model (max |diff| = 0.0). L = 24 (pythia-1.4b), 32 (pythia-2.8b, OLMo-2).
- n_cells and n_facts match the claimed values for all 12 B3 sets; n_facts match for all B6 sets (strict_all3 = 50, any_correct = 312).

## Table (graded value = statsmodels MixedLM REML)

| field | claimed | yours | abs diff | tolerance | result |
|---|---|---|---|---|---|
| B3 pythia-1.4b|D1|correct fact_plus_subject | 0.4645 | 0.4646 | 0.00001 | 0.02 | PASS |
| B3 pythia-1.4b|D1|correct template_main | 0.2127 | 0.2126 | 0.00001 | 0.02 | PASS |
| B3 pythia-1.4b|D1|correct residual | 0.2289 | 0.2289 | 0.00001 | 0.02 | PASS |
| B3 pythia-1.4b|D1|correct relation | 0.0939 | 0.0939 | 0.00001 | 0.02 | PASS |
| B3 pythia-1.4b|D1|all3 fact_plus_subject | 0.4393 | 0.4393 | 0.00001 | 0.02 | PASS |
| B3 pythia-1.4b|D1|all3 template_main | 0.3790 | 0.3790 | 0.00001 | 0.02 | PASS |
| B3 pythia-1.4b|D1|all3 residual | 0.1817 | 0.1817 | 0.00001 | 0.02 | PASS |
| B3 pythia-1.4b|D1|all3 relation | 0.0000 | 0.0000 | 0.00000 | 0.02 | PASS |
| B3 pythia-1.4b|D4|correct fact_plus_subject | 0.4838 | 0.4838 | 0.00001 | 0.02 | PASS |
| B3 pythia-1.4b|D4|correct template_main | 0.1510 | 0.1510 | 0.00002 | 0.02 | PASS |
| B3 pythia-1.4b|D4|correct residual | 0.1327 | 0.1327 | 0.00002 | 0.02 | PASS |
| B3 pythia-1.4b|D4|correct relation | 0.2325 | 0.2325 | 0.00002 | 0.02 | PASS |
| B3 pythia-1.4b|D4|all3 fact_plus_subject | 0.4069 | 0.4069 | 0.00001 | 0.02 | PASS |
| B3 pythia-1.4b|D4|all3 template_main | 0.3568 | 0.3568 | 0.00001 | 0.02 | PASS |
| B3 pythia-1.4b|D4|all3 residual | 0.2363 | 0.2363 | 0.00002 | 0.02 | PASS |
| B3 pythia-1.4b|D4|all3 relation | 0.0000 | 0.0000 | 0.00000 | 0.02 | PASS |
| B3 pythia-2.8b|D1|correct fact_plus_subject | 0.3788 | 0.3788 | 0.00000 | 0.02 | PASS |
| B3 pythia-2.8b|D1|correct template_main | 0.0511 | 0.0511 | 0.00000 | 0.02 | PASS |
| B3 pythia-2.8b|D1|correct residual | 0.2428 | 0.2428 | 0.00001 | 0.02 | PASS |
| B3 pythia-2.8b|D1|correct relation | 0.3273 | 0.3274 | 0.00001 | 0.02 | PASS |
| B3 pythia-2.8b|D1|all3 fact_plus_subject | 0.3015 | 0.3016 | 0.00003 | 0.02 | PASS |
| B3 pythia-2.8b|D1|all3 template_main | 0.0356 | 0.0357 | 0.00001 | 0.02 | PASS |
| B3 pythia-2.8b|D1|all3 residual | 0.2300 | 0.2300 | 0.00003 | 0.02 | PASS |
| B3 pythia-2.8b|D1|all3 relation | 0.4328 | 0.4328 | 0.00007 | 0.02 | PASS |
| B3 pythia-2.8b|D4|correct fact_plus_subject | 0.4303 | 0.4303 | 0.00000 | 0.02 | PASS |
| B3 pythia-2.8b|D4|correct template_main | 0.0721 | 0.0721 | 0.00000 | 0.02 | PASS |
| B3 pythia-2.8b|D4|correct residual | 0.1725 | 0.1725 | 0.00000 | 0.02 | PASS |
| B3 pythia-2.8b|D4|correct relation | 0.3251 | 0.3251 | 0.00000 | 0.02 | PASS |
| B3 pythia-2.8b|D4|all3 fact_plus_subject | 0.3388 | 0.3388 | 0.00002 | 0.02 | PASS |
| B3 pythia-2.8b|D4|all3 template_main | 0.0686 | 0.0686 | 0.00001 | 0.02 | PASS |
| B3 pythia-2.8b|D4|all3 residual | 0.2287 | 0.2287 | 0.00000 | 0.02 | PASS |
| B3 pythia-2.8b|D4|all3 relation | 0.3639 | 0.3638 | 0.00003 | 0.02 | PASS |
| B3 OLMo-2-1124-7B|D1|correct fact_plus_subject | 0.3060 | 0.3059 | 0.00009 | 0.02 | PASS |
| B3 OLMo-2-1124-7B|D1|correct template_main | 0.3322 | 0.3322 | 0.00001 | 0.02 | PASS |
| B3 OLMo-2-1124-7B|D1|correct residual | 0.1729 | 0.1729 | 0.00006 | 0.02 | PASS |
| B3 OLMo-2-1124-7B|D1|correct relation | 0.1889 | 0.1890 | 0.00016 | 0.02 | PASS |
| B3 OLMo-2-1124-7B|D1|all3 fact_plus_subject | 0.2779 | 0.2778 | 0.00000 | 0.02 | PASS |
| B3 OLMo-2-1124-7B|D1|all3 template_main | 0.4106 | 0.4107 | 0.00004 | 0.02 | PASS |
| B3 OLMo-2-1124-7B|D1|all3 residual | 0.1592 | 0.1592 | 0.00000 | 0.02 | PASS |
| B3 OLMo-2-1124-7B|D1|all3 relation | 0.1523 | 0.1522 | 0.00004 | 0.02 | PASS |
| B3 OLMo-2-1124-7B|D4|correct fact_plus_subject | 0.2871 | 0.2871 | 0.00002 | 0.02 | PASS |
| B3 OLMo-2-1124-7B|D4|correct template_main | 0.3664 | 0.3663 | 0.00006 | 0.02 | PASS |
| B3 OLMo-2-1124-7B|D4|correct residual | 0.1242 | 0.1242 | 0.00002 | 0.02 | PASS |
| B3 OLMo-2-1124-7B|D4|correct relation | 0.2223 | 0.2224 | 0.00010 | 0.02 | PASS |
| B3 OLMo-2-1124-7B|D4|all3 fact_plus_subject | 0.3008 | 0.3008 | 0.00000 | 0.02 | PASS |
| B3 OLMo-2-1124-7B|D4|all3 template_main | 0.3910 | 0.3910 | 0.00005 | 0.02 | PASS |
| B3 OLMo-2-1124-7B|D4|all3 residual | 0.1191 | 0.1191 | 0.00001 | 0.02 | PASS |
| B3 OLMo-2-1124-7B|D4|all3 relation | 0.1891 | 0.1891 | 0.00004 | 0.02 | PASS |
| B6 D1|strict_all3|pythia-1.4b vs pythia-2.8b rho (n=50) | -0.1727 | -0.1727 | 0.00000 | 0.03 | PASS |
| B6 D1|strict_all3|pythia-1.4b vs pythia-2.8b rho_within_relation (n=50) | 0.1448 | 0.1448 | 0.00000 | 0.03 | PASS |
| B6 D1|strict_all3|pythia-1.4b vs OLMo-2-1124-7B rho (n=50) | 0.0005 | 0.0005 | 0.00000 | 0.03 | PASS |
| B6 D1|strict_all3|pythia-1.4b vs OLMo-2-1124-7B rho_within_relation (n=50) | -0.0215 | -0.0215 | 0.00000 | 0.03 | PASS |
| B6 D1|strict_all3|pythia-2.8b vs OLMo-2-1124-7B rho (n=50) | 0.4109 | 0.4109 | 0.00000 | 0.03 | PASS |
| B6 D1|strict_all3|pythia-2.8b vs OLMo-2-1124-7B rho_within_relation (n=50) | 0.2885 | 0.2885 | 0.00000 | 0.03 | PASS |
| B6 D1|any_correct|pythia-1.4b vs pythia-2.8b rho (n=312) | 0.3471 | 0.3471 | 0.00000 | 0.03 | PASS |
| B6 D1|any_correct|pythia-1.4b vs pythia-2.8b rho_within_relation (n=312) | 0.1876 | 0.1876 | 0.00000 | 0.03 | PASS |
| B6 D1|any_correct|pythia-1.4b vs OLMo-2-1124-7B rho (n=312) | 0.3555 | 0.3555 | 0.00000 | 0.03 | PASS |
| B6 D1|any_correct|pythia-1.4b vs OLMo-2-1124-7B rho_within_relation (n=312) | 0.1131 | 0.1131 | 0.00000 | 0.03 | PASS |
| B6 D1|any_correct|pythia-2.8b vs OLMo-2-1124-7B rho (n=312) | 0.5270 | 0.5270 | 0.00000 | 0.03 | PASS |
| B6 D1|any_correct|pythia-2.8b vs OLMo-2-1124-7B rho_within_relation (n=312) | 0.2709 | 0.2709 | 0.00000 | 0.03 | PASS |
| B6 D4|strict_all3|pythia-1.4b vs pythia-2.8b rho (n=50) | 0.1820 | 0.1820 | 0.00000 | 0.03 | PASS |
| B6 D4|strict_all3|pythia-1.4b vs pythia-2.8b rho_within_relation (n=50) | 0.3078 | 0.3078 | 0.00000 | 0.03 | PASS |
| B6 D4|strict_all3|pythia-1.4b vs OLMo-2-1124-7B rho (n=50) | 0.3185 | 0.3185 | 0.00000 | 0.03 | PASS |
| B6 D4|strict_all3|pythia-1.4b vs OLMo-2-1124-7B rho_within_relation (n=50) | 0.1295 | 0.1295 | 0.00000 | 0.03 | PASS |
| B6 D4|strict_all3|pythia-2.8b vs OLMo-2-1124-7B rho (n=50) | 0.6119 | 0.6119 | 0.00000 | 0.03 | PASS |
| B6 D4|strict_all3|pythia-2.8b vs OLMo-2-1124-7B rho_within_relation (n=50) | 0.5069 | 0.5069 | 0.00000 | 0.03 | PASS |
| B6 D4|any_correct|pythia-1.4b vs pythia-2.8b rho (n=312) | 0.4989 | 0.4989 | 0.00000 | 0.03 | PASS |
| B6 D4|any_correct|pythia-1.4b vs pythia-2.8b rho_within_relation (n=312) | 0.3976 | 0.3976 | 0.00000 | 0.03 | PASS |
| B6 D4|any_correct|pythia-1.4b vs OLMo-2-1124-7B rho (n=312) | 0.4545 | 0.4545 | 0.00000 | 0.03 | PASS |
| B6 D4|any_correct|pythia-1.4b vs OLMo-2-1124-7B rho_within_relation (n=312) | 0.2215 | 0.2215 | 0.00000 | 0.03 | PASS |
| B6 D4|any_correct|pythia-2.8b vs OLMo-2-1124-7B rho (n=312) | 0.5501 | 0.5501 | 0.00000 | 0.03 | PASS |
| B6 D4|any_correct|pythia-2.8b vs OLMo-2-1124-7B rho_within_relation (n=312) | 0.3527 | 0.3527 | 0.00000 | 0.03 | PASS |

## Library / estimator

- B3: statsmodels 0.15.0 `MixedLM.from_formula('y ~ 1', groups=<one constant group>, re_formula='0', vc_formula={relation, relation:template, fact_id, subject}, use_sparse=True)`, `fit(reml=True, method='lbfgs')`. All reported fits converged=True. Share = component / (sum of 4 components + residual scale); fact_plus_subject = fact + subject.
- relation:template level = relation + template_id (0..2). subject = facts_g1cpu.subject (1300 facts, 1296 distinct subjects).
- B6: scipy.stats.spearmanr (average ranks for ties) on fact-level means; within-relation version subtracts, per model, the relation mean of fact-level means over the selected facts.
- Cross-check (not graded): own Henderson method III (sequential sums of squares: relation, relation:template | relation, fact | relation:template, residual; expected mean squares from exact trace coefficients; negatives clipped at 0) implemented in numpy. It is the plan's ANOVA generalized to unequal facts per relation.

## Ambiguities / estimator dependence

1. Subject vs fact confounding. In every all3 set n_subjects = n_facts (84, 107, 254), so subject and fact are not separately identified. With both terms, statsmodels raised LinAlgError (singular Hessian) for: pythia-1.4b|D4|all3, pythia-2.8b|D4|all3. For those two sets the graded value is from the same model without (1|subject), which is the same model when subject is identical to fact. Where both fits ran, dropping (1|subject) changed fact_plus_subject by at most 0.0040 (correct sets: 400/402, 433/436, 676/680 subjects/facts).
2. Estimator choice. The Henderson-III method-of-moments estimate differs from REML (claimed) by more than 0.02 in 26 of 48 B3 shares; max |diff| = 0.2527. The largest gaps are in the relation and template_main shares (e.g. OLMo-2 D1 all3: template_main REML 0.4106 vs MoM 0.1579; relation 0.1523 vs 0.3334). Fact and residual components (absolute variances) agree more closely (OLMo-2 D1 all3: fact 0.00253 vs 0.00255, residual 0.00145 vs 0.00144). Negative raw MoM estimates: none.
   - Simulation check of the MoM code (sim_anova.py, 300 draws per set, Gaussian data from the REML D1 components on each real design): MoM mean equals the true components (unbiased); MoM SD for relation:template is large, e.g. OLMo-2 D1 all3: true 0.00374, MoM SD 0.00116; observed MoM 0.00124 (about 2.2 SD below the REML value).
   - So the claimed shares are reproduced by an independent REML implementation, but not, within 0.02, by the method-of-moments estimator for many relation/template_main shares. The claims are defined as REML shares, so grading uses REML.
3. No other definitional choices changed any value: D1 matched the stored column exactly, and all 24 B6 rho values matched to <1e-9.

Resources: each process ran under nice -n 10, prlimit --as=1.8 GB, OMP_NUM_THREADS=1, ARROW_DEFAULT_MEMORY_POOL=system (the default mimalloc pool reserves about 1.2 GB of address space and caused allocation failures under the cap). Peak RSS was 344 MB or less. One earlier attempt using the dense statsmodels design hit the 10-minute background limit and produced no output; it was replaced by the sparse fits.

VERDICT: PASS
