# P2 materials: fact sampling rules v1 (fixed before sampling)

- **Written:** 2026-11-21, before `materials/facts_v1.jsonl` was drawn. Sampling code: `scripts/p2_sample_facts.py`. Seed 20261121.
- **Pool:** `data/facts.parquet` (5200 facts, 26 relations × 200; fact_id, subject, relation, object, templates, and precomputed object first-token ids for the pythia, olmo2, llama31, qwen3 and gemma3 tokenizers).
- **Counts:** `data/counts_exact.parquet` column `exact_dclm-baseline`: EXACT phrase co-occurrence on the DCLM-baseline index.
  - For P2's primary models (Qwen3-8B, Llama-3.1-8B) DCLM is not their training corpus, so these counts are labelled **PROXY** (CLAUDE.md, Indexes).

## Fact eligibility (all must hold)
1. **Distinct first token:** the object's first token (`obj_first_tok_*`) is not shared with any *different* canonical object in the same relation's pool, under every tokenizer used in P2 (llama31, qwen3, pythia, olmo2).
2. **Contentful first token:** the decoded first token of " " + object, stripped, under each of those tokenizers:
   - has ≥ 2 characters;
   - contains a letter;
   - is not in the weak-token list {"the", "a", "an", "of", "and", "de", "la", "le", "el", "university", "saint", "st", "san", "new", "north", "south", "east", "west", "royal", "national", "king", "prince", "lake", "mount", "fort", "port", "united", "republic"}, compared case-insensitively.
3. **Count present:** `exact_dclm-baseline` is not missing.

## Relation eligibility
- **Excluded:** a relation is excluded if
  - < 15 of its pool facts are eligible, or < 5 eligible facts in any of its three co-occurrence terciles; or
  - ≥ 20% of its pool facts fail rule 1 or rule 2 ("semantically weak first answer token", e.g. objects starting "University").
- **If more than 20 relations are eligible:** rank them by eligible-fact count (descending; ties alphabetical) and keep the top 20.
- **Influential relations** (|leave-one-out influence on the G1 diff| > 0.1 in Part 0a: company_ceo, developer, manufacturer):
  - not excluded for that reason;
  - if otherwise eligible and selected, included and reported in a prespecified sensitivity analysis (P2 results with each one dropped).

## Sampling
- **Terciles:** within each selected relation, log1p(exact_dclm-baseline) terciles over its eligible facts (pandas qcut, 3 bins, duplicates dropped by rank).
- **Draw:** 5 facts per tercile, drawn with numpy default_rng(20261121) in relation-name order. 15 per relation, 300 in total.
- **Saved fields:** fact_id, relation, subject, object, tercile, log1p_cooc_dclm (PROXY), first-token ids and decoded first tokens per tokenizer, influential_relation flag.
- **Outputs:** `materials/facts_v1.jsonl` and `materials/facts_v1.jsonl.sha256`. The selection report (relations kept or excluded and why) goes to `materials/facts_v1_report.md`.
