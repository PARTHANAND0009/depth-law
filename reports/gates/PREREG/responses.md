# PREREG gate: responses (2026-11-22 to 2026-11-23; rounds 1–3)

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

## Applied after the human's decision of 2026-11-22 ("GO with recommendations" on 1, 2, 4, 5, 10, 11)

| # | where | what was done |
|---|---|---|
| 1 | `p2_analysis.py` (`mom_cells`, `decide`), `p2_mom.py` docstring, prereg §4 and §5 | y is residualised by OLS on the 4 covariates and the carrier fixed effect before carrier-averaging. MoM is a direction check on diff: H1 needs MoM diff > 0; H1-alt needs MoM diff < 0 (was MoM ICC(1) ≥ 0.5). The change is disclosed in §5 as made before freezing, after round 1. |
| 2 | `p2_model.R` (`carrier = TRUE` from the analysis), `p2_analysis.R`, `p2_null.R`, prereg §4 | `carrier` fixed effect added. Its default stays off in `p2_model.R` so the finished CI simulations remain reproducible. |
| 3 | `run_p2.py`, `p2_analysis.py` (`completeness`), `scripts/p2_done_check.py`, `p2_gpu_run.sh`, prereg §1 | A resume sets any earlier `manifest.json` aside. The `done` event records n_facts, and all_ok also requires the manifest to cover every chunk. Analysis completeness rule as in §1. The driver done-check exits 1 on a shortfall and writes a deviation. |
| 4 | `p2_analysis.py` (`decide`), prereg §5–6 | Claims count families (Pythia counts as one). Conflict rule implemented. MoM agreement is limited to H1 and H1-alt. |
| 5 | `p2_null.R` (new), `p2_analysis.py` (`--set correct`, `--n-perm 1000`; sets `nomanufacturer`, `tcov`, `lofo`, `h4`), prereg §3–5, §7 | Null implemented as recommended; p < 0.01 rule kept (human). All preregistered sensitivities and H4 are implemented and frozen. |
| 6 | prereg §4 | CI paragraph now lists the simulation simplifications. Robustness simulation preregistered as non-selecting (human approval); its code is written before it runs, and it runs only when no other heavy job runs. |
| 7–9 | prereg §4 | One-sided misses (recomputed), pooled 0.928, v1 MCSE 0.041 and 100 replicates, 500 vs 1000 resamples, calc.derivs, two-chances sentence. |
| 10 | `p2_analysis.R`, `p2_analysis.py`, prereg §4 | Failures counted per column. More than 5% failed refits in icc1 or diff → fit MISSING → that model's hypotheses MISSING. Boundary estimates accepted; warnings reported only. |
| 11 | `p2_analysis.py`, prereg §3 | Minimum-data rule (≥ 150 facts with ≥ 2 correct paraphrases, ≥ 15 relations), else MISSING (insufficient data) for every set. MNAR caveat added. |
| 12 | prereg §4, §6 | Per-rule measure, residual, point-or-CI and undefined-n′ handling stated. |
| 13–14 | `p2_gpu_run.sh`, prereg §1 | Per-model rule described. Deviation files for every skip, Llama access failure, crash or failed done-check. `sync_meta` after each deviation, the pilot projection and each model, and in the budget hard-stop. A crash of `run_p2` no longer ends the session under `set -e`. |
| 15 | `p2_analysis.py` (`--nc`, n_carriers_used/available), prereg §3, §7 | Confirmatory call gets every run; sensitivities pass `--nc` and are refused if nc exceeds what every included model has. **Superseded on 2026-11-23** (round-2 finding 4): `--nc` was removed, and sensitivities use `--primary`. |
| 16 | `p2_model.R` header, prereg §4 | Comment corrected; "frames like these" sentence. |
| 17 | prereg §4 | ICC(1) is conditional on the covariates and not comparable with the G1 values. |
| 18 | `p2_analysis.py` (`depths`), prereg §2 | D1/D4 undefined when p_final = 0, with the count reported; censored D2/D3 dropped (stated). |
| 19 | `p2_analysis.py` (`g_at`, kbar), prereg §5 | H3 uses G(k̄); marked approximate. |
| 20 | prereg §4 | No further correction, with the reason stated. |

