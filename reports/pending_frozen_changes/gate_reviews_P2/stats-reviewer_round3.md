<!-- stats-reviewer subagent (.claude/agents/stats-reviewer.md), fresh context, 2026-11-23, PREREG gate round 3 (last review before freezing; severity rule set by the human: BLOCKING only if it could change a decision), on reports/pending_frozen_changes/P2_prompt_vs_fact.md and the frozen code at 5ac9e2e. Saved verbatim by the main session; not edited. Staged here for APPLY.sh (the deny rule Edit(prereg/**) also blocks reports/gates/PREREG/). Answers: responses.md. -->
Scope note: my launch instructions opened with a default task (compare results/*_gate.md with prereg/HR_revised.md). The brief said to ignore it, so I did. This review covers only the staged P2 prereg (/home/user/depth-law/reports/pending_frozen_changes/P2_prompt_vs_fact.md, cited as "prereg L<n>") and the code to be frozen with it, at HEAD 5ac9e2e.

The tested code matches HEAD: the input hashes the ledger recorded for the e2e v3 run and the three dry runs equal the current files. The materials sha256 values match prereg section 1, all 300 subjects are distinct, each template_id maps to one frame in every relation, and the first-token ids in the materials match `obj_ids` for all four tokenizers. I edited no repo files. I ran two small illustration scripts in the scratchpad (nice, prlimit), listed under B1.

## BLOCKING

**B1. The shuffled-fact null does not test "fact share > 0" when there is fact:carrier variance.**
- **Where:** /home/user/depth-law/analysis/p2/p2_null.R L27–36 (the permutation) and L47 (p). Prereg L192–198 (the null) and L248–249 (the sentence). The claim is computed in /home/user/depth-law/analysis/p2/p2_analysis.py L380–381.
- **Mechanism:**
  - Fact labels are permuted separately within each relation × paraphrase cell, and all carrier rows of a (fact, paraphrase) move with the label. So a new label's rows come from different original facts in different paraphrases.
  - This removes fact:carrier (fc) as well as fact. fc becomes cell × carrier noise. The reference distribution is therefore the one for fact = 0 **and** fc = 0.
  - The prereg's null hypothesis for the sentence is fact = 0. The model fits fc as a substantive component (section 4). With fc > 0 and fact = 0, the observed REML ICC(1) is more variable and higher on average than the permuted values, so p < 0.01 occurs far more often than 1%.
- **Evidence from the frozen model functions** (`p2_formula`, `p2_prep`, `p2_shares`; fact = 0, ft = e = 1, 300 facts × 5 random paraphrases × 3 carriers, carrier fixed effect; 40 independent null datasets against 40 permutations of one dataset):

  | fc | P(observed ICC(1) > permutation 95th percentile) |
  |---|---|
  | 0 | 0.03 (calibrated) |
  | 0.25 | 0.25 |
  | 1 | 0.35 |

  - With fc = 1, the observed ICC(1) has SD 0.0197; the permutation ICC(1) has SD 0.0034.
  - A moment-estimator version, 100 replicates × 100 permutations, rejected at p < 0.05 in: 7/100 (fc = 0), 18/100 (fc = 1, nc = 3) and 29/100 (fc = 1, nc = 2).
  - Scripts: /tmp/claude-0/-home-user-depth-law/79d106ca-74b7-5e19-8ef3-6880f992c1ff/scratchpad/r3/remlnull.R and /tmp/claude-0/-home-user-depth-law/79d106ca-74b7-5e19-8ef3-6880f992c1ff/scratchpad/r3/nullsim.py.
  - These are illustrations with small numbers of replicates, not a calibration study.
- **Decision it could change:** the section 6 headline "The fact share is above zero". It can be printed in ≥ 2 families when the fact share is 0 and only fact × carrier is non-zero.
- **Relation to the human's decision:** the permutation unit came from round-1 item 5 and was adopted on 2026-11-22. This finding does not question having a null or the p < 0.01 threshold. It shows that this unit tests a different null from the one the sentence states. The fix is the human's choice.
- **Minimal fix, either:**
  - **(a) Text only, no code change.** State in §4 that the reference distribution sets both fact and fact:carrier to zero. Reword the §6 sentence to what the test supports, e.g. "Facts have a depth component that is consistent across paraphrases (fact or fact × carrier)". Make the same change to the p2_null.R header comment.
  - **(b) Code change.** Replace the permutation reference with a parametric null in p2_null.R:
    - refit the primary model without `(1|fact)`;
    - `simulate()` 1000 datasets from that fit, seed 20261121;
    - refit the primary model on each and compute ICC(1);
    - keep the same p formula, then re-run the e2e test.

## NON-BLOCKING

1. **No failure threshold for permutations** (p2_null.R L38–47; prereg L196). If all permutations fail, p = 1, which is conservative. Round-2 N4 was not adopted, and the human did not decide on it. → Limitations.
2. **MoM truncates negative raw components at 0 before forming diff** (/home/user/depth-law/analysis/p2/p2_mom.py L59–63). The prereg does not say this. In rare cases (a negative raw frame or rt component) truncation can flip the sign of MoM diff relative to the raw components. → Limitations (one sentence in §4).
3. **Undefined n′ comes from carrier noise, not paraphrases** (prereg L121, L241–243). G(k) tends to fact/(fact + fc/nc) as k grows. An undefined n′ (coded 31) therefore means that carrier noise, which paraphrases cannot average out, keeps G(k) below 0.8. "It takes N paraphrases" would then misdescribe the result. → Limitations / wording of the sentence.
4. **The gating call accepts other values of `--n-boot` and `--n-perm`** (p2_analysis.py L215, L218, L299). `--n-perm 0` silently makes the null MISSING, so the sentence becomes false. The text fixes both at 1000. → Post-freeze fix list (refuse other values for `--set correct`), or record any change as a deviation.
5. **The analysis does not check run identity or the run list.** It does not compare the run's `meta.json` model with the `--runs` key, nor check dtype float32 or the revision (p2_analysis.py L248–258; `completeness` L85–122). It does not check that every model of the session is passed (prereg L83). The duplicate check is on the exact key string (L225–228), so the same run under two keys is not refused. Family counts cannot be inflated within a family. → Post-freeze fix list.
6. **`completeness()` trusts the `ok` flags in `manifest.json`** written at the end of the run (L91–93). It does not recompute the sha256 after the copy off the instance. → Post-freeze fix list.
7. **Driver failure handling** (/home/user/depth-law/scripts/p2_gpu_run.sh):
   - The FATAL exits (L57, L83, L105, L127) leave the auto-stop subshell (L62–64) running, so the instance is billed until the budget runs out.
   - A pilot crash writes no deviation file.
   - `STOP_P2` is created in the repo root (L64) and never removed. A later session on the same disk would skip every model at L142 without writing a deviation file.
   - → Post-freeze fix list (efficiency and provenance; cheap to fix before tagging).
8. **Spurious Llama deviation.** The post-pilot fallback-2 branch (driver L135) writes "Llama-3.1-8B not run" even when Llama is not in ORDER; dry run D-P2-20261123T102010Z-2 shows this. → Post-freeze fix list (cosmetic).
9. **Prereg L37 is inaccurate.** It says "the models dropped are the late ones in the order above", but the per-model rule (driver L141–151) can skip Llama or pythia-2.8b while a later, smaller model still runs. → Wording; correct the text before the freeze if possible, otherwise Limitations.
10. **Deviation file names disagree.** Prereg L8 and L287 give `D-P2-<n>.md`. L41 and the driver use `D-P2-<UTC>-<n>.md`, plus `D-P2-<UTC>-budget.md`. → Wording.
11. **The patch identity test runs only on pythia-70m** (driver L83). Nothing checks on the Qwen3, Llama or OLMo-2 architectures that the hook takes effect. The stored data allow a post-hoc check: p_object at layer L−1 should equal exp(`obj_first_logprob`) for each cell. → Post-freeze fix list (a separate check script, not frozen code).
12. **The hard-stop path was not exercised in the dry runs**, as the ledger NOTE acknowledges. → Limitations (test coverage).
13. **`n_subject_tokens` is tokenised with a leading space** (p2_analysis.py L272), but in subject-first frames the subject starts the prompt without one. This is covariate measurement noise. → Limitations.
14. **The MoM test's first run failed.** The 20-replicate run failed on frame (−0.23); the 200-replicate run passed. Prereg L133 reports only the passing run. The ledger has both. → Limitations (optional provenance sentence).
15. **Stale text in responses.md** (/home/user/depth-law/reports/pending_frozen_changes/gate_reviews_P2/responses.md):
    - the title still says "(2026-11-22)";
    - "Next steps" (L179–184) still describes round 2;
    - row 15 (L114) describes `--nc`, which was later removed (L166).
    - → Wording.
16. **Bootstrap cost.** bootMer refits inherit `calc.derivs = TRUE`: 1000 refits × 4 outcomes × up to 5 models × 6 CI sets, plus 1000-permutation nulls, on a 4-core machine shared with S5. → Post-freeze fix list (estimate the CPU time before the analysis; efficiency only).

VERDICT: BLOCK
