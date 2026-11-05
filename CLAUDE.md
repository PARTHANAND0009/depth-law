# CLAUDE.md: depth-law

## Project
Test whether the causal resolution depth of a factual association (earliest
normalized layer where it is causally transferable) falls with log pretraining
co-occurrence of subject and object; test it causally with controlled-frequency
pretraining; use deviations to detect tampered facts without the base model.

## Non-negotiable rules
1. Never fabricate, estimate, or "fill in" a result. Every number in any report,
   figure, or paper text must be read from a file in results/ produced by a logged
   run. Reports cite the file path and run_id for each number.
2. If a run fails or a result is missing, write "MISSING: <reason>" in place of it.
3. Stop at every GATE. Write the gate report, then wait for the human reply
   "GO <gate>" or "PIVOT <option>". Do not continue on your own.
4. Before scaling to a model >1.5B, all tests in tests/ must pass on pythia-70m.
5. Do not change a pre-registered threshold in configs/prereg.yaml after seeing
   data. If you think one is wrong, say so in the gate report.
6. Label every frequency count as EXACT or PROXY (see Indexes). Never mix them in
   one fit without a corpus indicator.
7. Ask before any action that costs >20 GPU-hours or downloads >200 GB.

## Repo layout
depth-law/
  CLAUDE.md
  pyproject.toml, requirements.lock
  configs/            # YAML, one per stage + tier.yaml + prereg.yaml
  src/depthlaw/
    hw.py             # hardware probe, tier selection
    io.py             # cache keys, parquet/safetensors IO, run_id
    facts/            # build_facts.py, aliases.py, templates.py, sanskriti.py
    freq/             # infinigram_client.py (retry, rate limit, cache), counts.py
    depth/            # causal.py, tuned_lens.py, patchscope.py, logit_lens.py
    stats/            # mixed.py, survival.py, bootstrap.py, transfer.py
    ckpt/             # revisions.py, dynamics.py
    pretrain/         # synth_facts.py, mix.py, train.py, eval.py
    zoo/              # rome.py, memit.py, alphaedit.py, lora_inject.py, synth_docs.py
    detect/           # features.py, score.py, eval.py, baselines/
    attack/           # layer_match.py, depth_reg.py, freq_spoof.py
    figs/             # one script per paper figure, reads results/ only
  scripts/            # thin CLI wrappers, one per stage
  tests/
  data/ cache/ results/ reports/ notes/   # data/cache gitignored

## Reproducibility
- Global seed from config; seed torch, numpy, random, CUDA; log it.
- run_id = <stage>-<model>-<git short hash>-<UTC timestamp>. Every results file
  carries run_id, config hash, model name, HF revision, library versions.
- Cache key for activations: (model, revision, fact_id, template_id, position,
  layer, dtype). Store as safetensors fp16 under cache/. Skip work if key exists.
