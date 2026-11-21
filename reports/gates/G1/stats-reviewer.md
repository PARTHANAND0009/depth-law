<!-- EXPLORATORY (post hoc, not preregistered). stats-reviewer subagent (.claude/agents/stats-reviewer.md), fresh context, 2026-11-21. Saved verbatim by the main session; not edited. -->
Scope: the first instruction asked for a check against prereg/HR_revised.md, but your later message narrowed this to the E-depthvar plan, so I reviewed against that plan only. The plan is unchanged since 853917a.

**Decision outcome under the plan's own definitions:** AMBIGUOUS (e_depthvar.json → decision_inputs; run.out).
- PASS-PROMPT fails. Only OLMo has a D1 difference CI that excludes 0: 0.199 [0.078, 0.341]. pythia-1.4b is −0.023 [−0.189, 0.210] and pythia-2.8b is −0.085 [−0.197, 0.073].
- PASS-FACT fails. Under D1 the fact+subject shares are 0.465 / 0.379 / 0.306, and under D4 they are 0.484 / 0.430 / 0.287.

**Checked and correct:**
- The random-effects structure matches the plan: fit.R:22, :28 in sim.R, and fit.R:83 for the carrier fit. rt is built from relation + template, so templates are nested correctly.
- Shares, ICC(1), ICC_rel and diff use the right components (fit.R:26-38).
- The bootstrap is within relation with relations fixed. fact_id is a string, so `byfact[[pick[i]]]` picks by name, not position. Duplicates get new fact and subject labels, and the difference uses paired draws from the same fit (fit.R:61-75).
- Φ and G match the plan's formulas.
- The ANOVA expected-mean-square algebra is correct for this nested, unbalanced design (run.py:38-63):
  - E[MS_f] = σ²_e + 3σ²_f.
  - E[MS_t] = σ²_e + n̄σ²_rt holds exactly, because SS_t is weighted by n_r and n̄ = n/R.
  - The relation term uses E[Σw(ȳ_r−ȳ_w)²] = Σw_r(1−w_r/N)·Var(ȳ_r), with Var(ȳ_r) = σ²_a + σ²_f/n_r + σ²_rt/3 + σ²_e/(3n_r).
- The D1 depth indexing in both simulators is correct (run.py:94-103; sim.R:16-25).

**Violations and errors**

1. **The PASS-FACT result depends on the denominator.** fit.R:30-33 divides by a total that includes σ²_relation, as the plan says (PLAN.md:50). Using the within-relation ICC(1) from the same fits (fit.R:34) gives 0.513 / 0.563 / 0.377 under D1 and 0.630 / 0.638 / 0.369 under D4. On that basis PASS-FACT would hold in 2 of 3 models. This is not a code error, but it **could change the decision (AMBIGUOUS → PASS-FACT)**. The report should state it.

2. **Wrong resampling unit for template-main and for the difference** (fit.R:66-69). Relations and their 3 templates are never resampled, so the CI for σ²_rt (78 levels) leaves out template sampling.
   - A one-way cluster bootstrap in a crossed facts × templates design is also biased.
   - Point estimates sit off-centre in the bootstrap distribution: P(draw < point) is 0.67-0.85 for fact+subject and residual, and 0.15-0.16 for template in pythia-2.8b. Bootstrap means are shifted about 0.01-0.04 toward "prompt".
   - The coverage simulation agrees: template-main coverage is 0.46-0.86 (report line 185-189).
   - A two-stage relation→fact bootstrap or a parametric bootstrap (bootMer) would be the right unit.
   - **Cannot change the decision.** Correct CIs would be wider and could only remove exclusions; only 1 of 3 models excludes 0 now.

3. **The D-study framing only holds for comparisons within a relation** (fit.R:29, 38).
   - Φ and G leave σ²_rel out of the true score. G, which drops σ²_rt, is right only for comparing facts within one relation. Across relations, rt/k is relative error and σ²_rel belongs in the true score.
   - In set (i), facts have on average 1.79 / 1.84 / 2.08 correct templates, so Φ(3) and G(3) describe a design that was never observed.
   - k > 3 assumes templates are exchangeable draws from an infinite population. In set (i) that population is selected by correctness, and σ²_rt and σ²_e are assumed equal across relations.
   - B6 (run.py:160, 165-172) divides the across-relation raw ρ by the within-relation G(3) from set (ii), including in the any_correct mode where facts have 1-3 templates. This mismatch biases the disattenuated ρ.
   - **Cannot change the decision.** The D-study and B6 are not in the rule.

