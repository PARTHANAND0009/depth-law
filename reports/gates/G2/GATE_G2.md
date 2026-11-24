# GATE G2: P2 (prompt vs fact in answer-readout depth)

STATUS: AWAITING GO G2. No paper text. (This is the P2 gate; `reports/GATE_G2.md` is the older S6 gate and is unchanged.)

Sources: every number below is copied from `reports/p2/RESULTS.md` (generated from results files by `analysis/p2/p2_results_md.py`, last ledger RUN line 127), which reads `results/P2analysis/correct/p2_results.json` and `p2_decision.json` (gating call: ledger RUN "P2 analysis: set correct", utc_start 2026-11-24T17:37:58Z, exit 0). Prereg `prereg/P2_prompt_vs_fact.md`, tag prereg-P2 = ff119ca. One deviation: `prereg/deviations/D-P2-20261124T044034Z-0.md` (off-instance copy mechanism; no measurement change). Run ids: `P2-Llama-3.1-8B-ff119ca-20261124T164743Z`, `P2-OLMo-2-1124-7B-ff119ca-20261124T171447Z` (and the three MISSING models in RESULTS §1).

Measure: final-token residual of each paraphrase patched into the final token of 3 neutral carriers; depth = layer of answer readout at the prediction position (D1 primary, D4 robustness). Subject position not patched. Correct cells only. Bootstrap: parametric bootMer, 1000; null: 1000 parametric datasets; seed 20261121.

## 1. Inclusion
| model | facts with ≥ 2 correct paraphrases (of 300) | relations | status |
|---|---|---|---|
| Qwen/Qwen3-8B | 125 | 20 | MISSING (insufficient data) |
| meta-llama/Llama-3.1-8B | 196 | 20 | included |
| EleutherAI/pythia-1.4b | 91 | 17 | MISSING (insufficient data) |
| EleutherAI/pythia-2.8b | 93 | 17 | MISSING (insufficient data) |
| allenai/OLMo-2-1124-7B | 205 | 20 | included |

Rule: ≥ 150 facts and ≥ 15 relations. Two families included; every family-level claim needs both.

## 2. Per model (set `correct`; 95% parametric bootstrap CIs)
| quantity | Llama-3.1-8B | OLMo-2-1124-7B |
|---|---|---|
| N rows / facts | 3663 / 222 | 4065 / 219 |
| ICC(1) D1 [CI] | 0.310 [0.242, 0.370] | 0.422 [0.347, 0.487] |
| ICC(1) band D1 (descriptive) | mixed | moderately fact-stable (CI spans the 0.4 edge into "mixed") |
| ICC(1) D4 [CI] | 0.282 [0.216, 0.349] | 0.373 [0.295, 0.444] |
| ICC(1) band D4 (descriptive) | mixed | mixed |
| diff D1 [CI] | 0.339 [0.220, 0.474] | 0.124 [−0.004, 0.272] |
| diff D4 [CI] | 0.396 [0.259, 0.526] | 0.239 [0.095, 0.397] |
| MoM diff D1 / D4 (direction check) | 0.392 / 0.406 | 0.203 / 0.265 |
| **H1 / H1-alt / neither** | **H1 condition met** | **neither** (H1 not established: D1 diff CI lower bound −0.004) |
| H1-alt | not met (ICC(1) < 0.5) | not met (ICC(1) < 0.5) |
| n′ for G = 0.8 (D1) [CI] (estimation only) | 8 [6, 13] | 4 [3, 5] |
| G ceiling (D1) | 0.957 | 0.990 |
| (rt + frame) − (ft + e/nc) D1 [CI] | −0.323 [−0.431, −0.223] | −0.168 [−0.264, −0.053] |
| fact-share null p (D1) / failed refits | ≤ 0.001 (floor 1/1001) / 0 | ≤ 0.001 (floor 1/1001) / 0 |
| singular fits D1/D4; warnings D1 | no / no; 0 | no / no; 0 |

OLMo: a boundary non-result. The stats-reviewer (finding 6) estimates the Monte Carlo SE of the CI end at about 0.006 (its approximation), so the family-level H1 = False is fragile to Monte Carlo error; the recorded decision stands (seed and B preregistered; no rerun). It is not evidence of fact dominance (H1-alt fails) or of a difference between models (no between-model test was preregistered; the diff CIs overlap). A flip would not change any section 6 headline (OLMo n′ = 4 < 8; tf − resid < 0 in both).

