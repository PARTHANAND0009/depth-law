# GATE A2: amended primary test (half_prob_depth), 3 gate models

- **Pre-registration:** `configs/prereg_amendment_2026-11-20.yaml` (amendment_2, committed c0a7825 before any gate-model computation). Thresholds are the g1 thresholds in `configs/prereg.yaml`, unchanged.
- **Source of every number:** `results/A2/A2-none-a7dfeb5-20261121T065218Z/a2.json` (run_id `A2-none-a7dfeb5-20261121T065218Z`), unless another file is named.
- **Depth runs** (branch `gpu-olmo-run`, merged fast-forward into master at 5a0f36e):
  - `S3b-OLMo-2-1124-7B-923945f-20261121T061237Z`
  - `S3b-pythia-1.4b-a7dfeb5-20261121T063528Z`
  - `S3b-pythia-2.8b-a7dfeb5-20261121T064110Z`
- **Counts:** EXACT only. OLMo-2 uses `v4_olmo-mix-1124_llama`; Pythia uses `v4_piletrain_llama`. Each model was fitted separately.

## Decision

| model | N rows / facts / relations | partial R² [95% CI] | slope cooc_within [95% CI] | p | p (Holm) | outcome |
|---|---|---|---|---|---|---|
| OLMo-2-1124-7B | 3900 / 1300 / 26 | -0.0261 [-0.0524, 0.0135] | +0.0056 [-0.0003, 0.0111] | 0.0085 | 0.0085 | FAIL |
| pythia-1.4b | 3900 / 1300 / 26 | 0.0061 [-0.0602, 0.0152] | +0.0130 [0.0047, 0.0174] | 1.1e-08 | 3.2e-08 | FAIL |
| pythia-2.8b | 3900 / 1300 / 26 | -0.0141 [-0.0473, 0.0162] | +0.0114 [0.0033, 0.0167] | 1.4e-07 | 2.8e-07 | FAIL |

- **Rule:**
  - Per model: PASS if partial R² ≥ 0.10 and slope < 0; WEAK if partial R² ≥ 0.05 and slope < 0; otherwise FAIL.
  - Overall: GO if ≥ 2 of 3 models PASS; WEAK if PASS + WEAK ≥ 2; otherwise NO-GO.
- **Result: 0/3 PASS, 0/3 WEAK. Outcome under the amended prereg: NO-GO.**
- **CIs:** relation-cluster bootstrap, 1000 resamples, seed 1234. There were 0 failed resamples per model.
- **Slope units:** normalized depth per log1p unit of within-relation EXACT co-occurrence.

### What the numbers show
- **The slope is positive in all 3 models.** Within a relation, facts with more subject-object co-occurrence reach half their final patched probability *later*, not earlier. This is the opposite of the hypothesis.
  - The Pythia slopes survive Holm, and their bootstrap CIs exclude 0.
  - For OLMo-2 the model p is 0.0085, but the cluster-bootstrap CI includes 0.
- **The outcome does not depend on the partial R² definition.** Every model fails on the slope sign alone.
- **Partial R² is ≤ 0.006 in every model** and negative in two.
  - Marginal R², full vs reduced model: OLMo-2 0.1959 vs 0.2220; pythia-1.4b 0.2826 vs 0.2765; pythia-2.8b 0.2421 vs 0.2562.
  - It goes negative because the full model adds a random slope, and that slope's variance enters the denominator of the marginal R².
  - I flagged this possibility before the run (`reports/A2_PRIMARY_DRYRUN.md`). The threshold was not changed (rule 5).
- **All 21 non-gating sensitivity fits** (7 variants × 3 models) also have a positive slope. The largest partial R² is 0.0191 (pythia-2.8b, original prereg controls, unsplit cooc).

## Descriptives (fit rows; from a2.json)

| model | correct@1 | median depth correct / wrong | Spearman with log cooc, raw / within relation | Spearman with obj logprob | share of rows where patched final p > carrier-alone p |
|---|---|---|---|---|---|
| OLMo-2-1124-7B | 0.363 | 0.625 / 0.562 | 0.102 / 0.129 | 0.295 | 0.980 |
| pythia-1.4b | 0.185 | 0.667 / 0.625 | 0.113 / 0.145 | 0.469 | 0.935 |
| pythia-2.8b | 0.206 | 0.594 / 0.531 | 0.120 / 0.166 | 0.435 | 0.940 |

N = 3900 rows per model. The row-level Spearman values treat a fact's 3 templates as independent.

