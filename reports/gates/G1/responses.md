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
| 1 | BLOCKING: OLMo prompt > fact driven by one template (company_ceo "{} is led by its CEO,"); bootstrap cannot see it | **Accepted; answered in part by Part 0a after "approve G1"** (`analysis/exploratory/E-depthvar/EXPLORATORY_post-hoc_not-preregistered__PART0A_REPORT.md`, EXPLORATORY). See the 0a answer below the table. The skeptic's BLOCK stays on record. |

**0a answer to skeptic issue 1:**
- **OLMo jackknife:** the OLMo D1 diff stays > 0 in 26/26 leave-one-relation-out fits (min 0.009, median 0.205, max 0.264); D4: 26/26 (min 0.002).
- **company_ceo:** it is the only relation that moves the OLMo diff by more than 0.1 (−0.190 D1, −0.201 D4). Without it the advantage nearly vanishes, so the skeptic's point stands for magnitude, not sign.
- **Self-readout:** the lens readout on the fact prompt is late (≥ 0.93) for every company_ceo template in every model, so it neither confirms nor refutes the carrier-transfer explanation. Inconclusive.
- **Not run:** the D1 ≥ (L−1)/L censoring variant.
- **Pythia 1.4b:** developer and manufacturer also exceed 0.1 influence. All three relations go into P2's prespecified sensitivity rule (A1).
| 2 | BLOCKING (text): "78 levels" wrong | **Fixed** in report v3 (commit 3298b0d): 56/60/72 (set i), 24/27/54 (set ii), read from the fit files. |
| 3 | Relation share counted on neither side; not identified from template main | **Deferred.** Shown as a sensitivity in GATE_G1. The next prereg needs a design that separates relation from wording (more templates per relation, shared frames across relations). |
| 4 | Correctness selection restricts fact variance | **Deferred** (report limitation 4). All-cells shares are in the ANOVA table. |
| 5 | Threshold choice; D1 ≈ D4; frac 0.25/0.75 variants not run | **Deferred.** frac 0.25/0.75 are in the H-R robustness run on all rows (results/HR_gate.md), not in E-depthvar. MISSING here. |
| 6 | B5: subject-to-final distance is constant within template | **Accepted** as a limitation of B5; no action. |
| 7 | Residual is mostly fact × template structure, not carrier noise | **Accepted.** Report limitation 2 is overstated; to be corrected in the next report version. Deferred. |
| 8 | Reliability with 3 templates; heavy-tailed template effects; singular fits | **Deferred** (limitations 3 and 10). Singular flag added in v3. |
| 9 | Controls pass only formally | **Accepted.** GATE_G1 shows the raw control numbers. Deferred to the next prereg. |

## novelty-scout (VERDICT: REVISE; added after "approve G1")
| finding | response |
|---|---|
| No headline claim ANTICIPATED or CONTRADICTED | No action. |
| Required wording changes, claims 1, 2, 3, 4, 7 | **Fixed** in claims/claims.md (commit 48d2ec2). |
| Paraphrased quotes must be re-checked against full text before the paper | **Deferred** to citation-verifier at G6. |
| UNVERIFIED neighbours (ZF443JePxe, 2411.10813, 2505.14824, 2604.08510, 2510.10280); 2411.10813 is a contradiction candidate for claim 5 | **Deferred.** Must be opened before any related-work text (A6 citation-verifier). |

## experiment-planner (RECOMMEND: E1; added after "approve G1")
| recommendation | response |
|---|---|
| E1 = P2 with 7 changes | P2 is being prepared per the human's Part A spec. Of the 7 changes: (1) fact:template **adopted** in the P2 model, with carrier and frame:carrier **proposed**; (2) fact+subject as one unit **adopted** (subject merged unless subjects recur); (3) final-token class factor and leave-one-frame-out **proposed** to the human; (4) primary = all cells **conflicts** with the human's spec (correct cells), so it is listed for the human; (5) outcome bands **conflict** with the human's thresholds, so they are listed for the human; (6) fresh facts: 74 of the 300 P2 facts were already in the G1/S3b set, **listed for the human**; (7) Pythia on GPU **listed for the human** (budget). |
| E2 (rest of the skeptic's tests) | Not run. Part (b), the two-stage or parametric bootstrap, is covered by the A4 simulation. |
