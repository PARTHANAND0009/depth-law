# GATE G1 — EXPLORATORY (post hoc, not preregistered): E-depthvar (prompt vs fact variance in causal depth)

- **Sources:** `results/EXPLORATORY_E-depthvar/EXPLORATORY_E-depthvar-none-321939b-20261121T153451Z/e_depthvar.json`. Reviews: `reports/gates/G1/{replicator,stats-reviewer,skeptic}.md` (verbatim). Responses: `reports/gates/G1/responses.md`.
- **Plan:** `analysis/exploratory/E-depthvar/EXPLORATORY_post-hoc_not-preregistered__PLAN.md` (commit 853917a, before any statistic).
- **Not blind:** the D1 all-rows components had been seen in the H-R gate.

## Per model × definition (set (i): correct cells; lme4 REML; 95% CI from 1000 cluster-bootstrap resamples of facts within relation)

| EXPLORATORY (post hoc, not preregistered) model | def | N cells | fact+subject share | template-main share | residual share | relation share | (tmpl+resid) − (fact+subj) [CI] | ICC(1) [CI] | n′ for Φ ≥ 0.8 [CI] | n′ for G ≥ 0.8 |
|---|---|---|---|---|---|---|---|---|---|---|
| pythia-1.4b | D1 | 720 | 0.465 [0.338, 0.539] | 0.213 [0.122, 0.354] | 0.229 [0.128, 0.310] | 0.094 | -0.023 [-0.189, 0.210] | 0.513 [0.383, 0.612] | 4.0 [3, 7] | 2 |
| pythia-1.4b | D4 | 720 | 0.484 [0.357, 0.522] | 0.151 [0.102, 0.235] | 0.133 [0.083, 0.162] | 0.233 | -0.200 [-0.278, -0.040] | 0.630 [0.526, 0.688] | 3.0 [2, 4] | 2 |
| pythia-2.8b | D1 | 804 | 0.379 [0.285, 0.431] | 0.051 [0.043, 0.100] | 0.243 [0.162, 0.301] | 0.327 | -0.085 [-0.197, 0.073] | 0.563 [0.444, 0.650] | 4.0 [3, 6] | 3 |
| pythia-2.8b | D4 | 804 | 0.430 [0.333, 0.477] | 0.072 [0.061, 0.130] | 0.173 [0.111, 0.212] | 0.325 | -0.186 [-0.261, -0.041] | 0.638 [0.533, 0.698] | 3.0 [2, 4] | 2 |
| OLMo-2-1124-7B | D1 | 1414 | 0.306 [0.251, 0.345] | 0.332 [0.234, 0.455] | 0.173 [0.129, 0.189] | 0.189 | 0.199 [0.078, 0.341] | 0.377 [0.305, 0.448] | 7.0 [5, 10] | 3 |
| OLMo-2-1124-7B | D4 | 1414 | 0.287 [0.237, 0.321] | 0.366 [0.267, 0.460] | 0.124 [0.096, 0.136] | 0.222 | 0.203 [0.091, 0.315] | 0.369 [0.306, 0.434] | 7.0 [6, 10] | 2 |

Set (ii) (facts correct under all 3 templates) and D2/D3 are in the report.

## Cross-model agreement of fact-level mean depth (B6; disattenuated by G(3) from the set-(ii) fits)

