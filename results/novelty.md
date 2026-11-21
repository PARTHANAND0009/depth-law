# Novelty check for revised H-R (STEP 3)

- **Produced by:** a general-purpose subagent spawned 2026-11-21 ~07:38 UTC with the human's STEP 3 prompt, plus the H1-H3 definitions from `prereg/HR_revised.md` as context. It finished ~07:47 UTC.
- **Report below:** the subagent's own text (its quotes come from PDFs it fetched). I added this header only.
- **Not re-verified by the main session:** the quotes and IDs. The PDFs and text files were saved in the session scratchpad and are not part of the repo.

---

# Literature check: per-relation resolution depth, cross-family ordering, and co-occurrence vs depth (H1–H3)

All 8 required arXiv IDs exist. I got their metadata from the arXiv export API and downloaded each full PDF. Quotes below come from the PDFs via `pdftotext`, unless a paper is marked "abstract only". Section numbers come from the extracted text.

**Bottom line:** no paper found claims H1, H2 or H3. Two findings are partly contrary:
- **Against H2, on a different measure:** 2606.21345 reports "significant rank discordance between models" for per-relation path length.
- **Against H1, framed for LRE faithfulness rather than depth:** 2610.27241 says decodability is "largely a property of" the subject representation, "rather than of the relation".

## (1) Required IDs

### 2606.21345: "Factual Retrieval in LLMs Is a Redundant, Distributed and Non-Contiguous Process"
- **Authors:** Hail Hochman, Natalie Shapira, Yoav Goldberg.
- **Posted:** 2026-06-19. ACL 2026 Main.
- **Setup:** iterative patching to find a minimal set of layers (the "attribute-computation path") on LLaMA-3.1-8B and Qwen3-8B. It measures path length and termination layer, not resolution depth.
- **Relevant to H2 (against it, on path length), §6.2 "Paths in Individual Relations":**
  - "We analyzed relation types with sufficient coverage (N ≥ 50). While not a universal trend, we observe anecdotal examples suggesting a potential link between semantic specificity and computational cost (Appendix E)."
  - "per-relation layer-usage heatmaps in Appendix E illustrate that distinct relations recruit specific sets of layers beyond simple path length differences. However, this length hierarchy is highly inconsistent: we observe significant rank discordance between models and between primary and alternative paths."
  - No Spearman value is given.
- **§6.2, on depth:** "Overall, while the amount of required computation (path length) is an intrinsic property of the task, the depth of this extraction is highly sensitive to counterfactual noise."
- **Frequency:** none. No co-occurrence analysis.

### 2609.17537: "Relation Before Entity: Deferred Commitment in Language Model Factual Recall"
- **Author:** Divyansh Agarwal.
- **Posted:** 2026-07-13. ICML 2026 Mechanistic Interpretability Workshop (OpenReview gcgoa7EN4v).
- **Models:** Llama-3.2-3B, Llama-3-8B, Qwen2.5-3B, Phi-2. Eight prompt families.
- **What it measures:** when relation-type information becomes active versus when entity information does. It does not give a per-relation depth ordering.
- **Abstract:** "Relation onset precedes entity onset by 10-16 tested layers (31-44% of network depth) at threshold 0.4, with the ordering holding across all 16 model-threshold combinations for thresholds 0.2-0.5."
- **Limitations section:** "The central claim is the ordering (relation before entity commitment), not any single absolute layer index."
- **Relevance:** no per-relation ordering across models, no cross-model Spearman, no frequency analysis. Tangential to H1 and H2.

### 2610.27241: "Predicting Linear Relational Decodability Without the Relation"
- **Authors:** Jonas Rohweder, Adrian Mülthaler, Faridoun Mehri, Sebastian Gerstner, Hinrich Schütze.
- **Posted:** 2026-10-19 (v2 on 2026-10-21).
- **Relevant to H1 (framing against it, for LRE faithfulness, not depth). Abstract:**
  - "Across 28 relations of the LRE dataset on Olmo-3-7B this relation-agnostic score correlates with LRE faithfulness at ρ = 0.7355 (p < .01). This suggests that linear decodability is largely a property of what a subject's representation already carries, rather than of the relation being decoded."
