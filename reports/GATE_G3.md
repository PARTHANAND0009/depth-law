# GATE G3

Decision rule (`configs/prereg.yaml` g3): the fact-level AUROC on non-adaptive ROME/MEMIT must be >= 0.8 (`fact_auroc_min: 0.8`).
Secondary targets: `locate_then_edit_auroc: 0.9`, `sft_auroc: 0.8`.
Detector, populations and score: `notes/s8_plan.md`, written before any S8 data. Model: pythia-1.4b. All runs on CPU.
Counts: EXACT only (v4_piletrain_llama). Rows without a count: 0.

## Gate number

| score | pool | N+ | N- | AUROC | 95% CI (bootstrap 1000) | >= 0.8 | source |
|---|---|---|---|---|---|---|---|
| s_maha (unsupervised, pre-registered primary) | rome_single + memit100 + memit1000, primary population | 1123 | 276 | 0.823 | [0.797, 0.848] | **PASS** on the point estimate; CI lower bound < 0.8 | `results/S8/S8-pythia-1.4b-aae6507-20261118T123031Z/summary.json` key `g3` (run_id `S8-pythia-1.4b-aae6507-20261118T123031Z`) |
| same, recomputed in the S9 scoring run | same | 1123 | 276 | 0.823 | [0.793, 0.848] | same | `results/S9score/S9score-pythia-1.4b-b70eba4-20261118T212041Z/summary.json` key `g3` |

- **Why the two CIs differ:** same inputs and point estimate. The CI differs only in bootstrap draws: one shared RNG, and more groups are scored before the pool in S9score.
- **CI not in the rule:** prereg.yaml states the rule on the AUROC with no CI condition.

## What drives the pass (same pool, N+ 1123, N- 276; S8 `auroc.csv`)

| single feature / baseline | AUROC [95% CI] |
|---|---|
| s_r_conf (confidence-vs-frequency residual) | 0.884 [0.862, 0.903] |
| s_maha (all four features) | 0.823 [0.797, 0.848] |
| s_lcf (LCF baseline) | 0.686 |
| s_d_profile | 0.667 |
| s_conf_rarity | 0.659 |
| s_abs_r_ll | 0.573 |
| s_perp | 0.566 |
| s_conf | 0.542 |
| s_abs_r_causal (depth residual, pre-registered sign-free) | 0.397 [0.358, 0.439] |
| s_r_causal (signed) | 0.344 |

The gate passes because of the confidence residual, not the depth residual.
- **Depth residual alone:** below 0.5.
- **Sign:** edited facts resolve earlier than the clean depth law predicts. That direction was not pre-registered.
- **Calibration slope:** the clean depth-law slope used by the detector is -0.00129 per log1p(count) unit (1000 facts / 3000 rows, `S3-pythia-1.4b-b9a353d-20261108T064941Z`).

## Secondary targets (s_maha, primary population; S8 run, attacks from S9score)

| target | model / pool | N+ | N- | s_maha | met |
|---|---|---|---|---|---|
| locate-then-edit >= 0.9 | rome_single | 100 | 114 | 0.911 | yes |
| | alphaedit100 | 100 | 76 | 0.924 | yes |
| | memit100 | 98 | 79 | 0.875 | no |
| | alphaedit1000 | 989 | 70 | 0.849 | no |
| | memit1000 | 925 | 83 | 0.780 | no |
| | locate family pooled | 2212 | 422 | 0.844 | no |
| SFT >= 0.8 | lora50 | 45 | 52 | 0.509 | no |
| | lora200 | 185 | 75 | 0.549 | no |
| | lora1000 | 957 | 90 | 0.607 | no |
| | synthdoc50 | 49 | 48 | 0.626 | no |
| | finetune family pooled | 1236 | 265 | 0.553 | no |

Locate-family and finetune-family values are from `results/S9score/S9score-pythia-1.4b-b70eba4-20261118T212041Z/auroc.csv`. Per-model values are the same in S8 and S9score.

## Adaptive attacker beside the gate number (S9; `reports/S9.md`)

