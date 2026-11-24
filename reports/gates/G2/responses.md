# G2 responses to reviewers (P2)

Reviews (verbatim, not edited): `replicator.md` (PASS), `stats-reviewer.md` (REVISE, 0 blocking), `skeptic.md` (REVISE), `claim-auditor.md` (REVISE).
No gating number or flag changed after any review. Every change below is to reporting (`analysis/p2/p2_results_md.py` → `reports/p2/RESULTS.md`, regenerated through `scripts/log_run.py`; ledger lines 121–127) or to non-frozen tooling. No frozen file, no analysis call and no threshold was changed. Reviewer [scratch] numbers are not copied into RESULTS.md.

## Replicator (PASS)
| item | response |
|---|---|
| All §2–§5 numbers reproduced from raw run dirs (max diff ≤ 7.3e-5 vs JSON) | No action. |
| Ambiguity 1: z-scoring convention | No action: shares are invariant to the affine map (reviewer's own check). |
| Ambiguity 2: `correct` includes facts with 1 correct paraphrase | Stated in RESULTS §5 caveats and §8 (Limitations). Reviewer's restricted H3 value (ρ 0.456, N 169) is not reported: not preregistered; would be EXPLORATORY. |
| Ambiguities 3–5 | No action (reproduce stored values exactly). |

## Stats-reviewer (REVISE; blocking: none)
| # | severity | response |
|---|---|---|
| 1 | should-fix | Robustness simulation listed as MISSING (not run) in RESULTS §7 and §8. Not run now: it needs new code committed first and cannot change any decision. |
| 2 | should-fix | lofo table now has ICC(1) D4 and MoM diff D4 (read from `lofo/p2_results.json`). |
| 3 | should-fix | Sensitivity table now has singular flags and warning counts; lofo singular/warning totals added. Warning-count bug (single R warning serialised as a string) fixed. |
| 4 | note | H4 cross-family part listed as MISSING (RESULTS §6, §7). |
| 5 | note | Confirmation; no action. |
| 6 | should-fix | OLMo worded "H1 not established" with the CI bound; GATE_G2 states the Monte Carlo fragility and that it is not evidence of fact dominance or of a model difference. No rerun with another seed (forking path). |
| 7 | note | Scope to the two included models stated in RESULTS line 5 and §8, and in GATE_G2. |
| 8 | note | Sensitivity flags labelled non-gating, not evidence. |
| 9 | note | No action. |
| 10 | should-fix | H3 caveats (a)–(e) in RESULTS §5; "no CI preregistered" stated. Reviewer scratch values not reported. |
| 11 | should-fix | Sensitivity columns relabelled "H1 flag (non-gating; not evidence)"; text states confirmatory H1 is met in 1 of 2 families. |
| 12a | note | Ledger NOTE appended (ledger line 120): sensitivity runs are preregistered, non-gating, despite the CONFIRMATORY status label. |
| 12b | note | `scripts/p2_run_analysis.sh` now captures `rc` before `date`; ledger NOTE (line 120) says the real exit codes are in the ledger (all 0). |
| 12c | note | Not fixable retroactively (ledger is append-only). Integrity of `.R` files and `p2_mom.py` rests on the clean `git diff prereg-P2` the reviewer ran. Future analysis calls should pass every frozen analysis file as `--in`. |
| 12d | note | Not renamed: H4 is exploratory by preregistration; its ledger tag and status are EXPLORATORY and RESULTS labels it. Renaming would break the path recorded in the ledger. |
| 13 | note | Band shown with its CI and labelled descriptive; n′ labelled estimation only. |

## Skeptic (REVISE; "reject as it stands")
| # | severity | response |
|---|---|---|
| 1 | major | Accepted. RESULTS line 5 and §8 scope the measure to answer-readout depth at the final (prediction) position; subject position not patched. GATE_G2 uses this scope. "Where a fact lives" is not used. |
| 2 | major | Accepted in reporting. The split (rt + frame vs ft) is now shown as EXPLORATORY rows read from the fit files (not the reviewer's scratch numbers). The preregistered "wording shifts together" quantity is negative in both models and labelled "rule not met". Neutral-prefix comparison is reviewer scratch; not reported. |
| 3 | major | Accepted as a caveat. The frozen formula has no relation × object term; RESULTS §4 and §8 now say the fact component includes answer-token identity and that the licensed sentence does not mean facts have their own depth. The permutation numbers are reviewer scratch; not reported. Adding the term would need a new prereg or amendment. |
| 4 | major | Caveat added to §8: D1 and D4 share one curve; no cross-model comparison of fact-stability is made. |
| 5 | minor | Scale in layers added as an EXPLORATORY row (from fit vc × L). |
| 6 | major (external validity) | Scope stated (2 models). Same-tokenisation observation is reviewer scratch; cited in GATE_G2 as the reviewer's point only. |
| 7 | minor | GATE_G2: no between-model test was preregistered; "H1 in Llama, not OLMo" is not a model difference. Robustness simulation MISSING. |
| 8 | minor | H3 is estimation only, with caveats; reviewer's decomposition not reported. |
| 9 | minor | No action beyond reporting `tcov` (already in §6). |
| 10 | minor | Correct-only scope and MNAR stated in §8. |
| Next experiment | — | Subject-position patching + (1\|relation:object) on Llama and OLMo. Listed in GATE_G2 as an option; needs a new preregistration and a human decision. Not started. |

## Claim-auditor (REVISE)
| line(s) in audited version | response |
|---|---|
| 52, 58 (H1 bold, "H1 holds") | Bold removed; row reads "H1 condition met …; per model, not a claim"; words row says met in 1 of 2 families, no H1-dependent sentence licensed. |
| 54 (n′) | Labelled "estimation only; licenses no sentence by itself"; §3 header says n′ assumes equal k. |
| 56 (tf − resid) | "(negative: rule not met)" appended where negative. |
| 59–61 (split, scale) | Labelled EXPLORATORY (not preregistered); "\|" separators replaced by ";". |
| 43, 48 (band) | Labelled "descriptive; read with the CI above"; §3 header says bands are not decision rules. |
| 66–76 (share of total) | Caption: relation included; the fact row is NOT ICC(1). |
| 78–87 (D2, D3) | Caption: descriptive, no hypothesis, censored rows dropped. |
| 101 (null p, licensed sentence) | p shown as "≤ 0.001 (floor 1/1001)"; sentence quoted verbatim with the §4/§10 caveats and the answer-token caveat. |
| 94–100 (False rows) | Sentence added: False = not licensed, not the opposite; otherwise report shares and n′. |
| 118–129 (sensitivity flags) | Relabelled non-gating, not evidence; confirmatory count stated. |
| 124–125 (all10) | Small-N, wide-interval note added; singular flag already in the table. |
| 148 (INR) | Removed from RESULTS; points to PROGRESS.md and the ledger. |
| 5 (D3 from rank) | Fixed. |
| 113 (H3 set) | "(set `correct`)" added. |
| Item 4 (Limitations) | §8 Limitations added (scope, correct-only/MNAR, conditional ICC, 10 frames, PROXY frequency, CI coverage 0.925, MoM offset, null size and power, no frequency test, final-position readout, robustness simulation MISSING). |