- **Controls, §6:**
  - "Removing k raises the correlation to ρ = 0.757." Here k is object cardinality.
  - "The correlation is 0.784 with both cardinality and answer frequency removed."
  - It names first-token collapse as a dataset problem: "semantically weak first tokens (e.g., most predicted universities' first token is "University")".
- **On layer choice, Appendix:**
  - Layer 17 "is the modal best layer for the LRE itself in our sweep (15 of 28 relations; the rest spread over 5, 11, 14, 20 and 23)."
  - "this does not establish robustness to the layer choice: changing the layer can affect relations differently. A systematic sensitivity analysis is left to future work."
- **Frequency, Table 5 (OLMo 3 7B, relation-level Spearman with LRE faithfulness).** These counts are "binary document presence" in OLMo's training mixes:

| Measure | ρ | p |
|---|---|---|
| Subject frequency | 0.1380 | 0.484 |
| Object frequency | 0.5712 | 0.001 |
| Joint frequency, cso | 0.4568 | 0.015 |
| Mean of log(1 + cso) | 0.4191 | 0.026 |
| Forward conditional, P(o \| s) | 0.4486 | 0.017 |

- **Table 4** gives per-model correlations (lens score vs faithfulness) for 7 models, including Pythia 6.9B and OLMo 3 7B. These are within-model only; no cross-model ordering of relations is reported.
  - Example: "Pythia 6.9B∗,† 0.5027" (contrastive entity lens).
  - Example: logit lens "−0.2047" (Pythia) vs "0.2056" (OLMo 3 7B).

### 2605.22532: "Relational Linear Properties in Language Models: An Empirical Investigation"
- **Authors:** Giovanni Valer, Luigi Gresele, Marco Bronzini, Emanuele Marconato.
- **Posted:** 2026-05-21.
- **Models:** Llama-3.1-8B and Gemma-2. Uses a KL-based probe of relational linearity layer by layer.
- **§4.4:** "Surface-level relations already achieve high F1 scores in early layers, whereas abstract relations show increasing F1(LLM), peaking in the middle layers. A similar pattern is also observed in Gemma-2, except for SUBJ".
- **Conclusion:** "layer-wise patterns emerge consistent with prior evidence on linguistic dynamics (i.e., LANG appear in early layers, while TRUTH peaks in intermediate layers)".
- **Relevance:** only qualitative agreement between 2 models across 4 coarse datasets (not factual relations). No Spearman, no frequency analysis. Weakly related to H2.

### 2308.09124: "Linearity of Relation Decoding in Transformer Language Models"
- **Authors:** Evan Hernandez, Arnab Sen Sharma, Tal Haklay, Kevin Meng, Martin Wattenberg, Jacob Andreas, Yonatan Belinkov, David Bau.
- **Posted:** 2023-08-17 (v2 on 2024-02-15). ICLR 2024. This predates 2024.
- **§4.3, on per-relation layers:** "there are considerable differences in LRE faithfulness when estimated from different layers. Figure 7 highlights an example relation that appears to be linearly decodable from representations in layer 7 until layer 17, at which point faithfulness plummets."
- **Appendix H, cross-model (faithfulness, not depth):** "According to Spearman's rank-order correlation, GPT-J's relation-wise performance is strongly correlated with both GPT2-xl (R = 0.85) and LLaMa-13B (R = 0.71), whereas GPT2-xl and LLaMa-13B are moderately corelated (R = 0.58)."
- **Frequency:** none.

