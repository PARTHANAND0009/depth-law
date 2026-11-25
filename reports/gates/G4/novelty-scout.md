<!-- novelty-scout subagent, fresh context, 2026-11-25, gate G4 (paper setup), on claims/claims.md and reports/paper/titles_abstract.md. Saved verbatim by the main session; not edited. -->
G4 hostile novelty check (read-only; no repo file edited). Coverage limits: I opened these on arXiv this session: 2405.14117, 2606.27237 (HTML), 2606.21345 (abs+HTML), 2607.01000 (abs+HTML), 2510.18871 (abs), 2301.04213 (abs), 2411.10813 (abs page only), 2510.00845 (abs). OpenReview was unreachable. I did not query Semantic Scholar or the ACL Anthology directly. "NEW" means "not found in reachable search", not "proven absent". Where an abstract page was too long to quote, I used a paraphrase and say so.

TABLE (claim | verdict | closest prior work | quote from opened paper | delta)

(i) Within-relation exact co-occurrence explains <2% of depth variance (equivalence bound)
- Verdict: PARTIALLY KNOWN. The equivalence-bounded null is NEW.
- Closest: 2504.12459 (Merullo et al.), 2411.10813 (Bajpai et al.), OpenReview ZF443JePxe (UNVERIFIED).
- Quote: Merullo, copied from the earlier opened-PDF report and not re-opened by me: "Co-occurrence frequencies highly correlate with causality (r = 0.82)", at relation level and for LRE quality. Bajpai (abstract page I opened, paraphrase only): popular questions make internal states converge early on the correct answer.
- Delta: both use a different outcome (LRE causality or lens convergence) and a pooled or relation-level unit. The delta is a within-relation, exact-count, patching-depth test with a preregistered equivalence bound. The Bajpai direction (popular means earlier) differs from your survival HR of about 0.93, which is slightly later. Cite it and state the measure differences. How Bajpai measures popularity is not stated on the page I opened.

(ii) ICC_rel <= 0.06, with moderately shared relation orderings across families
- Verdict: NEW as a variance share. The ordering part is PARTIALLY KNOWN.
- Closest: 2606.21345 (Hochman et al.); also 2610.27241 and 2308.09124 (from earlier reports, not re-opened).
- Quote: Hochman (opened): "significant rank discordance between models and between primary and alternative paths." The paper gives no statistic.
- Delta: different unit (minimal-path length vs a mixed-model relation share), different models (Llama/Qwen vs Pythia/OLMo), and an actual rho with a permutation test. Hochman's text does not contradict rho of about 0.5-0.6.

(iii) Fact share above zero (0.28-0.42); most of the rest is fact x paraphrase interaction
- Verdict: PARTIALLY KNOWN (the qualitative message). NEW (the quantification).
- Closest: 2606.27237 (Elhelo et al.), 2405.14117 (Chen et al.), 2607.01000 (Benz et al.).
- Quote:
  - Elhelo (opened HTML): "For each dataset-task pair we composed 10 prompt paraphrases." The fact x task interaction is tested by a two-way ANOVA, and "accounts for about 23% of variance in the final model." Paraphrase share rises from 0.09 to 0.39-0.48 over training.
  - Chen: knowledge neurons are "tied to the query rather than the fact itself, so localization results can vary with how the question is phrased." LLaMA3-8b: "77%" of facts violate the KL assumption.
  - Benz section 4.3 (GPT2-XL): the same fact is traced to layer 16, 12 and 20 under three phrasings, and "further facts and rephrasings showed similar patterns."
- Delta: "localization depends on phrasing" is already published, anecdotally (Benz) and at neuron level (Chen). Elhelo already runs a 10-paraphrase variance decomposition of fact-by-task behaviour. The delta is a preregistered variance decomposition of a patching depth, a fact-share null test, and the fact x paraphrase split, on Llama-3.1-8B and OLMo-2-7B. Do not frame it as discovering prompt dependence.

(iv) D-study: 4-8 paraphrases for G = 0.8
- Verdict: NEW for interpretability depth measures. The method is known elsewhere.
- Closest: 2510.00845 (Meloux et al., opened); 2609.04047 (UNVERIFIED, G-theory for LLM outputs).
- Quote: Meloux (abstract page, paraphrase): "small changes to inputs or hyperparameters can produce very different circuits."
- Delta: Meloux shows circuit-discovery instability but has no G coefficient and no per-fact depth. G-theory and D-studies for LLM outputs appear in 2026 preprints that I saw only as search snippets. Cite the method as borrowed.