## stats-reviewer, round 2 (REVISE: 7 should-fix, 8 notes, 0 blocking) — stopped for the human

File: `stats-reviewer_round2.md`. I checked findings 1 and 2 directly:
- rsync to a missing parent directory exits 11 (rsync 3.2.7);
- `decide()` runs before `p2_results.json` is written and reads `fits["D1"]["vc"]` unguarded.

**Choices for the human** (recommendation first):

| # | issue | recommendation |
|---|---|---|
| 3 | A D1 or D4 fit failure removes the whole model; the prereg says only the affected hypotheses | Evaluate each rule on the fits it uses. D1-only rules ("no fixed layer", null) need only the D1 fit. H1/H1-alt need the D1 and D4 fits and both MoM estimates. A MoM failure makes H1/H1-alt MISSING for that model, not False. |
| 4 | nc computed over the wrong models; two rules in the prereg | nc = minimum over models that pass **both** completeness and minimum data, stated once in §1 and §3; the minimum-data check moves before nc. Sensitivity calls read nc and `--runs` from the confirmatory `p2_results.json` and refuse any mismatch. |
| 6 | Which run when a model has several; deviation files overwritten | Per model, the first run that passes completeness is analysed. A later run replaces it only through a committed deviation naming the run_id it replaces. Duplicate model keys are refused. Deviation file names get the session's UTC timestamp (`D-P2-<utc>-<n>.md`), so nothing is overwritten. |

**Fixes without new decisions:**
- **1:** write `p2_results.json` before `decide`; skip H3 pairs whose D1 fit is not ok and record them MISSING; add an e2e case with a forced fit error in the correct set.
- **2:** sync with `--mkpath`; log the result of each sync; add a dry run with a local `SYNC_DEST`.
- **5:**
  - state the MoM diff estimand, REML diff + (e − fc)/(nc·den), and its asymmetry in §4;
  - list H1's three changes from this batch (residualised MoM input, carrier fixed effect, ≥ 2 families) instead of "H1 unchanged";
  - extend the MoM self-test with fc, a carrier shift and a covariate.
- **7:** one completeness rule. `p2_done_check.py` calls the analysis `completeness()`, which also gains the NaN check.

