# P2 post-freeze fix list (from stats-reviewer round 3, NON-BLOCKING group (ii))

Human decision 2026-11-23: findings that change a number used in a decision column or headline rule (group (i)) were fixed before the freeze. The items below do not, and are fixed after the freeze as code outside the frozen decision path, or recorded as a deviation if frozen code must change.

| round-3 # | item | planned fix |
|---|---|---|
| 7 (part) | FATAL exits in `scripts/p2_gpu_run.sh` leave the auto-stop timer running, so the instance is billed until the budget runs out | Kill the timer subshell on every FATAL exit (trap EXIT). **Before the GPU session, if the human allows a driver change, otherwise as an operational note: stop the instance by hand after any FATAL.** |
| 7 (part) | A pilot crash writes no deviation file | Write a deviation in the pilot FATAL branch. |
| 8 | The fallback-2 branch writes "Llama-3.1-8B not run" even when Llama is not in ORDER (cosmetic; dry-run D-P2-20261123T102010Z-2) | Write it only if Llama is in ORDER. |
| 11 | Patch identity is tested only on pythia-70m | A separate check script, not frozen code: for every cell, p_object at layer L−1 vs exp(obj_first_logprob). Report it next to the results. |
| 16 | Bootstrap cost: 1000 refits × 4 outcomes × up to 5 models × 6 CI sets, plus 1000-dataset nulls | Estimate the CPU time from one model before the analysis; schedule around S5. |
| 1 | No failure threshold for the fact-share null | Report the number of failed refits; any rule would need a deviation. (Also in prereg section 10.) |
| 12, 14 | Hard stop not exercised; MoM test's first run failed | Recorded in prereg section 10. |
| final review 4 | The calibration uses one seed for both the data and `simulate()` | Use a separate seed offset in `p2_null_calib.R` if the calibration is re-run (test code; does not affect the analysis). |
| final review 5 | The calibration fits no covariates | Optional extra calibration with the four covariates (non-selecting). |
| final review 8 | The null recomputes the observed ICC(1) instead of reading the primary fit | Add a cross-check against the primary fit's JSON in the report (equality was verified in the review). |
| final review 6 (part) | The CLI argument is still named `--n-perm` | Rename to `--n-null` after the freeze (cosmetic; changing it now would touch the frozen interface). |

Group (i), fixed before the freeze (2026-11-23):
- 2: MoM diff on raw components.
- 3: an undefined n′ does not meet the "N paraphrases" rule.
- 4: the gating call needs 1000/1000.
- 5: run identity; the five prereg models (MODEL=none); duplicate run dirs refused.
- 6: checksums recomputed.
- 7: a session-specific stop flag.
- 13: subject tokens counted in context.

Wording fixes 9, 10, 15 are applied.
