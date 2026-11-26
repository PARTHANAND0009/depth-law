PREREG-R round 3: stats-reviewer re-review of A_P2R_new_families revision 3. I edited nothing and ran no analysis or model.

The system prompt also asked for a comparison of results/*_gate.md against prereg/HR_revised.md. I did not do it, because your task replaced it (as in rounds 1 and 2).

**Bottom line:** 7 of the 9 round-2 findings are fixed and 2 are partly fixed (2 and 7). Two new problems in the wording rules are blocking, so the amendment needs another revision before GO PREREG-R.

**Checked directly:**
- The amendment's sha256 is `559eecbd…cf80`, as stated, and it did not change during the review.
- The current sha256 of every P2R script, `materials/p2r_weights_pinned.json` and `results/P2R/tokcheck.json` equals its last ledger entry.
- The frozen P2 code (prereg P2 §7 list) shows no diff against tag `prereg-P2`.
- The §5(b) facts match `p2_decision.json`: Llama has H1 True, n′ = 8 and `tf_gt_resid_D1` False; OLMo has H1 False.
- The session logs carry no outcome information (`run_p2.py:125,133`; `p2_done_check.py:18`). A rerun decision made from logs alone is therefore blind to results.
- Family mapping: "gemma" maps to gemma2 and "mistral" to mistral, and neither name matches "llama".
- The sync loop pushes `p2_syncdest/_p2r_preflight` (`p2_push_loop.sh:18`).

## Round-2 findings

| # | status | evidence |
|---|---|---|
| 1 weights check | FIXED | `A_P2R_new_families.md:20`; runbook `:43-49`, `:69`, `:73-75`, `:90`; `p2r_weights_check.py:20, 38-52`; 22 files pinned (14 Gemma, 8 Mistral). Small leftovers in N8 and N9. |
| 2 wording table | PARTLY | Locations L1–L5, exact text, placement, the five MISSING reasons, the abstract H1 rule and the mapping to the decision file are now present (`:45`, `:53-71`). New problems N1, N2 (both blocking), N3 and N4. |
| 3 rerun after seeing results | FIXED | `:40-41`; runbook `:91`. Small leftover in N6. |
| 4 deadline / non-reporting | FIXED | `:84-85` |
| 5 pilot FATAL / code fix | FIXED | `:40`. Small leftover in N10. |
| 6 `p2r_combine` gaps | FIXED | `p2r_combine.py:51-55` (full `per_model` checked against `decide()`), `:71-79` (`families_per_rule`); cross-references correct. |
| 7 APPLY script | PARTLY | Fixed in `APPLY_P2R.sh:14-15`, `:17-22`, `:37-38`. The same no-pathspec commit remains in `APPLY_precommit_fix.sh:17` (N11). |
| 8 attention check not logged | FIXED | `:23`; ledger NOTE 2026-11-26T06:06:51Z |
| 9 precision in §5(b) and §2 | FIXED | `:50`, `:26` |

## New findings

| # | class | where | finding | could change the outcome or its wording? |
|---|---|---|---|---|
| N1 | **BLOCKING** | `A_P2R_new_families.md:71`; `paper/main.tex:38-44` | **The abstract-length rule cannot be met in most failure cells.** The abstract is 199 words by whitespace count, matching the amendment's own figure. Cutting the last sentence frees 25 words (24 + the 1 spare), so the limit is 175 + the added cell sentence. Cell sentences filled with real model names and reasons give: R2 26 words, total 201; R3 26–29, total 201–204; R5 33–37, total 208–212; R6 with long reasons 27–29, total 202–204. The rule says "nothing else in the abstract changes", so in non-replication cells the authors must make unplanned abstract cuts after seeing the data. **Fix:** fix a shorter L1 sentence per cell that fits in 25 words with the longest reason, or fix a second cut in advance. | Yes: abstract wording in R2, R3, R5 and R6. |
| N2 | **BLOCKING** | `:62` (R1, L4/L5); `main.tex:377, 387` | **R1's rewrite extends EXPLORATORY claims to the new models.** The R1 replacement puts Gemma and Mistral at the start of sentences that go on to make EXPLORATORY claims for Llama/OLMo only. L4 continues "part of it is the identity of the answer (\expl)". For Gemma and Mistral that is the result of the P2R refit, which has not been run (`:80`), so the text could be false. L5 continues with refit numbers and frozen fact shares for Llama and OLMo only, which then read as if they covered all four models. Either way the Discussion or Conclusion would need unplanned rewording after the data. **Fix:** in R1, add the replication only to the confirmatory clause, keep the EXPLORATORY clause scoped to Llama and OLMo, and state that P2R refit results appear only in L3, labelled EXPLORATORY. | Yes: Discussion and Conclusion wording in R1. |
| N3 | NON-BLOCKING | `:69` | It is unclear whether "in cell R1 (PASS in both new families)" means the primary target's cell or that rule's own both-PASS result. Example: H1 passes in both models while the fact share fails in one. **Fix:** say which. | Yes, but only one sentence in L3; the per-model table shows the result regardless. |
| N4 | NON-BLOCKING | `:70`; `main.tex:42-43` | After the R1 change, L1 names four models, but the next sentences ("Estimated fact-level shares…", "…in one model") stay unscoped. "Stays scoped to the P2 models" gives no text. **Fix:** say "verbatim unchanged", or give the scoped text. | Minor. |
| N5 | NON-BLOCKING | `:45`, `:53`, `:20` | If the model files differ, the analysis receives `=none`, so the decision file says "MISSING (not run)". The mapping does not say the reason is then "its model files differed". A session whose check files failed to sync has no listed reason. | No: the cell is the same. |
| N6 | NON-BLOCKING | `:41`; `p2_analysis.py:378-380` | "Exactly once" has no rule for a gating call that crashes before writing `p2_decision.json` (for example, killed at the 1.8 GB cap). **Fix:** allow an identical rerun in that case and log both runs. | Procedural. |
| N7 | NON-BLOCKING | runbook `:14`, `:20`, `:71`; `p2_gpu_run.sh:19` | `RATE` is set without `export` before `tmux new`, so in window 0 step 10 computes an empty B. The driver then falls back to `BALANCE_INR=740`, a 199-min internal budget unrelated to the real rate. The step-3 OS timer could then stop a model without the driver writing its budget deviation. **Fix:** `export RATE`, or save it to a file. | No change to the confirmatory rules; it can make MISSING (incomplete) more likely. |
| N8 | NON-BLOCKING | runbook `:5` vs `p2r_weights_check.py:84-85`; amendment `:20` vs runbook `:90` | The manual stop rule waits for `WEIGHTS CHANGED`, but the script prints `FILES CHANGED` / `DIFFERENT:`. The `&&` gate still holds. Also, `hub_observed.json` is not among the files that §D requires. | No. |
| N9 | NON-BLOCKING | `p2r_weights_check.py:20, 48`; amendment `:20` | `check-cache` compares cache blob names (etags recorded at download), not hashes of the bytes, and `model.safetensors.index.json` is not pinned. "Only the verified files load" slightly overstates what is checked. | No (unlikely). |
| N10 | NON-BLOCKING | `:40`; `p2_gpu_run.sh:85`; runbook `:28` | The code-fix check is weak. The smoke run's exit status is never checked, and neither test compares against P2 outputs. A fixed file would differ from the code at `prereg-P2R`, and there is no procedure (such as a new tag or hash) for a second session. | Procedural. |
| N11 | NON-BLOCKING | `APPLY_precommit_fix.sh:17` | It runs `git commit` without a pathspec under `DEPTHLAW_FROZEN_OVERRIDE=1`. The index now stages S5 background-job files (`results/S5/...log.jsonl`, a chunk), `paper/main.tex`/`main.pdf`, the G5 review renames, `PROGRESS.md` and every P2R file; all of them would go into the "pre-commit fix" commit. **Fix:** commit with an explicit pathspec. | No. |
| N12 | NON-BLOCKING | `:83` vs `:85` | "The paper stays as committed at the tag" conflicts with the Limitations sentence allowed before the gating call. **Fix:** name `:85` as the only exception. | No. |

Files: `/home/user/depth-law/reports/pending_frozen_changes/P2R/A_P2R_new_families.md`, `/home/user/depth-law/reports/p2r/GPU_RUNBOOK_P2R.md`, `/home/user/depth-law/analysis/p2r/p2r_weights_check.py`, `/home/user/depth-law/analysis/p2r/p2r_combine.py`, `/home/user/depth-law/reports/pending_frozen_changes/P2R/APPLY_P2R.sh`, `/home/user/depth-law/reports/pending_frozen_changes/P2R/APPLY_precommit_fix.sh`, `/home/user/depth-law/scripts/p2_gpu_run.sh`, `/home/user/depth-law/analysis/p2/p2_analysis.py`, `/home/user/depth-law/paper/main.tex`

VERDICT: REVISE
