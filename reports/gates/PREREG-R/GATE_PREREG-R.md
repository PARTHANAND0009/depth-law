# GATE PREREG-R: P2R confirmatory replication in two new model families

STATUS: AWAITING GO PREREG-R. No P2R model has been run (tokenizers and Hub metadata only; no weights downloaded, no outputs on project data).

## 1. Verdict
| reviewer | rounds | final verdict | file |
|---|---|---|---|
| stats-reviewer | 7 (REVISE ×4, PASS at round 5, REVISE at round 6, PASS at round 7) | **PASS** (no blocking findings; 5 non-blocking, section 6) | `stats-reviewer.md` (round 7); earlier rounds `stats-reviewer_round1.md` … `_round6.md`; responses `responses.md` |

Reviewed text: amendment revision 7, sha256 `6e10c8f74a4eca6b9a95dcc64a2097220647cb37df33ab12b5cb7f1c28f7d17c`. It has not changed since the PASS.

## 2. What is staged (for you to review and install)
| item | file | install |
|---|---|---|
| Amendment (revision 7) | `reports/pending_frozen_changes/P2R/A_P2R_new_families.md` | `APPLY_P2R.sh` → `prereg/amendments/` + `.sha256`, tag `prereg-P2R` |
| Gate entry | `reports/pending_frozen_changes/P2R/gates_PREREGR.txt` | `APPLY_P2R.sh` → `gates.yaml` |
| Analysis wrapper | `analysis/p2r/p2r_analysis.py` (frozen `p2_analysis.py`; only the model list and two family names changed) | hashed |
| Four-family summary | `analysis/p2r/p2r_combine.py` (frozen `decide()` on the union; per-call decision files cross-checked; per-rule family lists) | hashed |
| Tests | `analysis/p2r/p2r_test.py`: all passed (ledger) | hashed |
| Tokenizer check | `analysis/p2r/p2r_tokcheck.py` → `results/P2R/tokcheck.json` | hashed |
| Model-file pins | `analysis/p2r/p2r_weights_check.py`, `materials/p2r_weights_pinned.json` (Gemma 15 files, Mistral 9: weights, index, config, generation config, tokenizer files) | hashed; tests `hubcheck_test.json` (OK, 24), `cachecheck_test.json` (OK, 9), `cachecheck_negtest.json` (one altered byte → FILES CHANGED) |
| GPU runbook | `reports/p2r/GPU_RUNBOOK_P2R.md` | you run it |
| Pre-commit fix (**urgent**) | `reports/pending_frozen_changes/P2R/pre-commit.proposed`, `APPLY_precommit_fix.sh` | decision 1 |

## 3. Model choice (published factual-QA accuracy; official sources only)
| model | family | TriviaQA | Natural Questions | source |
|---|---|---|---|---|
| **google/gemma-2-9b** | Gemma (new) | 76.6 | 29.2 | Gemma 2 report, Table 13, 5-shot |
| **mistralai/Mistral-7B-v0.1** | Mistral (new) | 69.9% | 28.8% | Mistral 7B paper, Table 2, 5-shot |
| deepseek-llm-7b-base | DeepSeek | 59.7 | 22.2 | DeepSeek LLM paper, Table 5 |
| Yi-1.5-9B, Falcon3-7B-Base, Granite-3.0-8B-base | — | not reported | not reported | official model cards |
| (P2) Llama-3.1-8B, included | Llama | 77.6 (TriviaQA-Wiki) | not reported | model card |
| (P2) Qwen3-8B, MISSING | Qwen | not reported | not reported | Qwen3 report §3.3 |

Tokenizer check (ledger, all 10 frames): for both new tokenizers, all 3000 fact–paraphrase pairs give the same first token as the continuation of the filled prompt; 0 bare-space first tokens; 0 shared within a relation. Disclosed in amendment §0: P2 results were seen; Qwen3's P2 failure motivated the QA-accuracy criterion; the first tokenizer check ran outside the ledger and the CPU cap.

