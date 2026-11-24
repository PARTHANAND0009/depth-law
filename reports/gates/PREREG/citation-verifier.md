<!-- citation-verifier subagent (.claude/agents/citation-verifier.md), fresh context, 2026-11-22, PREREG gate round 2, on reports/p2/related_work.tex + .bib and section 8 of reports/pending_frozen_changes/P2_prompt_vs_fact.md (at 3b4736f, after the round-1 fixes). Saved verbatim by the main session; not edited. Staged here for APPLY.sh (the deny rule Edit(prereg/**) also blocks reports/gates/PREREG/). Round 1: citation-verifier_round1.md. -->
## 1. verify_bib.py output (verbatim)
Command: `python3 scripts/verify_bib.py reports/p2/related_work.bib`
```
verify_bib: ok (8 entries)
```
Exit code 0. Note: the script's output is only this one line. I did not rely on it for the checks below. I looked up each entry on the arXiv API and read full text where the abstract was not enough.

## 2. Bib entries vs arXiv (title, authors, id, year)
| key | arXiv id | result |
|---|---|---|
| hase2023 | 2301.04213 | OK. Title and 4 authors match. Published 2023. |
| chen2024 | 2405.14117 | OK. Title and 5 authors match. Published 2024. |
| gupta2025 | 2510.18871 | OK. Title and 4 authors match. Published 2025-10. |
| hochman2026 | 2606.21345 | OK. Title and 3 authors match. 2026 (ACL 2026 Main). |
| elhelo2026 | 2606.27237 | OK. Title and 3 authors match. 2026. |
| benz2026 | 2607.01000 | OK. Title and 4 authors match. 2026. |
| agarwal2026 | 2609.17537 | OK. Title and sole author match. 2026. |
| rohweder2026 | 2610.27241 | OK. Title and 5 authors match (v2 is a metadata correction of an author name). 2026. |

All arXiv ids quoted in P2 section 8 match the bib. I found no mismatches.

## 3. Sentence labels
Where "related_work.tex" and "P2 section 8" make the same claim, they are listed together.

| key | sentence (short) | label | source quote or note |
|---|---|---|---|
| hase2023 | tex l.2 / md: localization is not necessarily where a fact is best edited; localisation does not reliably predict where editing works | SUPPORTED | Abstract: "localization conclusions from representation denoising (also known as Causal Tracing) do not provide any insight into which model MLP layer would be best to edit". |
| chen2024 | tex l.3: the knowledge-localization assumption does not hold for all facts; propose query localization | SUPPORTED | Full text: "the KL assumption does not hold universally". The abstract says "we ... present ... Query Localization (QL) assumption". Section 8 of the md does not characterise this paper, so there is nothing to check there. |
| hochman2026 | tex l.4 / md: redundant, distributed, non-contiguous retrieval; "significant rank discordance between models" in per-relation path length | SUPPORTED | Abstract: "paths are non-contiguous ... models possess multiple, functionally-equivalent paths ... knowledge computation is highly distributed". Full text: "this length hierarchy is highly inconsistent: we observe significant rank discordance between models and between primary and alternative paths". The "length hierarchy" is the ordering of relations by path length, so "per-relation path length" is a fair paraphrase. The study covers only two models (LLaMA 3.1 8B and Qwen3 8B). |
| gupta2025 | tex l.5 / md: first token of multi-token answers emerges later / needs more depth | SUPPORTED | Abstract: "Fact recall task analysis shows that in a multi-token answer, the first token requires more computational depth than the rest." |
| agarwal2026 | tex l.6 / md: relation information becomes causally active before entity information | SUPPORTED | Abstract: "relation information becomes generation-controlling before entity information does". Its opening question asks whether the two "become causally active ... at the same depth". |
| rohweder2026 | tex l.7 / md: predict linear relational decodability from the subject representation alone, without the relation | SUPPORTED | Abstract: "can be significantly predicted from a readout that is not aware of the underlying relation" (the entity lens, "without using any relation-specific information"). Also: "linear decodability is largely a property of what a subject's representation already carries". The study uses Olmo-3-7B only. |
| elhelo2026 | tex l.8: behavioural and parameter-localization analyses show task-specific encoding, so different tasks on the same fact rely on different parameters | SUPPORTED | Abstract: "Our results suggest that they encode knowledge in a task-specific manner ... Parameter localization experiments ... revealing distinct parameter subsets underlying different tasks for the same fact." |
| benz2026 | tex l.9: KnowledgeDebugger, a tool for exploring knowledge localization and editing in transformers | SUPPORTED | Abstract: "we propose KnowledgeDebugger, a GUI-based exploration tool for knowledge localization and editing in Transformers". |
| agarwal2026 | tex l.10 / md: closest work is Agarwal (eight prompt families) | SUPPORTED | Abstract: "four decoder-only models and eight prompt families". |
| elhelo2026 | tex l.10 / md: closest work is Elhelo et al. (task dependence / task-specific encoding of a fact) | SUPPORTED | See the Elhelo row above. |
| (none) | tex l.10 / md: "To our knowledge, none of these estimates how much of a fact's causal depth is a property of the fact versus the prompt wording" | UNVERIFIABLE | This is a negative novelty claim about the cited sources, not an attribution. Across the abstracts and the passages I read, none describes such a variance decomposition, so it is consistent with what I saw. It is hedged with "to our knowledge", which is appropriate. I did not read all eight papers in full, and a search beyond these eight is outside this check. |
| chen2024, elhelo2026, benz2026 | md section 8: "required citations ... content is to be verified ... not characterised here" | SUPPORTED | Nothing is attributed to these sources in the md. Their content is checked in the rows above. |

## Notes (no fix required)
- The md lists these sources under the heading "Measures", but Elhelo, Benz and Chen are not measure papers. This is a labelling issue, not a citation issue.
- Agarwal's abstract describes the effect with "generation-controlling". Its first sentence frames the question as "causally active", so the wording "causally active" is acceptable.
- Rohweder uses an unusually specific author-name correction in v2. The bib uses the corrected 5-author list.

## Required fixes
None.

VERDICT: PASS
