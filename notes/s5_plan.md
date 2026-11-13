# S5 plan (CPU), 2026-11-13, after the human's "do everything on cpu"

- Models: pythia-1.4b and pythia-2.8b. OLMo-2-1124-7B stage-1 revisions: MISSING (7B does not fit
  in 15 GB RAM on this CPU).
- Revisions (log-spaced): step1000, 2000, 4000, 8000, 16000, 32000, 64000, 96000, 128000, plus the
  final checkpoint (main = step143000), reused from the G1 depth runs (same code; a causal-only
  re-run of 6 rows reproduced the G1 causal_final values exactly).
- Measure: causal_final only (run_depth --causal-only), plus behaviour (correct@1, logprobs, logit lens).
- Facts: data/facts_s5.parquet = 508 facts from the G1 subsample with causal_final resolved for at
  least 1 template at the final checkpoint of either model (split in data/splits/s5_facts.json).
  3 templates per fact. This conditions on facts the final model knows, and is chosen to fit CPU time.
- Counts: exact Pile phrase co-occurrence (EXACT).
- Analyses (exploratory; nothing about S5 is pre-registered):
  1. Per checkpoint: share resolved; depth ~ log cooc slope among resolved rows.
  2. Acquisition step per fact = first checkpoint at which the fact is resolved (template-majority),
     stays resolved through the final checkpoint; Spearman(acquisition step, cooc); discrete-time
     hazard over checkpoints.
  3. Depth drift for facts resolved at both step N and the final checkpoint.
- Estimated time: about 12.5 s per fact on pythia-1.4b, so about 1.8 h per revision; about 4 h per
  revision on pythia-2.8b. Total about 53 h.
