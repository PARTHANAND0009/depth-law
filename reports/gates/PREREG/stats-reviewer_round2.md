<!-- stats-reviewer subagent (.claude/agents/stats-reviewer.md), fresh context, 2026-11-22, PREREG gate round 2, on reports/pending_frozen_changes/P2_prompt_vs_fact.md and the code to be frozen (at 7050a73). Saved verbatim by the main session; not edited. Staged here for APPLY.sh (the deny rule Edit(prereg/**) also blocks reports/gates/PREREG/). Answers: responses.md. -->
Scope note: my launch instructions began with a default task, comparing results/*_gate.md with prereg/HR_revised.md. The brief said to ignore it, and I did. This review covers only the staged P2 prereg and the code to be frozen with it. I edited no repo files. Scratch tests were run only in /tmp/claude-0/-home-user-depth-law/79d106ca-74b7-5e19-8ef3-6880f992c1ff/scratchpad/rv/.

"Prereg" means /home/user/depth-law/reports/pending_frozen_changes/P2_prompt_vs_fact.md, cited by its line numbers. Code was reviewed at HEAD 7050a73 with a clean working tree. The hashes of p2_analysis.py/.R, p2_null.R, p2_model.R and run_p2.py match the inputs recorded in the ledger for the e2e v2 test and for the second pair of dry runs.

## A. Status of the round-1 findings

| # | status | evidence / remaining gap |
|---|---|---|
| 1 MoM quantity | **partly resolved** | Code residualises y (`mom_cells`, p2_analysis.py L135–143) and uses MoM as a direction check (L284–286). Prereg L115 says what MoM's fact component is. But MoM diff is also a different estimand from REML diff, and the "H1 unchanged" sentence is inaccurate (finding 5). |
| 2 carrier main effect | resolved | p2_model.R L29; p2_analysis.R L23–24; p2_null.R L21; prereg L87, L99–102. Remaining gaps: the two-way path lacks it (N3); its effect on the CI selection is asserted, not shown (N6). |
| 3 partly run model | resolved | run_p2.py L86–87 sets the old manifest aside; L133–134 `done` records n_facts and requires every chunk in the manifest; `completeness` L70–105. e2e: P (pilot with a false `done` event) and D are rejected. Residual issue: finding 6. |
| 4 multi-model rules | resolved | Families L300–303; conflict rule L302, L309–312; MoM limited to H1/H1-alt (prereg L119). Notes N1 and N2. |
| 5 null and sensitivities without code | resolved | p2_null.R matches prereg L159–164 (statistic, permutation unit, p formula, role). All sets are implemented (p2_analysis.py L220–261). Notes N4 and N5. |
| 6 simulation wording | resolved in text | Prereg L127–134, L151. The robustness simulation is under-specified (N6). |
| 7 one-sided misses | resolved | I recomputed from results/P2sim_v2/p2_bootsim_v2.json: ICC1 below the lower bound 4/5, above the upper 1/4; diff below 1/3, above 5/5. These match L145–146. MCSE 0.041 and pooled 0.928 are correct. |
| 8 second-look disclosure | resolved | L137, L149. |
| 9 resamples, calc.derivs | resolved | L133–134. |
| 10 failed refits | **partly resolved** | Per-column rule is implemented (p2_analysis.R L42–43). The code over-applies it (finding 3). |
| 11 minimum data | resolved | p2_analysis.py L210–217; prereg L68–72. |
| 12 headline-rule definitions | resolved | Prereg L193–200 matches decide L293–294, L307–312. |
| 13 driver fallbacks | resolved in text and code | Prereg L34–39; p2_gpu_run.sh L76–79, L125–144. Gaps: N8. |
| 14 sync of deviations and log | **unresolved in practice** | sync_meta cannot succeed as written (finding 2). |
| 15 nc depends on runs | **partly resolved** | `--nc` guard exists. nc is still taken over the wrong set of models, and the prereg contradicts itself (finding 4). |
| 16 frames random; stale comment | resolved | p2_model.R L8–14; prereg L94. |
| 17 conditional ICC | resolved | Prereg L93. |
| 18 D2/D3 censoring; p_final = 0 | resolved | p2_analysis.py L57–67; prereg L62–63. N7 remains. |
| 19 H3 G(k̄) | resolved | L252, L321; prereg L184–186. |
| 20 multiple comparisons | resolved in substance | The intersection-union description is not exact for "≥ 2 of k families" (N2). |

## B. Findings

**1. [should-fix] A single fit error crashes the decision for every model, and nothing is written.**
- File: /home/user/depth-law/analysis/p2/p2_analysis.py, L321.
- When `rfit` fails it returns `{"status": "MISSING: fit error", "missing": ...}` (L150), with no `vc` key. `fact_means[model]` is still filled (L251).
- In `decide`, H3 then reads `res["models"][x]["fits"]["D1"]["vc"]` and raises KeyError. I reproduced this: a two-model res, one with a D1 fit error, gives `KeyError 'vc'`.
- `p2_results.json` is written only after `decide` (L263–265), so the call leaves neither output file.
- The e2e test missed this because in all10 the failing models had fewer than 10 common facts, so the loop skipped them.
- Prereg L124 says a fit that errors is MISSING for that model only. Any lmer error in the correct set would force a change to frozen code after the data.
- Can change GO / PARTIAL / NO-GO: not directly, because the intended rule is clear; the risk is a post-data edit to frozen code.
- **Fix:**
  - skip H3 pairs whose D1 fit is not `ok` and record them as MISSING;
  - write `p2_results.json` before calling `decide`;
  - add an e2e case with a forced fit error in the correct set.

**2. [should-fix] Deviation files and the session log are never copied off the instance (round-1 item 14 still open).**
- File: /home/user/depth-law/scripts/p2_gpu_run.sh, L28–32.
- sync_meta runs `rsync -a "$DEVDIR/" "$SYNC_DEST/_session/deviations_pending/"`. Nothing ever creates `$SYNC_DEST/_session`. rsync creates only the last path component, so the command fails. Locally (rsync 3.2.7) it gives `mkdir ... failed: No such file or directory`, exit 11.
- Because of `&&`, the log rsync never runs either. `|| true` hides the failure, and nothing is written to `$LOG`.
- The dry runs did not set SYNC_DEST, so this was never exercised.
- Prereg L40 promises these copies. They are the only evidence that each deviation was written before its step, and the hard stop shuts the instance down.
- Can change GO / PARTIAL / NO-GO: no (record integrity only).
- **Fix:**
  - create the directory first (`rsync --mkpath`, or `ssh host mkdir -p` for remote targets);
  - log success or failure of each sync in `$LOG`;
  - dry-run once with a local SYNC_DEST.

**3. [should-fix] If either fit fails, code marks the whole model MISSING; the prereg makes only the affected hypotheses MISSING.**
- Code: p2_analysis.py L278–281 marks the whole model `MISSING (D1 or D4 fit)` if either the D1 or the D4 fit is not `ok`. The model then drops out of every claim.
- That includes the D1-only rules: "no fixed layer" (prereg L193–195) and the shuffled-null sentence (L203–204).
- Prereg L123: such a fit "is MISSING, so the hypotheses that use it are MISSING for that model". A D4-only failure should therefore leave the D1-only rules evaluable.
- MoM failure is a related gap. In code it makes H1 / H1-alt False, not MISSING (`mom_ok`, L283–286), so the model still counts as an included model. The prereg is silent on this.
- Can change GO / PARTIAL / NO-GO: yes. It changes which families count for "no fixed layer" and "fact share > 0".
- **Fix:** make text and code agree. Either:
  - evaluate each rule on the fits it uses; or
  - state in prereg §4 that a D1 or D4 fit failure removes the model from all claims.
  Also state what a MoM failure does.

**4. [should-fix] The number of carriers (nc) is taken over the wrong set of models, and the prereg gives two different rules.**
- Prereg L45: after fallback 1, "analyses then use carriers 0 and 1 for every model".
- Prereg L75: nc is "the smallest carrier count available in every included model". It is an included model only after the minimum-data rule.
- Code (p2_analysis.py L191–192) takes the minimum over models that pass the completeness rule, before the minimum-data rule (L210–217). Two cases go wrong:
  - a 2-carrier model that is complete but has insufficient data still forces nc = 2 everywhere, against L75;
  - a 2-carrier model that crashed (incomplete) gives nc = 3, against L45.
- nc enters den (fc/nc, e/nc) and the carrier set, so ICC(1) and diff, and hence H1 / H1-alt, can move.
- `--nc` also accepts a value below the confirmatory nc (only `>` is refused, L194), and nothing checks that sensitivity calls use the same `--runs`.
- Can change GO / PARTIAL / NO-GO: yes.
- **Fix:**
  - choose one rule, e.g. "nc = min over models that pass both completeness and minimum data", and say so at both L45 and L75;
  - apply the minimum-data rule before computing nc (it does not depend on nc);
  - in sensitivity calls, refuse any `--nc` that differs from the confirmatory call's `n_carriers_used`, e.g. by reading it from the confirmatory `p2_results.json` and also asserting equal `--runs`.

**5. [should-fix] The MoM change is not described accurately, and H1's own changes are not disclosed.**
- (a) Prereg L115 says MoM ICC(1) is not the REML ICC(1) "so MoM is used only as a direction check on diff". This implies MoM diff targets the same quantity as REML diff. It does not.
  - On the carrier-averaged scale, MoM den equals REML den, but MoM diff = (rt + frame + ft + e/nc − fact − fc/nc)/den = REML diff + (e − fc)/(nc·den).
  - So the check is not symmetric. When fc > e, the H1 MoM condition is harder than the REML one.
  - For H1-alt, the REML condition ICC(1) ≥ 0.5 implies, in expectation, MoM diff ≤ −2fc/(nc·den) < 0. The new MoM condition is therefore nearly redundant for H1-alt and binding only for H1.
- (b) Prereg L173 says "all of H1 [is] unchanged". But H1 has three changes, all from the same batch and all approved:
  - its MoM input is now covariate- and carrier-residualised (before: raw cell means; compare 75ca3d7:p2_analysis.py L130);
  - its REML model now has the carrier fixed effect;
  - "≥ 2 models" became "≥ 2 families".
- (c) The MoM self-test (p2_mom.py L66–81) still has no fc term, no carrier effect and no covariate residualisation. So the description at L115 is untested.
- I do not re-litigate the human decision. This finding is about accuracy only.
- Can change GO / PARTIAL / NO-GO: no (text). Point (a) affects how a REML/MoM disagreement on H1 would be read.
- **Fix:**
  - state the MoM diff estimand and the asymmetry in §4;
  - reword L173 to list the H1 changes above;
  - optionally extend the self-test with fc, a carrier shift and one covariate, and check the expected MoM components.

**6. [should-fix] The prereg does not say which run is analysed when a model has more than one run, and deviation records can be overwritten.**
- Prereg L8 and L237 allow reruns after a deviation. L221 says `--runs <every model run>`.
- `comp` is a dict keyed by model name (p2_analysis.py L185–188). If two runs of one model are passed, the last one silently wins, so the choice of run is open after seeing data.
- p2_gpu_run.sh numbers deviations from `NDEV=0` on every invocation (L33) and writes them with `>` (L36). A second invocation, e.g. after an instance restart, overwrites D-P2-1.md, D-P2-2.md and so on, on the instance and through rsync at SYNC_DEST.
- The 16:00 dry run did exactly this: it replaced the 15:58 run's files in results/P2dry/deviations_test/.
- Can change GO / PARTIAL / NO-GO: yes, through the choice of run.
- **Fix:**
  - prereg rule, e.g.: "for each model, the first run that passes completeness; later runs only after a committed deviation naming the run_id it replaces";
  - make `p2_analysis.py` refuse duplicate model keys;
  - make deviation names unique per invocation (UTC timestamp in the name, or `set -o noclobber` with a counter that resumes from existing files).

**7. [should-fix] The two completeness checks are not the same.**
- Prereg L49 names both `p2_analysis.py completeness` and `scripts/p2_done_check.py` as the completeness rule. They check different things:
  - the done-check fails on any NaN p (p2_done_check.py L16–18); `completeness()` does not;
  - `completeness()` checks carrier ids 0..k−1, equal layer counts and the exact fact × paraphrase set; the done-check does not.
- So the driver can write a "MISSING (incomplete)" deviation for a model that the analysis then includes, or the reverse.
- Can change GO / PARTIAL / NO-GO: yes, in principle (model inclusion), though NaN is unlikely in fp32.
- **Fix:** make the analysis `completeness()` the only rule (add the NaN check). Have the done-check call it, or state that the done-check is informational only.

## C. Notes

**N1. [note] Family mapping and within-family splits.**
- `fam` is None for an unrecognised model name (p2_analysis.py L202), and `fams` would count None as a family (L300). This does not happen for the five prereg models; failing hard would be safer.
- A family where pythia-1.4b meets H1 and pythia-2.8b meets H1-alt counts toward both, including in the conflict rule. Consider stating this.

**N2. [note] The multiple-comparisons wording is not exact.**
- Prereg L165 calls each claim an intersection-union test. D1 ∧ D4 ∧ MoM within a model is one.
- "≥ 2 of k families" is a union over pairs, and there are several headline sentences with no family-wise control across them.
- The error stays small (round 1 estimated about 0.006), but the sentence should say "conjunction within model; at least 2 of up to 4 families; no correction across sentences".

**N3. [note] The two-way bootstrap path ignores the carrier fixed effect.**
- `twoway_boot` (p2_bootsim_fns.R L17) fits `p2_formula("y", COV, subj)` without the carrier fixed effect.
- It is frozen code but not the prereg method (boot=param). Remove it, or add `carrier = TRUE`, so the frozen code has no non-prereg path.

**N4. [note] The shuffled-fact null has no rule for failed permutations.**
- p2_null.R drops failed permutations (L37, L41–44) with no failure threshold, unlike the 5% bootstrap rule.
- If an mclapply worker dies, `unlist` returns a character vector, not NA.
- **Fix:** add a > 5% failed-permutations → MISSING rule, and coerce with `as.numeric`.
- The null also runs with `calc.derivs = FALSE` (L22) while prereg L86 says checks are ON. The estimates are the same; one line in §4 would cover it.

**N5. [note] Sensitivity decision files carry the same `claims` block as the confirmatory call.**
- `decide()` computes it for every CI set (L304–314). Since sensitivities are "reported, not gating" (L77), mark those files non-gating, e.g. `"gating": false`, so a sensitivity claim cannot be quoted as a headline.

**N6. [note] The carrier fixed effect and the CI-method selection.**
- Prereg L101 asserts that the selection "still applies" because fixed effects do not enter the shares. The simulations had neither covariates nor a carrier effect, so this is an assumption, not a result. Say so.
- The robustness simulation (L152–158) does not say which model it fits. It should fit the frozen formula: four covariates plus the carrier fixed effect.
- A carrier × relation interaction would still be absorbed into fact:carrier, so into den as fc/nc. This is the same mechanism as round-1 item 2, at relation level. Consider reporting a `(1|relation:carrier)` fit as a non-gating check.

**N7. [note] Tiny non-zero p_final in the all-cells sensitivity.**
- With float16 storage (run_p2.py L117), a subnormal final p gives a coarse 0.5·p_final threshold and D4 ≈ 0. This affects only the all-cells sensitivity.
- Report the count with p_final < 1e-4 next to the p_final = 0 count, or store log p.

**N8. [note] Driver provenance and dry-run coverage.**
- The driver logs `git rev-parse --short HEAD` (L40) with no dirty flag and no check against tag `prereg-P2`. The post-fix dry runs were logged as git 50bc75c while running uncommitted code.
- Material hashes are printed (L42–44) but never compared with prereg §1. The analysis does not verify them either.
- `SKIP_ENV=1` skips the Llama access check (L53–61).
- The measurement depends on `depthlaw.depth.causal` / `depthlaw.depth.common`, which are not in the frozen list (prereg L215–218). The tag covers them, but the list does not.
- The dry runs ran one model only. They never exercised:
  - a second model (no `--run-dir`);
  - the per-model fallback or skip;
  - the crash path;
  - the hard stop;
  - SYNC_DEST.

## D. Prereg text against code
Every threshold matches the code: 0.5 / 0.4, CI lower > 0, upper < 0.15, n′ ≥ 8 with undefined → 31, tf − resid > 0, p < 0.01, ≥ 150 facts / ≥ 15 relations, > 5% refits, quantiles 0.025 / 0.975, 1000 resamples and permutations, seed 20261121 (+ i). The disagreements are in findings 3, 4, 5 and 7.

## E. Still to be decided after seeing data
- which nc applies when the minimum-carrier model is MISSING (finding 4);
- which run of a model is analysed if it has more than one (finding 6);
- whether a D4-only or MoM failure removes D1-only claims (finding 3);
- how to proceed if a fit errors (finding 1: currently a crash).

VERDICT: REVISE
