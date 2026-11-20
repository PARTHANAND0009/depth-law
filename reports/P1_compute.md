# P1 compute estimate (planning only; not results)

Hardware now: no GPU. CPU tier: 4 cores, 15 GB RAM, 14.3 GB memory cap for this session (`PROGRESS.md`).
Every figure below is an estimate from FLOP and bandwidth arithmetic, not a measurement. Each item lists its assumptions. A 15-minute timing pilot on the target GPU should replace these figures before any launch.

## Summary

| job | GPU-hours (A100 80GB) | GPU-hours (H100 80GB) | peak VRAM | min GPU | single job > 20 GPU-h? |
|---|---|---|---|---|---|
| OLMo-2-1124-7B S3 depth, 1300-fact G1 subsample (26 x 50, as for Pythia) | 1-3 | 0.5-1.5 | ~18-20 GB | 24 GB | no |
| OLMo-2-1124-7B S3 depth, full 5200 facts | 4-9 | 2-4 | ~18-20 GB | 24 GB | no |
| OLMo-2-1124-7B tuned-lens training (no pretrained lens exists) | 2-4 | 1-2 | ~30-35 GB | 40 GB | no |
| G1 statistics | 0 (CPU, < 1 h) | 0 | – | – | – |
| **OLMo-2 S3 + G1 total** | **3-7 (1300 facts) / 6-13 (5200)** | **1.5-3.5 / 3-6** | | **40 GB** (24 GB without tuned lens) | no |
| Claim 2: 160M model, 5B tokens, one seed | 10-15 | 4-7 | ~15-25 GB (micro-batch dependent) | 24 GB | no |
| Claim 2: 3 seeds + 50M-token pilot + depth evals | **31-46** | **13-22** | same | 24 GB | each seed no; the 3-seed total is above 20 GPU-h |

Downloads (all below the 200 GB rule):
- OLMo-2-1124-7B weights: about 15-30 GB.
- FineWeb-Edu sample-10BT: about 25-30 GB, to take 5B tokens.

## Assumptions

### OLMo-2-1124-7B depth (current S3 code, all measures)
- **Model:** 7.3B parameters, 32 layers, bf16 weights 14.6 GB.
- **Forward passes per (fact, template), each a batch of ≤ 32 rows of ~10-20 tokens:**

  | measure | batched forwards |
  |---|---|
  | behaviour / logit lens | 1 |
  | causal (source + 3 carriers × subject and final) | 7 |
  | override | 1 |
  | Patchscope (6 greedy steps, no KV cache) | 6 |
  | **total** | **~15** |

- **Time per forward:** 40-80 ms on an A100 with HF eager kernels and Python hooks. That gives about 1-2 s per (fact, template).
- **Totals:** 3900 (fact, template) pairs take 1.1-2.2 h; 15,600 pairs take 4.3-8.7 h.
- **Lower-cost option:** causal_final only (S5 mode) needs 4 forwards per pair, about 3x less than the full measure set.
- **Tuned lens:** tuned-lens default schedule, about 65M tokens forward through the frozen model. That is 2 × 7.3e9 × 6.5e7 ≈ 9.5e17 FLOP, or about 2 h at 125 TFLOP/s effective. Lens parameters plus Adam take about 8.6 GB, which is why it needs ≥ 40 GB.
- **Counts:** OLMo-mix EXACT counts already exist (`S2x-none-5516178-20261108T042549Z`); no GPU needed.
- **Caveat:** the headline causal_final is being audited (`reports/AUDIT_causal_depth.md`). If a new depth measure is approved, OLMo should be run with the new measure, and the estimate scales with its forward count.

### Claim 2: 160M controlled pretraining
- **Setup:** Pythia-160M-like model (12 layers, d 768, 162M parameters including embeddings), 5B FineWeb-Edu tokens, one pass. The inserted facts follow `configs/s6.yaml`: 2000 facts at {1, 4, 16, 64, 256} occurrences, 20 templates.
- **Compute:** training needs 6 × 1.62e8 × 5e9 ≈ 4.9e18 FLOP per seed.
  - A100 (bf16, 35-45% MFU, ≈ 110-140 TFLOP/s): about 10-12.5 h.
  - H100 (≈ 300 TFLOP/s at the lower MFU of a small model): about 4.5 h.
  - The range adds about 20% for data loading, checkpoints and evals.
- **Pilot:** 50M tokens, about 0.1-0.2 GPU-h; CLAUDE.md asks for it before launch.
- **Evals:** causal depth on 2000 facts × eval templates per seed is under 0.5 GPU-h (tiny model).
- **VRAM:** weights, grads and Adam in fp32 take 162M × 16 B ≈ 2.6 GB. Activations depend on micro-batch (16 × 2048 tokens with flash attention ≈ 10-20 GB), so a 24 GB GPU works with a smaller micro-batch.
- **Risk (from the CPU run, `reports/GATE_G2.md`):** the gate counts only facts learned in all 3 seeds. At CPU scale that left 21 facts, 18 of them in the top frequency bin. The same can happen at 160M if low-frequency facts are not learned. The prereg rule is unchanged; I flag this so the run is planned with it in mind.

## Rule check
- No single job is above 20 GPU-hours.
- The Claim 2 total (3 seeds) is 31-46 A100-hours, so it needs approval as a block.
- No download exceeds 200 GB.
