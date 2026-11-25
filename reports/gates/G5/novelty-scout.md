G5 NOVELTY / LITERATURE CHECK (read-only; no repo file edited)

COVERAGE. Opened this session (arXiv abs or HTML): 2606.27237 (HTML), 2607.01000 (abs + HTML 4.3), 2606.21345 (abs + HTML), 2510.18871 (abs), 2609.17537 (abs), 2510.00845 (abs + HTML), 2411.10813 (abs + HTML), 2504.12459 (abs), 2405.14117 (abs), 2301.04213 (abs), 2308.09124 (abs), 2610.27241 (abs), 2611.01945 (abs), 2410.14405, 2512.18792, 2509.22831, 2607.19386, 2103.06944, 2302.10086, 2305.10519, 2403.19521, 2608.15507, 2510.17028 (abs pages only unless noted). The fetch tool returns summaries, with verbatim quotes capped near 125 characters, so quotes below are short. OpenReview, the ACL Anthology and Semantic Scholar were not queried directly (web search only). "NEW" means "not found", not "proven absent". UNVERIFIED (search snippet only, not used as evidence): 2609.04047, 2607.13304, 2603.00883, 2601.21339, 2309.16042 and 2404.15255 (only appeared as hits; cited in paper as zhang2024patching/heimersheim2024patching, not opened by me).

== A. Verdicts on abstract sentences and contribution bullets ==

A1. Abstract S2, "We patch a prompt's final hidden state, layer by layer, into neutral carrier prompts". Method, not a claim. Closest: Patchscopes-style and Hochman's iterative patching. KNOWN as a technique; the paper does not claim it as new.

A2. Abstract S3 / Contribution 1 (exact within-relation co-occurrence adds little marginal R2; relation share small).
- Verdict: PARTIALLY KNOWN. The equivalence-bounded, within-relation, exact-count patching-depth result is NEW.
- Closest: 2504.12459 (Merullo). Abstract: "formation of linear representations is strongly connected to pretraining term frequencies". 2411.10813 (Bajpai) is the second closest.
- Bajpai details (opened HTML). Popularity is Wikipedia page views from PopQA, not pretraining counts. Models are Llama-2 7B/13B/70B. Convergence is measured by KL of the layer-projected distribution to a one-hot target. Quote: "converges much more rapidly towards the target probability distribution" for head questions. The authors themselves flag the key test as weak (one-sided Welch p = 0.097).
- Delta: Merullo's unit is the relation and the outcome is LRE formation. Bajpai uses a page-view proxy, a pooled unit and a different outcome. Neither uses exact within-relation co-occurrence on a patching depth with an equivalence bound.
- The direction conflict with Bajpai (popular means earlier; your survival HR < 1 means later) is properly flagged in claims.md but is NOT in main.tex. See B.

A3. Abstract S3 / Contribution 1 clause "relation identity carries a large share of depth fails".
- Verdict: NEW as a variance share. The ordering part is PARTIALLY KNOWN.
- Closest: Hochman 2606.21345, quote: "we observe significant rank discordance between models and between primary and alternative paths."
- Also relevant, and uncited in main.tex: Rohweder 2610.27241. Its abstract says LRE decodability "depends mostly on what a subject's representation already encodes, not on the relation itself". That is directionally consistent with a small relation share, so the paper should cite it.
- Niwa 2611.01945 is a smaller point: the balance of recall routes "shifts with the query (for example, with the relation)".
- Delta: Hochman uses per-relation minimal-path length and no statistic. Your measure is a mixed-model ICC, so Hochman does not contradict a small ICC_rel or rho of about 0.5-0.6.

