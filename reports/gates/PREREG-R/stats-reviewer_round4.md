PREREG-R round 4: stats-reviewer re-review of A_P2R_new_families revision 4. I edited nothing and ran no analysis or model.

The system prompt also asked for a comparison of results/*_gate.md against prereg/HR_revised.md. I did not do it, because your task replaced it (as in rounds 1–3).

**Bottom line:** 11 of the 12 round-3 findings are fixed and 1 is partly fixed (N2). The fixed cell sentences have two new problems, both blocking: where they are inserted, and how a FAIL is worded. The amendment needs another revision before GO PREREG-R.

**Checked directly:**
- The amendment's sha256 is `1329a470…1725f`, as stated, and it did not change during the review.
- The current sha256 of every P2R script, `materials/p2r_weights_pinned.json`, `results/P2R/tokcheck.json` and `results/P2R/cachecheck_test.json` equals its last ledger entry (`results/ledger.jsonl:196-199`).
- The frozen code (`src/depthlaw/depth/common.py`, `scripts/p2_gpu_run.sh`, `analysis/p2/p2_analysis.py`) shows no change against tag `prereg-P2`, and `prereg/HASH_P2.txt` lists only the P2 prereg file.
- The pin file lists 15 files for Gemma and 9 for Mistral, so 24 in total, which matches the runbook's expected "24 files compared".
- The bootstrap and the null test are reproducible: `bootMer` draws its simulations before the parallel step after `set.seed` (`p2_analysis.R:35-37`), and the null uses `simulate(seed=)` (`p2_null_fns.R:23`). So an identical rerun after a crash (§4:41) cannot give a different result.
- **Abstract word count (§5(c)), by whitespace on the current `paper/main.tex:38-44`:** 199 words. Removing the last sentence (24 words) leaves 175. With the real model names, the cell sentence S adds 18 / 19 / 20 / 17 / 20 / 11 words for R1–R6, giving totals of 193 / 194 / 195 / 192 / 195 / 186. This matches the amendment's 186–195; all totals are 200 or less.

## Round-3 findings
| # | status | evidence |
|---|---|---|
| N1 abstract length | FIXED | `A_P2R_new_families.md:63`, `:71-76`; counts verified above |
| N2 EXPLORATORY clauses extended to the new models | PARTLY | No existing sentence is edited any more (`:62`), but the insertion point re-creates the problem through the sentences that follow: see new finding A |
| N3 which cell governs the other rules | FIXED | `:78`. The sentence to add for H1 is undefined: see new finding C |
| N4 abstract scope | FIXED as proposed ("verbatim", `:63`). The text still reads misleadingly: see A |
| N5 MISSING reasons for file problems | FIXED | `:20`, `:53`; runbook `:92` |
| N6 gating call that crashes | FIXED | `:41` |
| N7 RATE not passed to the driver | FIXED | runbook `:14`, `:70`, `:74`. An empty RATE makes the assert fail, so the driver does not start |
| N8 stop-rule text, `hub_observed.json` | FIXED | runbook `:5`, `:92` |
| N9 bytes not hashed, index file not pinned | FIXED | `p2r_weights_check.py:27`, `:30-40`, `:59-64`, `:79-81`. The altered-byte test is not in the ledger: see E |
| N10 code-fix check | FIXED | `:40` |
| N11 no-pathspec commit | FIXED | `APPLY_precommit_fix.sh:17-18` |
| N12 paper exception | FIXED | `:91` |
| Round-2 #2 (wording table), PARTLY in round 3 | PARTLY | Still open through A and B |
| Round-2 #7 (APPLY script), PARTLY in round 3 | FIXED | `APPLY_precommit_fix.sh:17-18`; `APPLY_P2R.sh:37-38` |

## New findings
| # | class | where | finding | could change the outcome or its wording? |
|---|---|---|---|---|
| A | **BLOCKING** | `A_P2R_new_families.md:63`, `:66`; `paper/main.tex:377-378`, `:387-388`, `:41-43` | **The inserted sentence makes the next, unchanged sentences read as if they were about Gemma and Mistral.** Lg goes directly after the first sentence of the Discussion paragraph and of the Conclusion; S goes directly after L1 in the abstract. The next sentences stay verbatim and unscoped. In the Discussion, `:378` "In both models the estimated paraphrase-related share is larger … confirmed by the preregistered test in one model only; … under D4 not in \olmo{}" would follow a sentence naming Gemma-2-9B and Mistral-7B-v0.1, so "both models" reads as those two. This attributes P2's H1 results to the new models, and that is false whenever their H1 results differ. The Conclusion (`:388` "one of two models") and the abstract (`:42-43`, the share range and "in one model") have the same problem. §5(c) forbids editing these sentences, so after the data the authors must either print misattributed text or reword it unplanned. **Fix:** fix the positions in advance where no unscoped sentence follows. In the abstract, put S last (in place of the removed decision-study sentence; the word count is unchanged). Put Lg as the last sentence of the Discussion paragraph, and after the Conclusion's second sentence (before "Code, materials…"). | Yes: wording at L1, L4 and L5 |
| B | **BLOCKING** | `:72`, `:74`, `:75` (Lg for R2, R4, R5); P2 prereg `:276` | **The FAIL sentences state absence instead of "not shown".** FAIL means the null test gave p ≥ 0.01. Lg says "the fact share was … not [above zero] in <FAIL model>" and "was not above zero in either model". That states the share is zero, which the test cannot show; a point estimate around 0.2 with p = 0.02 would be printed as "not above zero". It also departs from the frozen P2 §6 ("Otherwise: report the estimated shares and n′ as an intermediate result"), which §2 says is unchanged. These sentences go into the contribution bullet, the Discussion and the Conclusion, so any later correction would be rewording after the data. **Fix:** "the preregistered test did not show a fact share above zero in <FAIL model>". The S sentences ("found no …", "but not in") can stay. | Yes: wording at L2–L5 in R2, R4 and R5 |
| C | NON-BLOCKING | `:78`; P2 prereg `:262-276` | "H1 / H1-alt themselves … its P2 section 6 sentence is added". P2 §6 has no sentence for H1 itself, so the L3 sentence for a both-PASS H1 would be written after the data. **Fix:** give the exact sentence. | L3 only; the per-model table shows the result anyway |
| D | NON-BLOCKING | `p2r_weights_check.py:74-75`; runbook `:43-46`; amendment `:20`, `:40` | **Any new commit on `main`, even a README edit, ends the replication.** `check-hub` compares the main commit as well as the file ids, and `snapshot_download` has no `revision=`. A commit that leaves every pinned file unchanged therefore makes both models MISSING ("its model files differed"), with no rerun allowed: a needless route to R6. **Fix:** download with `revision=<pinned commit>` and require only that the file ids match. | No bias (no data seen yet); can make the replication MISSING |
| E | NON-BLOCKING | `:20` "(ledger: … ; a test with one altered byte … fails)"; `responses.md:43` ("scratch test") | The altered-byte test has no ledger entry (the last ledger lines are 198-199, the OK run only). Either log it or say it was not logged. | No |
| F | NON-BLOCKING | `:26` vs `:62-79` | §5(c) and §5(d) do not say where the P2R non-gating sensitivity sets appear. | Minor reporting choice |
| G | NON-BLOCKING | `APPLY_P2R.sh:17-22`; amendment `:53`, `:63` | The 186–195 counts and the L1–L5 anchors assume the abstract as it stands now (currently staged, not committed). `APPLY_P2R.sh` does not check either before tagging. **Fix:** assert 199 words and the five anchor strings in the APPLY script. | Only if the paper changes before the tag |
| H | NON-BLOCKING | `:71` vs `:72-75` | R1's Lg has "which includes answer-token identity"; the Lg sentences for R2, R3 and R5 do not. | Minor |
| I | NON-BLOCKING | `paper/main.tex:392`; amendment `:91-94` | The Limitations sentence "\STwo includes two model families…" is not among L1–L5, and nothing says whether it stays or changes after P2R. | Minor wording, after the data |
| J | NON-BLOCKING | runbook `:28`; amendment `:40` (4) | The runbook only checks out `prereg-P2R`. It has no steps for a second session at `prereg-P2R-fix1`. | Procedural |

Files: `/home/user/depth-law/reports/pending_frozen_changes/P2R/A_P2R_new_families.md`, `/home/user/depth-law/paper/main.tex`, `/home/user/depth-law/prereg/P2_prompt_vs_fact.md`, `/home/user/depth-law/analysis/p2r/p2r_weights_check.py`, `/home/user/depth-law/reports/p2r/GPU_RUNBOOK_P2R.md`, `/home/user/depth-law/reports/pending_frozen_changes/P2R/APPLY_P2R.sh`, `/home/user/depth-law/reports/pending_frozen_changes/P2R/APPLY_precommit_fix.sh`, `/home/user/depth-law/reports/gates/PREREG-R/responses.md`, `/home/user/depth-law/results/ledger.jsonl`

VERDICT: REVISE