## 3. Family-level claims (`p2_decision.json`)
| rule | result |
|---|---|
| H1 in ≥ 2 families | False (1 of 2: llama31) |
| H1-alt in ≥ 2 families | False (0 of 2) |
| model-dependent | False |
| no fixed layer (ICC(1) D1 upper < 0.15) | False |
| single prompt poor (H1 and n′ ≥ 8) | False |
| wording shifts together (H1 and tf > resid) | False |
| fact depth unexplained (H1-alt) | False |
| fact share > 0 (null p < 0.01) | **True** (2 of 2) |

**Permitted headline sentence (prereg section 6, verbatim): "The fact share is above zero."**
Scope required with it: Llama-3.1-8B and OLMo-2-1124-7B only; answer-readout depth at the final position, correct cells only; conditional on the four covariates and the carrier effect; the fact component includes answer-token identity (no relation × object term); the null was mildly liberal in calibration (0.020 at p < 0.01) with power 0.46 at a fact share of 0.10 (prereg section 10). It does not say the fact share is large or fixed, or that facts have their own depth. Every other sentence is unlicensed; the prereg rule is to report the shares and n′ as an intermediate result.

## 4. Cross-model ρ (H3, estimation only)
| pair | N facts | Spearman ρ (fact-mean D1) | k̄ | G(k̄) | disattenuated (approx.) |
|---|---|---|---|---|---|
| Llama vs OLMo | 190 | 0.373 | 5.50, 6.19 | 0.748, 0.868 | 0.463 |

No interval preregistered. G(k̄) assumes equal k and overstates reliability, so 0.463 is under-corrected; ρ pools across relations; single-correct-paraphrase facts are included (RESULTS §5).

## 5. Reviewer verdicts
| reviewer | verdict | blocking | file |
|---|---|---|---|
| replicator | PASS | — | `reports/gates/G2/replicator.md` |
| stats-reviewer | REVISE | none | `reports/gates/G2/stats-reviewer.md` |
| skeptic | REVISE ("reject as it stands" as a paper claim) | n/a | `reports/gates/G2/skeptic.md` |
| claim-auditor | REVISE | n/a | `reports/gates/G2/claim-auditor.md` |

All REVISE items were reporting or interpretation fixes; responses in `reports/gates/G2/responses.md`. RESULTS.md was regenerated after the reviews (reporting only; ledger lines 121–127); no gating number or flag changed. The revised RESULTS.md was not re-reviewed.

Skeptic's main points (accepted as scope limits; its own [scratch] numbers are not reported here):
- The measure is readout depth at the prediction position, not "where a fact lives".
- The wording share is mostly the fact × paraphrase interaction, not a shift common to all facts (consistent with tf − resid < 0 above).
- The licensed sentence was close to foreknown, and the fact component includes answer-token identity.
- D1 and D4 come from one curve; the fact share varies across D1–D4, so no cross-model fact-stability comparison.
- The two included models tokenize answers the same way (reviewer's observation), which weakens "≥ 2 families" for token-driven effects.

## 6. MISSING
- Qwen3-8B, pythia-1.4b, pythia-2.8b: MISSING (insufficient data).
- Robustness simulation (prereg section 4; non-selecting): MISSING, not run.
- H4 cross-family comparison (EXPLORATORY): MISSING (needs the missing models).

## 7. Options for the human (none started)
1. GO G2: accept P2 as recorded (one licensed sentence; everything else intermediate).
2. Run the preregistered robustness simulation (CPU; code to be committed before it runs; cannot change any decision). Would run only when no other heavy job runs (S5 is running).
3. The skeptic's suggested experiment: same design with subject-last-token patching and a (1|relation:object) term, on Llama and OLMo. Needs a new preregistration (or amendment) and GPU time; INR left: 386 (human figure, PROGRESS.md). Skeptic's cost estimate: under an hour of GPU for two models (its estimate, not measured).

Background: S5 (pythia-2.8b step96000) is running under the standing authorization.
