# S6 plan (CPU-scaled), 2026-11-13. Written before any S6 training data or evaluation.

Human instruction: "do everything on cpu" (2026-11-13). The CLAUDE.md S6 spec (160M model, 5B
FineWeb-Edu tokens, 3 seeds) needs about 6 * 160e6 * 5e9 = 4.8e18 training FLOPs per seed. At the
pilot's throughput that is years of CPU time, so the model and token budget are scaled down. The
fact design follows the spec. CPU only: no GPU-hours are spent (rule 7 not triggered).

## Pilot (throughput, 40 steps each, measured while S5 shared the 4 cores)
| config | params | tokens/s | run |
|---|---|---|---|
| 8 layers, d 256, ff 1024, ctx 256, batch 32 | 10,512,896 | 821.8 | results/S6pilot/S6pilot-s6lm_seed1-fd39e8d-20261113T114226Z |
| 6 layers, d 384, ff 1536, ctx 256, batch 32 | 16,939,008 | 874.7 | results/S6pilot/S6pilot-s6lm_seed1-fd39e8d-20261113T114909Z |

Chosen: 8 layers, d 256 (more layers give finer depth resolution; similar throughput).

## Estimate (reported before launch)
- 40M tokens per seed (4,882 steps of 8,192 tokens) at about 820 tokens/s is about 13.5 h per seed.
- 3 seeds take about 41 CPU-hours while S5 shares the CPU, less after S5 ends.
- Evaluation (causal depth for 2000 facts x 3 eval templates on the 8-layer model) takes under 1 h per seed (estimate, to be measured).

## Design (deviations from the CLAUDE.md spec are marked *)
- Model*: GPT-NeoX, 8 layers, d 256, 8 heads, ff 1024, ctx 256, untied embeddings; about 10.5M parameters.
- Tokenizer*: byte-level BPE with an 8192 vocabulary, trained on 30,000 FineWeb-Edu documents
  (data/s6/tokenizer). The small vocabulary keeps the unembedding cheap on CPU.
- Corpus*: FineWeb-Edu sample-10BT stream prefix (data/s6/corpus/meta.json); about 40M training tokens per seed instead of 5B.
- Facts: 2000 fictional (subject, relation, object) across 5 relations (birthplace, occupation,
  food, color, language) x 5 frequency bins {1, 4, 16, 64, 256}, 400 facts per bin.
  - Subjects are invented two-word names of exactly 4 tokens.
  - Objects come from 10 single-token objects per relation, assigned round-robin, so every bin has an identical object distribution (8 facts per object per bin).
  - Templates: 20 training paraphrases per relation (configs/s6.yaml) and 3 held-out evaluation paraphrases never seen in training.
- Spacing: k occurrences at fractions (j+u)/k of the stream (u uniform per fact and seed), snapped
  to the next document boundary; template drawn uniformly from the 20 per occurrence (mix.py).
- Training: one pass in stream order, AdamW (lr 1e-3, betas 0.9/0.95, wd 0.1), 300 warmup steps,
  cosine to 10%, grad clip 1.0.
- Seeds 1, 2, 3: each seed changes model init, insertion offsets and template draws; the corpus is the same.

## Evaluation and G2 (fixed now, before training)
- For each seed's final model: run_depth --causal-only on data/s6/facts.parquet with the 3 eval
  templates and the S3 carriers. Depth = causal_final, (l+1)/L with L = 8.
- Learned (per seed) = correct@1 (object first token is the top-1 next token) on >= 2 of 3 eval templates.
- Fact depth per seed = mean causal_final over resolved eval templates. Fact depth = mean over seeds.
- G2 statistic (prereg g2.spearman_max = -0.5): Spearman(freq, fact depth) over facts learned in
  all 3 seeds that have a depth in every seed. PASS if rho < -0.5. N is reported per bin.
- Also reported: share learned per bin and seed; depth per bin (median, IQR); depth resolution caveat (8 layers gives depths in steps of 1/8).

## Update 2026-11-13 12:05Z (throughput only; design unchanged)
Running S5 and S6 with 4 threads each oversubscribed the 4 cores (load average about 8). Both were
restarted with 2 threads each; S6 seed 1 restarted from step 0 in the same run dir. Measured throughput
with 2 threads is in the training log (results/S6/S6-s6lm_seed1-*/log.jsonl, tok_per_s).

## Seed 1 learnability (2026-11-13, written after seeing seed-1 results; G2 rule and threshold unchanged)

- Eval run `S6eval_seed1-final-e538cd9-20261113T163228Z`: 4 of 2000 facts meet the "learned" rule (correct@1 on >= 2/3 eval templates). G2 needs facts learned in all 3 seeds, so with this design the gate outcome would be MISSING.
- Learnability check `results/S6learn/S6learn-none-e538cd9-20261113T175744Z/learn.json` (60 facts per bin, 3 prompts each, N = 180 prompts per cell). Accuracy among the relation's 10 candidate objects (chance 0.1): on training templates, from 0.111 at freq 1 to 0.272 at freq 256; on eval templates, from 0.078 to 0.189. Share of top-1 predictions that are in the candidate set, on training templates: 0.889 to 0.933. The model learns each relation's object type but stores little of the subject-to-object binding, even at 256 occurrences.
- Diagnosis: a 10.5M-parameter model on a single 40M-token pass gets too few exposures per fact. This is a capacity and exposure limit of the CPU scale-down, not a bug in the eval.
- S6 is paused: seed 2 stopped at step 1400 (state.pt saved at step 1000). No design change is made until the human decides.
