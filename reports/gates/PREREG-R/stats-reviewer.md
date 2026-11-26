PREREG-R round 7: stats-reviewer confirmation review of A_P2R_new_families revision 7. I edited no file and ran no analysis or model.

My instructions also asked me to compare results/*_gate.md with prereg/HR_revised.md. I did not do that, because your task replaced it (as in rounds 1–6).

**Bottom line:** all seven round-6 findings are fixed, and revision 7 adds nothing BLOCKING. The four-family tally (F1) now has a fixed place, a fixed table structure and one exact introducing sentence, in every cell. There are five small NON-BLOCKING points, listed below.

**Checked directly:**
- **Amendment hash:** sha256 is `6e10c8f74a4eca6b9a95dcc64a2097220647cb37df33ab12b5cb7f1c28f7d17c`, as stated.
- **Files said to be unchanged:**
  - The `analysis/p2r/*.py` files, `materials/p2r_weights_pinned.json` and all four `results/P2R/*.json` match their sha256 entries in `results/ledger.jsonl`. The only ledger lines added since round 6 (203–204) are `make_tables.py` runs.
  - The runbook's mtime (06:38) is earlier than the round-6 report (06:44), so it has not changed since then.
- **The tally's code source:** `p2r_combine.py:71-77` produces `families_per_rule` with exactly the 7 rows the tally needs: the 5 rules from P2 §6, plus H1 and H1-alt.
- **Conflict rule:** it cannot trigger in the four-family union either. H1-alt in ≥ 2 families would need both Gemma and Mistral, and then H1 holds only in Llama.
- **APPLY anchors:** every anchor at `APPLY_P2R.sh:34-51` occurs exactly once in `main.tex`, and both macro lines exist in `models.tex:12-13`.
- **Macros used in the fixed texts:** `\ptRuleAltIcc`, `\ptRuleAltIccLo` and `\ptCiLevel` exist (`numbers.tex:705-710`), and `\label{sec:p2}` is at `main.tex:204`.
- **Git state:** none of the P2R files is committed yet. `APPLY_P2R.sh:17-23` refuses to run until they are, so this is expected.

**Abstract word count** (whitespace split, `main.tex:38-44`): 199 words. Removing the decision-study sentence (24 words) leaves 175.

| cell | S | total |
|---|---|---|
| R1 | 18 | 193 |
| R2 | 22 | 197 |
| R3 | 20 | 195 |
| R4 | 19 | 194 |
| R5 | 22 | 197 |
| R6 | 11 | 186 |

Every cell is at most 200 words. Writing the names as `\GemmaTwoNineB{}` and `\MistralSevenB{}` keeps the same word count. This matches amendment `:63`.

## Round-6 findings
| # | status | evidence |
|---|---|---|
| F1 | FIXED | **Amendment `:65`:** the tally is an L3 item in every cell, R6 included. It is one table: 7 rows, condition, families (from `families_per_rule`), "k of four", label `tab:p2rtally`. It is introduced by one exact sentence, and "No other sentence about the summary is written". **`:81`:** "Nothing else" now covers it, since it is a listed item. **`:51` and `:86`:** consistent with this (small wording gap: see N3). |
| F2 | FIXED (runbook gap: see N1) | **Amendment `:29`:** `MODELS=` the models that passed, Gemma first. **`:35`:** the test loop runs once and is not repeated; a failed or absent `arch_test` file gives `=none`, "it was not run". **`:53`:** the reason definition includes "failed or lacks". **`:40`:** the rerun list includes a failed patching test. |
| F3 | FIXED | **Amendment `:80`(iii):** `main.tex:372` becomes "is not licensed in \llama{} and \olmo{} (…)", and the `:298` caption becomes "(\llama{} and \olmo{})". Both anchors are in APPLY (`:35`, `:36`). |
| F4 | FIXED | **Paper:** `main.tex:41` now reads `\llama{} and \olmo,`. No other model macro is followed directly by a space and a word: a grep of `paper/*.tex` finds only cases followed by `&`. **APPLY:** anchor `:34` is updated. **Amendment:** edit (i) at `:80` is written "in \llama{} and \olmo{}", and the section name is correct. |
| F5 | FIXED | **Amendment `:78`:** the H1-alt sentence uses `$\ge$ \ptRuleAltIcc`, `\ptCiLevel\%` and `\ptRuleAltIccLo`. **`:82`:** uses `Section~\ref{sec:p2}`. **`:79`:** model-name macros; every number goes through `numbers.tex`. No bare `≥`, `%` or "5.2" is left in the fixed texts. |
| F6 | n/a (no change needed) | runbook unchanged |
| F7 | FIXED | **Amendment `:80`(ii):** the sentence becomes "(at most eight in the original \STwo models, seven in \SOne)", and the condition for using it is stated. It is correct: Study 1's largest model is OLMo-2-1124-7B, and the original Study 2's largest models are 8B. |

## New findings (revision 7)
| # | class | where | finding | fix |
|---|---|---|---|---|
| N1 | NON-BLOCKING | runbook `:117` vs amendment `:35` | The runbook says only that a model whose `arch_test` file shows a failure "was not run". It does not repeat the new amendment rule that a model whose `arch_test` file is **absent** from the synced files is passed as `=none` even if it ran. The amendment governs and the rule is mechanical (file present or not), so there is no outcome bias. Amendment `:40`, the rerun list, also names only "failed", not "lacks"; `:35` covers this by saying such models are rerun-eligible. | Add to runbook D: "or whose `arch_test_*.txt` is absent: `=none`, 'it was not run'". |
| N2 | NON-BLOCKING | amendment `:65` | The caption text of `tab:p2rtally` is not given. The order of items inside the L3 paragraph (table, Lg, rule sentences, tally, EXPLORATORY refit) is listed but not stated as binding. "Nothing else" at `:81` already forbids outcome text in captions, so only neutral wording is left open. | Give the caption, e.g. "Preregistered four-family summary (not independent; \llama{} and \olmo{} analysed before registration): families meeting each condition.", and state that the items appear in the listed order. |
| N3 | NON-BLOCKING | amendment `:51` vs `:65` | §5(b) still gives the tally format as "k of 4 families (2 analysed before this amendment)". `:65` gives "k of four", with the disclosure in the introducing sentence. The two say the same thing, but the operative text should be unique. | Make `:51` point to the `:65` format. |
| N4 | NON-BLOCKING | `main.tex:310`, `:318` (L3, before the replication paragraph; not edited, by `:81`) | Two unscoped P2 statements stay in the same subsection: "This is the one headline sentence the preregistration licenses" and "no family-level sentence about wording is licensed". If a replication rule passes in both families, a scoped rule sentence follows later in that subsection. This is the same kind of problem as F3, but weaker: the P2 sentences come first, and the added sentence names its models (`:66`). The text is fixed, so no choice is made after the data. | Optional fixed edit (iv): "…the preregistration licenses in \llama{} and \olmo{}…". |
| N5 | NON-BLOCKING | amendment `:80`(ii) | "At most nine billion parameters" follows nominal sizes: Gemma-2-9B has about 9.24B parameters. This matches the existing convention (Llama-3.1-8B is about 8.03B, and the existing text says "at most eight"). | Optional: say "nominal" in the sentence. |

**Statistical points re-checked:**
- §5(b) error-rate statement: unchanged and correct.
- The tally licenses no sentence. It reports only families and k, with the non-independence stated.
- Mapping from `is True` to PASS: matches `p2r_combine.py:70`.

**Ways to pick an outcome or wording after seeing P2R data:** none found. The things that remain open (the tally caption, the order inside L3, the condition-column phrasing) are presentational. They are already limited by "Nothing else" at `:81`.

**Agreement between amendment, runbook and APPLY:** apart from N1, they agree on the model order, offline loading, the test loop running once, the `=none` reasons, the anchors, the macros, and the hashed files, which now include `paper/models.tex` (`APPLY_P2R.sh:20` and `:61`).

Files:
- /home/user/depth-law/reports/pending_frozen_changes/P2R/A_P2R_new_families.md
- /home/user/depth-law/reports/pending_frozen_changes/P2R/APPLY_P2R.sh
- /home/user/depth-law/reports/p2r/GPU_RUNBOOK_P2R.md
- /home/user/depth-law/paper/main.tex
- /home/user/depth-law/paper/models.tex
- /home/user/depth-law/paper/numbers.tex
- /home/user/depth-law/analysis/p2r/p2r_combine.py
- /home/user/depth-law/prereg/P2_prompt_vs_fact.md
- /home/user/depth-law/results/ledger.jsonl

VERDICT: PASS
