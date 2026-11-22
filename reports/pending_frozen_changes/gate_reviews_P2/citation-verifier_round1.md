<!-- citation-verifier subagent (.claude/agents/citation-verifier.md), fresh context, 2026-11-22, PREREG gate round 1, on reports/p2/related_work.tex + .bib and section 8 of reports/pending_frozen_changes/P2_prompt_vs_fact.md (at 6df9cf3). Saved verbatim by the main session; not edited. Staged here because the deny rule Edit(prereg/**) also blocks reports/gates/PREREG/; APPLY.sh copies it there. Fixes and round 2: responses.md, citation-verifier.md. -->
CITATION VERIFIER REPORT (PREREG gate). No files edited.

## 1. verify_bib output (verbatim)
`python3 scripts/verify_bib.py reports/p2/related_work.bib`
```
verify_bib: ok (8 entries)
```
Exit code 0. Note: the script checks only that the arXiv title matches the bib title (ratio >= 0.85). It does not check authors, years or content, so I checked those by hand below.

## 2. Bib entries against arXiv abs pages
I fetched each abs page and compared title, authors, year and id.

| key | arXiv id | title | authors | year |
|---|---|---|---|---|
| hase2023 | 2301.04213 | match | match (Hase, Bansal, Kim, Ghandeharioun) | 2023 ok (v1 Jan 2023) |
| chen2024 | 2405.14117 | match | match (Yuheng Chen, Cao, Yubo Chen, Liu, Zhao) | 2024 ok |
| hochman2026 | 2606.21345 | match | match (Hochman, Shapira, Goldberg) | 2026 ok (19 Jun 2026) |
| gupta2025 | 2510.18871 | match | match (Gupta, Yeung, Anumanchipalli, Ivanova) | 2025 ok (v1 Oct 2025) |
| agarwal2026 | 2609.17537 | match | match (Divyansh Agarwal) | 2026 ok (13 Jul 2026) |
| rohweder2026 | 2610.27241 | match | match (all 5) | 2026 ok (19 Oct 2026) |
| elhelo2026 | 2606.27237 | match | match (Elhelo, Globerson, Geva) | 2026 ok (25 Jun 2026) |
| benz2026 | 2607.01000 | match | match (Benz, Stöpler, Bolik, Andrzejak) | 2026 ok (1 Jul 2026) |

All 8 exist, and all ids in Section 8 match the bib. Two arXiv-id ordering oddities (Agarwal 2609 submitted "13 July 2026" and Elhelo 2606.27237 submitted "25 June 2026") come from the fetched pages. I did not check the arXiv listing independently and flag them only for awareness.

The Section 8 mention "Meng et al." has no arXiv id and no bib entry. It is not in the .tex, so it is not a cited claim there.

## 3. Sentence labels: related_work.tex

| line / key | sentence (short) | label | source quote / note |
|---|---|---|---|
| L2 hase2023 | Where a fact is localized need not be where it is best edited | SUPPORTED | Abstract (summarised by fetch tool; not a verbatim quote): facts can be changed by editing weights "in a different location than where Causal Tracing says they are stored"; the editing layer "is a much better predictor of success". The first clause, "causal tracing and activation patching are used to locate...", has no cite of its own (Meng et al. is absent from the bib). |
| L3 chen2024 | Knowledge-localization assumption does not hold for all facts; propose query localization | SUPPORTED | Full text, intro: "KL assumption does not hold universally." Abstract: proposes the "Query Localization" assumption. |
| L4 hochman2026 | Redundant, distributed, non-contiguous retrieval; significant rank discordance between models in per-relation path length | SUPPORTED | PDF text, Sec. on "Paths in Individual Relations": "this length hierarchy is highly inconsistent: we observe significant rank discordance between models and between primary and alternative paths." Abstract: paths are non-contiguous and there are multiple functionally equivalent paths. Caveat: the paper tests only Llama-3.1-8B and Qwen3-8B, so "between models" means those two. |
| L5 gupta2025 | First token of multi-token answers emerges later in depth than single-token answers | SUPPORTED | PDF text: "first appearance of the single-token answer ... (layer 20 for Llama3-8B) compared to the first token of the multi-token facts (layer 25 for both models). This shows that recalling multi-token facts, especially the first token ..., is harder". Abstract: "in a multi-token answer, the first token requires more computational depth". |
| L6 agarwal2026 | Relation info becomes causally active before entity info during factual recall | SUPPORTED | Abstract (summarised, not verbatim): relation information becomes generation-controlling earlier than entity information, by 10 to 16 layers, across 4 decoder-only models and 8 prompt families. |
| L7 rohweder2026 | Predict how linearly decodable a relation is from the subject representation alone, without the relation | SUPPORTED | Abstract (summarised, not verbatim): an "entity lens" trained under a neutral prompt gives a relation-agnostic score that correlates with LRE faithfulness across 28 relations (Olmo-3-7B, rho = 0.7355). Caveat: the evidence is one model and 28 relations. |
| L8 elhelo2026 | Analyse LMs used as task-specific knowledge bases with interpretability methods | PARTIAL | See Section 4. The paper tests whether LMs behave like knowledge bases and concludes they do not. Suggested wording: "Elhelo et al. find, with behavioural and parameter-localization analyses, that LMs encode a fact's knowledge in a task-specific manner, so that different tasks on the same fact rely on different parameters \cite{elhelo2026}." |
| L9 benz2026 | KnowledgeDebugger, a tool for exploring knowledge localization and editing in transformers | SUPPORTED | Abstract: "we propose KnowledgeDebugger, a GUI-based exploration tool for knowledge localization and editing in Transformers." It gives no-code access to EasyEdit methods. |
| L10 (no cite) | None of these estimates how much of a fact's causal depth is a property of the fact vs the prompt wording | UNVERIFIABLE | A universal negative. I read abstracts for all eight, plus partial full text for Hochman, Gupta and Chen. I did not read full bodies. No abstract claims such an estimate. Elhelo (task-specific encoding), Agarwal (8 prompt families) and Chen (query localization) are adjacent to this question, so the claim could be challenged by a reader. Recommend softening to "To our knowledge, none of these ..." and having the author check the Elhelo and Agarwal bodies for variance-style decompositions. |

## Section 8 of P2_prompt_vs_fact.md

| line | sentence | label | note |
|---|---|---|---|
| L123 | Causal tracing localises factual recall (Meng et al.; Hase et al. show localisation does not predict where editing works) | PARTIAL | Hase's abstract says Causal Tracing "doesn't reliably indicate" which layer to edit, and that for some editing variants the relationship is "only weak". It does not say localisation "does not predict". Suggested wording: "does not reliably predict". Meng et al. has no id and is not verifiable as written. |
| L124 | Hochman et al. (2606.21345): redundant, non-contiguous paths; "significant rank discordance between models" in per-relation path length | SUPPORTED | The quoted phrase appears verbatim in the PDF (see L4 above). |
| L125 | Gupta et al. (2510.18871): first token of multi-token answers needs more depth | SUPPORTED | Abstract: "the first token requires more computational depth". |
| L126 | Agarwal (2609.17537): relation information becomes causally active before entity information | SUPPORTED | See L6. |
| L127 | Rohweder et al. (2610.27241): predict linear relational decodability from the subject representation alone | SUPPORTED | See L7. |
| L128 | Chen, Elhelo, Benz "required citations; content not characterised here" | SUPPORTED (as a statement about the file) | Section 8 itself makes no claim about them. However, related_work.tex L3, L8 and L9 do characterise them; those are labelled above. |
| L129 | None of these estimates ... fact vs prompt wording | UNVERIFIABLE | Same as L10 above. |

## 4. What the three "to be verified" papers are actually about
- **Chen et al. (2405.14117), ICLR 2025 spotlight.** It argues that the Knowledge Localization assumption (a fact is stored in a few "knowledge neurons") "does not hold universally". Facts that violate it are separated from Consistent Knowledge facts. It proposes Query Localization, giving the attention module a role in expression, and a Consistency-Aware Knowledge Neuron editing method. The paper uses 39 sets of experiments. The related_work.tex L3 characterisation is accurate.
- **Elhelo, Globerson, Geva (2606.27237).** It asks whether LMs behave like knowledge bases, i.e. whether different queries about one fact return consistent answers. Behavioural and mechanistic analyses show that:
  - they encode knowledge "in a task-specific manner";
  - facts learned on one task often do not appear on others;
  - parameter localization finds different parameter subsets for different tasks on the same fact;
  - chain-of-thought reliance on task-specific parameters goes beyond those tied to the evaluation task.

  The conclusion is that what a model knows and how it is asked are intertwined, which challenges the knowledge-base analogy. L8 of the tex file mislabels this as an analysis of LMs "used as" task-specific KBs. Because the paper concerns query/task dependence of facts, it is the closest of the eight to P2's question. L10's "none of these" sentence needs the hedge.
- **Benz et al. (2607.01000).** A tool paper: KnowledgeDebugger is a GUI exploration tool, inspired by LM-Debugger, with no-code access to EasyEdit methods, shown through case studies of recent findings. It reports no empirical findings about depth or prompt dependence. The tex L9 claim is accurate.
- **Does the text claim anything else about them?** Only related_work.tex L3, L8 and L9, covered above. Section 8 makes no characterisation of any of the three.

## 5. Required fixes (before freezing)
1. Reword related_work.tex L8 (Elhelo) as suggested above. This is the only PARTIAL in the .tex.
2. Reword Section 8 L123 from "does not predict" to "does not reliably predict" where editing works. Either add a Meng et al. bib entry with arXiv id 2202.05262, or drop the name. I did not verify that id here. If added, it must go through verify_bib again.
3. Optional but recommended: hedge L10 and Section 8 L129 with "To our knowledge", and note that Elhelo and Agarwal are adjacent work.

Sources fetched: arxiv.org/abs/<id> for all 8 ids. Full text via arxiv.org/pdf for Hochman, Chen and Gupta. Agarwal, Rohweder, Elhelo, Benz, Hase: abstract page only, in summarised form. The fetch tool returned summaries, not verbatim abstracts, for these. Where I wrote "summarised", the quoted wording is the tool's paraphrase, not a verbatim source sentence.

VERDICT: REVISE