(v) Rank-1 stable-from-l depth is defined only for correct prompts
- Verdict: PARTIALLY KNOWN. It is a trivial derivation; restricting to correct prompts is standard practice.
- Closest: 2606.21345 (earlier-report claim that it uses correctly predicted prompts; not re-verified by me).
- Quote: none opened that states the derivation.
- Delta: I found no paper that states or audits it. Present it as a methods note, not a contribution. The claims.md audit counts (720/0/0/3180) support it.

ABSTRACT AS A WHOLE: no paper found decomposes fact vs prompt variance of layer-of-recall with a fact-share test and a D-study. Searches covered G-theory in interpretability, logit-lens/patching layer under paraphrase, 2026 fact-vs-prompt recall decompositions, and frequency vs layer. Verdict: NEW in combination, with PARTIALLY KNOWN sub-messages. No central claim is already published.

MISCHARACTERISATIONS IN claims.md (the six required papers)
1. Benz et al. 2607.01000 is WRONG. The table says "no depth or prompt-dependence findings; cite as tooling context only". Section 4.3 ("Causal Tracing is a poor predictor for knowledge localization", GPT2-XL) shows causal tracing placing "Paris" at layers 16, 12 and 20 under three phrasings. This is the closest prior demonstration of your paraphrase result. It is anecdotal, with no variance decomposition, but it must be cited as such and the "tool paper only" wording removed.
2. Chen et al. 2405.14117 is understated. The table calls it "complementary: their facts differ in whether they localise". Their Query Localization assumption says localization depends on the query. They test ParaRel paraphrases on GPT-2, LLaMA2-7b and LLaMA3-8b. Reword the delta to: neuron-level, per-fact inconsistency across paraphrases vs a depth readout with a fact-share estimate.
3. Elhelo et al. 2606.27237 is called "closest", but the stated delta overclaims. Elhelo already uses 10 paraphrases per fact-task, a two-way ANOVA with a fact x task interaction (about 23%) and a paraphrase share. Its mechanistic part uses OLMo-2-7B/13B and Gemma-2-9B/27B. Drop "estimate its share" as a differentiator. The delta holds only on "depth readout" and "D-study".
4. Hochman et al. 2606.21345 is accurate on measure and models (Llama-3.1-8B, Qwen3-8B). Add two points. It does no template or paraphrase analysis beyond an entity-first vs relation-first check (App. D), and it uses one CounterFact prompt per fact. It gives no rank statistic, so say "no statistic reported".
5. Hase 2301.04213 is accurate (localization vs editing).
6. Gupta 2510.18871 is accurate in substance. The abstract page says "probe-based" with activation patching and early-exit checks. The "TunedLens" label comes from the earlier report and I did not confirm it. Write "probe-based lens".

TITLE AND ABSTRACT RISKS
- "at most" in the abstract. "Relation identity explained at most 0.060" and "added at most 0.0016" are point estimates, but "at most" reads as a bound. The upper 95% bounds are 0.123 and 0.0104 (OLMo). Write "point estimate X, upper 95% bound Y".
- Titles 2 and 3 ("Fact or Phrasing?", "One Fact, Many Depths") invite an "already known" reaction from Benz and Chen. They also promise a phrasing-wins result that H1 failed to support at family level. Title 1 is safest. If you keep 2 or 3, add "readout depth" and "preregistered".
- "reliable per-fact depth" rests on exchangeable paraphrases and correct cells only. Add "among correctly answered facts".
- Related work must cite Benz (the 16/12/20 example) and Chen to pre-empt reviewers who know them, and Elhelo for the 10-paraphrase ANOVA precedent.

MUST-CITE (opened this session): 2405.14117, 2606.27237, 2606.21345, 2607.01000, 2510.18871, 2301.04213, 2411.10813 (abstract page only), 2510.00845.
Cite from earlier opened-PDF reports, not re-opened by me: 2504.12459, 2610.27241, 2308.09124.
UNVERIFIED (do not use as evidence): OpenReview ZF443JePxe, 2609.04047, 2603.00883, 2604.18389, 2602.14080.

One-line experiment per claim:
- (i) Run Bajpai-style convergence layer vs exact count on your facts.
- (iii) Report fact x paraphrase by relation to separate it from Elhelo's fact x task interaction.
- (iv) Add a bootstrap over facts and paraphrases for the G interval.

VERDICT: REVISE
