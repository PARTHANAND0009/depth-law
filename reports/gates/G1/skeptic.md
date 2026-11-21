<!-- EXPLORATORY (post hoc, not preregistered). skeptic subagent (.claude/agents/skeptic.md), fresh context, 2026-11-21. Saved verbatim by the main session; not edited. -->
## Skeptic review: E-depthvar (EXPLORATORY, post hoc, not preregistered)

**Bottom line.** Under the human's rule the G1 outcome is **AMBIGUOUS**. Every issue below leaves it AMBIGUOUS, and the stored `decision_inputs` say the same. But the one "prompt wins" result (OLMo) comes from one template. The report also contains one wrong number. So two issues are BLOCKING for the report's numbers and claims, not for the category.

Files reviewed:
- Report: `/home/user/depth-law/analysis/exploratory/E-depthvar/EXPLORATORY_post-hoc_not-preregistered__REPORT_EXPLORATORY.md`
- Results: `/home/user/depth-law/results/EXPLORATORY_E-depthvar/EXPLORATORY_E-depthvar-none-321939b-20261121T153451Z/e_depthvar.json` (sha256 f8938143… matches the ledger; the run.py, fit.R and sim.R hashes match the ledger inputs)

### Rule outcome, set (i), from `e_depthvar.json` → `components` and `decision_inputs`

| model | D1 (tmpl+resid) − (fact+subj) [CI] | D4 diff [CI] | fact+subj D1 / D4 |
|---|---|---|---|
| pythia-1.4b | −0.023 [−0.189, 0.210] | −0.200 [−0.278, −0.040] | 0.465 / 0.484 |
| pythia-2.8b | −0.085 [−0.197, 0.073] | −0.186 [−0.261, −0.041] | 0.379 / 0.430 |
| OLMo-2-7B | +0.199 [0.078, 0.341] | +0.203 [0.091, 0.315] | 0.306 / 0.287 |

- **PASS-PROMPT fails:** only 1 of 3 models qualifies, and D4 favours fact in both Pythia models with CIs excluding 0.
- **PASS-FACT fails:** no fact+subject share reaches 0.5.
- The report never states the rule outcome. It should.

### Number check
- **Matches:** every B2, B3 (all 30 rows), ANOVA, B7a, B7b bias, B5, B6 and B7c number in the report matches `e_depthvar.json`, `build_summary.json` or `run.time`. The coverage summary (0.46–0.98 median 0.74; fact 0.50–0.98 median 0.84; template 0.46–0.86 median 0.69) also matches.
- **One wrong number (see 3a):** limitation 3 says template main "is estimated from 78 levels". The fitted `n_rt` in `fits/*point*_correct.json` is 56 / 60 / 72 in set (i) and 24 / 27 / 54 in set (ii).

### Issues

**1. BLOCKING: the template-main component is driven by one or two outlier templates, and the bootstrap cannot see it.**
- OLMo `company_ceo` template 1, `"{} is led by its CEO,"`: all 11 correct cells have D1 between 0.969 and 1.000. The model's other two `company_ceo` templates average 0.606 and 0.619, and no other correct cell in OLMo has D1 ≥ 0.95. Source: `tables/*cells_OLMo-2-1124-7B.csv`.
- I refit the same lme4 model leaving one relation out (my check, not in results/; script `/tmp/claude-0/-home-user-depth-law/79d106ca-74b7-5e19-8ef3-6880f992c1ff/scratchpad/loro.R`). It reproduces the published point estimates exactly when nothing is dropped.
  - Dropping `company_ceo` (29 of 1414 cells) moves the OLMo D1 diff from 0.199 to 0.009 and the D4 diff from 0.203 to 0.002. Template share falls from 0.332 to 0.188.
  - In pythia-1.4b, dropping `developer` moves template share from 0.213 to 0.050 and the D1 diff from −0.023 to −0.194. The driver is template 2, "The developer of {} is": 7 correct cells, mean D1 0.804 against 0.636–0.663 for the other two.
- The cluster bootstrap resamples facts within fixed relations and templates, so it cannot show this sensitivity. The OLMo "CI excludes 0" decision input is therefore not credible.
- The same outlier explains why the "ANOVA cross-check" disagrees with REML on set (ii) without the report saying so. OLMo D1 template share is 0.158 (ANOVA) vs 0.411 (REML), and relation share 0.333 vs 0.152. ANOVA weights each relation by its number of facts; REML weights each template level equally, so a 5-fact relation with a template-mean variance about 150× the median dominates REML.
- The category does not change, but this invalidates the OLMo decision input and any statement that prompts dominate in OLMo.

**2. BLOCKING (text fix): the "78 levels" in limitation 3 is wrong.** The correct counts are 56 / 60 / 72 in set (i) and 24 / 27 / 54 in set (ii). In set (i), 14 / 10 / 7 of these template levels rest on ≤ 2 correct cells. In pythia-1.4b, five relations have only 1–2 facts.

**3. NON-BLOCKING (but it removes interpretability): the relation share, 0.094–0.327 under D1, counts on neither side, and its split from template main is not identified.** Because templates are nested in relations, the relation component also contains the average wording effect of each relation's 3 templates.
- **Relation counted as fact:** fact shares become 0.559 / 0.706 / 0.495 (D1) and 0.717 / 0.755 / 0.509 (D4), which is PASS-FACT.
- **Relation counted as prompt:** the diffs become +0.071 / +0.242 / +0.388 (D1) and +0.033 / +0.140 / +0.425 (D4).
- So AMBIGUOUS here is largely a consequence of the rule excluding relation, not a finding about depth.