### 2510.18871: "How Do LLMs Use Their Depth?"
- **Authors:** Akshat Gupta, Jay Yeung, Gopala Anumanchipalli, Anna Ivanova.
- **Posted:** 2025-10-21 (v2 on 2026-03-01).
- **Method:** TunedLens. Frequency here means token frequency, not fact co-occurrence.
- **§4.2:** "the first appearance of the single-token answer happens much earlier into a model (layer 15 for Pythia-6.9B, layer 20 for Llama3-8B) compared to the first token of the multi-token facts (layer 25 for both models)."
- **§4.2:** "for a 3-token fact, the first token on average emerges around layer 27 for Pythia-6.9B, whereas the subsequent second and third tokens emerge around layers 20 and 12 respectively."
- **Relevance:** supports controlling for answer token count. No per-relation analysis, no co-occurrence analysis.

### 2504.12459: "On Linear Representations and Pretraining Data Frequency in Language Models"
- **Authors:** Jack Merullo, Noah A. Smith, Sarah Wiegreffe, Yanai Elazar.
- **Posted:** 2025-04-16. ICLR 2025.
- **What it measures:** relation-level LRE causality against mean subject-object co-occurrence. It does not measure depth.
- **§4.2:** "Co-occurrence frequencies highly correlate with causality (r = 0.82). This is notably higher than the correlations with subject frequencies: r = 0.66, and object frequencies: r = 0.59 for both OLMo-7B and OLMo-1B, respectively." This is Pearson, at the relation level.
- **Abstract:** "a linear representation consistently (but not exclusively) forms when the subjects and objects within a relation co-occur at least 1k and 2k times, respectively".
- **Layer:** chosen per relation by a causality sweep (Appendix C). The paper does not relate it to frequency.

### 2611.01945: "Tracing How Language Models Integrate Temporal Anchors into Factual Recall"
- **Authors:** Ayana Niwa, Masahiro Kaneko, Kentaro Inui.
- **Posted:** 2026-11-01.
- **Models:** Llama-3.1-8B, Qwen2.5-7B, Ministral-8B, DeepSeek-R1-Distill-Llama-8B.
- **Cross-model agreement on route balance (not depth). §4.3, route-combination results:** "For subject–relation groups analyzed in two models, GS −GL is positively correlated in all six model pairs (Spearman's ρ = 0.54–0.82). This cross-model agreement suggests that the relative contribution of the two routes reflects properties of the queried fact rather than model-specific noise. One such property is the relation."
- **§4.2:** "Although the magnitude and layer range of each effect vary across models, this layer-wise ordering is consistent across the models." This refers to the ordering of the routes, not of relations.
- **Frequency:** none.

## (2) Other relevant papers found

- **OpenReview ZF443JePxe**, "Corpus Evidence and Factual Recall Causal Tracing with Audited Labels". ICLR 2027, desk rejected. **Abstract only.** Closest to H3.
  - Quote: "We compare activation-patching profiles under these operational labels on Pythia-2.8B and Pythia-6.9B. Across 2,216 traced fact–model pairs, recovery concentrates early in both networks. Among recallable facts, the groups have equal median peak depths, with no detected rank-distribution difference (p = 0.568/0.390)."
  - The groups are a binary present/absent label in a reference corpus, not continuous co-occurrence. The measure is peak causal-tracing depth. There is no within-relation ΔR².
- **arXiv 2411.10813**, "Information Anxiety in Large Language Models" (Bajpai, Masud, Chakraborty, 2024-11-16). Llama-2 family on PopQA. Popularity is measured by Wikipedia pageviews, not co-occurrence.
  - Abstract: "popular questions facilitate early convergence of internal states toward the correct answer."
  - Discussion: "the predicted probability distribution associated with highly popular queries converges much more rapidly compared to the case of less popular questions."
  - This is lens/KL-based and pooled across relations. It is the only direction found that partly runs against H3, and it uses a different predictor and measure.
