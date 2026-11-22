# PREREG gate: responses (2026-11-22)

**Reviews (fresh subagents, saved verbatim in this directory):**

| review | file | verdict |
|---|---|---|
| citation-verifier, round 1 | citation-verifier_round1.md | REVISE |
| citation-verifier, round 2 | citation-verifier.md | PASS |
| stats-reviewer, round 1 | stats-reviewer_round1.md | **REVISE (5 blocking)** |

**Status.** The prereg is **not ready to freeze.** Six stats-reviewer items change a hypothesis condition, the model formula or a decision rule. Those choices are the human's (marked **DECIDE** below). The other items are fixes that change no hypothesis or threshold (marked **FIX**). They are not applied yet: they will be applied in one batch with the decisions, then re-tested and reviewed again by a fresh stats-reviewer (round 2). APPLY.sh refuses to run until the status line in PROGRESS.md says the prereg is ready.

Why these reviews are staged here: the deny rule `Edit(prereg/**)` also matches `reports/gates/PREREG/`, so Claude cannot write there. APPLY.sh copies these files there unchanged.

## citation-verifier

| # | finding | response |
|---|---|---|
| R1-1 | related_work.tex L8 (Elhelo) PARTIAL | FIXED: replaced with the reviewer's suggested sentence (commit 3b4736f). |
| R1-2 | Section 8: "does not predict"; Meng et al. not verifiable | FIXED: now "does not reliably predict". The Meng et al. mention was dropped rather than adding an unverified id. |
| R1-3 | "None of these..." is an unverifiable universal negative | FIXED: hedged with "To our knowledge" in both files, naming Elhelo and Agarwal as the closest adjacent work. |
| R1 note | Agarwal / Elhelo arXiv-id ordering oddities | Noted. Round 2 checked the ids against the arXiv API: they match. |
| R2 | PASS, no required fixes | — |
| R2 note | Section 8 heading "Measures" lists non-measure papers | FIXED: renamed "Prior work on where and how facts are processed" (label only; commit 8a6d4fc). |
| R2 note | Agarwal "causally active" vs "generation-controlling" | Accepted as is; the reviewer judged it acceptable. |

## stats-reviewer, round 1

The reviewer's scope note says its agent brief opens with a default instruction about the H-R comparison, which it skipped. No action needed: the P2 brief defined the scope.

I checked its main factual claims in the code:
- `p2_formula` has no carrier term;
- `manifest.json` is written only after the chunk loop (`run_p2.py` L123–129);
- there is no permutation code in `analysis/p2/`.

All three are confirmed.

### DECIDE (human): items that change a hypothesis condition, the formula or a decision rule

**1. MoM estimates a different quantity.** Recommended:
- residualise y on the same four covariates (OLS) before the Henderson III MoM;
- state in §4 that MoM fact = fact + fc/nc on the carrier-averaged scale;
- make the MoM condition a **direction check only**:
  - H1 needs MoM diff > 0 (as now);
  - H1-alt needs MoM diff < 0, replacing MoM ICC(1) ≥ 0.5.

This changes the MoM part of H1-alt. H1 and H1-alt were declared unchanged on 2026-11-22, so this is your call. The alternative (MoM on carrier-level rows with ft and fc terms) needs a new Henderson III derivation and self-test, which carries more risk.

**2. No carrier main effect.** Recommended: add `carrier` as a fixed effect (2–3 levels) to the frozen formula.
- Fixed effects do not enter the shares, so the v2 CI-method selection still applies.
- The robustness simulation (item 6) would include a carrier shift.
- It changes the formula accepted on 2026-11-22.

**4. Multi-model claim rules.** Recommended:
- (a) "≥ 2 models" means ≥ 2 models from ≥ 2 families. Pythia-1.4b and 2.8b count as one family.
- (b) If H1 and H1-alt each meet (a), neither headline sentence is used. The result is reported as model-dependent, with per-model shares.
- (c) Limit "REML and MoM agree in direction" to H1 and H1-alt, defined as in item 1.

