G5 citation verification (read-only). Paths: /home/user/depth-law/paper/main.tex, appendix.tex (no \cite in appendix), refs.bib.

(1) scripts/verify_bib.py output: "verify_bib: ok (33 entries)", exit 0. It only checks titles against arXiv/Crossref (may have used .cache/bib.json); it does not check authors, years or claims. I checked those separately (section 4).

(2) Table: key | sentence (main.tex line) | status | quote/reason
- benz2026knowledgedebugger | l.58,82,281 "for one fact, causal tracing placing it at different layers under three phrasings" | SUPPORTED | Full-text PDF sec 4.3: "For the triplet ("Eiffel Tower", "The {} is in the middle of", " Paris"), causal tracing localized the knowledge of "Paris" at layer 16, however for (... "You can find the {} in the city of") -> layer 12, and for (... "The {} remains the most iconic structure in") -> layer 20." Paper also reports a second fact (Space Needle, two phrasings) and says causal tracing "may not be suitable for localizing... on the granularity of a single layer". Abstract alone only describes the tool.
- chen2024knowledge | l.58,81,281 localisation tied to query, varies across ParaRel paraphrases | SUPPORTED | Full text sec 1 (A2): "for facts in K_I, localization results are influenced by the query context rather than being fixed. In other words, knowledge neurons are associated with the query rather than the fact." Sec 2: "we employ the ParaRel dataset". Conclusion: "many facts do not conform to" the localization assumption. Neuron-level (l.281 says so).
- elhelo2026task | l.58,83,281 | SUPPORTED | App D.1: "we evaluate the model's performance across all 10 paraphrases for every (dataset, task) pair"; App C Table 3 "Variance decomposition of the (fact, task) ANOVA" with task/fact/interaction/"within-cell paraphrase noise" shares; abstract: facts stored task-specifically.
- hochman2026factual | l.55,87 redundant, distributed, non-contiguous; per-relation path lengths differ between models | SUPPORTED (optional tightening) | Abstract: non-contiguous paths, multiple functionally equivalent paths. Body: "this length hierarchy is highly inconsistent: we observe significant rank discordance between models". Paper calls the relation trend "not a universal trend"/"anecdotal"; the models differ in how they rank relations by path length.
- agarwal2026relation | l.55,87 | SUPPORTED | Abstract page: relation information "starts controlling generation earlier, by 10 to 16 layers"; entity information only controls generation at the final token after routing. Abstract only; full text not opened.
- gupta2025depth | l.55,86 | SUPPORTED | Abstract: "In fact recall, the first token of a multi-token answer needs more depth than the rest." Abstract only.
- meloux2025circuits | l.88 | SUPPORTED | Abstract (PDF p.1): "small perturbations in input data or hyperparameters yield vastly different circuits"; "circuit discovery is not a standalone task but a statistical estimation problem".
- bajpai2024popular | l.90 | SUPPORTED | Abstract: "popular questions facilitate early convergence of internal states toward the correct answer". Sec "Effect of Popularity on Convergence": next-token distribution obtained by "invert[ing] the hidden states after each decoder block"; distance to golden distribution "decreases much more rapidly for the batch of highly popular questions (Head)". A logit-lens-style readout; the passage does not name it a lens.
- merullo2025linear | l.90 | SUPPORTED | Abstract page: subject-object co-occurrence frequency and ICL accuracy "correlate strongly with linear representations".
- hernandez2024linearity | l.90,113 | SUPPORTED | Abstract: computation "closely approximated by a single linear transformation applied to the subject's representation" for factual, commonsense and linguistic relations. LRE-dataset use at l.113 not checked in text.
- razeghi2022frequencies | l.90 | SUPPORTED | Abstract: numerical deduction tasks (arithmetic, unit conversion), performance "strongly correlated with the frequency of the terms in the pretraining data".
- zhang2024patching, heimersheim2024patching | l.96 | SUPPORTED | Abstract pages: activation-patching metrics/methods and best practices; practical guidance on use and interpretation.
- liu2024infinigram | l.91,114 | SUPPORTED | Abstract page: suffix-array engine computing counts/probabilities over trillion-token corpora at millisecond latency.
- meng2022rome | l.55,80,113 | PARTLY SUPPORTED | Abstract: causal intervention points to "middle-layer feed-forward modules". Full text not opened for the exact "causal tracing"/"MLP" wording; CounterFact-source claim at l.113 not verified.
- hase2023localization | l.80 | SUPPORTED | Abstract page: localization results "do not provide any insight into which model MLP layer would be best to edit".
- geva2023dissecting, belrose2023tuned, ghandeharioun2024patchscopes | l.55 | SUPPORTED | Abstract pages: information-flow analysis of recall; tuned lens decodes each block's hidden state to vocabulary; Patchscopes framework for inspecting hidden representations.
- elazar2021pararel | l.58 | SUPPORTED | Abstract page: ParaRel (328 paraphrases, 38 relations); "all tested models are inconsistent".
- kandpal2023longtail, mallen2023popqa | l.90,113 | SUPPORTED | Abstract pages: accuracy tracks pretraining document counts; models struggle with less popular facts (PopQA).
- biderman2023pythia, olmo2025two, li2024dclm, yang2025qwen3, grattafiori2024llama | l.113,197,209 | SUPPORTED | Existence, title, date verified on arXiv pages (model/dataset references only).
- bates2015lme4 | l.115 | SUPPORTED (metadata only) | Crossref title/authors/2015.
- nakagawa2013r2 | l.118 | PARTLY SUPPORTED | Crossref confirms title/authors; I did not read the claim. Year inconsistency: Crossref online 3 Dec 2012, print Feb 2013; bib year = 2012, so it renders "Nakagawa and Schielzeth (2012)" (main.bbl l.257) while the key says 2013. Make key and year consistent (2013 volume year is the usual form).
- brennan2001gtheory | l.73,88 | UNVERIFIED | Book could not be opened. Crossref confirms title, author, Springer 2001 (DOI 10.1007/978-1-4757-3456-0). No quote for the G-theory/decision-study claim.

(3) Never cited anywhere in main/appendix/models/outline: rohweder2026predicting, petroni2019lama, nosek2018prereg.

(4) Author/year checks vs source pages: Benz, Chen, Elhelo, Hochman, Agarwal, Gupta, Meloux, Bajpai, Merullo, Hernandez (8 authors), Zhang, Heimersheim, Liu all match the bib. Razeghi: page gives "Robert L. Logan IV", bib has "Robert L. Logan" (minor fix). Nakagawa year issue above; Brennan author/year match Crossref. Long author lists (Llama 3, OLMo 2, DCLM, Qwen3) checked only for title and first authors.

Open items: Nakagawa year/key mismatch; Brennan unverified; 3 uncited entries; Razeghi "IV"; optional wording tightening for Hochman and Meng.

VERDICT: REVISE
