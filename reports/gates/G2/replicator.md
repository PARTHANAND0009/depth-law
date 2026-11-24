<!-- replicator subagent (.claude/agents/replicator.md), fresh context, 2026-11-24, gate G2 (P2 results), on reports/p2/RESULTS.md and the raw results/P2/ run dirs. Saved verbatim by the main session; not edited. -->
# G2 replicator report: P2 confirmatory set `correct`

Every number in `reports/p2/RESULTS.md` sections 2–5 that I could recompute matches within tolerance, and there are no count mismatches. All five runs pass the completeness rule; only Llama-3.1-8B and OLMo-2-1124-7B pass the minimum-data rule.

**What I computed myself:** completeness and inclusion, D1–D4 per curve, the covariates (re-tokenised with the cached Llama and OLMo tokenizers), the MoM residualisation and cell means, H3 and the decision logic. All of it comes from the raw `results/P2/*/chunks/{b,c}*.parquet`, `manifest.json`, `log.jsonl`, `meta.json` and `materials/*.jsonl`.

**What I reused:** only `p2_formula`, `p2_prep`, `p2_fit` and `p2_shares` from `analysis/p2/p2_model.R`, and `henderson3` from `analysis/p2/p2_mom.py`.

**What I did not run:** bootMer and the 1000-dataset null were not rerun. Every job was point-estimate only and run under `nice -n 10`; each took under 10 s.

## 1. Inclusion (prereg §1, §3)
For every run I checked:
- every manifest sha256 recomputed matches, and no parquet file is missing from the manifest;
- the last log event is `done` with all_ok and n_facts = 300;
- all 3000 fact × paraphrase cells are present in both b and c, with no duplicates and no NaN p;
- every cell has carriers {0,1,2};
- every curve has a single, complete layer set;
- the `start` events name the right model with float32;
- meta revision is `main`.

| model | complete (reported / mine) | facts ≥2 correct (reported / mine) | relations (reported / mine) | status (reported / mine) |
|---|---|---|---|---|
| Qwen3-8B | yes / yes | 125 / 125 | 20 / 20 | MISSING insufficient / same |
| Llama-3.1-8B | yes / yes | 196 / 196 | 20 / 20 | ok / ok |
| pythia-1.4b | yes / yes | 91 / 91 | 17 / 17 | MISSING insufficient / same |
| pythia-2.8b | yes / yes | 93 / 93 | 17 / 17 | MISSING insufficient / same |
| OLMo-2-1124-7B | yes / yes | 205 / 205 | 20 / 20 | ok / ok |

nc = 3 for both included models.

## 2. Primary quantities (set `correct`)
"Reported" is the RESULTS.md value, which matches the JSON value it was read from. The difference is against the 3-dp RESULTS.md value. Against the full-precision JSON, every REML share differs by ≤ 7.3e-5, and the MoM values agree to about 1e-15.