- Log to results/<stage>/<run_id>/log.jsonl; optional wandb if WANDB_API_KEY set.
- Deterministic data splits saved to data/splits/*.json; never regenerate silently.

## Hardware tiers (choose in hw.py)
- CPU: no CUDA GPU. Only pythia-70m/410m tests, fact building, and frequency
  counting (S0-S2). No depth runs on gate models.
- T0: <24 GB per GPU. Pythia 70M-1.4B, Gemma-3-1B only. Pretraining 160M allowed.
- T1: 24-48 GB. Add Pythia-2.8B/6.9B, OLMo-2-1124-7B, Llama-3.1-8B, Qwen3-8B,
  Gemma-3-4B in bf16 for inference and patching. No 8B MEMIT covariance or LoRA
  without asking.
- T2: >=80 GB. Everything, including zoo construction on 8B.
- Multi-GPU: shard facts across GPUs (one process per GPU); do not use tensor
  parallel unless a model does not fit.

## Indexes (infini-gram API https://api.infini-gram.io/)
- Pythia (standard, NOT deduped): v4_piletrain_llama -> EXACT
- OLMo-2-1124-7B: v4_olmo-mix-1124_llama -> EXACT for stage-1 pretraining
- Llama-3.1-8B, Qwen3-8B, Gemma-3-4B: v4_dclm-baseline_llama (primary) and
  v4_olmo-mix-1124_llama (secondary) -> PROXY
- Counting rules: sum surface variants (case, leading space, curly/straight
  apostrophe); CNF "A AND B" with max_diff_tokens in {32,100,500} (100 primary);
  max_clause_freq=500000; store the 'approx' flag; OR-join aliases inside a
  clause; retry with exponential backoff; cache every response in cache/freq/.

## Models
Core: EleutherAI/pythia-{1.4b,2.8b,6.9b}, allenai/OLMo-2-1124-7B.
Transfer: meta-llama/Llama-3.1-8B, Qwen/Qwen3-8B, google/gemma-3-4b-pt.
Test: EleutherAI/pythia-70m, pythia-410m.
Stretch (ask first): allenai/Olmo-3-1025-7B (revisions "stage1-stepXXX"; no
exact public index found), 14B-class models.
Libraries: nnsight for interventions (fallback: raw HF forward hooks);
tuned-lens package for lenses (pretrained lenses from HF Space
AlignmentResearch/tuned-lens where they exist; train otherwise).

## Stages and gates
S0 setup: hw probe, env lock, tests on pythia-70m.
  tests: patching identity (patch layer l from same prompt -> unchanged logits),
  causal depth on 20 hand facts is in [0,1] and monotone-consistent, lens loads,
  Patchscope returns object for >=1 easy fact, infini-gram client returns known
  count for a fixed query, cache round-trip.
S1 facts: PopQA + CounterFact true facts + LRE relations + T-REx subset.
  Output data/facts.parquet with >=3 templates per relation and per-tokenizer
  answer token counts. 4-6k facts, >=15 relations, >=150 per relation.
  SANSKRITI: convert MCQ items to (subject, relation, object) cloze where the
  correct option is a short entity; write data/sanskriti_cloze.parquet and a
  report of how many items survived and why others were dropped.
S2 frequency: counts for every fact x index; audit 100 random facts into
  reports/count_audit.csv for human checking.
S3 depth + regression:
  causal depth: patch the subject-last-token residual at layer l from the fact
  prompt into 3 neutral carrier prompts ("<X> is associated with", etc., stored in
  config); depth = min l such that the object first token is rank 1 for all
  l' >= l; normalized by L; mean over carriers; censored if never.
  tuned-lens depth: first layer where object first token is rank 1 at the final
  position and stays rank 1 to the last layer.
  Patchscope depth: first source layer where the attribute-extraction target
  prompt generates the object (exact or alias match) and stays correct.
  Also store: logit-lens curve, object logprob, margin, correctness.
  Regression (stats/): mixed model with relation random slope, template and
  subject random intercepts, controls listed in configs/prereg.yaml; marginal R^2
  with and without log cooc; cluster bootstrap over relations (1000);
  discrete-time survival model; AIC comparison linear vs piecewise vs logistic;
  Holm correction across models x measures.
  ==> GATE G1: write reports/GATE_G1.md with: per model x measure partial R^2
  (CI), slope (CI), N resolved/censored, survival hazard ratio, measure agreement
  (Spearman), 5 example facts per frequency decile, and the decision rule outcome
  from prereg.yaml. STOP.
S4 transfer + controls: held-out families, minimal pairs (same object token,
  >=10x cooc difference), SANSKRITI slice, LRE-faithfulness nested model.
S5 checkpoint dynamics: Pythia 1.4B/2.8B ~10 log-spaced revisions, OLMo-2 ~8
  stage-1 revisions; causal depth only.
S6 controlled pretraining: 160M model, FineWeb-Edu 5B tokens, 2000 fictional
  facts at frequencies {1,4,16,64,256}, 20 paraphrase templates, uniform spacing,
  matched object-token pool and subject token lengths across bins, 3 seeds.
  Estimate GPU-hours from a 50M-token pilot and report before launching.
  ==> GATE G2: monotone depth vs frequency (Spearman < -0.5 on facts learned in all
  seeds). STOP.
S7 zoo: ROME, MEMIT (batch 100/1000), AlphaEdit, LoRA SFT (50/200/1000 facts),
  synthetic-doc FT; true-new-fact and counterfactual edits; verify efficacy
  >=90% before keeping a model; write zoo/manifest.json with exact edited facts.
S8 detector: features (depth residuals per measure, confidence-frequency
  residual, recall-vs-two-hop depth gap, within-relation profile distance);
  unsupervised score calibrated on clean models only; supervised upper bound;
  baselines: Youssef-style AdaBoost, LCF (diag Mahalanobis on inter-layer
  differences, Ledoit-Wolf, 200 clean calibration prompts), confidence-only,
  perplexity, confidence x rarity. Fact-level and model-level AUROC, held-out
  method, held-out family, bootstrap CIs.
S9 adaptive attacker: A1 layer matching, A2 depth-regularized edit loss, A3
  frequency spoofing by synthetic docs; AUROC vs efficacy vs collateral vs compute.
  ==> GATE G3: fact-level AUROC on non-adaptive ROME/MEMIT vs 0.8. STOP.
S10 figures: one script per figure in figs/, reading only results/; save PDF+PNG
  and a JSON of the plotted numbers.

## Style for reports
Terse. Tables first. State N for every number. Distinguish EXACT vs PROXY counts.
No claims beyond what the numbers show.