A4. Abstract S4-S5 / Contribution 2 (fact share above zero; paraphrase-related shares; fact share includes answer-token identity).
- Verdict: PARTIALLY KNOWN (qualitative message). The preregistered quantification for a layer-wise readout depth is NEW.
- Closest priors:
  - 2606.27237 (Elhelo), HTML: "For each dataset-task pair we composed 10 prompt paraphrases." A two-way ANOVA tests the fact x task interaction, which grows and explains "23%" of variance in the final model (the page I read says it uses paraphrases as replications within each cell, and the source text describes the ANOVA as "with no interaction term", so the exact model needs checking before you characterise it). The outcome is behaviour plus parameter localization (heads and neurons) on OLMo-2-7B/13B and Gemma-2-9B/27B. It reports no layer-sweep depth.
  - 2607.01000 (Benz) 4.3, GPT2-XL: causal tracing places "Paris" at layers 16, 12 and 20 under three phrasings, and "Further facts and rephrasings showed similar patterns."
  - 2405.14117 (Chen): query localization.
  - 2411.10813 (Bajpai): 10 lexical variants per query, paraphrase variability that "increases with the logarithm of the popularity", and cross-paraphrase cosine similarity of FFN up-projections by layer. This is a closer prior on "paraphrase variability of layer-wise internals" than main.tex admits.
- Delta: nobody decomposes the variance of a layer-wise readout depth into fact and paraphrase components with a null test.
- Caveat: the sentence "fact share above zero" is a weak claim, and the paper states this itself.

A5. Abstract S4 "paraphrase-related shares of X--Y, exceeding the fact share ... in one model".
- Verdict: NEW as an estimate; the H1 result is weak (the paper says so). No contradiction found.