| quantity | reported | recomputed | abs diff |
|---|---|---|---|
| Llama rows / facts | 3663 / 222 | 3663 / 222 | 0 / 0 |
| Llama correct cells (MoM n_cells) | 1221 | 1221 | 0 |
| Llama ICC(1) D1 | 0.310 | 0.31006 | 0.0001 |
| Llama wording D1 | 0.649 | 0.64915 | 0.0002 |
| Llama diff D1 | 0.339 | 0.33910 | 0.0001 |
| Llama MoM diff D1 | 0.392 | 0.39192 | 0.0001 |
| Llama ICC(1) D4 | 0.282 | 0.28239 | 0.0004 |
| Llama wording D4 | 0.678 | 0.67805 | 0.0001 |
| Llama diff D4 | 0.396 | 0.39566 | 0.0003 |
| Llama MoM diff D4 | 0.406 | 0.40599 | 0.0000 |
| Llama n′ (G = 0.8, D1) | 8 | 8 | 0 |
| Llama G ceiling D1 | 0.957 | 0.95740 | 0.0004 |
| Llama (rt+frame)−(ft+e/nc) D1 | −0.323 | −0.32297 | 0.0000 |
| Llama singular D1/D4; warnings | False/False; 0 | False/False; 0 | — |
| Llama curves p_final = 0 / < 1e-4 | 0 / 369 | 0 / 369 | 0 / 0 |
| OLMo rows / facts | 4065 / 219 | 4065 / 219 | 0 / 0 |
| OLMo correct cells | 1355 | 1355 | 0 |
| OLMo ICC(1) D1 | 0.422 | 0.42182 | 0.0002 |
| OLMo wording D1 | 0.546 | 0.54601 | 0.0000 |
| OLMo diff D1 | 0.124 | 0.12419 | 0.0002 |
| OLMo MoM diff D1 | 0.203 | 0.20269 | 0.0003 |
| OLMo ICC(1) D4 | 0.373 | 0.37267 | 0.0003 |
| OLMo wording D4 | 0.612 | 0.61188 | 0.0001 |
| OLMo diff D4 | 0.239 | 0.23920 | 0.0002 |
| OLMo MoM diff D4 | 0.265 | 0.26522 | 0.0002 |
| OLMo n′ (G = 0.8, D1) | 4 | 4 | 0 |
| OLMo G ceiling D1 | 0.990 | 0.98988 | 0.0001 |
| OLMo (rt+frame)−(ft+e/nc) D1 | −0.168 | −0.16841 | 0.0004 |
| OLMo singular D1/D4; warnings | False/False; 0 | False/False; 0 | — |
| OLMo curves p_final = 0 / < 1e-4 | 0 / 372 | 0 / 372 | 0 / 0 |

**D1 share of total variance (Llama / OLMo):**

| component | reported | recomputed | max abs diff |
|---|---|---|---|
| fact | .285 / .368 | .2850 / .3679 | 0.0001 |
| relation | .081 / .128 | .0808 / .1277 | 0.0003 |
| frame | .032 / .065 | .0322 / .0653 | 0.0003 |
| rt | .130 / .112 | .1302 / .1116 | 0.0004 |
| ft | .434 / .299 | .4344 / .2994 | 0.0004 |
| fc | .013 / .004 | .0127 / .0038 | 0.0003 |
| residual | .025 / .024 | .0248 / .0243 | 0.0003 |

**Extra, not requested: D2/D3, my own curves and REML fits.**

| quantity | reported | recomputed | max abs diff |
|---|---|---|---|
| Llama D2 rows; ICC(1), diff | 3564; .406, .142 | 3564; .4060, .1422 | 0.0002 |
| Llama D3 rows; ICC(1), diff | 3663; .172, .609 | 3663; .1723, .6095 | 0.0005 |
| OLMo D2 rows; ICC(1), diff | 3933; .275, .428 | 3933; .2747, .4278 | 0.0003 |
| OLMo D3 rows; ICC(1), diff | 4065; .290, .384 | 4065; .2903, .3839 | 0.0003 |

- **D1/D4 per curve:** my values equal those in `long_*_correct.csv` exactly (max abs diff 0.0) on all 3663 + 4065 rows.
- **Post-hoc patch-identity check (prereg §10):** at the last layer, |p_final − exp(obj_first_logprob)| ≤ 2.45e-4, which is float16 precision.
- **`correct_at1` against the curves:** it equals "rank 1 at the last layer" for all 9000 curves of each model (0 disagreements).

## 3. CIs (read check only)
Every CI in RESULTS.md §3 matches `fit_*_correct_D{1,2,3,4}.json` `boot.ci` to 3 dp. That covers ICC(1), wording, diff, tf_minus_resid and n′ for D1/D4, plus ICC(1) and diff for D2/D3. The D1/D4 CIs in `p2_decision.json` are identical. Every fit has 0 failed bootstrap refits (n_boot 1000).

## 4. H3
| quantity | reported | recomputed | abs diff |
|---|---|---|---|
| N common facts | 190 | 190 | 0 |
| Spearman ρ (fact-mean D1) | 0.373 | 0.37265 | 0.0003 |
| k̄ Llama / OLMo | 5.50 / 6.19 | 5.500 / 6.187 | 0.000 / 0.003 |
| G(k̄) Llama / OLMo | 0.748 / 0.868 | 0.74770 / 0.86773 | 0.0003 / 0.0003 |
| disattenuated ρ | 0.463 | 0.46264 | 0.0004 |