**5. The shuffled-fact null and other preregistered sensitivities have no frozen code.** Recommended: implement and freeze all of them before APPLY.sh.
- **Shuffled-fact null:**
  - statistic: REML ICC(1) of D1 (correct set);
  - permutation: fact labels shuffled within each relation × paraphrase cell, with a fact's carrier rows moving together;
  - 1000 permutations; p = (1 + #{perm ≥ observed}) / 1001;
  - it gates only the sentence "fact share > 0".
- **Leave-one-frame-out, `manufacturer` dropped, the template-covariate model, H4:** code to be written now.
- Cost: about 1000 REML fits per model. The synthetic test fitted 8 models plus 20 resamples in 59 s, so this is CPU-hours after the GPU session, not GPU time.
- Alternative: declare these EXPLORATORY and written after the data, and drop the p < 0.01 rule.

**10. Singular fits, convergence warnings, failed refits.** Recommended:
- boundary (zero) variance estimates are accepted and reported;
- a fit with > 5% failed bootstrap refits in any decision column is MISSING (counted per column, not only in column 1);
- convergence warnings are reported and do not change H1 / H1-alt unless the fit itself failed.

**11. Minimum data for a model to enter.** Recommended: a model enters the confirmatory analysis only if, in the correct set, it has:
- ≥ 150 of 300 facts with ≥ 2 correct paraphrases; and
- ≥ 15 of the 20 relations (15 facts each).

Otherwise it is MISSING (insufficient data). The MNAR caveat goes in §4: the all-cells and all-10 sensitivities partly address it.

### FIX: no hypothesis or threshold changes (to be applied with the decisions above)

| # | finding | fix |
|---|---|---|
| 3 | Partly run model analysed as complete | `load_model` requires 300 × 10 behaviour rows, 300 × 10 × nc long rows per carrier set, 30 chunk checksums and a "done" event; otherwise the model is MISSING (incomplete). `run_p2` deletes `manifest.json` when a resume starts. The driver's done-check exits non-zero on a shortfall. Implements prereg L42. |
| 6 | Simulation design wording | Reword the CI paragraph: "Gaussian, MCAR 50%, nc = 3, no covariates or carrier effect"; list the limits in the caveat. No re-selection. **Pending your OK:** a preregistered non-selecting robustness simulation (discretised D1, correctness-linked missingness, nc = 2, truths near ICC 0.4–0.5 and diff ≈ 0, a carrier shift), reported next to the results. |
| 7 | One-sided miss rates; pooled coverage; MCSE typo | Add to the prereg: ICC1 truth below the lower bound 4/120 and 5/120; diff truth below the lower bound 1/120 and 3/120. I recomputed these from `results/P2sim_v2/p2_bootsim_v2.json` and they match. The upper-side misses are ICC1 1 and 4, diff 5 and 5. pooled v1 + v2 parametric diff coverage for edepthvar_like 167/180 = 0.928; v1 used 100 replicates. Correct the v1 MCSE to sqrt(0.883 × 0.117 / 60) = 0.041. |
| 8 | Second-look disclosure | Add a sentence: v2 gave two chances to pass (95%, 97.5%), and v1 had preferred the two-way bootstrap, which failed. |
| 9 | 500 vs 1000 resamples; calc.derivs | Add a line stating both points. |
| 12 | Headline rules: measure, residual, CI, undefined n′ | State per rule what the code does: D1 only; "residual" = ft + e/nc; point estimates; n′ undefined (G(k) < 0.8 for all k ≤ 30) is coded 31 and counts as ≥ 8. If you would rather require D1 and D4 for these rules, say so (that would be a DECIDE). |
| 13 | Driver fallbacks beyond the prereg | Describe the per-model rule (static upper estimates; any model may be skipped if it does not fit) in §1. Write a deviation file for every skipped or failed model, including a failed Llama access check. Remove the unused `PROJ_NOLLAMA2`, or use it for the fallback-2 test. |
| 14 | Deviations and log not synced | rsync `deviations_pending/` and the session log right after each deviation, after the pilot projection, and after each model. |
| 15 | nc depends on the runs passed | State in the prereg: the confirmatory call includes every non-MISSING model, and its nc is used for all sensitivities. The code will record and assert it. |
| 16 | Frames as random; stale comment | Add the "frames like these" generalisation sentence. Correct the `p2_model.R` header (subject term). |
| 17 | ICC(1) is conditional on covariates | State in §4 that it is not directly comparable with G1's unconditional 0.37–0.64. |
| 18 | Censored D2/D3; float16 underflow | State that censored D2/D3 rows are dropped. In the all-cells set, exclude rows with p_final = 0 (count reported). |
| 19 | H3 disattenuation approximate | State that G(10) overstates reliability for correct-set means, and that it is used for estimation only. Use G(k̄) with k̄ = the mean number of correct paraphrases. |
| 20 | Multiple comparisons | State that no further correction is applied, because the conjunction rules are intersection-union tests. |

## Next steps after your decisions

1. Apply the decisions and all FIX items. This changes the prereg text, `p2_analysis.py/.R`, `p2_mom.py`, `p2_model.R`, `run_p2.py`, `p2_gpu_run.sh`, and new sensitivity/null code.
2. Re-run the synthetic test, extended to cover a partly run model (MISSING), an insufficient-data model, the null and the sensitivities. Re-run both dry runs.
3. Run a fresh stats-reviewer, round 2 → `stats-reviewer.md`.
4. Set the PROGRESS status line that APPLY.sh requires. Then you run APPLY.sh and reply GO PREREG.
