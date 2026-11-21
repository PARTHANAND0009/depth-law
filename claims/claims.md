# Candidate claims (all EXPLORATORY (post hoc, not preregistered) unless stated otherwise)

- **Status:** written 2026-11-21 for the G1 novelty check. These are candidates, not paper text. Each is marked EXPLORATORY as the human instructed.
- **Prior preregistered tests:** where a claim rests on a test that was preregistered earlier (prereg/HR_revised.md, frozen 7725c5b), that is noted. Those tests were run after data had partly been seen (see the prereg's disclosure).
- **Depth definitions:**
  - "Depth" = causal half-probability depth (D1): the first layer from which the patched probability of the object's first token stays ≥ 50% of its final value. Patch = the fact prompt's final-token residual written into the final token of 3 neutral carrier prompts; normalized l/L, averaged over the carriers.
  - D4 = 1 − mean_l min(1, p_l/p_final).
- **Data:** 1300 facts × 3 templates, 26 relations; models pythia-1.4b, pythia-2.8b, OLMo-2-1124-7B (fp32).

## 1. Depth is partly a property of the fact and partly of the wording
- **Claim (EXPLORATORY):** among correctly answered prompts, the variance of causal depth splits into:
  - fact+subject: 0.29–0.48 of total;
  - relation:template (wording): 0.05–0.37;
  - fact × template residual: 0.12–0.24;
  - relation: 0.09–0.33.
  - These ranges are over 3 models and D1/D4.
- **Scope:** 3 models in 2 families; correct cells only (720 / 804 / 1414 cells); 3 templates per relation; lme4 REML.
- **Caveats:**
  - Relation and template are not identified separately.
  - A method-of-moments estimator moves the relation and template shares by up to 0.25 (replicator).
  - Simulated CI coverage is below nominal.
- **Source:** `reports/gates/G1/GATE_G1.md`; `results/EXPLORATORY_E-depthvar/EXPLORATORY_E-depthvar-none-321939b-20261121T153451Z/e_depthvar.json`.

## 2. Within a relation, a fact's depth is moderately stable across wordings
- **Claim (EXPLORATORY):** with relation variance removed, the single-template fact ICC(1) is 0.38–0.64 (0.37–0.64 over D1/D4).
  - An absolute-agreement reliability of 0.8 would need about 3–7 templates per fact (extrapolated from 3).
- **Scope:** as claim 1. In the D-study, k > 3 assumes exchangeable templates; the skeptic found heavy-tailed template effects.
- **Source:** GATE_G1.md; `analysis/exploratory/E-depthvar/EXPLORATORY_post-hoc_not-preregistered__REPORT_EXPLORATORY.md`.

## 3. The wording-vs-fact balance differs between model families
- **Claim (EXPLORATORY):** in OLMo-2-7B, wording (template + residual) exceeds the fact+subject share; in both Pythia models it does not.
  - OLMo D1 diff +0.199. With company_ceo dropped it is +0.009, but it stays > 0 in all 26 leave-one-relation-out fits.
  - Pythia D1 diffs −0.023 and −0.085.
- **Scope:** 1 OLMo vs 2 Pythia models; one influential relation (company_ceo; one template ending in a comma).
- **Source:** GATE_G1.md; `analysis/exploratory/E-depthvar/EXPLORATORY_post-hoc_not-preregistered__PART0A_REPORT.md`.

## 4. Facts that resolve late in one model tend to resolve late in another, but only moderately
- **Claim (EXPLORATORY):** fact-level mean depth correlates across models at Spearman ρ 0.35–0.55.
  - This is over 312 facts answered correctly by all three models.
  - It falls to 0.11–0.40 once relation means are removed.
- **Scope:** 3 model pairs, 2 families; one is a within-family pair (pythia-1.4b vs 2.8b).
- **Source:** GATE_G1.md (B6).

## 5. Within a relation, pretraining co-occurrence does not predict depth
- **Claim (EXPLORATORY; rests on H3 of prereg/HR_revised.md):**
  - Adding within-relation log co-occurrence (EXACT counts) to the depth model changes marginal R² by at most 0.0016 in each model. The upper 95% bound is ≤ 0.0104 (H3 passed in 3/3 models).
  - The within-relation slope is positive (later depth with more co-occurrence) under amendment 2.
- **Scope:** pythia-1.4b, pythia-2.8b (Pile, EXACT), OLMo-2-7B (OLMo-mix stage-1, EXACT); all rows.
- **Source:** `results/HR_gate.md` (run HR-none-f431f35-20261121T081116Z); `reports/GATE_A2.md` (run A2-none-a7dfeb5-20261121T065218Z).

## 6. Co-occurrence predicts whether a fact is answered, not how deep it resolves
- **Claim (EXPLORATORY):** the odds ratio for correctness per log1p unit of within-relation co-occurrence is 1.28–1.43 in each of the 3 models, while depth is unaffected (claim 5).
- **Scope:** as claim 5.
- **Source:** `results/HR_gate.md`.

## 7. The ordering of relations by depth is only moderately shared across families
- **Claim (EXPLORATORY; rests on H2 of prereg/HR_revised.md, which FAILED):**
  - Spearman ρ of relation random effects between Pythia and OLMo-2 is 0.52 and 0.60, below the preregistered 0.7.
  - The within-Pythia pair is 0.83.
- **Scope:** 26 relations; 2 cross-family pairs that share OLMo.
- **Source:** `results/HR_gate.md`.
