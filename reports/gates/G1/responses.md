# EXPLORATORY (post hoc, not preregistered) — G1 responses

Every finding in `replicator.md`, `stats-reviewer.md` and `skeptic.md` is answered as fixed (commit), rebutted (reason), or deferred (Limitations / next prereg).

## replicator (VERDICT: PASS)
| finding | response |
|---|---|
| 1. Subject and fact cannot be separated in the all3 sets; statsmodels singular for two D4 sets | **Deferred.** Already stated as report limitation 5 ("fact vs subject: confounded; only their sum is reported"). |
| 2. Method-of-moments moves relation/template-main shares by up to 0.25 | **Deferred.** Estimator dependence is added to GATE_G1. The decision uses REML shares as planned. The next prereg must fix one estimator and test it in simulation on its own design. |
| 3. No other definition choice changed any value | No action. |

## stats-reviewer (VERDICT: REVISE)
| # | finding | response |
|---|---|---|
| 1 | PASS-FACT depends on the denominator (within-relation ICC(1) gives 2 of 3) | **Deferred.** Not changed after seeing data: the rule as given uses shares of total including relation. Shown as a sensitivity line in GATE_G1 for the human to decide. |
| 2 | Bootstrap does not resample relations or templates; CIs too narrow | **Deferred** (report limitation 10). It can only widen CIs, so it cannot create PASS-PROMPT. The next prereg needs a two-stage or parametric bootstrap. |
| 3 | D-study only holds within relation; k > 3 assumes exchangeable templates; B6 disattenuation mixes designs | **Deferred** (report limitations 3 and 7). n′ and the disattenuated ρ are descriptive only. |
| 4 | Coverage arm used set-(ii) facts, not the balanced set-(i) design; coverage scored on latent shares; deviation not logged | **Fixed (logged)** as a deviation in the ledger (DEVIATION entry "E-depthvar coverage design"), here, and in report limitation 10. |
| 5 | Null threshold p < 0.01 was not in the plan; the null cannot fail | **Rebutted in part.** The threshold is used only to say "passes"; the gate reports raw p and percentiles. Agreed that the null is weak; deferred to the next prereg (test on the decision set). |
| 6 | Planted grid does not cover the observed shares; no selection or subject effect; p_fin dropped | **Deferred**, logged as a deviation (p_fin) in the ledger. The planted check is reported as covering only the planted grid. |
| 7 | B4 (template vs residual) has no paired CI | **Deferred.** Not computed; listed as missing here. |
| 8 | B5 "% change" label shows fractions; z-scoring within set | **Fixed** in report v3 (commit 3298b0d). z-scoring has no effect on the variance components. |
| 9 | Convergence checks off; singular refits counted | **Fixed in part:** report v3 adds a singular-fit column. The convergence checks stay off; deferred. |

## skeptic (VERDICT: BLOCK)
| # | finding | response |
|---|---|---|
| 1 | BLOCKING: OLMo prompt > fact driven by one template (company_ceo "{} is led by its CEO,"); bootstrap cannot see it | **Accepted, not fixed.** The OLMo decision input is not credible, and GATE_G1 says so. It does not change the category (PASS-PROMPT already fails on 1/3). The skeptic's test (leave-one-relation/template-out jackknife, self-readout of the flagged templates, D1 ≥ (L−1)/L censoring) is not run: it is outside the human's G1 scope. Deferred to the next prereg. |
| 2 | BLOCKING (text): "78 levels" wrong | **Fixed** in report v3 (commit 3298b0d): 56/60/72 (set i), 24/27/54 (set ii), read from the fit files. |
| 3 | Relation share counted on neither side; not identified from template main | **Deferred.** Shown as a sensitivity in GATE_G1. The next prereg needs a design that separates relation from wording (more templates per relation, shared frames across relations). |
| 4 | Correctness selection restricts fact variance | **Deferred** (report limitation 4). All-cells shares are in the ANOVA table. |
| 5 | Threshold choice; D1 ≈ D4; frac 0.25/0.75 variants not run | **Deferred.** frac 0.25/0.75 are in the H-R robustness run on all rows (results/HR_gate.md), not in E-depthvar. MISSING here. |
| 6 | B5: subject-to-final distance is constant within template | **Accepted** as a limitation of B5; no action. |
| 7 | Residual is mostly fact × template structure, not carrier noise | **Accepted.** Report limitation 2 is overstated; to be corrected in the next report version. Deferred. |
| 8 | Reliability with 3 templates; heavy-tailed template effects; singular fits | **Deferred** (limitations 3 and 10). Singular flag added in v3. |
| 9 | Controls pass only formally | **Accepted.** GATE_G1 shows the raw control numbers. Deferred to the next prereg. |