## 5. Decision flags (`p2_decision.json`), checked against the numbers and prereg §5–6
- **H1:**
  - Llama is True: the diff CI lower bounds are 0.220 (D1) and 0.259 (D4), both > 0, and MoM diff is 0.392 / 0.406, both > 0.
  - OLMo is False: the D1 diff CI lower bound is −0.004, which does not exclude 0. Consistent.
- **H1-alt:** False for both models, since ICC(1) is < 0.5 for D1 and D4. Consistent.
- **Family counts:** H1 holds in 1 family {llama31} and H1-alt in 0, so the H1 claim, H1-alt claim, model-dependent and fact-depth-unexplained are all False. Consistent.
- **No fixed layer:** the ICC(1) D1 upper CIs are 0.370 and 0.487, both ≥ 0.15, so False. Consistent.
- **Single prompt poor:** Llama has H1 and n′ = 8 ≥ 8, but that is only 1 family, so False. Consistent.
- **Wording shifts together:** tf − resid is < 0 for both models, so False. Consistent.
- **Fact share > 0:** both null files have n_failed = 0 and n_sim = 1000. The maximum null ICC(1) is 0.0553 (Llama) and 0.0458 (OLMo), below the observed 0.3101 and 0.4219. That gives 0 exceedances, so p = 1/1001 = 0.000999 < 0.01 in 2 families, and True. Consistent.
  - The observed values in the null files match my REML ICC(1) within 4e-5.
  - The null distribution itself was not recomputed, per the compute limit.

## 6. Definitional ambiguities
1. **Covariate z-scoring.** Prereg §4 says "fact-level and z-scored within model × set", which does not say over what.
   - The project z-scores over carrier-level rows (ddof = 1); I matched its CSV exactly under that convention.
   - I z-scored over unique facts instead. My raw token counts, cooc and answer_prior are identical to the project's, up to that affine map.
   - REML variance components and the OLS residualisation do not change under an affine rescaling of covariates. My shares differ only by optimizer noise (≤ 7.3e-5), so this choice does not change any number.
2. **The `correct` set includes facts with only 1 correct paraphrase.** Llama has 222 facts, of which 196 have ≥ 2; OLMo has 219, of which 205 have ≥ 2. The prereg uses "≥ 2 correct" only as an inclusion threshold for the model, and the reported numbers follow that reading.
   - If H3 were restricted to facts with ≥ 2 correct paraphrases in both models, N = 169 and ρ = 0.456 (vs 0.373).
   - k̄ also includes the single-paraphrase facts.
3. **Fact-level mean D1 for H3.** I used the mean over all rows of the fact. This equals the mean of cell means, because every cell has 3 carriers.
4. **n_subject_tokens.** I counted without a leading space only when the template starts with "{}" (all of frame 0 and 19 of 20 frame-8 templates), and with a leading space otherwise. This reproduced the project's counts exactly (correlation 1.0).
5. **D4's mean over layers** includes the final layer, which contributes 1. **D1's comparison** was done on float16 values cast to float64, which is exact. Both choices reproduce the stored D1/D4 exactly.

## Files
Scratch directory: /tmp/claude-0/-home-user-depth-law/79d106ca-74b7-5e19-8ef3-6880f992c1ff/scratchpad/g2rep/

| file | what it does |
|---|---|
| s1_inclusion.py, s1_inclusion.json | completeness and minimum-data checks |
| s2_build.py, tab_llama.csv, tab_olmo.csv, s2_summary.json | builds the analysis tables, curves and covariates |
| s3_reml.R, s3_reml.json | REML point fits for D1/D4 |
| s4_mom_h3.py, s4_mom_h3.json | MoM diffs and H3 |
| s5_d2d3.py, s5_d2d3.R | extra D2/D3 curves and fits |

No repo file was edited.

VERDICT: PASS
