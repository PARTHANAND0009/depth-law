# GATE G2

Source of every number: `results/G2/G2-none-1e14c66-20261115T142350Z/g2.json` (run_id `G2-none-1e14c66-20261115T142350Z`). Plan: `notes/s6_plan.md` (CPU-scaled S6; deviations from the CLAUDE.md spec are listed there).

## Decision rule (configs/prereg.yaml g2)
PASS = Spearman(frequency, causal depth) < -0.5 on facts learned in all seeds.

| N facts learned in all 3 seeds | Spearman | p | outcome |
|---|---|---|---|
| 21 | -0.130 | 0.5735 | **FAIL** |

## Depth per frequency bin (facts learned in all seeds; depth = mean over seeds of the template-mean causal_final, (l+1)/8)

| freq | N | median | IQR |
|---|---|---|---|
| 16 | 1 | 0.722 | [0.722, 0.722] |
| 64 | 2 | 0.656 | [0.620, 0.693] |
| 256 | 18 | 0.646 | [0.564, 0.726] |

## Per seed

| seed | eval run | learned (of 2000) | learned share by freq (1/4/16/64/256) | Spearman on learned | N | final train loss |
|---|---|---|---|---|---|---|
| 1 | S6eval_mp4_seed1-final-e95c62f-20261115T044244Z | 116 | 0.01/0.01/0.04/0.07/0.17 | -0.191 | 116 | 4.100 |
| 2 | S6eval_mp4_seed2-final-d05ac5d-20261115T092826Z | 65 | 0.01/0.01/0.02/0.03/0.09 | -0.177 | 65 | 4.071 |
| 3 | S6eval_mp4_seed3-final-1e14c66-20261115T141646Z | 99 | 0.01/0.01/0.03/0.06/0.14 | -0.137 | 99 | 3.932 |

Training runs: results/S6/S6-s6lm_mp4_seed1-1a46b0d-20261115T001759Z, results/S6/S6-s6lm_mp4_seed2-e95c62f-20261115T044953Z, results/S6/S6-s6lm_mp4_seed3-d05ac5d-20261115T093510Z.

## Learnability (accuracy among the relation's 10 candidate objects; chance 0.1; N = 180 prompts per cell)

| seed | run | templates | freq 1 | 4 | 16 | 64 | 256 |
|---|---|---|---|---|---|---|---|
| 1 | S6learn-none-e95c62f-20261115T044858Z | train | 0.194 | 0.211 | 0.339 | 0.628 | 0.922 |
| 1 | same | eval | 0.133 | 0.183 | 0.150 | 0.239 | 0.422 |
| 2 | S6learn-none-d05ac5d-20261115T093445Z | train | 0.178 | 0.183 | 0.444 | 0.694 | 0.972 |
| 2 | same | eval | 0.150 | 0.128 | 0.267 | 0.289 | 0.506 |
| 3 | S6learn-none-1e14c66-20261115T142241Z | train | 0.239 | 0.189 | 0.406 | 0.672 | 0.972 |
| 3 | same | eval | 0.117 | 0.150 | 0.322 | 0.294 | 0.456 |

Files: `results/S6learn/<run>/learn.json`.

## Design history (notes/s6_plan.md)

- **v1 (failed, not used for G2):** one pass over a 40M-token stream. Seed 1 learned 4 of 2000 facts (`S6eval_seed1-final-e538cd9-20261113T163228Z`; learnability `S6learn-none-e538cd9-20261113T175744Z`: training-template candidate accuracy 0.272 at freq 256). Seeds 2 and 3 were not run.
- **mp4 (this gate):** the human chose a multi-pass pilot on 2026-11-15: 4 passes over a 10M-token stream, so each fact gets 4k exposures with the same bin ratios. The rule for continuing past the seed-1 pilot (>= 100 learned and >= 3 bins with >= 10 learned) was fixed before training and was met (116 learned; 16/26/68 learned at freq 16/64/256).

## Agent notes (interpretation; not part of the decision rule)

1. **Outcome: FAIL by the pre-registered rule.** Spearman -0.130 (p 0.5735), N = 21 facts learned in all 3 seeds, against the threshold -0.5. Threshold not changed.
2. **The test has almost no spread in frequency.** Of the 21 facts, 18 are at freq 256, 2 at freq 64 and 1 at freq 16. The gate statistic mostly compares depth within one bin, so it says little about depth vs frequency. I think the rule as written could not pass at this scale: requiring facts learned in all 3 seeds leaves almost only the top bin. I am not changing the rule; this is for the human.
3. **Per-seed Spearman on learned facts** (each seed's learned facts, all bins): -0.191 (N 116), -0.177 (N 65), -0.137 (N 99). All three are negative, the same sign as the hypothesis, but all are far above -0.5 and none was tested for significance here.
4. **Median depth by bin** (facts learned in all seeds): 0.722 (freq 16, N 1), 0.656 (freq 64, N 2), 0.646 (freq 256, N 18). The N values are too small to read a trend.
5. **Scale limits.** The model has 8 layers (10.5M parameters), so depth takes only 8 values per carrier. Facts are memorized on training templates (candidate accuracy 0.92-0.97 at freq 256) but carry over only partly to held-out paraphrases (0.42-0.51), and "learned" is judged on the paraphrases. The spec model (160M on 5B tokens) needs a GPU.

## Options for the human
- **GO G2**: record FAIL and continue to S7 (S7-S9 mostly need a GPU for 8B models).
- **PIVOT (a)**: re-run S6 at spec scale when a GPU is available. The G2 rule is unchanged.
- **PIVOT (b)**: a CPU follow-up with more exposures at the low bins (e.g. 8-16 passes), ~4.4 h per seed per 4 passes. This would be a further design change after seeing data.

## Status note (2026-11-20, recorded at the human's request)

- The human replied **"GO G2"** although the pre-registered outcome was **FAIL** (Spearman -0.130, N = 21, threshold -0.5; run `G2-none-1e14c66-20261115T142350Z`). The FAIL stands.
- **Claim 2 (controlled-frequency pretraining makes facts resolve earlier) is currently unsupported.**
  - The only test so far used a CPU-scaled 10.5M-parameter, 8-layer model.
  - The specified 160M / 5B-token run has not been done (needs a GPU; estimate in `reports/P1_compute.md`).
