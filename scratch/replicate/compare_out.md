116 rows; FAIL: 6
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
