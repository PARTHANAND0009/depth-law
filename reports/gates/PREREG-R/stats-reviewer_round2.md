PREREG-R round 2: stats-reviewer re-review of A_P2R_new_families revision 2. Read-only; I edited nothing and ran no analysis.

**Bottom line:** 12 of the 16 round-1 findings are fixed, 3 are partly fixed (3, 4, 15) and 1 is fixed only in its text (12). The new summary code applies the frozen `decide()` rules correctly. Four blocking problems remain:
- The weights check can be skipped by the runbook flow, and it does not cover the files that actually get loaded.
- The wording table covers every cell but is ambiguous about which paper sentences it rewrites, and where.
- The rerun decision can be made after seeing the other model's analysed result.
- The submission deadline lets P2R go unreported.

**What I checked directly:**
- The current sha256 of `analysis/p2r/*.py`, `materials/p2r_weights_pinned.json` and `results/P2R/tokcheck.json` equal the inputs and outputs recorded in the ledger (`results/ledger.jsonl` lines 191–193).
- `results/P2analysis/correct/p2_results.json` and `p2_decision.json` have the sha256 pinned in `p2r_combine.py:27-28`.
- The cached tokenizer snapshots are the pinned commits (33c1930…, 27d67f1…). No weight files are cached for Gemma-2-9B, Mistral-7B-v0.1 or Mistral-7B-v0.3.
- Installed transformers has `_supports_sdpa = False  # sdpa does not support softcapping` at `/home/user/depth-law/.venv/lib/python3.13/site-packages/transformers/models/gemma2/modeling_gemma2.py:352`.

## Round-1 findings

| # | status | where | note |
|---|---|---|---|
| 1 | FIXED | `p2r_combine.py:44-58`, `p2r_test.py:59-80` | Refuses non-gating and `--test` inputs; P2 files pinned by sha256; nc = 0 handled; per-model values come from each call's own decision file; rule flags cross-checked; tests cover both MISSING, one MISSING, nc 3 vs 2, test input refused. |
| 2 | FIXED | `A_P2R_new_families.md:47-48, 71` | Says the summary is partly decided in advance, gives its higher error rate, keeps it out of the abstract and headlines, and corrects the multiplicity text. |
| 3 | PARTLY | `A_P2R_new_families.md:50-67` | The 3×3 table covers every cell, but the target sentences, where they go and the reasons for MISSING are ambiguous (new finding 2). |
| 4 | PARTLY | `A_P2R_new_families.md:20`; `GPU_RUNBOOK_P2R.md:42-43, 73-74` | Weights are pinned and the observed values are written to a file, but the check does not stop the driver and does not cover the bytes loaded (new finding 1). |
| 5 | FIXED | `A_P2R_new_families.md:10-11, 30`; `results/P2R/tokcheck.json` | Lists every tokenizer loaded and the cap breach; counts quoted for 3000 pairs × 2 tokenizers; ledger output hash matches; the HF cache matches the disclosure. |
| 6 | FIXED | `A_P2R_new_families.md:44` | States the conflict rule cannot trigger. Snapshot hashes are not recorded, but I confirmed the cached snapshots are the pinned commits. |
| 7 | FIXED | `A_P2R_new_families.md:76`; `g5_expl_object.R:10, 21` | Only the generic refit is preplanned; it takes CSV arguments and gets nc from the data. |
| 8 | FIXED | `APPLY_P2R.sh:16-26` | Checks that every file is committed and clean, and hashes the runbook, the pinned weights and the tokenizer check. |
| 9 | FIXED | `GPU_RUNBOOK_P2R.md:9, 73, 77-78`; `A_P2R_new_families.md:29, 38` | Same GPU type as P2, `SKIP_ENV=1`, a projection scaled from P2's measured times, and the "Llama-3.1-8B not run" deviation files declared no-ops. |
| 10 | FIXED | `GPU_RUNBOOK_P2R.md:19`; `A_P2R_new_families.md:38` | Checks billing at the first stop, and the manual stop rule always applies; acceptable given about 2× headroom in the budget. |
| 11 | FIXED | ledger line 191 | Peak RSS 522,184 kB under the 1.8 GB cap; no cap raise requested. |
| 12 | FIXED (text) | `A_P2R_new_families.md:40` | The rule as written now exists, but it leaves a post-data choice (new finding 3). |
| 13 | FIXED | `A_P2R_new_families.md:9, 10, 19` | Discloses that P2 data motivated the selection criterion, the candidates not checked, the scope, and the empty Gemma-3 S4 run. |
| 14 | FIXED | `A_P2R_new_families.md:23`; `GPU_RUNBOOK_P2R.md:50-62` | Correct (confirmed at `modeling_gemma2.py:352`), but the check has no ledger entry (new finding 8). |
| 15 | PARTLY | `A_P2R_new_families.md:79` | `paper/main.tex` is still staged, not committed (git status "M "), and `APPLY_P2R.sh:16-21` does not check it. |
| 16 | FIXED | `A_P2R_new_families.md:69` | Pairs across the two calls are declared not reported. |