| model | efficacy | N+ | N- | s_maha [95% CI] | s_r_conf | vs non-adaptive twin |
|---|---|---|---|---|---|---|
| G3 pool (non-adaptive) | – | 1123 | 276 | 0.823 [0.797, 0.848] | 0.884 | – |
| rome_single (twin of A1, A2) | 1.00 | 100 | 114 | 0.911 [0.871, 0.949] | 0.936 | – |
| A1 layer match | 1.00 | 100 | 117 | 0.904 [0.861, 0.942] | 0.926 | -0.007 |
| A2 depth-reg loss | 1.00 | 100 | 115 | 0.820 [0.759, 0.874] | 0.911 | -0.091 |
| synthdoc50 (twin of A3) | 0.98 | 49 | 48 | 0.626 [0.509, 0.726] | 0.640 | – |
| A3 frequency spoof | 0.96 | 48 | 61 | 0.732 [0.636, 0.822] | 0.752 | +0.106 |
| adaptive family pooled | – | 248 | 293 | 0.808 [0.768, 0.845] | 0.861 | – |

Sources:
- AUROCs: `results/S9score/S9score-pythia-1.4b-b70eba4-20261118T212041Z/auroc.csv`.
- Efficacy: `results/S9/S9-pythia-1.4b-aae6507-20261118T124110Z/a{1,2}_*/report.json`, the `a3_model` log event, and `reports/S7.md`.

Collateral and compute: `reports/S9.md`.

## MISSING
- MISSING: model-level AUROC. Only one clean model of this architecture exists (`summary.json` `model_level_auroc`).
- MISSING: recall-vs-two-hop depth gap feature. No two-hop prompts were built (CPU budget).
- MISSING: tuned-lens features. There is no pretrained lens for pythia-1.4b (HF 404), and none was trained.
- MISSING: s_lcf for A1-A3. The LCF hidden-state pass was not run on the attack models.
- MISSING: ROME seconds per edit for rome_single (not logged in S7).
- Scale: the gate runs on pythia-1.4b only (CPU tier). No 7-8B models, and no GPU zoo.

## Notes for the decision (rule 5: no threshold changed)
- The pre-registered rule passes on its point estimate (0.823 >= 0.8), but the CI lower bound (0.797) is below 0.8.
- The pass comes from the r_conf feature inside s_maha. That feature was pre-registered (notes/s8_plan.md), but it is not depth. The depth feature the project is about scores below 0.5. This is consistent with the flat depth-frequency slope in the calibration fit and with G2 FAIL.
- In my view the gate as written does not test whether depth adds detection signal. A reader should not take the G3 pass as evidence that depth residuals detect tampering. I am not changing the rule; I am stating this so you can weigh it.
- Of the secondary targets, locate-then-edit >= 0.9 is met by 2 of 5 models, and SFT >= 0.8 by 0 of 4.

## Waiting for "GO G3" or "PIVOT <option>"
Nothing else runs until you reply. S5/S4T stay paused on `results/HOLD_S5`.
Options I see (yours to choose):
- **GO G3:** resume S5 checkpoint dynamics and the S4 Gemma transfer, then S10 figures.
- **PIVOT confidence:** reframe S8 around the confidence-frequency residual, with depth reported as a negative or null feature. This needs no new runs; it changes the report framing.
- **PIVOT stop:** write up G1/G2/G3 as they stand and skip the remaining stages.

## Human decision

2026-11-19: the human replied **"GO G3"**. G3 stands as reported above (PASS on the point estimate, driven by r_conf).
Next: `results/HOLD_S5` removed; S5 checkpoint dynamics resume (pythia-2.8b from step4000, resuming from its chunks),
then S4 transfer on gemma-3-4b-pt (causal-only), then S10 figures.

## Status note (2026-11-20, recorded at the human's request)

- **The detector's signal comes from the confidence-vs-frequency residual, not from depth.**
  - On the G3 pool (N+ 1123, N- 276), the depth residual alone scores AUROC 0.397 [0.358, 0.439] (s_abs_r_causal); the signed depth residual scores 0.344.
  - The confidence-frequency residual alone scores 0.884 [0.862, 0.903], higher than the combined s_maha (0.823).
  - Source: `results/S8/S8-pythia-1.4b-aae6507-20261118T123031Z/auroc.csv`.
- G3 passes the pre-registered rule on its point estimate, but it is not evidence that depth residuals detect edited facts.
- **Claim 3 as stated (depth residuals flag edited facts) is currently unsupported.**
