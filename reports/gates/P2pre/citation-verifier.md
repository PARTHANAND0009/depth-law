<!-- citation-verifier subagent (.claude/agents/citation-verifier.md), fresh context, 2026-11-21, on reports/p2/related_work.tex + reports/p2/related_work.bib (P2 A6). Saved verbatim by the main session; not edited. -->
## Step 1: verify_bib output (verbatim)
Command: python3 scripts/verify_bib.py reports/p2/related_work.bib
```
verify_bib: ok (8 entries)
```
Exit code 0. No failures.

Note on method: the fetch tool summarizes pages and refuses quotes over 125 characters. Quotes below are short source quotes from the arXiv abs or HTML pages. Where only a paraphrase was returned, I say so.

## Steps 2-3: claim table (source: reports/p2/related_work.tex)

| key | sentence (short) | label | source quote / note |
|---|---|---|---|
| hase2023 | Where a fact is localized need not be where it is best edited | SUPPORTED | HTML: "Causal Tracing is not indicative of which layer to select for model editing." Also: it "answers a different question than model editing does." |
| chen2024 | Knowledge-localization assumption does not hold for all facts; propose query localization | SUPPORTED | HTML intro: "the KL assumption is not always valid." Also: "facts that violate the KL assumption are categorized as Inconsistent Knowledge." The authors "summarize these findings as Query Localization (QL) assumption." |
| hochman2026 | Retrieval is redundant, distributed and non-contiguous; significant rank discordance between models in per-relation path length | SUPPORTED | HTML Sec. 6.2: "we observe significant rank discordance between models". This is qualitative; the text gives no correlation statistic. The paper says paths are non-contiguous and redundant (LLaMA 3.1 8B and Qwen3 8B). The "per-relation path length" part rests on Sec. 6.2 ("Paths in Individual Relations") and Fig. 12, as reported by the fetch tool. |
| gupta2025 | First token of multi-token answers emerges later in depth than single-token answers | SUPPORTED | HTML: "the first appearance of the single-token answer happens much earlier into a model." It then notes that multi-token first tokens appear at a later layer. Also: "the earliest appearance of the first token in the multi-token fact requires the largest number of layers". The abstract compares the first token to the *remaining* tokens. The single-token comparison is in the body, so the wording stands. |
| agarwal2026 | Relation information becomes causally active before entity information | SUPPORTED | Abs page: "relation information becomes generation-controlling before entity information does." Relation onset precedes entity onset by 10-16 tested layers. |
| rohweder2026 | Predict how linearly decodable a relation is from the subject representation alone, without the relation | SUPPORTED | Abs page (paraphrase): an "entity lens" is a relation-agnostic readout, and its score correlates with LRE faithfulness (rho = 0.7355 on Olmo-3-7B). The authors conclude that decodability depends largely on what the subject representation already carries. No verbatim abstract sentence was returned. |
| elhelo2026 | Analyse LMs used as task-specific knowledge bases with interpretability methods | SUPPORTED | Abs page: "Our results suggest that they encode knowledge in a task-specific manner." The paper uses parameter-localization experiments. The sentence is vague but not wrong. |
| benz2026 | KnowledgeDebugger is a tool for exploring knowledge localization and editing in transformers | SUPPORTED | Abs page (paraphrase): a GUI-based tool for exploring how Transformers localize and edit stored knowledge. The title matches. |

The final sentence ("None of these estimates how much of a fact's causal resolution depth is a property of the fact vs prompt wording") has no \cite{}, so I did not check it. It is a novelty claim, and these abstracts and sections do not obviously contradict it. I did not read the full texts for it.

## Step 4: author lists and years (all 8 entries, against the arXiv abs pages)
- hase2023: Hase, Bansal, Kim, Ghandeharioun. Year 2023 (submitted Jan 2023). Match.
- chen2024: Yuheng Chen, Pengfei Cao, Yubo Chen, Kang Liu, Jun Zhao. Submitted May 2024. Match.
- hochman2026: Hail Hochman, Natalie Shapira, Yoav Goldberg. Submitted 19 June 2026. Match.
- gupta2025: Akshat Gupta, Jay Yeung, Gopala Anumanchipalli, Anna Ivanova. Submitted Oct 2025. Match.
- agarwal2026: Divyansh Agarwal. Submitted 13 July 2026. Match.
- rohweder2026: Rohweder, Mülthaler, Mehri, Gerstner, Schütze. Submitted 19 Oct 2026. Match.
- elhelo2026: Amit Elhelo, Amir Globerson, Mor Geva. Submitted 25 June 2026. Match.
- benz2026: Eric Benz, Lennart Stöpler, Nikolai Bolik, Artur Andrzejak. Submitted 1 July 2026. Match.

Titles also match the bib for all 8 entries.

No file was modified.

VERDICT: PASS