**Notes (all to be applied):**
- N1: fail on an unknown family; state the within-family split.
- N2: exact multiple-comparisons wording.
- N3: carrier fixed effect in the two-way path.
- N4: rule that more than 5% failed permutations makes the null MISSING; `as.numeric`; a calc.derivs line in the prereg.
- N5: sensitivity decision files marked `"gating": false`.
- N6: state the carrier and CI-selection point as an assumption; the robustness simulation fits the frozen formula; a non-gating `(1|relation:carrier)` check (optional; the human's choice).
- N7: report the count of curves with p_final < 1e-4.
- N8:
  - git dirty flag and a materials-hash check against §1 in the driver (and in the analysis);
  - `depthlaw.depth.causal` and `depthlaw.depth.common` added to the frozen list;
  - dry runs extended to two models, a crash and SYNC_DEST.

### Applied after the human's decision of 2026-11-23

The human's message numbered the three choices 1, 2 and 3. They are round-2 findings 3, 4 and 6, and the descriptions in the message match those findings. The decision was "GO with recommendations", plus the four definite fixes.

| round-2 # | where | what was done |
|---|---|---|
| 1 fit error crashed `decide` | `p2_analysis.py` | `p2_results.json` is written before `decide`. H3 skips pairs with a MISSING D1 fit and records them. Tested with forced fit failures (in-process, `rfit` patched). |
| 2 sync never succeeded | `p2_gpu_run.sh` | `rsync --mkpath` into `SYNC_DEST/_session_<UTC>/`. Each sync's result is logged, including failures. Dry run with a local nested `SYNC_DEST`. |
| 3 (decision) per-rule fit dependency | `p2_analysis.py` `decide`, prereg §4 table | Each rule is evaluated on its own inputs; MISSING inputs make that rule MISSING (None) for that model only. A MoM failure makes H1/H1-alt MISSING, not False. `rules_missing` is listed per model. |
| 4 (decision) nc | `p2_analysis.py`, prereg §1, §3, §7 | Minimum data is computed from the behaviour rows before nc. nc = minimum over models that pass completeness and minimum data. Sensitivities use `--primary`, which reuses nc and requires the same `--runs`. `--nc` was removed. |
| 5 MoM text, H1 changes | prereg §4, §5; `analysis/p2/p2_test_mom.py` | The MoM diff estimand and its asymmetry are stated. The H1 and H1-alt changes are listed. A carrier-level MoM test was added (200 replicates; the 20-replicate first run failed on frame variance, −0.23, Monte Carlo noise; both runs are in the ledger). |
| 6 (decision) one run per model, deviation overwrite | `p2_analysis.py`, `p2_gpu_run.sh`, prereg §1 | First complete run per model, replaced only through a committed deviation naming the run_id. Duplicate model keys are refused. Deviation files are named `D-P2-<UTC>-<n>.md` and refuse to overwrite. |
| 7 two completeness checks | `scripts/p2_done_check.py`, `p2_analysis.py` | The done-check calls `completeness()`; NaN check added. |
| N1 | `p2_analysis.py` `family`, prereg §5 | An unknown family is refused; the within-family split is stated. |
| N2 | prereg §4 | Multiple-comparisons wording made exact. |
| N3 | `p2_analysis.R`, `p2_analysis.py` | Only `boot=param` is accepted. The two-way path in `p2_bootsim_fns.R` is left unchanged so the v1 simulation stays reproducible, and it cannot be reached from the analysis. |
| N4 | `p2_null.R`, prereg §4 | Coerced with `vapply`; failed permutations are dropped and counted; calc.derivs line added. No new failure threshold (not decided by the human). |
| N5 | `p2_analysis.py` | `"gating"`: true only for `--set correct`. |
| N6 | prereg §4 | CI-selection-with-carrier-effect stated as an assumption; the robustness simulation fits the frozen formula; relation × carrier noted as a limitation. The `(1|relation:carrier)` check was not added (optional; not decided). |
| N7 | `p2_analysis.py`, prereg §2 | Count of curves with p_final < 1e-4 reported. |
| N8 | `p2_gpu_run.sh`, `p2_analysis.py`, prereg §1, §7 | Dirty flag and prereg-P2 tag logged; materials sha256 checked against §1 (driver FATAL, analysis refuses); Llama access check also under SKIP_ENV; depthlaw dependencies listed in §7; crash, second-model and SYNC_DEST dry run added. Hard-stop path not exercised (DRY arms no timer). |

## stats-reviewer, round 3 (last review; VERDICT: BLOCK; 1 BLOCKING, 16 NON-BLOCKING) — stopped for the human

File: `stats-reviewer_round3.md`. The reviewer's illustration scripts are copied to `results/P2review_round3_scripts/`.

**B1 (BLOCKING): the shuffled-fact null tests fact = 0 *and* fact:carrier = 0, not fact = 0.** Permuting fact labels within relation × paraphrase cells also destroys fact:carrier. With fact = 0 and fc > 0, the observed ICC(1) is more variable than the permutation distribution, so "the fact share is above zero" can pass too often. In the reviewer's illustration, the share of observed values above the permutation 95th percentile was 0.25–0.35 when fc > 0. Options:
- (a) text only: describe the null as fact = fc = 0 and reword the sentence to "a depth component consistent across paraphrases (fact or fact × carrier)";
- (b) code: a parametric null, which refits without (1|fact), simulates 1000 datasets from that fit and refits each, then re-test.

Awaiting the human's choice.

**NON-BLOCKING 1–16:** these go to Limitations or the post-freeze fix list as the reviewer classified them. They will be applied after the human's choice on B1. The wording items (9, 10, 15) and Limitations sentences go into the prereg text before the freeze. The code items (4–8, 11, 16) go on a post-freeze fix list, unless the human wants them before tagging.

## Round 3: human decision of 2026-11-23 and how it was applied

The human chose (b) for B1: a parametric bootstrap null; the p formula, the p < 0.01 threshold and the sentence are unchanged. NON-BLOCKING items are sorted into (i) those that change a number used in a decision column or headline rule (fixed before the freeze, then the synthetic test re-run) and (ii) the rest (post-freeze list). Wording fixes and Limitations go into the prereg.

| round-3 # | group | where | what was done |
|---|---|---|---|
| B1 | — | `p2_null_fns.R` (new), `p2_null.R`, `p2_model.R` (`fact = FALSE`), prereg §4 | Parametric null: the fit without `(1|fact)` (all other terms kept), 1000 `simulate` datasets, the full model refitted with `refit`; ICC(1) null distribution; same p. Calibration and power: `p2_null_calib.R` → `results/P2null_calib/`. A narrow fresh review follows. |
| 2 | (i) | `p2_mom.py`, prereg §4 | MoM diff from raw components; truncated shares reported only. |
| 3 | (i) | `p2_analysis.py` `decide`, prereg §4, §6 | An undefined n′ does not meet the "N paraphrases" rule; the G ceiling fact/(fact + fc/nc) is reported. |
| 4 | (i) | `p2_analysis.py`, prereg §3 | The gating call refuses `--n-boot` or `--n-perm` other than 1000. `--test` is required for synthetic runs and makes the output non-gating. |
| 5 | (i) | `p2_analysis.py` `run_identity`, prereg §1, §3 | Start events must name the model, with dtype float32 and revision main. The five prereg models must be named, with MODEL=none for a model with no run. The same run dir under two keys is refused. |
| 6 | (i) | `p2_analysis.py` `completeness`, prereg §1 | Checksums are recomputed. |
| 7 (stop flag) | (i) | `p2_gpu_run.sh`, prereg §1 | `STOP_P2_<session UTC>`. |
| 13 | (i) | `p2_analysis.py` `subject_tokens_in_context`, prereg §4 | Subject tokens are counted in context. |
| 9, 10, 15 | wording | prereg §1, §9, header; this file | Fixed. |
| 1, 12, 14 | (ii) Limitations | prereg §10 | Recorded. |
| 7 (timer, pilot deviation), 8, 11, 16 | (ii) post-freeze | `analysis/p2/POST_FREEZE_FIXES.md` | Listed. |

## Final narrow review of the new null (2026-11-23): VERDICT PASS, no BLOCKING

File: `stats-reviewer.md` (the final review read by the gate check; rounds 1–3 kept as `stats-reviewer_round*.md`). Steps the human required, all done:
1. **Calibration** (rejection at p < 0.01 ≤ 0.02 with fact = 0 and fc > 0): met. 0.020 (MCSE 0.0099) at fc = 1, nc = 3; 0.005 at fc = 0.25; 0.005 at fc = 1, nc = 2. B = 100 per replicate. The reviewer recomputed all 700 job files.
2. **Power** at a fact share of 0.10: 0.46 at p < 0.01 (MCSE 0.050).
3. **End-to-end:** 50/50 after a test-side fix. The first run was 47/49, kept on file.
4. **Narrow review:** PASS.

| final-review # | handling |
|---|---|
| 1 mild liberalness at p < 0.05 | Prereg §4 and §10 now give the exact binomial P = 0.005 (about 3 SE) and the pooled rates. |
| 2 B = 100 → 1000 claims wrong | Corrected in §4: the level carries over only approximately; power at B = 1000 can be higher or lower. |
| 3 partial refit failures could be liberal | Added to §10; n_failed is reported. |
| 4 shared calibration seed | Post-freeze list; header comment in `p2_null_calib.R`. |
| 5 calibration without covariates; header said B = 200 | Header corrected; §4 says "without covariates"; optional extra calibration on the post-freeze list. |
| 6 stale "shuffled-fact" docstrings | Fixed (comments only); the `--n-perm` rename is on the post-freeze list. |
| 7 latent (1|subject) mismatch | Comment in `p2_null_fns.R`; it cannot arise in P2 (subject = FALSE). |
| 8 observed ICC(1) recomputed | §4 wording made exact; cross-check on the post-freeze list. |

## Next steps (done except the human's steps)
1. Calibration and power of the parametric null: done.
2. The synthetic end-to-end test, re-run after the group (i) fixes: done.
3. A narrow fresh stats-reviewer on the new null only: done, PASS.
4. If the calibration passes (rejection at p < 0.01 ≤ 0.02) and the narrow review has no BLOCKING finding: set the PROGRESS status line that APPLY.sh requires. Then the human runs APPLY.sh, which installs the gate, the reviews and the status line awaiting GO PREREG.
