# S4 plan (CPU), 2026-11-12, after "GO G1" (pre-registered G1 outcome was NO-GO)

Written after the G1 results were seen. Every S4 analysis except the TOST is therefore
EXPLORATORY. TOST margin from prereg: transfer_tost_margin_per_decade = 0.02. The slope per
decade of cooc is slope_per_log1p_unit * ln(10); the TOST is done on that scale with a 90% CI.
No prereg threshold is changed.

Hardware: CPU only (4 cores, 15 GB RAM, no CUDA). This is outside the CPU tier in CLAUDE.md,
continuing the "OK CPU G1" exception for pythia-1.4b / pythia-2.8b only.

| S4 item | data | status on CPU |
|---|---|---|
| A. held-out families | existing G1 depth (pythia-1.4b, 2.8b) | run: leave-one-family-out fit; per-family slope; TOST of each slope vs 0 |
| B. minimal pairs | existing G1 depth | run: fact pairs with the same object first token (pythia tokenizer), exact Pile cooc ratio >= 10, both resolved on causal_final; paired depth difference (high minus low cooc), Wilcoxon signed-rank test, N pairs |
| C. SANSKRITI slice | data/sanskriti_cloze.parquet, counts from S2x-none-531d22f-20261108T232633Z | run on pythia-1.4b only: 300 items (150 per relation, seed 1234), split in data/splits/s4_sanskriti_slice.json; same S3 depth runner and carriers |
| D. LRE faithfulness nested model | pythia-1.4b | run if CPU time allows: per relation, LRE (Hernandez et al. 2024) Jacobian estimated on 8 facts, faithfulness on the rest; nested fit depth ~ controls + lre_faithfulness (+ log_cooc) |
| transfer models (Llama-3.1-8B, Qwen3-8B, Gemma-3-4B) | PROXY dclm counts | MISSING: an 8B bf16 model does not fit in 15 GB RAM; Gemma-3-4B bf16 on CPU is estimated at >100 h. Needs a T1 GPU; asking the human |

Relation families (fixed here, before the S4 fits):
- geo_place: capital, continent, country, headquarters, formation_location, place_of_birth, place_of_death, work_location
- language: native_language, official_language, original_language
- person_role: occupation, field_of_work, sport, sport_position, instrument, music_genre, citizenship, employer
- org_product: manufacturer, developer, company_ceo, country_of_origin
- other: any relation not listed above (reported, not dropped)
