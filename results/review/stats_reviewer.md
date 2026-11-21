# stats-reviewer report: revised H-R gate

- **Agent:** `stats-reviewer` (`.claude/agents/stats-reviewer.md`), run 2026-11-21 ~09:27-09:50 UTC.
- **Reviewed:** `results/HR_gate.md`, run `HR-none-f431f35-20261121T081116Z`.
- **Saved by the main session:** the agent returned its report as its final message without writing this file. The text below is verbatim; only this header is added.

---

None of the violations below could change the NO-GO decision.

I did not write results/review/stats_reviewer.md. My instructions here say not to write report files, so this message is the report.

What I checked:
- **Prereg is unchanged since it was frozen.** prereg/HASH.txt points to commit 7725c5b, the only commit that touches prereg/HR_revised.md. `git diff 7725c5b -- prereg/` shows only HASH.txt being added.
- **Gating numbers are as reported.**
  - From run HR-none-f431f35-20261121T081116Z: the three H2 pairs (ρ, permutation p, partial ρ, covariate-only ρ, both bootstrap CIs) and every robustness permutation p.
  - The OLMo main lme4 fit (ICC, ΔR², log OR, BLUPs).
- **Tests match the prereg.**
  - All thresholds in run.py:25-26 equal the prereg, with the right inequalities.
  - The decision logic (run.py:191-201) is the rule in prereg B8.
  - Only the pythia-vs-OLMo pairs count (assemble.py:19, run.py:159); Pythia-1.4b vs 2.8b is reported but not counted.
  - The permutation test shuffles the relation labels of one model's BLUP vector. Its statistic equals Spearman.
  - All CIs resample relations, not facts: H1 ICC, H3 ΔR², the OR, and the H2 ρ / partial ρ CIs.
- **Outcome is computed as stated.** Recomputing it from the stored curves reproduces half_prob_depth exactly (max difference 0).
- **No multiple-comparison correction is applied, and the prereg specifies none.** The rule is a conjunction over the two cross-family pairs.
- **No extra test is presented as confirmatory.**

## Violations that could change GO / PARTIAL / NO-GO

None. H2 raw fails in both cross-family pairs (ρ = 0.519 and 0.597 against a 0.7 threshold), and that alone sets NO-GO.

## Violations that cannot change the decision

1. **Handling of undefined split-half splits is not in prereg/DEVIATIONS.md.**
   - Where: src/depthlaw/hr/run.py:118-127 and 163-165; results/HR_gate.md:29; prereg/DEVIATIONS.md:5 still says "(none yet)".
   - What was done: splits whose Spearman is undefined are dropped from the mean r_SB (prereg B6, prereg/HR_revised.md:114-119).
   - Effect: for pythia-2.8b that is 32 of 200 splits, which raises its r_SB from 0.754 (undefined counted as 0) to 0.897.
   - Why it cannot change the decision: split-half reliability and disattenuated ρ are reporting-only.

2. **Permutation p set to null after the run is not in prereg/DEVIATIONS.md, and the results file was patched by hand.**
   - Where: results/HR_gate.json:3934 ("corrections"); results/HR_gate.md:168; prereg/DEVIATIONS.md:5.
   - The patched rows (results/HR_gate.json:3480-3486, 3499-3505, 3665-3671, 3813-3819, 3832-3838) contain `"rho": NaN` and a "(sigma2_relation estimated 0)" message.
   - Neither the run's code (f431f35) nor the current code produced that content. The current run.py:64-67 returns None with a different message.
   - So results/HR_gate.json and its copy in the run directory are no longer the run's raw output.
   - Why it cannot change the decision: only five non-gating robustness rows are affected.

3. **The reported run used code that was never committed.**
   - Where: run_id HR-none-f431f35-20261121T081116Z; `git diff f431f35 a16e158 -- src/depthlaw/hr/`.
   - The split-half NA handling that the run needed only exists in commit a16e158, made after the run, which also adds the NaN guard. No commit contains exactly the code that ran.
   - This breaks the CLAUDE.md reproducibility rule; the gating statistics themselves are unaffected.
   - Why it cannot change the decision: the diff touches only the split-half, disattenuation and NaN-guard code. All gating numbers reproduce exactly.

4. **Part A and Part B of the prereg disagree on "template", and this is not logged.**
   - Where: prereg/HR_revised.md:16 and 18 versus :82; src/depthlaw/hr/hr_fit.R:11 and 19.
   - Part A lists template as a fact covariate. Part B (and the code) only include it as `(1|relation:template)`.
   - By the prereg's own rule (line 7) this conflict is a deviation that should be logged, and it was not.
   - Why it cannot change the decision: I refitted with `factor(template_id)` added as a fixed effect.
     - Cross-family ρ: 0.510 (pythia-1.4b vs OLMo) and 0.592 (pythia-2.8b vs OLMo).
     - ICC_rel: 0.053, 0.014 and 0.065.
     - All conclusions stay the same.

5. **The seeding scheme differs from the prereg and the report misdescribes it.**
   - Where: src/depthlaw/hr/hr_fit.R:68 (`set.seed(seed + b)`) and :81 (`set.seed(seed + s)`).
   - The prereg (B10, prereg/HR_revised.md:162) says one seed, 20261121, for everything. The R bootstrap and split-half tasks instead use seeds 20261122 and up.
   - results/HR_gate.md:4 says 20261121 was used "for every bootstrap, permutation and split", which is not accurate for the R side. This is not logged.
   - Why it cannot change the decision: the H1 point estimates (0.013-0.060) are far below 0.30, and the H3 CI upper bounds (≤ 0.0104) are far below 0.02.

6. **Bootstrap relabels subjects in every relation, not only duplicated ones.**
   - Where: src/depthlaw/hr/hr_fit.R:44, against prereg B4 (prereg/HR_revised.md:95).
   - This breaks subject crossing across relations even when a relation is not duplicated.
   - Why it cannot change the decision: only 4 of 1296 subjects (24 rows) appear in more than one relation.

7. **"Warnings 0" is guaranteed by construction (not a prereg rule; it affects how the report reads).**
   - Where: src/depthlaw/hr/hr_fit.R:12 and :105 use `calc.derivs = FALSE`, which turns off lme4's gradient and Hessian convergence checks.
   - So the "warnings 0" column (results/HR_gate.md:147-151) and the empty warnings_h1/h3 fields cannot detect convergence problems.
   - Why it cannot change the decision: the gating fits reproduce exactly, and the margins to every threshold are large.