## New findings

**1. BLOCKING: the weights check can be bypassed by the runbook, and it does not check what is loaded.**
- **Not a gate.** `GPU_RUNBOOK_P2R.md:42-43` is `check ... && echo WEIGHTS_OK || echo "WEIGHTS CHANGED..."`, so a failure only prints a line. Step 10 (`:73-74`) starts the driver regardless. Neither the driver nor the analysis reads `weights_observed.json`: run identity checks only `revision main` (`p2_analysis.py:135`). The statement at `A_P2R_new_families.md:20` ("the runbook does not start the driver after a non-zero exit") is therefore true only if the human reads the line.
- **Checks metadata, not the files used.** The check compares Hub metadata before the download (`:44-49`). The downloaded bytes are never compared. At each model load, `from_pretrained` re-resolves `main` online (`common.py:105-106`; step 10 does not set `HF_HUB_OFFLINE`), so a later move of `main` would be loaded silently.
- **Only weight files are checked.** `p2r_weights_check.py:37` compares `*.safetensors` only. `config.json` (softcapping, `query_pre_attn_scalar`, rope) and the tokenizer files change the measurement and the target token ids. The CPU analysis uses the cached tokenizer at the pinned commit. "Same weights, so proceed" was my round-1 suggestion, and it was too loose.
- **Fix:**
  - After the download, compare the HF-cache blob names (the LFS sha256) under `snapshots/<commit>/` with the pinned values.
  - Pin and check the blob ids of `config.json`, `generation_config.json`, `tokenizer*` and `special_tokens_map.json`.
  - In step 10, `export HF_HUB_OFFLINE=1` and run `check && SKIP_ENV=1 ... bash scripts/p2_gpu_run.sh`. The driver's Llama access check will then fail into a no-op deviation, which is already declared.
  - Add to the amendment: a run whose session has no matching `weights_observed.json` is MISSING (not run). The runbook's section D verifies this before the gating call.
- **Effect on the outcome:** only if `main` moves, which is unlikely, but the provenance claim is not met as written.

**2. BLOCKING: the 3×3 wording table (§5(c)) covers every cell but is ambiguous.**
- **Which sentence.** "The paper's P2 sentence" is singular, but it appears in different forms at `paper/main.tex:41, 74, 309, 377, 387`. The table does not say which of these it rewrites.
- **R1 text overclaims.** The R1 sentence (`:58`) drops "on correctly answered prompts" and "which includes answer-token identity", which the current text carries (`main.tex:41, 74, 312`).
- **Placement.** Placement is given only for R4 and R5 ("in the abstract"). For R1, R2, R3 and R6 it is not stated.
- **MISSING reasons.** The reasons allowed in R3 and R5 are only "too few correct answers | incomplete run". They omit "not run" (pilot FATAL, budget skip, weights changed) and "rule input MISSING" (failed fit or failed null).
- **Abstract H1 tally.** The abstract's H1 tally ("in one model", `main.tex:43`; also `:378`) has no rule. It could be rewritten to "two of four" or left as it is, at the authors' choice after seeing the data.
- **Mapping to the decision file.** PASS, FAIL and MISSING are not tied to decision fields.
- **Fix:**
  - Name every paper location and give the exact text per cell, keeping the qualifiers.
  - Give the placement for each cell.
  - Use the full list of MISSING reasons.
  - Rule now on the abstract H1 tally (for example: it stays scoped to P2, and P2R per-model H1 results appear in the results section only).
  - Tie the outcomes to the P2R decision file: PASS = rule predicate True, FAIL = False, MISSING = None or status ≠ ok (`p2_analysis.py:443-452`). An H1-dependent rule whose H1 is None is MISSING.
- **Effect on the outcome:** it changes abstract wording under several outcomes.

