<!-- stats-reviewer subagent (.claude/agents/stats-reviewer.md), fresh context, 2026-11-22, PREREG gate round 1, on reports/pending_frozen_changes/P2_prompt_vs_fact.md and the material listed in its brief (at 3b4736f). Saved verbatim by the main session; not edited. Staged here for APPLY.sh (the deny rule Edit(prereg/**) also blocks reports/gates/PREREG/). Answers: responses.md. -->
Scope note: the brief opened with a different instruction, to compare results/*_gate.md with prereg/HR_revised.md. I did not do that comparison. This review covers only the P2 PREREG gate described in the rest of the brief. I edited no files.

Staged prereg: /home/user/depth-law/reports/pending_frozen_changes/P2_prompt_vs_fact.md, cited as "prereg" with its line numbers.

**1. [blocking] The MoM sensitivity estimates a different quantity from the prereg's ICC(1) and diff, but it gates both H1 and H1-alt.**
- The prereg defines ICC(1) as fact/den, with den = fact + rt + frame + ft + fc/nc + e/nc (prereg L72–76).
- `p2_mom.py` works on carrier-averaged cell means (L4–8, L57–59). On that scale fc/nc goes into "fact" and ft + e/nc goes into "residual". So:
  - MoM ICC1 = (fact + fc/nc)/den;
  - MoM wording = (frame + rt + ft + e/nc)/den.
- MoM also has no covariates. REML's fact variance is net of n_answer_tokens, n_subject_tokens, log_cooc_proxy and answer_prior; MoM's is not.
- Effect: MoM ICC1 is systematically higher than REML ICC1. This makes the "MoM ICC(1) ≥ 0.5" condition for H1-alt easier and the "MoM diff > 0" condition for H1 harder (`p2_analysis.py` L143–145).
- The MoM self-test (`p2_mom.py` L62–81) has no fc term and no covariates, so it cannot catch this.
- **Fix:** either
  - run MoM on carrier-level rows with fact:template and fact:carrier terms, and on covariate-residualised y; or
  - state in prereg §4–5 exactly what MoM estimates, and recast the MoM conditions as a direction check only, not the 0.5 threshold.

**2. [blocking] The model has no carrier main effect.**
- `p2_formula` (`p2_model.R` L22) has `(1|fc)` but no carrier term.
- Any systematic difference between carriers is therefore absorbed into fact:carrier variance. For example, "A word that goes with X is" could resolve later than "X is associated with".
- That variance then enters den as fc/nc (`p2_model.R` L47) and lowers ICC(1) and wording by the same factor. On the carrier-averaged scale a carrier main effect is a constant and should not be in den at all.
- Illustration (assumed values, not from data): a mean shift of 0.1 between carriers is a variance of about 0.003, which is about the size of the simulated fact variance (0.0027). A shift that size could move ICC(1) across the 0.5 / 0.4 thresholds of H1-alt.
- It also changes between models depending on whether fallback 1 drops carrier 2.
- **Fix:** add `carrier` as a fixed effect (2–3 levels) to the frozen formula (prereg L63) and to the simulation model.

**3. [blocking] A partly run model can be analysed as if it were complete; MISSING is not enforced.**
- `run_p2.py` writes `manifest.json` only after its chunk loop finishes (L123–128).
- The pilot run (20 facts) writes a `manifest.json` listing 2 chunks. The full Qwen run then resumes the same run dir (`p2_gpu_run.sh` L122).
- If the hard stop hits mid-Qwen, the pilot's manifest stays, and all its entries are "ok".
- `load_model` (`p2_analysis.py` L61–66) checks only the chunks listed in that manifest, then reads every `c*.parquet` present. A model with, say, 150 of 300 facts enters the confirmatory analysis silently.
- The driver's done-check (L126–132) prints counts but never fails.
- This contradicts prereg L42 ("reported as MISSING (incomplete)").
- **Fix:**
  - `load_model` should require 300 facts × 10 templates × nc behaviour/long rows, all 30 chunk checksums and a `"done"` log event; otherwise mark the model MISSING and exclude it.
  - `run_p2` should rewrite or invalidate `manifest.json` at the start of a resume.

**4. [blocking] The multi-model claim rules are undefined in ways that would have to be settled after seeing data.**
- (a) "≥ 2 models" can be met by pythia-1.4b + pythia-2.8b alone: same family, data and tokenizer. `fam` is computed in `p2_analysis.py` L102 but never used (L165–171). Under fallback 2 or per-model skips, the claim may rest on the Pythia pair. State whether the two Pythia models count as 2 models; I recommend requiring ≥ 2 families.
- (b) With 5 models, H1 can hold in 2 models and H1-alt in 2 others. That allows both the "wording" and the "fact" headline sentences at once (prereg L111–113; code L167, L171). Add a rule for this case, e.g.:
  - a majority of completed models; or
  - H1 in ≥ 2 models and H1-alt in none; or
  - otherwise report per-model shares only.
- (c) "A claim holds only if REML and MoM agree in direction" (prereg L83):
  - "direction" is undefined for ICC(1), which is never negative;
  - the code applies MoM only to H1 and H1-alt, not to the "no fixed layer", "N paraphrases" or "wording shifts together" claims.
  Define "direction" for each claim, or limit the rule to H1 and H1-alt.

**5. [blocking] The shuffled-fact null is preregistered with an acceptance rule (p < 0.01, prereg L92) but has no frozen code and no defined test statistic.**
- Undefined:
  - the test statistic (REML ICC1? MoM? D1 and/or D4?);
  - whether a fact's carrier rows move together when fact IDs are permuted;
  - which claims this null gates.
- Grep shows no permutation code in `analysis/p2/`.
- The other preregistered sensitivities also have no frozen code: leave-one-frame-out, `manufacturer` dropped, the template-covariate sensitivity model, and the H4 fit. `p2_analysis.py` implements only correct / all10 / all / new226.
- Prereg §7 says the code is frozen with the file.
- **Fix:** implement and freeze all of these, and specify the null's statistic, permutation unit and role. Otherwise state that they will be written after the data and are not confirmatory.

**6. [should-fix] The simulated conditions do not represent the design; the claim "on this exact design" (prereg L84) overstates them.**
- `p2_simulate` (`p2_model.R` L61–81) generates:
  - continuous, unbounded Gaussian y;
  - 50% MCAR cell loss;
  - nc = 3 only;
  - no covariates and no carrier effect.
- The real data differ:
  - D1 is a discrete grid of (l*+1)/L with L = 24–36, bounded and probably skewed;
  - inclusion is correct cells, so missingness is related to the outcome (MNAR), and accuracy for pythia-1.4b may be far below 50%;
  - fallback 1 gives nc = 2, which was never simulated.
- Both true values sit far from the decision boundaries: ICC 0.372 / 0.709 and diff 0.206 / −0.461. Coverage near ICC ≈ 0.4–0.5 and diff ≈ 0 is untested.
- A parametric bootstrap tested on data from its own model mostly checks the implementation.
- **Fix:** do not re-select (that would be a third look). Instead:
  - reword L84 ("Gaussian, MCAR, nc = 3, no covariates");
  - list these limits in the caveat (L91);
  - preregister a non-selecting robustness simulation (discretised D1, correctness-linked missingness, nc = 2, true values at the boundaries) to be reported alongside the results.

**7. [note] Choosing 95% with coverage 0.925 is defensible but should be disclosed more fully.**
- Keeping 95% follows the pre-committed v2 rule (`bootsim_v2_plan.md` L37). Switching to 97.5% now would be a further data-dependent choice.
- However, 0.925 with MCSE 0.024 does not establish coverage ≥ 0.90: about 1.96 SE below the point estimate is about 0.88.
- The decision-relevant errors are one-sided. I computed them from `results/P2sim_v2/p2_bootsim_v2.json` at 95%:
  - ICC1, truth below the lower bound (the error that matters for H1-alt): 4/120 in edepthvar_like and 5/120 in fact_dominant, against a nominal 3/120.
  - diff, truth below the lower bound (the error that matters for H1): 1/120 and 3/120.
- **Fix:** add the one-sided miss rates to the prereg. Also add the pooled v1 + v2 parametric diff coverage for edepthvar_like, (53 + 114)/180 = 0.928. Note that v1 used 100 replicates, which by itself adds Monte Carlo noise to the percentile endpoints.
- Minor: prereg L86 gives MCSE 0.039, which is the value for c = 0.90. For 0.883 with N = 60 it is about 0.041.

**8. [note] Second-look disclosure (prereg L85–91, ledger entries 54/57, plan committed in 875ba33 before launch) is adequate.**
- It names the near-miss, the new seeds and the pre-fixed 95% → 97.5% → STOP rule.
- Add one sentence: the second look gave two chances to pass (95% and 97.5%), and v1 had preferred the two-way bootstrap, which failed.

**9. [note] 500 resamples in the simulation versus 1000 in the analysis is not a problem.**
- More resamples only reduce Monte Carlo error in the endpoints.
- The simulation fits with `calc.derivs = FALSE` (`p2_bootsim_v2.R` L18) and the analysis with TRUE. This changes only the warnings, not the estimates. Both points can be stated in one line.

**10. [should-fix] There is no rule for singular fits, convergence warnings or failed bootstrap refits.**
- `p2_analysis.R` L29 takes quantiles with `na.rm = TRUE`. L34 counts failures only in column 1.
- A singular fit is likely, e.g. frame variance 0 with 10 frames.
- **Fix:** prespecify:
  - whether boundary (zero) estimates are accepted;
  - the maximum fraction of failed refits (e.g. > 5% → that fit is MISSING);
  - what a convergence warning does to H1 / H1-alt.

**11. [should-fix] There is no minimum amount of data for a model to enter the confirmatory analysis.**
- Inclusion is correct cells only. A weak model may leave whole relations empty, or many facts with one correct paraphrase. A single correct paraphrase gives no information to separate fact from fact × template.
- **Fix:** add a threshold (e.g. ≥ X facts with ≥ 2 correct paraphrases and ≥ Y relations), below which the model is reported as MISSING (insufficient data).
- Also state that selecting on correctness can bias the components (MNAR); the all-cells and all-10 sensitivities partly address this.

**12. [should-fix] The headline rules leave measure and residual definitions open.**
- "No fixed layer" (`p2_analysis.py` L149), "N paraphrases" (L150, L169) and "wording shifts together" (L151, L170) use D1 only. Prereg L110–112 does not say which measure applies.
- When n′ is undefined (G(k) < 0.8 for all k ≤ 30), the code sets it to 31 and counts it as n′ ≥ 8 (L169; `p2_analysis.R` L19). This is not stated in the prereg.
- "Template + frame share exceeds the fact×template residual" (prereg L112): the code compares rt + frame with ft + e/nc (`p2_model.R` L54), i.e. the combined residual, not ft alone. It uses point estimates only.
- **Fix:** state in the prereg, for each rule:
  - the measure(s);
  - the residual definition;
  - point estimate or CI;
  - the handling of undefined n′.

**13. [should-fix] Driver fallbacks go beyond the prereg text.**
- After the pilot, the projection uses the measured rate. The per-model checks use static upper estimates instead (`p2_gpu_run.sh` L58–59, L110–119).
- The per-model "fallback 2" can skip any model, e.g. OLMo or a Pythia model. Prereg L40 allows dropping only Llama-3.1-8B.
- `PROJ_NOLLAMA2` is computed but never tested (L96–105).
- A failed Llama download or access check gives only a WARNING (L44–45), then "FATAL ... continue" (L125), with no deviation file written.
- Bias risk is low, because these choices depend on budget, not results. But they interact with finding 4(a): late models are the ones dropped.
- **Fix:** describe the per-model rule and the skip-any-model behaviour in prereg §1, and write a deviation file for every skipped or failed model.

**14. [should-fix] Deviation records and the session log are not synced off the rented instance.**
- `rsync` copies only `$RD/` (L133), and only after a model finishes.
- `deviations_pending/` and `results/logs/p2_gpu_run_*.log` stay on the instance. The hard stop runs `shutdown -h` (L33), so they can be lost. These files are the evidence that each deviation was written before its step.
- **Fix:** rsync `deviations_pending/` and the log right after each `dev()` call and after the pilot projection.

**15. [should-fix] The set of runs passed to the analysis changes the number of carriers used.**
- `carriers_everywhere` (`p2_analysis.py` L52–58) takes the minimum carrier count over the runs passed in one call. Leaving out the model that ran with 2 carriers gives nc = 3, so the same model's ICC(1) changes with the call.
- **Fix:** state in the prereg that the confirmatory call includes every completed (non-MISSING) model, and that nc is fixed by that call for all sensitivities.

**16. [note] Identifiability and the random factors.**
- With ≥ 2 templates and ≥ 2 carriers per fact, the components are identifiable:
  - relation:frame (200 levels) is identified because frames are crossed with relations;
  - fact:template is separated from the residual by the carriers;
  - fact:carrier is separated from the residual by the templates.
- With nc = 2, the fact:carrier versus residual split rests on fewer degrees of freedom.
- Treating the 10 frames as random is an interpretive choice:
  - they are a 2×2×2 factorial plus two lexical variants of frames 0 and 2 (`materials/paraphrases_v1.jsonl`), not exchangeable draws;
  - the frame variance has 9 df;
  - the wording share should be described as generalising to "frames like these".
- The `p2_model.R` header (L8–14) still lists `(1|subject)` and f = fact + subject. Correct the comment. The code drops the subject term automatically (`p2_analysis.R` L14).

**17. [note] Covariates make ICC(1) conditional.**
- REML ICC(1) is net of frequency, length and answer prior, but the G1 values disclosed in prereg §0 (0.37–0.64) may not be.
- State this in §4, so that H1-alt (≥ 0.5) is not read against unconditional G1 values.

**18. [note] D2/D3 and the all-cells sensitivity.**
- Censored D2/D3 rows become NA and are dropped (`p2_analysis.R` L10), not modelled as censored. State this.
- p is stored as float16 (`run_p2.py` L113). In the all-cells sensitivity, an incorrect cell whose final p underflows to 0 gets D1 = 1/L, because every layer passes p ≥ 0 (`p2_analysis.py` L46), and D4 = None. Exclude p_final = 0, or store log-probabilities.

**19. [note] H3 disattenuation is approximate.**
- It uses G(10) (`p2_analysis.py` L161), but correct-set fact means average fewer than 10 paraphrases, so reliability is overstated and the correction is too small.
- Spearman disattenuation by G is itself approximate. Estimation only; state this.

**20. [note] Multiple comparisons are not discussed.**
- The prereg is silent. The conjunction rules (D1 and D4, REML and MoM, ≥ 2 models) are intersection-union tests and are conservative.
- Rough estimate (my calculation, assuming independence): the chance of ≥ 2 false one-sided passes in 5 models at α = 0.025 is about 0.006.
- State explicitly that no further correction is applied, and why.

Checked and matching the prereg:
- D1–D4 formulas (`p2_analysis.py` L35–49);
- 0.025 / 0.975 quantiles;
- the thresholds and CI sides for H1 and H1-alt;
- the subject term dropped when subjects are unique;
- fallback-1 carrier restriction to 0–1, including answer_prior (L73–76);
- the bands as description only;
- `relation:template` equal to relation × frame (frames are shared, `materials/paraphrases_v1.jsonl`);
- seed 20261121.

VERDICT: REVISE