## Sensitivities (not gating)

| variant | OLMo-2: N, partial R², slope | pythia-1.4b | pythia-2.8b |
|---|---|---|---|
| drop rows where final p ≤ carrier-alone p | 3822, -0.0182, +0.0052 | 3645, -0.0070, +0.0133 | 3667, -0.0085, +0.0105 |
| + margin | 3900, -0.0276, +0.0056 | 3900, 0.0054, +0.0130 | 3900, -0.0153, +0.0114 |
| + template and subject intercepts | 3900, 0.0066, +0.0043 | 3900, 0.0042, +0.0104 | 3900, 0.0042, +0.0093 |
| original prereg controls, cooc unsplit | 3900, 0.0189, +0.0102 | 3900, 0.0166, +0.0167 | 3900, 0.0191, +0.0160 |
| correct@1 rows only | 1414, 0.0012, +0.0032 | 720, -0.0519, +0.0051 | 804, -0.0071, +0.0073 |
| secondary: causal_final (resolved rows) | 1414, -0.0493, +0.0065 | 720, -0.1229, +0.0094 | 804, -0.1117, +0.0118 |
| secondary: logit_lens_depth (resolved rows) | 1414, -0.0130, +0.0012 | 720, -0.0274, +0.0030 | 804, -0.0476, +0.0026 |

p-values are in `reports/A2_PRIMARY_gpu_20261121T065217Z.md` and in a2.json.

## Completeness checks (done 2026-11-21 on this machine, CPU)

| check | result |
|---|---|
| rows per depth parquet | 3900 per model; 1300 facts × 3 templates; the fact set equals `data/facts_g1cpu.parquet`; 26 relations |
| half_prob_depth | 0 NaN in all 3 models; 3 per-carrier values per row; range OLMo 0.031–1.000, pythia-1.4b 0.042–0.958, pythia-2.8b 0.031–0.938 |
| run settings (log.jsonl) | fp32, cuda:0, tuned lens off, 52/52 chunks, revision main; n_layers 32 / 24 / 32 |
| weights | OLMo-2: 6 hub shards. Pythia: hub main (`weights_shard0.json`) |
| fit | 3900 rows fitted per model; full and reduced models converged; bootstrap 0/1000 failures; all 7 sensitivities present (none MISSING) |
| CPU reproduction of point estimates | `stats.amend2.analyse` re-run here from the 3 parquets with n_boot 0: partial R², slope and p match a2.json to 6 decimals in all 3 models. The bootstrap was not re-run |
| GPU vs CPU S3, Pythia, same 3900 rows | correct@1 identical on 3900/3900 rows in both models; causal_final identical on all resolved rows (720/720 pythia-1.4b, 804/804 pythia-2.8b); max \|obj_first_logprob\| difference 3.3e-4 (1.4b) and 1.4e-4 (2.8b). CPU runs: `S3-pythia-1.4b-b9a353d-20261108T064941Z`, `S3-pythia-2.8b-be99060-20261109T021915Z` |
| interim OLMo-only test | `A2-none-0219059-20261121T063336Z`: OLMo estimates and CIs identical to the final run. Its outcome was "UNDECIDED (gate models missing)"; superseded |

## Deviations and caveats
- **GPU:** the run used an RTX PRO 6000 Blackwell (97,887 MiB), not the A100 80GB the script was written for. The fp32 matmul check against CPU fp64 gave max abs err 1.6e-4 with TF32 off (`reports/env_gpu.md`).
- **How Pythia was run:** through a separate chain script (`results/logs/pythia_chain_20261121.sh`), not `WITH_PYTHIA=1`. It used the same flags (`--halfprob --no-tuned-lens --dtype float32`, 3 templates, G1 facts) and the same test command. The pytest/pythia-70m smoke step ran once, in the OLMo session (`results/S3bsmoke/`).
- **OLMo counts:** the olmo-mix-1124 index is EXACT for OLMo-2's stage-1 pretraining data only (CLAUDE.md). The released main checkpoint also had stage-2 (mid-training) data, which these counts do not include.
- **Scope:** 26 relations and 1300 facts, with one count index per family.
- **Wording:** neither "law" nor "regularity" is supported for depth vs co-occurrence on this measure.
- **Skeptic review:** not run for this report. Its log `notes/review_log.md` does not exist yet, and the earlier instruction was not to start the skeptic unless asked.

## Human decision
Waiting for "GO A2" or "PIVOT <option>". Claim 2 has been on hold until this result.