- **arXiv 2409.14057**, "Co-occurrence is not Factual Association in Language Models" (Zhang, Li, Wu, 2024). Abstract: "knowledge in the form of co-occurrence statistics is encoded in the middle layers of the transformer model … while true factual associations are encoded in the lower layers". This is about fine-tuning; it is not a pretraining-count vs depth regression.
- **arXiv 2603.17624**, "Do Language Models Encode Semantic Relations?" (Diera, Scherp; LREC 2026). Pythia-70M, GPT-2 and Llama 3.1 8B on 4 lexical relations.
  - Abstract: "relation signals … peak in the mid-layers … Difficulty is consistent across models (antonymy easiest, synonymy hardest)."
  - Probing only. No Spearman.
- **OpenReview Pr5m6txuPR**, "Persistent Depth Ordering amid Shifting Block-Bypass Responses…" (ICLR 2027 submission). **Abstract only.** It ranks layers by block importance, not relations, on OLMo-2 and Pythia.
  - Quote: "nearby checkpoints agree closely (median rank correlation 0.91), the first and last less so (0.67)". Useful as a caution for H2 and S5.
- **OpenReview BhrfhXyPMR**, "Predicting Where Recall Fails: The Fact Matters More Than the Entity…" (ICLR 2027 submission). **Abstract only.** Black-box error analysis, not depth.
  - Quote: "the statistic being asked explains about half of the variance in answer error and the player about 5%, and entity popularity has no held-out predictive value." This is analogous in spirit to H1 and H3, but uses error rather than depth.
- **arXiv 2610.22300**, "Knowledge That Is Linear Before Fine-Tuning Generalizes After It" (Mehri, Schütze, 2026). Across 11 models, pre-linearity and generalization correlate "at Pearson r = 0.87 to 0.92" within each model. Not depth, no cross-model ordering.
- **arXiv 2606.01202**, "The Shape of Wisdom" (Rana, 2026). Onset layer (where answers become readable from answer centroids) "differs between models, from 47% to 71% of the way through the network." Not per relation, no frequency.
- **arXiv 2509.08778** (EMNLP 2025) and **ICML 2026 MI workshop L5FqdcbS9n**: cross-architecture differences in which components (attention vs MLP) carry recall. No per-relation depth ordering.
- **NeurIPS 2026 zA0npfmnIS**, "Module Specialization in Transformer Factual Recall…". **Abstract only.** Quote: "A comparison of three natural factual relations in pretrained language models also reveals relation-dependent differences in an intervention-based localization measure."
- **ICML 2026 MI workshop kQc2R75Ysm**, "Rethinking Relation-Specific Neurons". **Abstract only.** About neurons, not depth.
- **Background on frequency and recall accuracy, not depth:**
  - 2505.14824: "more frequent facts are more likely to be recalled correctly".
  - 2509.03405, LMEnt (TACL 2026).
  - 2611.16882 (NeurIPS 2026).

## (3) Cross-model Spearman or similar statistics found

None of these is computed on per-relation resolution depth.

| Source | Measure | Models | Statistic (verbatim) |
|---|---|---|---|
| 2308.09124, App. H | Relation-wise LRE faithfulness | GPT-J, GPT2-XL, LLaMA-13B | "GPT-J's relation-wise performance is strongly correlated with both GPT2-xl (R = 0.85) and LLaMa-13B (R = 0.71), whereas GPT2-xl and LLaMa-13B are moderately corelated (R = 0.58)." |
| 2611.01945, §4.3 | Route balance GS−GL per subject–relation group | 4 models, 6 pairs | "positively correlated in all six model pairs (Spearman's ρ = 0.54–0.82)" |
| 2606.21345, §6.2 | Per-relation minimal path length | LLaMA-3.1-8B vs Qwen3-8B | "significant rank discordance between models" (no number given) |
| OpenReview Pr5m6txuPR (abstract) | Block-bypass layer ranking across checkpoints | OLMo-2, Pythia, SmolLM2 | "median rank correlation 0.91 … the first and last less so (0.67)" |

No cross-family Spearman of per-relation depth or relation random effects was found, for Pythia vs OLMo-2 or any other pair.

## (4) Verdicts

