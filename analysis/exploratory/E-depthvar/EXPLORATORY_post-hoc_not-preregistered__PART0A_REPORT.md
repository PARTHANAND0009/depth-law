# EXPLORATORY (post hoc, not preregistered) — Part 0a: leave-one-relation-out jackknife and company_ceo diagnostics

- **Source:** `results/EXPLORATORY_E-depthvar/EXPLORATORY_E-depthvar-none-321939b-20261121T153451Z/part0a/EXPLORATORY_post-hoc_not-preregistered__part0a.json`.
- **Fit:** set (i) correct cells, lme4 REML, the B3 model; convergence checks ON. diff = (template-main + residual) − (fact+subject), shares of total including relation.
- **Pre-logged criterion:** OLMo D1 diff <= 0 in > 13 of 26 leave-one-relation-out fits -> STOP. Result: STOP = False.

| EXPLORATORY (post hoc, not preregistered) model | def | full diff | LOO diff min / median / max | LOO fits with diff ≤ 0 | full ICC(1) | LOO ICC(1) min / median / max | most influential relations (change in diff) | singular LOO fits |
|---|---|---|---|---|---|---|---|---|
| pythia-1.4b | D1 | -0.023 | -0.194 / -0.018 / 0.054 | 22/26 | 0.513 | 0.470 / 0.510 / 0.625 | developer -0.171; manufacturer -0.102; capital +0.077 | 0 |
| pythia-1.4b | D4 | -0.200 | -0.310 / -0.198 / -0.162 | 26/26 | 0.630 | 0.606 / 0.628 / 0.738 | developer -0.110; music_genre -0.051; manufacturer -0.039 | 1 |
| pythia-2.8b | D1 | -0.085 | -0.163 / -0.084 / -0.054 | 26/26 | 0.563 | 0.541 / 0.563 / 0.621 | native_language -0.078; headquarters +0.031; capital +0.025 | 3 |
| pythia-2.8b | D4 | -0.186 | -0.279 / -0.184 / -0.162 | 26/26 | 0.638 | 0.621 / 0.637 / 0.708 | native_language -0.093; capital +0.023; continent +0.020 | 3 |
| OLMo-2-1124-7B | D1 | 0.199 | 0.009 / 0.205 / 0.264 | 0/26 | 0.377 | 0.339 / 0.374 / 0.494 | company_ceo -0.190; official_language +0.065; citizenship -0.059 | 2 |
| OLMo-2-1124-7B | D4 | 0.203 | 0.002 / 0.207 / 0.297 | 0/26 | 0.369 | 0.313 / 0.367 / 0.498 | company_ceo -0.201; official_language +0.094; citizenship -0.050 | 2 |

**Relations with |leave-one-out influence on the diff| > 0.1 in any model × def:** company_ceo, developer, manufacturer.

## EXPLORATORY (post hoc, not preregistered): company_ceo diagnostics

- **Templates:** ['The CEO of {} is', '{} is led by its CEO,', 'The chief executive officer of {} is'].
- **Self-readout depth:** the half-probability rule on the stored logit-lens probability of the object first token at the fact prompt's own final position (no carrier). It is a lens readout, not a causal patch, so its scale is not comparable to D1.

| EXPLORATORY (post hoc, not preregistered) model | template | correct / all cells | mean D1 (correct) | mean D4 (correct) | D1 per carrier | share D1 ≥ 0.95 | self-readout half-prob depth (correct) | logit-lens rank-1 depth (correct) |
|---|---|---|---|---|---|---|---|---|
| pythia-1.4b | 0 | 2 / 50 | 0.764 | 0.743 | 0.792 / 0.729 / 0.771 | 0.000 | 0.958 | 0.979 |
| pythia-1.4b | 1 | 4 / 50 | 0.715 | 0.683 | 0.719 / 0.729 / 0.698 | 0.000 | 1.000 | 0.979 |
| pythia-1.4b | 2 | 1 / 50 | 0.722 | 0.724 | 0.750 / 0.667 / 0.750 | 0.000 | 1.000 | 1.000 |
| pythia-1.4b | all | correct cells with D1 ≥ 0.95 in the whole model: 2, of which company_ceo: 0 | | | | | | |
| pythia-2.8b | 0 | 1 / 50 | 0.750 | 0.689 | 0.750 / 0.750 / 0.750 | 0.000 | 0.969 | 0.969 |
| pythia-2.8b | 1 | 8 / 50 | 0.668 | 0.656 | 0.660 / 0.688 / 0.656 | 0.000 | 0.988 | 0.949 |
| pythia-2.8b | 2 | 1 / 50 | 0.750 | 0.703 | 0.750 / 0.750 / 0.750 | 0.000 | 0.969 | 0.875 |
| pythia-2.8b | all | correct cells with D1 ≥ 0.95 in the whole model: 0, of which company_ceo: 0 | | | | | | |
| OLMo-2-1124-7B | 0 | 6 / 50 | 0.649 | 0.614 | 0.677 / 0.589 / 0.682 | 0.000 | 0.932 | 0.927 |
| OLMo-2-1124-7B | 1 | 11 / 50 | 0.991 | 0.947 | 0.994 / 0.989 / 0.991 | 1.000 | 1.000 | 0.997 |
| OLMo-2-1124-7B | 2 | 12 / 50 | 0.701 | 0.671 | 0.703 / 0.674 / 0.724 | 0.000 | 0.953 | 0.948 |
| OLMo-2-1124-7B | all | correct cells with D1 ≥ 0.95 in the whole model: 11, of which company_ceo: 11 | | | | | | |

## Reading (numbers only)
- **OLMo:** the diff stays > 0 in every leave-one-relation-out fit. Its minimum is the fit without company_ceo; the full-fit value and the minimum are in the table.
- **company_ceo, OLMo template 1** ("{} is led by its CEO,"):
  - Carrier-patched D1 is near 1.0 on all three carriers.
  - Self-readout is near 1.0 for all three company_ceo templates, in every model. It therefore does not separate template 1 from its siblings, and does not confirm or refute the carrier-transfer explanation.
- **Skeptic's confirm/refute test:**
  - It needed self-readout ≈ 0.61 for template 1. The lens readout is late for every template, so the test as stated is inconclusive.
  - The leave-one-relation-out part of the test is answered by the table.