4. **Undocumented deviation in the coverage arm** (run.py:107-108). The plan (PLAN.md:95, 100) asks for the balanced version of the set-(i) design: set-(i) facts across 26 relations, each with all 3 templates. The code uses set-(ii) facts only: 84 / 107 / 254 facts in 8 / 9 / 18 relations.
   - Coverage is also scored against latent planted shares, not shares on the D1 scale (run.py:130-131), which mixes transform bias with miscoverage.
   - The CIs that actually drive the decision (lme4 cluster bootstrap, set (i)) were never tested for coverage.
   - The deviation is not logged anywhere: there is no deviation file for E-depthvar, and prereg/DEVIATIONS.md does not mention it.
   - **Cannot change the decision.** Coverage is not part of the pass criterion.

5. **Null pass threshold not in the plan** (run.py:285). The `p < 0.01` threshold was chosen in code; the plan (PLAN.md:91-93) only asks to report the null.
   - The null also tests σ²_f > 0 with the ANOVA estimator on balanced sets, not the lme4 comparison on set (i) that the rule uses. It cannot fail in practice: every p = 1/1001.
   - **Cannot change the decision.**

6. **The planted grid does not cover the observed values** (sim.R:33; run.py:112-113).
   - Planted template-main is {0.05, 0.2}, but observed values reach 0.33-0.37 (OLMo, set (i)) and 0.51 (pythia-1.4b, set (ii)).
   - Relation is fixed at 0.05, but observed values are 0.09-0.33.
   - No subject effect and no correctness selection are simulated.
   - The "planted check passes" result therefore does not cover the observed configuration.
   - sim.R:17 also drops the planned p_fin factor (PLAN.md:97). This is harmless because D1 and D4 do not depend on scale, but it is a deviation that was not logged.
   - **Cannot change the decision.** PASS-PROMPT already fails on the CI criterion.

7. **B4 not delivered as planned.** PLAN.md:71 asks to state which of template-main and residual is larger, with bootstrap CIs. No CI of the paired difference is computed (fit.R:74 does not output it), and the report only says the answer "can be read directly" (REPORT:58). **Cannot change the decision.**

8. **B5 labels and scaling.**
   - The report header says "% change" (REPORT:141-150), but run.py and fit.R:53, 56 produce fractions (2.020 means +202%).
   - z-scoring is done within the analysis set (fit.R:49), not within the model as planned. This has no effect on the variance components.
   - **Cannot change the decision.**

9. **Convergence checks are switched off.** `calc.derivs = FALSE` (fit.R:15; sim.R:15) skips the gradient convergence checks, and singular bootstrap refits are counted as successes (fit.R:72-73). Some set-(ii) fits have relation share 0.000. **Cannot change the decision** for set (i): all D1 and D4 point fits are non-singular with no warnings.

Relevant files:
- /home/user/depth-law/analysis/exploratory/E-depthvar/EXPLORATORY_post-hoc_not-preregistered__fit.R
- /home/user/depth-law/analysis/exploratory/E-depthvar/EXPLORATORY_post-hoc_not-preregistered__run.py
- /home/user/depth-law/analysis/exploratory/E-depthvar/EXPLORATORY_post-hoc_not-preregistered__sim.R
- /home/user/depth-law/analysis/exploratory/E-depthvar/EXPLORATORY_post-hoc_not-preregistered__PLAN.md
- /home/user/depth-law/analysis/exploratory/E-depthvar/EXPLORATORY_post-hoc_not-preregistered__REPORT_EXPLORATORY.md
- /home/user/depth-law/results/EXPLORATORY_E-depthvar/EXPLORATORY_E-depthvar-none-321939b-20261121T153451Z/e_depthvar.json
- /home/user/depth-law/results/EXPLORATORY_E-depthvar/EXPLORATORY_E-depthvar-none-321939b-20261121T153451Z/fits/

VERDICT: REVISE
