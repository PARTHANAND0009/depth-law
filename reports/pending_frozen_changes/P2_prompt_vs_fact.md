<!-- STAGED DRAFT for the human. Intended path: prereg/P2_prompt_vs_fact.md. Claude cannot write prereg/
     (permission deny rule Edit(prereg/**), protect_frozen.py, pre-commit). The human installs it, commits it
     before any P2 GPU data exists, and records the commit in prereg/HASH_P2.txt / PROGRESS.md. -->
# Preregistration P2: prompt vs fact in causal resolution depth

- **Status:** DRAFT 2026-11-21, written before any P2 data exist. No P2 model run has been made; only a pythia-70m plumbing pre-flight (5 facts × 2 paraphrases) and synthetic-data tests.
- **Freeze:** this file is committed and tagged `prereg-P2` before the GPU session.
- **Decision text:** sections 1–9, as written; deviations go in `prereg/deviations/` with reason and UTC time, written before any rerun.

## 0. Disclosure (data seen before this file)
- **G1 / E-depthvar (EXPLORATORY):** variance shares of D1/D4 on S3b rows of pythia-1.4b, pythia-2.8b and OLMo-2-7B (3 templates per relation, 26 relations, correct cells).
  - Fact+subject 0.29–0.48 of total, template-main 0.05–0.37, residual 0.12–0.24, relation 0.09–0.33.
  - Within-relation ICC(1) 0.37–0.64.
  - The OLMo wording advantage drops to 0.009 without `company_ceo` (`reports/gates/G1/GATE_G1.md`, `analysis/exploratory/E-depthvar/*PART0A_REPORT.md`).
- **Earlier preregistered and exploratory results** on these models: H-R gate (`results/HR_gate.md`), amendment 2 (`reports/GATE_A2.md`), C1 re-analysis.
- **Fact overlap:** 74 of the 300 P2 facts were among the 1300 facts analysed in G1 (their 3 old templates differ from the P2 paraphrases).
- **Excluded relations:** `company_ceo` (the relation that drove the G1 OLMo result) is excluded by the prespecified first-token rule, so P2 cannot test it.
- **New data:** nothing from Qwen3-8B or Llama-3.1-8B has been run or seen.

## 1. Design (materials frozen with this file)
| item | file | sha256 |
|---|---|---|
| facts: 300 = 20 relations × 15, 5 per co-occurrence tercile (DCLM EXACT phrase counts, labelled PROXY), seed 20261121, rules `materials/SAMPLING_RULES_v1.md` | `materials/facts_v1.jsonl` | 0f596cd7385a318b9f2d8bea84d5d8cf483ee62c9333fa3bec0ecd60d9f1bfe3 |
| paraphrases: 10 per relation = 8 shared frames + 2 lexical variants | `materials/paraphrases_v1.jsonl` | dd481a359860bcb4a8cfec6ed6e85a35904dfcc42b7042a4278d030c1c707548 |
| carriers: `{} is associated with` (existing) + `{} is linked to`, `A word that goes with {} is` (new) | `materials/carriers_v1.jsonl` | dea5a8910cb356d8b42c8d91f09db9cecb646a924bba23e9ea3b07578258aadd |

- **Frames:** the 8 frames are order (subject-first / relation-first) × form (cloze / "Q: …? A:") × length (short / long). The long version adds the shared neutral clause "According to reference sources, ".
- **Prompt checks:** every prompt ends where the next token is the answer's first token. Subject appears exactly once and the answer string is absent in 3000/3000 prompts (`materials/paraphrases_v1_report.md`).
- **Models, in order:** Qwen/Qwen3-8B, meta-llama/Llama-3.1-8B (rented GPU, fp32). Then EleutherAI/pythia-1.4b and pythia-2.8b (CPU after S5 ends with > 8 GB free RAM, or GPU if budget remains). Then allenai/OLMo-2-1124-7B only if GPU budget remains.
- **Measurement** (`src/depthlaw/p2/run_p2.py`):
  - For each fact × paraphrase, write the final-token residual at the output of every block into the final token of each carrier (filled with "X").
  - Store p(object first token) as float16 and its rank as int16 at the carrier's final position, for every layer.
- **Compute fallback order** (if the projected cost exceeds the minute budget): (1) drop to 2 carriers (drop carrier 2); (2) drop Llama-3.1-8B. Each step is logged as a deviation before continuing.

## 2. Outcomes
- **Primary D1, per carrier:** l\* = min l with p(l') ≥ 0.5·p(L−1) for all l' ≥ l; value (l\*+1)/L.
- **Required robustness, D4:** 1 − mean_l min(1, p_l/p_final).
- **Secondary:**
  - D2: stable p ≥ 0.1 onset; censored if the final p < 0.1.
  - D3: stable rank-1 onset; censored if not rank 1 at the last layer.
- **Carrier averaging:** shares are reported on the carrier-averaged scale (section 4).

## 3. Inclusion
- **Primary:** correct cells, i.e. (fact, paraphrase) where the model's top-1 next token on the paraphrase is the object's first token.
- **Sensitivities (reported, not gating):**
  - facts correct under all 10 paraphrases;
  - all cells;
  - with `manufacturer` dropped (the only Part-0a influential relation in the sample);
  - leave-one-frame-out of the decision quantities.

## 4. Model
- **Formula,** fitted on carrier-level rows (fact × paraphrase × carrier) by REML with lme4 convergence checks ON (`calc.derivs = TRUE`); singular fits and warnings are logged:
  `y ~ n_answer_tokens + n_subject_tokens + log_cooc_proxy + answer_prior + (1|relation) + (1|frame) + (1|relation:template) + (1|fact) + (1|fact:template) + (1|fact:carrier) + residual`
- **Covariates:**
  - All fixed effects are fact-level and z-scored within model × set.
  - answer_prior is the object first-token log-prob on the carriers alone, averaged.
  - Template-level covariates (length, subject-to-final distance) are not in the primary model, because they would remove wording variance by construction. They go in a sensitivity model.
- **Changes from the human's formula** (all three are written here before any data):
  - `relation:template` = relation × frame, because each paraphrase id is one frame.
  - `(1|fact:template)` is added so that fact × wording interaction (G1's "residual") is separated from carrier-level noise. The combined residual is also reported.
  - `(1|subject)` is dropped: all 300 subjects are distinct, so it equals `(1|fact)`.
- **Shares** (within relation, carrier-averaged; nc = number of carriers):
  - den = fact + rt + frame + ft + fc/nc + e/nc.
  - **Primary fact share = within-relation ICC(1) = fact / den.**
  - Wording share = (rt + frame + ft) / den; diff = wording − ICC(1).
  - The share of total variance (relation included) is also reported for every component.
  - G(k) = fact / (fact + ft/k + fc/nc + e/(k·nc)), for the same k paraphrases for every fact.
  - Φ(k) adds (rt + frame)/k.
  - n′ = min k with G(k) ≥ 0.8.
- **Estimators:**
  - REML primary.
  - Henderson-III method-of-moments sensitivity on carrier-averaged cell means (`analysis/p2/p2_mom.py`, unbiased in self-test).
  - **A claim holds only if REML and MoM agree in direction.**
- **CIs:** 1000 resamples by the method chosen in `results/P2sim/` (two-way cluster bootstrap over facts-within-relation and frames, or parametric `bootMer`). The rule: coverage ≥ 0.90 and |bias| ≤ 0.05 for ICC(1) and diff on this exact design. **[filled from the simulation report before freezing]**
- **Shuffled-fact null:** permute fact IDs within relation × paraphrase cells, 1000 times. "Fact share > 0" is accepted only if p < 0.01.
- **Seed:** 20261121 everywhere.

## 5. Hypotheses (per model; a claim needs ≥ 2 models)
- **H1 (wording):** wording share > ICC(1), with the 95% CI of the difference excluding 0, under D1 **and** D4, and the MoM difference > 0 under both.
- **H1-alt (fact):** ICC(1) ≥ 0.5 with lower 95% CI ≥ 0.4, under D1 and D4, and MoM ICC(1) ≥ 0.5 under both.
- **H2 (estimation):** ICC(1) [CI] and n′ for G = 0.8 [CI].
- **H3 (estimation):** cross-model Spearman ρ of fact-level mean depth (D1), raw and disattenuated by G(10) of each model.
- **H4 (EXPLORATORY):**
  - order and form effects: frame-level fixed effects in a separate fit;
  - whether the wording share is larger in Qwen3-8B / Llama-3.1-8B / OLMo-2-7B than in Pythia.

## 6. Headline wording rules (enforced by claim-auditor)
- "There is no fixed layer where a fact lives": only if the ICC(1) upper CI is < 0.15 in ≥ 2 models.
- "A single prompt is a poor estimate of a fact's depth; it takes N paraphrases": only if H1 holds and n′ ≥ 8 (≥ 2 models).
- "Wording shifts every fact's depth together": only if template + frame share exceeds the fact×template residual and H1 holds (≥ 2 models).
- "Facts have a depth that frequency and relation do not explain": only if H1-alt holds (≥ 2 models).
- Otherwise: report the estimated shares and n′ as an intermediate result.

## 7. Code (frozen with this file)
- `analysis/p2/p2_model.R`, `analysis/p2/p2_analysis.R`, `analysis/p2/p2_bootsim_fns.R`, `analysis/p2/p2_mom.py`, `analysis/p2/p2_analysis.py`, `src/depthlaw/p2/run_p2.py`.
- Simulation: `analysis/p2/p2_bootsim.R` → `results/P2sim/p2_bootsim.json`.

## 8. Related work (for citation-verifier)
- **Measures:**
  - Causal tracing / activation patching localises factual recall (Meng et al.; Hase et al. 2301.04213 show localisation does not predict where editing works).
  - Hochman, Shapira, Goldberg (2606.21345) find redundant, non-contiguous retrieval paths and "significant rank discordance between models" in per-relation path length.
  - Gupta et al. (2510.18871) show the first token of multi-token answers needs more depth.
  - Agarwal (2609.17537) finds relation information becomes causally active before entity information.
  - Rohweder et al. (2610.27241) predict linear relational decodability from the subject representation alone.
  - Chen et al. (2405.14117), Elhelo et al. (2606.27237) and Benz et al. (2607.01000) are required citations. **Their content is to be verified by citation-verifier; it is not characterised here.**
- **P2's question:** none of these estimates how much of a fact's causal depth is a property of the fact versus the prompt wording.

## 9. Deviations
`prereg/deviations/D-P2-<n>.md`, write-once, with reason and UTC time, committed before any rerun.
