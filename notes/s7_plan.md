# S7 plan (CPU), 2026-11-16, after the human's "GO G2"

Written before any S7 code is run on the zoo model. Nothing in S7 is pre-registered in
configs/prereg.yaml except the efficacy rule (CLAUDE.md: efficacy >= 90% before keeping a model).
All choices below are fixed now; any later change is logged here with a date and reason.

## Model and hardware
- Zoo model: EleutherAI/pythia-1.4b (main), fp32 on CPU, 4 threads. 2.8B+ does not fit next to
  anything else in 15 GB RAM and is about 2x slower; the 1.4b model has S3 clean depth rows and
  EXACT Pile counts.
- S5 (pythia-2.8b checkpoints) is PAUSED while S7 runs on pythia-1.4b (RAM: 2.8b uses ~12 GB).
  It resumes from its chunks afterwards. The Gemma (S4T) queue stays queued behind S5.
- Code is tested on pythia-70m first (tests/test_zoo.py).

## Edit requests (data/splits/s7_requests.json, seeded 1234)
- Control facts: 300 facts from the G1 subsample (data/splits/g1_cpu_subsample.json), seeded
  sample stratified by relation; they have clean S3 rows and EXACT counts. Never edited.
- Edit pool: the 3,900 facts in data/facts.parquet outside the G1 subsample.
- Clean behaviour pass on the edit pool (pythia-1.4b, 3 templates, correct@1 of object first token).
- 1,000 requests, ordered by a seeded shuffle, alternating type:
  - counterfactual (500): any pool fact; new object = seeded random object of the same relation
    with a different first token from the true object.
  - true-new (500): pool facts with correct@1 = 0 on all 3 templates; new object = true object.
- Edit prompt = template 0. Paraphrase prompts = templates 1, 2.
- Prefixes of the same ordered list define every model's edit set, so methods are comparable.

## Methods (zoo/)
| model id | method | edits | layers / params |
|---|---|---|---|
| rome_single | ROME, one edit at a time, reverted after eval | first 100 | layer 5 |
| memit100, memit1000 | MEMIT batch | first 100 / 1000 | layers 3-7, mom2 weight 15000 |
| alphaedit100, alphaedit1000 | AlphaEdit batch | first 100 / 1000 | layers 3-7, null space eigval < 2e-2 of normalized cov, L2 10 |
| lora50, lora200, lora1000 | LoRA SFT on edit prompt + new object | first 50/200/1000 | r 8, alpha 16, query_key_value + dense_4h_to_h, all layers, lr 3e-4, until efficacy >= 0.9 or 20 epochs |
| synthdoc50 | LoRA FT on synthetic docs (10 docs per fact from 20 doc templates, fact stated once per doc) | first 50 | same LoRA settings, causal LM loss on whole doc |
- Layers 5 and 3-7 are scaled from the published GPT-J settings (ROME layer 5, MEMIT 3-8 of 28);
  pythia-1.4b has 24 layers. No layer search on our data.
- v*/z optimisation: Adam lr 0.5, up to 25 steps, early stop when mean target prob > 0.9, 5
  random-prefix contexts + the bare prompt, KL weight 0.0625, weight decay 0.5 (ROME defaults).
- Second-moment stats (C = E[k k^T] at each edited layer's MLP down-projection input): 60,000
  tokens of FineWeb-Edu from data/s6/corpus/docs.jsonl (local; MEMIT used Wikipedia; this is a
  deviation forced by CPU time). Cached under cache/zoo/.
- Stored: weight deltas (fp16 safetensors) or LoRA adapters, never full models.
  zoo/manifest.json lists each kept model, its exact edited facts, delta path, efficacy.

## Efficacy and keep rule
- Efficacy per edit = new-object first token is rank 1 at the edit prompt in the edited model.
- Batch / LoRA models: kept if efficacy >= 0.90 over their edits (CLAUDE.md rule). A model below
  0.90 is reported, not kept, not tuned on its eval data.
- rome_single: each successful edit is kept; the success rate is reported.
- Also reported (not gating): paraphrase efficacy (templates 1-2), control-fact correct@1 change.

## Evaluation for S8 (per kept model)
- run_depth --causal-only on: the edited facts with the NEW object (3 templates) and the 300
  control facts (true object). rome_single: edited fact + 5 seeded control facts per edit (corrected 2026-11-17: the code used 5 from the start; text said 10).
- Measures: causal_final, logit-lens depth, logprob, margin, correct@1. Tuned lens is MISSING for
  pythia-1.4b (no pretrained lens; see S3). Override and Patchscope are not run (CPU time).
- Counterfactual (subject, new object) pairs get EXACT Pile phrase counts with the S2x code
  (same patterns) before S8.

## Time estimate (pythia-1.4b, CPU)
- Stats ~2 h; ROME 100 edits + evals ~2 h; z for 1000 requests ~8 h; LoRA training ~3 h;
  evals ~20 h. Total about 35 h wall clock with S5 paused.

## Addendum A (2026-11-16, before any pythia-1.4b S7 run)
pythia-70m smoke test (code check only; 4 hand requests, layers 1-3): ROME 4/4, AlphaEdit 3/4,
LoRA 4/4, synth-doc 4/4 at rank 1; MEMIT with mom2 weight 15000 moved 1/4 to rank 1, with
1500 / 150 / 15 it moved 3/4, 3/4, 4/4. The GPT-J weight does not transfer across models, so the
MEMIT mom2 weight is chosen on a PILOT set, never on the 1,000 eval requests:
- pilot = 100 extra requests from the edit pool (50 counterfactual, 50 true-new), disjoint from
  the 1,000 requests and the 300 controls, same construction.
- candidates {15000, 1500, 150, 15}; pick the LARGEST weight whose MEMIT-100 pilot edit reaches
  efficacy >= 0.9 (largest = smallest update). The same weight is used for memit100 and memit1000.
- AlphaEdit settings stay fixed (threshold 2e-2, L2 10); its pilot efficacy is only reported.