| EXPLORATORY (post hoc, not preregistered) def | facts | pair | N facts | ρ [CI] | disattenuated ρ | ρ within relation |
|---|---|---|---|---|---|---|
| D1 | strict_all3 | pythia-1.4b vs pythia-2.8b | 50 | -0.173 [-0.422, 0.100] | -0.206 | 0.145 |
| D1 | strict_all3 | pythia-1.4b vs OLMo-2-1124-7B | 50 | 0.001 [-0.287, 0.301] | 0.001 | -0.021 |
| D1 | strict_all3 | pythia-2.8b vs OLMo-2-1124-7B | 50 | 0.411 [0.106, 0.638] | 0.502 | 0.288 |
| D1 | any_correct | pythia-1.4b vs pythia-2.8b | 312 | 0.347 [0.247, 0.443] | 0.415 | 0.188 |
| D1 | any_correct | pythia-1.4b vs OLMo-2-1124-7B | 312 | 0.356 [0.252, 0.451] | 0.414 | 0.113 |
| D1 | any_correct | pythia-2.8b vs OLMo-2-1124-7B | 312 | 0.527 [0.437, 0.608] | 0.644 | 0.271 |
| D4 | strict_all3 | pythia-1.4b vs pythia-2.8b | 50 | 0.182 [-0.100, 0.436] | 0.220 | 0.308 |
| D4 | strict_all3 | pythia-1.4b vs OLMo-2-1124-7B | 50 | 0.319 [0.026, 0.562] | 0.370 | 0.130 |
| D4 | strict_all3 | pythia-2.8b vs OLMo-2-1124-7B | 50 | 0.612 [0.382, 0.778] | 0.721 | 0.507 |
| D4 | any_correct | pythia-1.4b vs pythia-2.8b | 312 | 0.499 [0.407, 0.583] | 0.603 | 0.398 |
| D4 | any_correct | pythia-1.4b vs OLMo-2-1124-7B | 312 | 0.455 [0.358, 0.542] | 0.528 | 0.222 |
| D4 | any_correct | pythia-2.8b vs OLMo-2-1124-7B | 312 | 0.550 [0.460, 0.630] | 0.648 | 0.353 |

## Controls

| EXPLORATORY (post hoc, not preregistered) check | result |
|---|---|
| B7a shuffled-fact null (ANOVA fact share; all cells and set ii) | observed share above the null 99th percentile in 12/12 cases; p = 0.0010–0.0010 |
| B7b planted recovery: max abs bias of recovered fact / template shares (lme4, correct-cell design) | pythia-1.4b 0.028; pythia-2.8b 0.018; OLMo-2-1124-7B 0.013 (pass ±0.05: True) |
| B7b CI coverage (nominal 0.95) | 0.46–0.98, median 0.74 (template main 0.46–0.86); see report limitation 10 |
| B7c carrier facet | 3 carriers present; fit in the report |

## Reviews

| reviewer | verdict | decision-relevant findings |
|---|---|---|
| replicator (statsmodels REML, raw files only) | PASS | All 72 numbers within tolerance: 48 B3 shares (max gap 0.00016) and 24 B6 ρ (gap 0). A method-of-moments estimator moves the relation and template-main shares by up to 0.25; the fact and residual variances agree. |
| stats-reviewer (spec, bootstrap, D-study) | REVISE | 9 findings; 1 could change the category. Measured within relation (ICC(1)), the fact share is ≥ 0.5 in 2 of 3 models under D1 and D4, which would be PASS-FACT. Also: the bootstrap leaves out template sampling (CIs too narrow), and the planted grid does not cover the observed shares. |
| skeptic | BLOCK | The category stays AMBIGUOUS. BLOCKING 1: OLMo's prompt > fact comes from one template (dropping company_ceo moves the D1 diff from 0.199 to 0.009). BLOCKING 2: wrong "78 levels" text (fixed in report v3). The relation share counts on neither side. |

## Decision (human's G1 rule; set (i); shares of total variance including relation)

- **PASS-PROMPT:** (tmpl+resid) > (fact+subj), CI excluding 0, under D1 in: OLMo-2-1124-7B. The rule needs ≥ 2 of 3. **Not met.** The skeptic's BLOCKING issue 1 is also unresolved.
- **PASS-FACT:** fact+subject ≥ 0.5 under both D1 and D4 in: none. The rule needs ≥ 2 of 3. **Not met.**
- **Outcome: AMBIGUOUS.**
- **Sensitivity of the category** (from the reviews; neither is the rule as written):
  - With the fact share measured within relation (ICC(1)), or with the relation component counted as fact, PASS-FACT would hold in 2 of 3 models.
  - With the relation component counted as prompt, the prompt side wins in all 3 models.
  - The relation component, which also carries each relation's average wording effect, decides the category.

## Recommendation (one next step, per the human's instruction)
AMBIGUOUS leads to the confirmatory preregistration (prompt 2). It is not started: it needs the human's "approve G1".