## 4. What the amendment fixes in advance
- **Replication test (confirmatory):** each P2 headline rule must hold in **both** Gemma-2-9B and Mistral-7B-v0.1. Primary: "The fact share is above zero".
- **Wording:** a 3×3 outcome table (PASS / FAIL / MISSING per model) with exact sentences for the abstract (replaces the decision-study sentence; 186–197 words in every cell), contribution 2, a fixed replication paragraph in §5.2, the Discussion and the Conclusion. FAIL is worded "the preregistered test did not show …". Fixed MISSING reasons. Three fixed scope edits and two Limitations sentences. No other text about P2R anywhere.
- **Four-family summary:** one fixed table plus one fixed sentence in the replication paragraph. Not independent (Llama and OLMo were analysed before); never in the abstract, contributions, headings or conclusion. Error rate stated (at least about 0.05, possibly up to about 0.2).
- **Provenance:** pinned commits; byte hashes of every weight, config and tokenizer file checked before the driver starts; offline loading. A failed check makes that session's models MISSING.
- **Patching tests** on each new architecture before the driver; a failing model is not run (rerun-eligible).
- **Sessions:** one session, INR 700. A second session only for incomplete or not-run models, decided from logs only. The gating analysis runs **once**, after the rerun decision is committed.
- **Reporting:** once a session starts, its outcome is reported in every later paper version. If the analysis is not done by Dec 20, the current draft is submitted with one fixed Limitations sentence.

## 5. Decisions for you
1. **Commits are blocked since e7c79a1.** The legacy pre-commit check compares `prereg/` with 7725c5b byte for byte, so the human-authorized DEVIATIONS.md line makes every commit fail. The fix (`pre-commit.proposed`) excludes DEVIATIONS.md from that comparison and requires it to be append-only against 7725c5b and HEAD. Run `bash reports/pending_frozen_changes/P2R/APPLY_precommit_fix.sh`, or authorize me once. **Everything since e7c79a1 is uncommitted** (G5 renames, the GO G5 paper edit, all P2R files, these reviews); I commit and push it as soon as commits work.
2. **GO PREREG-R**: approve the amendment as reviewed, or with some or all of the optional edits in section 6, which I would apply before installing. Then run `APPLY_P2R.sh` (or authorize me once), then push `master` and the tag `prereg-P2R`.
3. **GPU session** (yours, after the tag): runbook `reports/p2r/GPU_RUNBOOK_P2R.md`.
   - RTX PRO 6000 only; INR 700 in total including set-up.
   - Three stops: an instance shutdown timer at login, the driver's budget, and the manual stop rule.
   - Planning estimate: about 21 min for Gemma, 13 min for Mistral and 25–30 min of set-up, including downloads, the hash checks and the patching tests.
4. Main residual risk (stated in the amendment): a model fails the inclusion rule, as Qwen3-8B did, and is MISSING with no substitute. The replication is then inconclusive (cells R3/R5).

## 6. Optional edits (round-7 non-blocking findings; not applied, so the PASS covers the text you approve)
| # | edit |
|---|---|
| N1 | Runbook section D: also state "a model whose `arch_test_*.txt` is absent: `=none`, 'it was not run'" (the amendment already says this). |
| N2 | Give the tally table's caption text; state that the L3 items appear in the listed order. |
| N3 | §5(b): point to the §5(c) tally format instead of repeating it. |
| N4 | Fixed edit (iv): scope two earlier §5.2 sentences ("…the preregistration licenses in \llama{} and \olmo{}…"). |
| N5 | Say "nominal" in the "at most nine billion parameters" sentence. |

## 7. Paper changes in this round (outside "keep the paper as is"; no change of content)
- Abstract: `\llama and` → `\llama{} and` (it rendered "Llama-3.1-8Band"); same words, 199 words. Needed because the amendment freezes that sentence verbatim.
- `paper/models.tex`: two name macros (`\GemmaTwoNineB`, `\MistralSevenB`), unused until the replication is reported.
- Rebuilt: check_numbers ok, verify_bib ok (37), 14 pages.

## 8. GO G5 items done earlier in this round
- APPLY_guard.sh: human-authorized one-line edit and a single run (commit e7c79a1, pushed). Installed hook 25/25, kill/S5 13/13, guard 11/11; 22 frozen files immutable.
- G5 review renames (contents unchanged): `gate_check.py G5` → ready.
- Paper item 4: the answer-identity refit (D1 fact share 0.186 / 0.206) is in the abstract, contribution 2, Table 3, the Figure 1 caption and a §5.2 heading.