A6. Abstract S5 / Contribution 3 (decision study: n' paraphrases for G = 0.8).
- Verdict: NEW for interpretability depth measures. The method (G-theory) is KNOWN: Brennan, plus 2026 uses for LLM outputs and annotation (2609.04047, 2607.13304 are UNVERIFIED snippets).
- Closest: 2510.00845 (Meloux). Abstract: "small changes to inputs or hyperparameters can produce very different circuits." HTML: no ICC or reliability coefficients, and "future work should aim to decompose the total observed variance." This supports your delta.
- Also near: 2512.18792 (Meloux et al., "Dead Salmons"), which discusses variance due to finite input sampling. 2607.19386 (van der Ben et al.) has a variance decomposition of autointerpretability scores. Neither is a G-study of patching depth.

A7. Contribution 3, second clause ("an open record of every preregistered test ... integrity incident").
- Verdict: PARTIALLY KNOWN as a practice. Preregistration in NLP is advocated in 2103.06944 (van Miltenburg et al., NAACL 2021) and debated in 2302.10086 (Søgaard et al., EACL 2023). I found no preregistered mechanistic-interpretability study. Both of these should be cited. Do not claim "first preregistered" unless you have searched OSF.

A8. Title and framing ("How much of ... is fact-level?"). The question is framed fairly. The intro sentence "What has not been measured is how much of a layer-wise depth is fact-level at all" is defensible but needs "to our knowledge", given Bajpai and Elhelo.

== B. Fairness of related-work characterisations ==
- Hase 2301.04213: FAIR. Abstract: localization results do not predict which MLP layer is best to edit.
- Chen 2405.14117: FAIR for the sentence in main.tex. The abstract page I opened frames it as a Query Localization assumption (a generalisation of Knowledge Localization) plus a Consistency-Aware Knowledge Neuron method. The statement that it is "varying across ParaRel paraphrases" is from the G4 scout's earlier read, which I did not re-verify on the paper body. Mark that detail UNVERIFIED here.
- Benz 2607.01000: FAIR. The "for one fact ... three phrasings" wording matches 4.3. It is anecdotal, and the paper correctly says so.
- Elhelo 2606.27237: MOSTLY FAIR, but the "variance decomposition of behaviour" wording needs care. The page says the ANOVA is "with no interaction term" in one place and reports an interaction share of 23% elsewhere. Check the exact model and paraphrase handling in section 2.3 before the camera-ready. Also mention that its abstract is about task-specific encoding and training dynamics.
- Gupta 2510.18871: FAIR. The abstract says the first token of a multi-token answer "needs more depth", checked with activation patching and early exit. Write "probe-based".
- Hochman 2606.21345: FAIR but incomplete. "Per-relation path lengths that differ between models" matches "significant rank discordance between models and between primary and alternative paths". The paper itself calls the relation-to-path-length link "anecdotal" and "not a universal trend", so say "reports no statistic". Its prompts are correct predictions only (2,000 per model, single-token targets), and the minimal-path patching differs from a half-probability onset.
- Agarwal 2609.17537: FAIR for "relation information active before entity information". Relation onset precedes entity onset by 10-16 tested layers across four models and eight prompt families. Note that Agarwal varies prompt families, so it is also a prompt-dependence data point. The intro sentence lists it among papers that compare depths "across facts, models and training", which slightly overstates it.
- Meloux 2510.00845: FAIR. Its abstract mentions input and hyperparameter instability. It has no G coefficient.
- Bajpai 2411.10813: UNDERSTATED. main.tex says only "relate popularity to how early answers converge in a lens". Add these points:
  - Popularity there is Wikipedia page views, not co-occurrence.
  - It uses 10 lexical variants per query and reports paraphrase variability that grows with popularity.
  - Its direction (popular means earlier) is the opposite of your survival HR (later).
  - The test is weak (p = 0.097).
- Merullo 2504.12459: FAIR. The sentence "linearity of relation representations" is accurate. Add that it is relation-level and uses OLMo-7B/GPT-J.
- Hernandez 2308.09124: FAIR (LRE).

== C. Missing references a reviewer would expect (all abs pages opened) ==
- Paraphrase robustness and prompt sensitivity: 2305.10519 (Dong et al., KaRR; stability of knowledge under paraphrased prompts); 2410.14405 (Saynova et al.; causal tracing differs across prediction scenarios, which bears on your correct-cells-only design); 2403.19521 (Lv et al.; factual-recall mechanisms, whose template-robustness claim I could not verify, so it is UNVERIFIED for that point).
- Reliability and generalizability of interpretability: 2510.00845 (already cited); 2512.18792 (Dead Salmons); 2509.22831 (Trott, generalizability across models); 2607.19386 (variance decomposition of autointerp scores).
- Preregistration: 2103.06944 (van Miltenburg et al., NAACL 2021); 2302.10086 (Søgaard et al., EACL 2023).
- Relation-level and frequency work relevant to H1/H3: 2610.27241 (Rohweder; LRE decodability depends mostly on the subject representation, not the relation) and 2611.01945 (Niwa; the balance of recall routes shifts with the query). Neither is cited in main.tex.
- Not located: a G-theory or ICC study of patching depth. A statement that none exists should be hedged ("we found none").

== D. Required changes (wording) ==
1. Add Bajpai details, and move its opposite-direction note from claims.md into the Frequency paragraph or Discussion.
2. Cite van Miltenburg 2021 and Søgaard 2023 where preregistration is introduced. Soften any implication of novelty for preregistration itself.
3. Add Rohweder (2610.27241) to the Study 1 discussion. Optionally add Niwa.
4. In the abstract and intro, write "to our knowledge" before "not measured".
5. Re-check Elhelo section 2.3 (the "no interaction term" versus 23% interaction wording) before describing its model.
6. Replace "at most" wording for point estimates with "point estimate X, upper 95% bound Y". The abstract sentence "point estimates <= ...; all upper bounds below ..." is already fine. Check the Contribution 1 bullet, which says "by at most \hrDRsqMax"; it should name the bound.
7. Change "Chen ... varying across ParaRel paraphrases" to hedged wording unless the paper body is re-opened.

No headline claim is ANTICIPATED. The combination (preregistered fact-share null on a layer-wise readout depth, exact-count equivalence bound, and a G/D-study) is NEW. Individual sub-messages are PARTIALLY KNOWN.

VERDICT: REVISE
