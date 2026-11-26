PREREG-R round 5: stats-reviewer re-review of A_P2R_new_families revision 5. I edited no file and ran no analysis or model.

The system prompt also asked for a comparison of results/*_gate.md against prereg/HR_revised.md. I did not do it, because your task replaced it (as in rounds 1–4).

**Bottom line:** all ten round-4 findings (A–J) are fixed, and so are the two earlier items still open in round 4 (round-3 N2, round-2 #2). I found 11 new problems, none blocking: none lets the outcome or its main wording be chosen after the P2R data are seen. The most useful fixes are N1 (one runbook step can needlessly make both models MISSING), N2 (a Limitations sentence becomes false) and N3 (where the new results paragraph goes).

**Checked directly:**
- The amendment's sha256 is `dd570736…cccee`, as stated.
- Every P2R script, the pin file and all four `results/P2R/*.json` files hash to the outputs of their last ledger entries (`results/ledger.jsonl:191-202`).
- The frozen code (`common.py`, `p2_gpu_run.sh`, `p2_analysis.py`, `run_p2.py`, `p2_done_check.py`, `tests/test_depth.py`) has no change against tag `prereg-P2`. The only additions in `analysis/p2/` are report and simulation scripts.
- The pin file has 15 Gemma files and 9 Mistral files. The hub check and the positive cache check report no differences. The negative test reports exactly one difference and exits 1.
- `APPLY_P2R.sh:30-38`: grep finds each of the 9 anchors exactly once in the current `paper/main.tex`. I could not run the script's own Python check (the permission classifier blocked it), so its 199-word assert was not run. My own count of the abstract is 199.
- The P2 decision file agrees with amendment §5(b): Llama has H1 true and n′ = 8; `tf_gt_resid` is false in Llama and OLMo; `icc1_upper_lt_0.15` is false in both; H1-alt holds in neither. A conflict-rule trigger is impossible in both (a) and (b).
- The session logs (`run_p2.py:125`, `p2_done_check.py`) contain no correctness or outcome data, so a rerun decided "from logs only" cannot be steered by results.

**Abstract word count (whitespace, `paper/main.tex:38-44`):** 199 words. The last sentence (decision study, 24 words) is replaced by S, leaving 175.

| cell | S words | total |
|---|---|---|
| R1 | 18 | 193 |
| R2 (either order) | 22 | 197 |
| R3 (either order) | 20 | 195 |
| R4 | 19 | 194 |
| R5 (either order) | 22 | 197 |
| R6 | 11 | 186 |

This matches the amendment's 186–197 (`:63`). Every total is 200 or less. The macros expand to single tokens, so the rendered count is the same.

## Round-4 findings and earlier open items
| # | status | evidence |
|---|---|---|
| A (insertion points) | FIXED | `A_P2R…md:63` (S is the abstract's last sentence), `:66` (Lg last in the Discussion paragraph; in the Conclusion after sentence 2, before "Code, materials…"). Checked against `main.tex:41-44`, `:376-379`, `:386-389`. L3's position is still loose: see N3. |
| B (FAIL worded as absence) | FIXED | `:53` (the rule, citing P2 §6), `:72`, `:74`, `:75`; S for R2/R4/R5 says "did not show" |
| C (H1 sentence for L3) | FIXED | `:78`. The H1-alt wording overstates: see N7 |
| D (a new `main` commit voids the run) | FIXED in `p2r_weights_check.py:45-57`, `:60-69` and runbook `:43-53`. The runbook's attention check brings the exposure back: see N1 |
| E (altered-byte test not logged) | FIXED | ledger `:201`; `cachecheck_negtest.json:56-58` |
| F (where the sensitivity sets go) | FIXED | `:82` |
| G (paper state not checked before the tag) | FIXED | `APPLY_P2R.sh:23-41`; anchors verified as above |
| H (qualifiers in every sentence) | FIXED for R1–R5. The rule at `:53` conflicts with R6 and the Limitations sentences: see N6 |
| I (Limitations sentence) | FIXED | `:80`. A second Limitations sentence is affected: see N2 |
| J (second session) | FIXED | runbook `:94-100` |
| Round-3 N2 (PARTLY in round 4) | FIXED | via A |
| Round-2 #2 (PARTLY in round 4) | FIXED | via A and B |

## New findings
| # | class | where | finding | could change the outcome or its wording? |
|---|---|---|---|---|
| N1 | NON-BLOCKING | runbook `:54-63` (`AutoConfig.from_pretrained("google/gemma-2-9b")` runs online, after `set-ref`/`check-cache` at `:52-53`) vs `:79`; amendment `:20`, `:40` | **The attention check can make both models MISSING for nothing.** It loads the config online with revision `main`. If Gemma's `main` has moved since the pin, huggingface_hub rewrites `refs/main` to the new commit. The pre-start `check-cache` at `:79` then fails ("commit … != pinned") and the driver never starts. Under §1 both models become MISSING ("its model files differed"), with no rerun allowed (`:40`). Yet the amendment says a later `main` commit "does not matter" (`:20`), so runbook and amendment disagree. **Fix:** run that block with `HF_HUB_OFFLINE=1`, or pass `revision=<pinned commit>`, or move it before `set-ref`. | No bias. Can push the outcome to R6 |
| N2 | NON-BLOCKING | `main.tex:393`; amendment `:80`, `:92` | "Both studies … use models of at most eight billion parameters" becomes false once Gemma-2-9B is reported. The amendment does not cover this sentence, and §7 freezes the paper, so it would have to be reworded after the data. **Fix:** give the replacement text now (e.g. "…at most nine billion parameters (eight in \SOne and the original \STwo models)"). | Minor wording after the data |
| N3 | NON-BLOCKING | amendment `:65`; `main.tex:336-353`, `:371` | **The L3 position is loose.** "After the P2 paragraphs" does not fix where the new paragraph goes. Placed before "Agreement across models" or "Decision study", the unscoped "both models" (`:337`) would follow text naming Gemma and Mistral; this is the round-4 A problem again. §6's "in our two models" (`:371`) also follows. **Fix:** name the anchor (immediately before `\subsection{Robustness simulation`), add it to the APPLY anchor check, and give §6's "our two models" a fixed scope. | Wording placement |
| N4 | NON-BLOCKING | amendment `:53`, `:62`, `:92` | **Nothing explicitly bars other P2R text.** After the gating call, §7 constrains only L1–L5 and the Limitations sentence. The amendment never says P2R results appear nowhere else, or that L3 holds only the listed items (no free commentary). "Exhaustive" and "enters only as added text" imply it but do not say it. **Fix:** one sentence: "No other text about P2R outcomes is added anywhere in the paper; L3 contains only the listed items." | Interpretive wording after the data (minor; the main sentences are fixed) |
| N5 | NON-BLOCKING | amendment `:50`; `numbers.tex:670-671`; `main.tex:360` | **The stated error rate is optimistic.** "About 0.05" assumes the nominal 0.025 per model. The project's own simulation found the single-measure H1 interval condition passing in 0.050–0.120 of datasets with a true difference of zero, and the full H1 condition was not simulated. A false one-family H1 licence in the summary could therefore be clearly above 0.05. **Fix:** state it as "at least about 0.05; possibly up to about 0.2 given the simulated liberality". | No: (b) is a results-only tally |
| N6 | NON-BLOCKING | amendment `:53` vs `:76`, `:80` | The rule says every added sentence carries "on correctly answered prompts" and every Lg carries "which includes answer-token identity". R6's S and Lg and both Limitations sentences carry neither. **Fix:** limit the rule to sentences that state a result. | Trivial, but the rule and the table disagree |
| N7 | NON-BLOCKING | amendment `:78`; P2 prereg `:248`, `:271-272` | The H1-alt L3 sentence "the fact share was at least 0.5 by the preregistered test" overstates. The condition is a point estimate ≥ 0.5 with a lower bound ≥ 0.4 (plus the MoM sign), not a test that the share is ≥ 0.5. **Fix:** "met the preregistered H1-alt condition (point estimate ≥ 0.5, lower bound ≥ 0.4) in both models". | L3 wording, only if H1-alt passes in both (unlikely) |
| N8 | NON-BLOCKING | `p2_analysis.py:332`; runbook `:104-106` | The gating call reads the local tokenizer cache (`local_files_only`), whose `refs/main` could move before the analysis. That would change the `n_answer_tokens`/`n_subject_tokens` covariates. **Fix:** run `check-cache --only-present` through the ledger right before the gating call, and require OK. | No bias. Provenance |
| N9 | NON-BLOCKING | `p2_gpu_run.sh:84` (frozen pytest on pythia-70m only); `tests/conftest.py:12`; amendment `:35` | **No check that patching works on the new architectures, and no rule if it does not.** The hooks (`common.py:156-173`) are never tested on Gemma-2 or Mistral; the pilot checks only that a chunk is written. A silent fault would produce data, and no prespecified rule says when data are invalid. **Fix:** in the runbook, before the driver, run the frozen `test_patching_identity` and `test_final_patch_last_layer_equals_source` with `DEPTHLAW_TEST_MODEL=<model>` (frozen code, env var only, output in the logs). Stop on failure as a pilot FATAL. | A post-data invalidation choice would be unregulated; unlikely |
| N10 | NON-BLOCKING | `APPLY_P2R.sh:17-19`, `:44-47`; amendment `:20` | `hubcheck_test.json`, `cachecheck_test.json` and `cachecheck_negtest.json`, which §1 cites, are not required to be committed and are not hashed at the tag. | No |
| N11 | NON-BLOCKING | amendment `:20` vs runbook `:104` | With two sessions, it is unclear whether a failed provenance check in session 2 also voids the verified session-1 model: §1 says "both models", the runbook says "for each session". It is decided before any analysis, so it is blind to outcomes. **Fix:** "the models run in that session". | No bias |

Files:
- /home/user/depth-law/reports/pending_frozen_changes/P2R/A_P2R_new_families.md
- /home/user/depth-law/reports/p2r/GPU_RUNBOOK_P2R.md
- /home/user/depth-law/reports/pending_frozen_changes/P2R/APPLY_P2R.sh
- /home/user/depth-law/analysis/p2r/p2r_weights_check.py
- /home/user/depth-law/analysis/p2r/p2r_combine.py
- /home/user/depth-law/analysis/p2/p2_analysis.py
- /home/user/depth-law/scripts/p2_gpu_run.sh
- /home/user/depth-law/src/depthlaw/depth/common.py
- /home/user/depth-law/tests/conftest.py
- /home/user/depth-law/paper/main.tex
- /home/user/depth-law/paper/numbers.tex
- /home/user/depth-law/prereg/P2_prompt_vs_fact.md
- /home/user/depth-law/results/P2analysis/correct/p2_decision.json
- /home/user/depth-law/results/ledger.jsonl

VERDICT: PASS