**3. BLOCKING: the rerun decision can depend on the other model's analysed outcome (`A_P2R_new_families.md:40`).**
- The rule only requires the decision to come before anyone opens the incomplete model's chunks. Nothing stops the complete model from being analysed first. Nor does the rule say which gating call counts if a rerun follows.
- **Fix:** run the P2R gating call exactly once, after the rerun decision is committed and, if there is a rerun, after the second session. Alternatively, make the rerun automatic within a stated budget.
- **Effect on the outcome:** yes; it chooses between R3 and R5 on one side and R1, R2 and R4 on the other.

**4. BLOCKING: the deadline in §7 (`A_P2R_new_families.md:80`) allows selective non-reporting.**
- After P2R data exist, the authors control whether the analysis finishes by 2026-12-20. Nothing says P2R is ever reported if it misses that date.
- **Fix:** once the P2R session has started, its §5(c) outcome is reported in every later version of the paper, whatever the date.

**5. NON-BLOCKING: a pilot FATAL on Gemma ends the session (`p2_gpu_run.sh:16, 105`), so Mistral is never run.**
- The rerun rule covers only "incomplete because of the budget or a crash", not "not run".
- The plumbing for these two architectures has never succeeded (dry runs exited 1, ledger line 187; `A_P2R_new_families.md:35`).
- A fix to frozen code needed for a new architecture has no stated procedure.
- **Fix:** extend the rerun rule to a model not run because the session stopped before it. Require a deviation committed before any code fix and rerun.
- **Effect on the outcome:** it decides between R6 or R3 and a testable model.

**6. NON-BLOCKING: `p2r_combine.py` gaps.**
- `p2r_combine.py:53-58`: only rule flags of status-ok models are cross-checked. Per-model status, `runs` and the G ceiling are copied from the P2R decision file without checking them against the P2R results. **Fix:** compare the full `per_model` against `decide()` run on the P2R results alone with their own nc.
- Stale cross-references: `:14` says "5(e)" (now 5(d)); `:37` says "5(b)" (the pin is in §3).
- The output has family lists only for H1 and H1-alt (`p2_analysis.py:441`), so the "k of 4" tallies for the other rules must be counted by hand. **Fix:** add a per-rule family list.

**7. NON-BLOCKING: `APPLY_P2R.sh`.**
- `:14` runs `p2r_test.py` outside `log_run.py` and without nice/prlimit.
- `:35` runs `git commit` without a pathspec, so it would sweep everything staged into the freeze commit. Staged now: S5 background-job files, `PROGRESS.md`, `paper/main.tex`, and the G5 review renames.
- **Fix:**
  - Run the test through `log_run.py` at the cap.
  - Commit with an explicit pathspec.
  - Add `paper/main.tex` to the committed-and-clean check.

**8. NON-BLOCKING: the Gemma-2 attention check (`A_P2R_new_families.md:23`) has no ledger entry.**
- It is correct (confirmed at `modeling_gemma2.py:352`).
- **Fix:** log the check, or cite that line.

**9. NON-BLOCKING: precision in §5(b) and §2.**
- `:47`: Llama's `tf_gt_resid_D1` is False (`p2_decision.json`). So "wording shifts together" still needs both new families. Only "H1 holds" and "single prompt poor" (if the new family's n′ ≥ 8) can be licensed by one.
- §2 inherits the `new226` sensitivity, which is meaningless for models G1 never analysed. **Fix:** say it is run as frozen and is just a 226-fact subset.

## Checked and correct

- `combine()` with the frozen `decide()`:
  - family claims come from the union, counting status-ok models only;
  - the per-model rule flags do not depend on nc;
  - the nc passed in affects only the G ceiling, which is then replaced by each call's own value;
  - cross-call H3 pairs are empty as declared;
  - the output is non-gating.
- The conflict rule cannot trigger with two families.
- The table's nine cells are all assigned, symmetrically.

As in round 1, I did not do the HR_gate vs HR_revised comparison in my standing instructions, because your request replaced it.

Files: `/home/user/depth-law/reports/pending_frozen_changes/P2R/A_P2R_new_families.md`, `/home/user/depth-law/analysis/p2r/p2r_combine.py`, `/home/user/depth-law/analysis/p2r/p2r_weights_check.py`, `/home/user/depth-law/reports/p2r/GPU_RUNBOOK_P2R.md`, `/home/user/depth-law/reports/pending_frozen_changes/P2R/APPLY_P2R.sh`, `/home/user/depth-law/scripts/p2_gpu_run.sh`, `/home/user/depth-law/src/depthlaw/depth/common.py`, `/home/user/depth-law/paper/main.tex`

VERDICT: REVISE