- **H1 (relation ICC of causal half-probability depth is at least 0.30 after fact-level controls): open.**
  - No paper estimates the share of depth variance due to relation.
  - 2606.21345 shows per-relation layer usage differs but calls the evidence "anecdotal".
  - 2308.09124 §4.3 shows per-relation layer differences in LRE faithfulness.
  - 2610.27241 argues the opposite framing for LRE decodability ("largely a property of what a subject's representation already carries, rather than of the relation"). That is a different measure, but expect reviewers to raise it.
- **H2 (per-relation depth ordering shared across families, Spearman of at least 0.7, surviving relation-level controls): open, with weak contrary evidence on a different measure.**
  - Against: 2606.21345 reports "significant rank discordance between models" for path length (LLaMA vs Qwen).
  - Analogous cross-model agreement on other measures: 2308.09124 (0.85/0.71/0.58 for LRE faithfulness) and 2611.01945 (0.54–0.82 for route balance).
  - Nothing found on Pythia vs OLMo-2 depth, and none of these controls for relation-level properties.
- **H3 (within-relation co-occurrence explains almost no depth variance, ΔR² upper CI below 0.02): open.**
  - Closest supporting evidence: ZF443JePxe (abstract only). It finds no peak-depth difference between corpus-evidence groups on Pythia-2.8B/6.9B ("equal median peak depths … p = 0.568/0.390"). That uses a binary label and no within-relation regression.
  - Partly contrary: 2411.10813 (pageview popularity leads to faster lens convergence, Llama-2).
  - 2504.12459 and 2610.27241 (Table 5) relate co-occurrence to relation-level LRE quality, not to depth.

## (5) Search log

- **arXiv export API, by ID:** all 8 required IDs resolved. A second batch fetched 13 candidates and a third fetched 3 more. PDFs were downloaded for the 8 required IDs plus 2606.01202, 2610.22300, 2403.20009 and 2411.10813.
- **arXiv API keyword search:** `abs:"factual recall" AND abs:layer AND abs:frequency`, `abs:"factual recall" AND abs:"co-occurrence"`, `abs:relation AND abs:layer AND abs:"across models" AND abs:factual`, `abs:popularity AND abs:layer AND abs:"factual"`, `abs:"knowledge localization" AND abs:models`, `abs:"factual" AND abs:"pretraining" AND abs:frequency AND abs:"layers"`. Results were mostly empty or noisy.
- **WebSearch:**
  - "relation-specific layers factual recall consistent across model families arXiv 2026"
  - "pretraining co-occurrence frequency layer at which fact is resolved language model"
  - "entity popularity earlier layers factual recall frequency pretraining logit lens"
  - "relation explains variance layer … activation patching relations Pythia OLMo"
  - "openreview ICLR 2027 factual recall layer depth relation pretraining frequency"
  - "knowledge layer co-occurrence infini-gram factual association depth"
  - "per-relation layer … Spearman correlation across models … logit lens tuned lens"
  - "long-tail rare facts resolved in later layers than popular facts"
  - "prediction depth language models token frequency factual"
  - "depth of factual recall depends on relation type intraclass correlation"
  - "PopQA popularity logit lens layer answer emerges earlier"
- **OpenReview API (`/notes/search`):** 4 queries × ICLR 2027, NeurIPS 2026 and ICML 2026: "factual recall layer frequency", "relation layer factual recall across models", "co-occurrence factual recall layer", "pretraining frequency depth factual".
  - The `/notes?id=` endpoint failed with a 403 ChallengeRequiredError. I got abstracts through the search endpoint instead, so OpenReview items are abstract only.
- **Semantic Scholar:** almost every search call returned 429 (rate limited). Only the query "pretraining frequency layer factual association resolves" returned results. The citations endpoint for 2504.12459 worked after retries (30 citing papers), which led to 2610.22300 and 2601.11429.
- **Not checked:** the transformer-circuits.pub "Verbalizable Representations Form a Global Workspace" page (Gurnee et al. 2026), which 2610.27241 cites. Full texts of the OpenReview-only items were not read.
