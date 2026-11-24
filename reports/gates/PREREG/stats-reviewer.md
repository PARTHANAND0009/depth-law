<!-- stats-reviewer subagent (.claude/agents/stats-reviewer.md), fresh context, 2026-11-23: the FINAL, narrow PREREG review after round 3 (human-set scope: only the new parametric fact-share null, its prereg text, and its calibration and power results; BLOCKING only if the null still does not test "fact = 0"). Earlier full reviews: stats-reviewer_round1.md (REVISE), stats-reviewer_round2.md (REVISE), stats-reviewer_round3.md (BLOCK, finding B1 on the old null). Saved verbatim by the main session; not edited. Staged here for APPLY.sh (the deny rule Edit(prereg/**) also blocks reports/gates/PREREG/). Answers: responses.md. -->
## BLOCKING

No BLOCKING findings.

The code tests H0: fact variance = 0, and the prereg text describes that same null. Checks behind this:
- **Null model.** `p2_formula(..., fact = FALSE)` (/home/user/depth-law/analysis/p2/p2_model.R L25–31) drops only `(1|fact)`. It keeps `(1|relation)`, `(1|frame)`, `(1|rt)`, `(1|ft)`, `(1|fc)`, the covariates and `carrier_f`. Both `m0` and `m1` are built from the same `p2_prep` data, covariate list, subject flag and carrier flag (/home/user/depth-law/analysis/p2/p2_null_fns.R L13–17).
- **simulate().** lme4 1.1.35.1 defaults are `use.u = FALSE, re.form = NA`. `.simulateFun` draws `u <- rnorm(ncol(U) * nsim)` for every random-effects column and then new residuals. So every term gets new draws. Two simulated responses correlated -0.02 with each other and 0.005 with `fitted(m0)`.
- **refit().** `refit(m1, newresp = ...)` reuses `m1`'s X and Z, so the carrier fixed effect and covariates stay in. It keeps REML (`mkRespMod(..., REML = object@resp$REML)`), keeps `calc.derivs = FALSE` (taken from `object@optinfo$derivs`), and starts from `m1`'s theta, as bootMer does.
- **Observed vs null statistic.** Both go through the same `icc()` → `p2_shares(...)$icc1` with the same `nc`. On a check dataset, `m1` with `calc.derivs = FALSE` gave ICC(1) = 0.1406686, identical to the primary path (`p2_fit`, `calc.derivs = TRUE`).
- **p-value.** `p = (1 + #{null ≥ obs}) / (1 + n_ok)` (L29) matches prereg L205. Ties at a boundary zero count as ≥, which is conservative.
- **Seeds.** `SEED = 20261121` is passed by p2_analysis.py L363–364. The gating call refuses an `--n-perm` other than 1000 (L275–276).
- **Failures.** A non-zero exit gives `{"missing": ...}`, so `null_ok` is False and the rule is MISSING (L365, L416–426). The family rule needs ≥ 2 families (L451–452).
- **Reproduction.** I reran two replicates with the current code: null_fc1_nc3 #3 (written 16:45:10, before commit 70c2552 at 16:48:26) and power_icc010 #1. Both reproduce the job files exactly (p = 1 / obs 0, and p = 0.0099 / obs 0.1406686).
- **Calibration numbers.** Recomputed from all 700 job files, they match the summaries and the prereg table exactly. All replicates have status ok and n_failed = 0. The design matches the human's specification: fact = 0 with fc ∈ {1, 0.25}, nc ∈ {3, 2}, ft = e = 1 and 5 of 10 paraphrases. MCSEs are reported, and the power at ICC(1) = 0.10 is reported (fact = 0.185185 → 0.09999991).

| condition | p < 0.01 | p < 0.05 |
|---|---|---|
| null fc1 nc3 | 4/200 = 0.020 (MCSE 0.0099) | 19/200 = 0.095 |
| null fc025 nc3 | 1/200 = 0.005 | 10/200 = 0.050 |
| null fc1 nc2 | 1/200 = 0.005 | 7/200 = 0.035 |
| power icc010 | 46/100 = 0.46 | 84/100 = 0.84 |

## NON-BLOCKING

1. **The primary null condition looks mildly liberal, and the prereg wording understates it.** /home/user/depth-law/reports/pending_frozen_changes/P2_prompt_vs_fact.md L223 says "about 2 SE above the nominal 0.05".
   - At B = 100 the nominal rate for p < 0.05 is 5/101 = 0.0495. Under that, 19/200 has an exact one-sided binomial tail P = 0.005. That is ≈ 3.0 SE using the SE under the null (0.0153), or 2.2 SE using the reported MCSE.
   - The k = 0..4 counts are 4, 3, 2, 3, 7, against an expected ≈ 2 each.
   - Pooled over the three null conditions the rates are 36/600 at p < 0.05 (P = 0.14) and 6/600 at p < 0.01, which is consistent with nominal.
   - Could change the decision: only marginally. A model near p ≈ 0.01 with large fc could pass "fact share > 0" a little more often than 1%. The ≥ 2-family requirement limits this. Under the severity rule it is calibration precision, and the pre-set criterion is met (0.020 ≤ 0.02, at the limit). Suggest stating it as "≈ 3 SE (exact binomial P = 0.005)" and/or adding replicates to the primary condition.
2. **The B = 100 → B = 1000 claims are not right as stated.**
   - L224 says power at B = 1000 "can only be equal or higher". That is false in general. If the observed statistic's tail probability under the null is q = 0.015, B = 100 rejects with probability 0.22 and B = 1000 with 0.07. At q = 0.02 the figures are 0.13 and 0.005. B = 1000 is higher only for q below ~0.01 (q = 0.005: 0.61 vs 0.97).
   - L212 says "a Monte Carlo p-value keeps its level at any B". That holds only if the reference distribution is exact. The parametric bootstrap plugs in estimated nuisance variances, and item 1 suggests extra mass at small q. So the calibrated size at B = 100 does not carry over exactly to B = 1000; the size at B = 1000 could sit a little above or below.
   - Could change the decision: only via item 1's mild liberalness. Fix the wording.
3. **Failed refits are dropped with no threshold.** p2_null_fns.R L25 and L29; prereg L205 and L336.
   - The Limitations text says only that p = 1 when all refits fail (conservative).
   - Partial failures that cluster among high-ICC null draws would shrink the numerator and make p liberal. This is not mentioned.
   - None occurred in calibration (n_failed = 0 everywhere).
   - Could change the decision: only if many refits fail on the real data. `n_failed` is reported.
4. **Shared RNG stream in the calibration.** /home/user/depth-law/analysis/p2/p2_null_calib.R L28 uses `seed = base + i` both for `sim(base + i)` and as the `simulate()` seed.
   - In about half the replicates the data's normal draws reappear in the simulate stream, shifted. For seed 7000002, all 3900 fc/ft draws reappear from position 1053, landing in other roles in null datasets 1–2.
   - The overlap does not track rejection: null_fc1_nc3 had 1/100 rejections with overlap vs 3/100 without, and power had 24/49 vs 22/51.
   - Hygiene only. Use a different seed offset for `simulate`. It does not affect the real analysis.
5. **The calibration departs slightly from the frozen procedure.**
   - It fits with no covariates (p2_null_calib.R L28, `character(0)`), while the analysis uses 4.
   - Its header (L7–9, L13) still describes defaults of nsim = 200 and "B = 200 … k ≤ 1", but the runs used nsim = 100 (p2_null_calib_run.sh L12–15). The prereg correctly says B = 100.
   - Power is estimated at B = 100 with 100 replicates (MCSE 0.05).
6. **Stale text in the analysis driver.** /home/user/depth-law/analysis/p2/p2_analysis.py L18 (module docstring) and L392 (`decide` docstring) still say "shuffled-fact null". The CLI argument is still named `--n-perm` (L263), and p2_null.R L5 says so. Wording only.
7. **Latent `(1|subject)` mismatch.** If `subject = TRUE`, the null model would keep `(1|subject)` (p2_model.R L28), while the statistic counts subject inside f (p2_shares, p2_model.R L54). The null would then not be f = 0. This cannot happen in P2 because all 300 subjects are distinct and `subj` is FALSE (p2_null.R L15), so it cannot change the decision. Consider a guard or a comment.
8. **The observed statistic is recomputed, not read from the primary fit.** p2_null_fns.R L16 and L19 recompute it from a fresh `lmer` rather than reading the primary fit's JSON, while prereg L204 says "the primary fit's ICC(1)". I checked they are numerically identical (calc.derivs does not change estimates). There is no cross-check in the code. Cosmetic.

VERDICT: PASS