**4. NON-BLOCKING: correctness selection (720 / 804 / 1414 cells) restricts the range of fact variance.**
- In OLMo under D1, raw fact variance falls from 0.0123 (all cells, ANOVA) to 0.00273 (set i), while template variance only falls from 0.00384 to 0.00296.
- The fact share therefore falls 0.489 → 0.306 → 0.278 (all cells → set i → set ii), and the sign of the OLMo diff flips from about −0.05 on all cells to +0.199 on set (i).
- Single-cell facts are 168 / 175 / 200 (42% / 40% / 29% of the facts in set i), so the fact-vs-residual split rests on the multi-cell facts.
- Incorrect cells have lower mean D1 (0.56 / 0.50 / 0.56 vs 0.69 / 0.61 / 0.63 for correct cells), so the all-cells estimate is a different quantity, not a clean answer.
- Every set still gives AMBIGUOUS. On all cells, only pythia-2.8b reaches ≥ 0.5 under both D1 (0.515) and D4 (0.531). No analysis that models the selection was run.

**5. NON-BLOCKING: threshold choice (i).**
- In set (i), the absolute-threshold measures lean toward prompt. D2 and D3 diffs (+0.141, −0.104, +0.098; +0.115, −0.051, +0.105) all have CIs that include 0.
- D2 with censored carriers set to (L+1)/L gives +0.187 [0.120, 0.374] and +0.125 [0.018, 0.326] for the two Pythia models, the opposite direction to D4. These definitions mix in the template-dependent final confidence.
- D1 and D4 are close to duplicates (cell-level Spearman 0.85 / 0.89 / 0.94, my check), so their agreement is weak evidence of robustness.
- The 0.25 / 0.75 fraction variants were not run; no file exists. They cannot change the category, because D4 alone blocks both PASS outcomes.

**6. NON-BLOCKING: B5 confounds (iv).**
- Subject-to-final distance is constant within each template (SD 0 within template). Adjusting for it just moves template variance into relation (relation +79% / +46% / +22% under D1).
- After adjusting for all six covariates the diffs are −0.086 / −0.101 / +0.140 (D1) and −0.149 / −0.168 / +0.152 (D4), from `covariates_B5.joint_summary`. Same category.
- Answer prior correlates with D1 at ρ = −0.37 in OLMo correct cells (my check). That is a floor artifact that inflates the fact/object side, not the prompt side.

**7. NON-BLOCKING: whether the residual is interaction or noise (v) can be tested with existing data.**
- Carrier readout noise in the cell mean (within-cell carrier variance / 3) is at most 0.00024 / 0.00027 / 0.00056. The residual σ² is 0.00092 / 0.00142 / 0.00154. Layer-grid quantization is ≤ 5e-5.
- So at least 64–81% of the residual is the same across all three carriers. It is fact × template structure, not readout noise. Carriers share the source state, so this cannot rule out noise on the source side, but an fp32 forward pass has none.
- The B7c model leaves out `(1|fact_id:rt)`, so its "Residual" mixes the two. Limitation 2 ("cannot be separated") is overstated.
- If the residual were noise, the prompt side would shrink, so this cannot produce PASS-PROMPT.

**8. NON-BLOCKING: reliability with 3 templates (vi).**
- ICC(1) under D1 is 0.513 / 0.563 / 0.377, which is a description of these particular templates only.
- The D-study for k > 3 assumes exchangeable Gaussian template effects, and issue 1 shows they are heavy-tailed. So n′ (4 / 4 / 7) and its CIs do not generalise to new templates.
- Simulated CI coverage was only 0.46–0.86 for template main. The lme4 CIs actually reported were never tested for coverage.
- Several percentile CIs sit off-centre, e.g. OLMo D1 residual 0.173 in [0.129, 0.189] and 1.4b D4 fact+subject 0.484 in [0.357, 0.522], which points to bootstrap bias.
- 8 of 30 B3 fits are singular. The report tables omit that flag, and `calc.derivs=FALSE` turns off the convergence-gradient checks.

**9. NON-BLOCKING: the controls pass only formally.**
- B7a tests whether fact share is above 0, which nobody disputes. It was run on all cells and set (ii), not on the decision set (i).
- B7b plants Gaussian effects with a fixed relation share of 0.05 (observed 0.09–0.33). It has no correctness selection, no outlier templates and no carrier noise, and it never tests the CI of the diff.

### Most damaging alternative explanation
The "prompt" variance is mostly a carrier-transfer artifact of one or two specific templates, not a general effect of wording. For `"{} is led by its CEO,"` (ends in a comma), the final-position state transfers into the neutral carriers only at the last layer.

**Test**
1. Run a leave-one-relation-out and leave-one-template-out jackknife of the diff, plus a two-stage bootstrap over relations and templates, for all 3 models × D1/D4 on set (i).
2. For the flagged templates, measure depth by reading out the fact prompt's own final position (tuned or logit lens), without the carrier.
3. Rerun with cells where D1 ≥ (L−1)/L treated as censored.

**What would confirm or refute it**
- **Confirmed** if the self-readout depth for the comma template matches its siblings (about 0.61) while the carrier-patched D1 is about 1.0, and the OLMo diff's CI includes 0 under jackknife or censoring.
- **Refuted** if self-readout also resolves at the last layer and the OLMo diff stays > 0 with CI excluding 0 for every left-out relation.
- My partial leave-one-relation-out run already points toward confirmation (0.199 → 0.009).

**Decision: reject as it stands.** The AMBIGUOUS category holds, but the one directional result (OLMo prompt > fact) is a single-template effect and the CIs do not account for which templates were sampled. The experiment most likely to change my mind is the self-readout plus jackknife test above. If OLMo's prompt dominance survives dropping `company_ceo` and every other relation, and the comma template's late depth also shows up without the carrier, I would move to weak accept.

VERDICT: BLOCK
