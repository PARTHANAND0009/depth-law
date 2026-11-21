# PROGRESS (depth-law)

Updated 2026-11-20 ~14:40 UTC. Source of truth for project status (CLAUDE.md). Every number below is copied
from the report named next to it, and each report cites its results file and run_id.

STATUS: P2 PREPARATION (G1 approved by the human 2026-11-21; Part 0 done; Part A in progress)

- **P2 Part A (2026-11-21):**
  - Done:
    - A1 `materials/facts_v1.jsonl`: 300 facts / 20 relations; company_ceo excluded by the first-token rule; 74 facts overlap G1.
    - A2 `materials/paraphrases_v1.jsonl`: 200, all valid.
    - A3 `materials/carriers_v1.jsonl`: 3.
    - A4 code: `analysis/p2/`; Henderson-III MoM self-test unbiased; end-to-end synthetic test passed.
    - A7 pythia-70m pre-flight passed.
    - A5 prereg draft staged in `reports/pending_frozen_changes/P2_prompt_vs_fact.md`, because prereg/ is write-protected.
  - Running:
    - A4 bootstrap-method simulation (`results/P2sim/`, started 17:05 UTC, about 2 h).
    - A6 citation-verifier and experiment-planner (run_manifest).
  - Pending: stats-reviewer on the prereg and simulation report.

- **Gate G1 (E-depthvar, EXPLORATORY post hoc):** outcome AMBIGUOUS under the human's rule. Reported in `reports/gates/G1/GATE_G1.md`; review answers in `responses.md`.
  - Reviews: replicator PASS, stats-reviewer REVISE, skeptic BLOCK. The skeptic's block concerns the OLMo single-template effect; the category is unchanged.
  - Waiting for "approve G1". Prompt 2 (confirmatory preregistration) is not started.
  - G0 was never answered by the human.
  - `gates.yaml` G1 also lists novelty-scout and experiment-planner. They were not run, because the human's G1 instruction named three reviewers, so `gate_check.py G1` reports them missing.

## Budget (2026-11-21)
| item | value |
|---|---|
| GPU minutes left | 0 (none rented) |
| INR left | Jarvislabs balance INR 240 on 2026-11-21. RTX Pro 6000 Blackwell 96GB at INR 207.36/h billed per second, so about 69 min. Minimum top-up in India is INR 500 (INR 500 buys about 145 min). |
| deadline candidates | ARR Jan 4 AoE; ICML abstract Jan 14, paper Jan 22 AoE |
| Pro usage tier | normal. Two review subagents hit the 5-hour usage limit on 2026-11-21 ~09:0x UTC (reset 09:20) |
| RAM free | ~2.4 GB of the 14.3 GB cap while S5 runs (S5 ~11.9 GB) |

## EXPLORATORY (post hoc, not preregistered) E-depthvar (2026-11-21, human's part B)
- **Plan:** `analysis/exploratory/E-depthvar/EXPLORATORY_post-hoc_not-preregistered__PLAN.md`, committed at 853917a before any statistic.
  - It discloses that the D1 all-rows variance components were already seen in the H-R gate.
- **Build:** run dir `results/EXPLORATORY_E-depthvar/EXPLORATORY_E-depthvar-none-321939b-20261121T153451Z`. Peak RSS 516 MB; D1 recomputed equals the stored half_prob_depth.
  - Correct cells: 720 / 804 / 1414.
  - Facts correct under all 3 templates: 84 / 107 / 254.
- **Main run (B3-B7):** started 15:4x UTC in the background through log_run.py (3 R workers); outputs go to the same run dir.
  - Finished 16:22 UTC: exit 0, 42 min, largest single process 258 MB.
  - Outputs: `e_depthvar.json` in the run dir; `analysis/exploratory/E-depthvar/` holds the report, the components table and 3 figures.
  - G1 rule inputs (set i, correct cells):
    - (template + residual) > (fact + subject) with the CI excluding 0 under D1 in OLMo-2 only.
    - fact+subject share ≥ 0.5 in no model.
    - The null passes in all 12 cells; planted bias ≤ 0.028.
    - CI coverage in simulation is 0.46–0.98.
  - Reviews and GATE_G1 come next.
- **Parts C and D** (reviews, GATE_G1) follow after the run.

## Housekeeping (2026-11-21, human's part A)
- **A1 D-A0 (A0 withdrawn; A0 proposals EXPLORATORY): BLOCKED.**
  - `prereg/deviations/D-A0.md` and a prereg index cannot be written by Claude: the deny rule Edit(prereg/**), protect_frozen.py and pre-commit all block it.
  - The text is staged in `reports/pending_frozen_changes/`. Ledger entry DEVIATION D-A0.
  - No A0 file was ever written.
- **A2 budget:** Budget block above, plus a ledger BUDGET entry.
- **A3 agent edits:** PENDING_AGENT_EDITS_NOT_FOUND (ledger). The section 3.1 text is not in the repo; no agent file changed.
- **A4 kill hook:** narrowed version with an explicit S5 guard staged in `hooks/proposed/protect_frozen.py`. `hooks/tests/test_kill_hook.sh`: 13/13 correct (installed: 9/13).
- **A5 S5 exemption:** staged in `hooks/proposed/stop_check.py`. `hooks/tests/test_stop_s5.sh`: 7/7 (installed: 5/7).
- **Not installed:** A4 and A5, because `.claude/hooks/` is frozen. The human runs `reports/pending_frozen_changes/APPLY.sh` and edits the settings.json deny rule as described in it.
- **S5 NOT RUNNING since a worker restart (seen 15:28 UTC):**
  - pythia-2.8b step32000 stopped at 18/21 chunks.
  - Not relaunched: the human's rule forbids restarting S5 from this session.
  - Human relaunch: `nohup setsid bash scripts/run_s5_cpu.sh >> results/s5_cpu.out 2>&1 < /dev/null &`

## Gate G0 (2026-11-21): guards installed and tested
- **Files (commit 3c87115):**
  - hooks: `.claude/hooks/protect_frozen.py`, `.claude/hooks/stop_check.py`
  - settings: `.claude/settings.json`, without the `.claude/hooks/**` deny rules until GO G0
  - scripts: `scripts/check_numbers.py`, `gate_check.py`, `verify_bib.py`, `log_run.py`, `pre-commit` (installed to `.git/hooks/`), `gen_required_macros.py`
  - config: `gates.yaml`; `config/required_macros.json` (329 macros), with the mapping in `config/required_macros.md`; `paper/models.tex`
  - agents: novelty-scout, citation-verifier, claim-auditor, experiment-planner
  - CLAUDE.md integrity rules; `docs/guards.md`
- **Tests:** `reports/guards_test.md`. Every deliberate violation was blocked. It also lists 2 gaps and 3 problems.
- **Not done:**
  - Section 3.1 edits to skeptic/replicator/stats-reviewer/reviewer-sim: MISSING, the text was not received.
  - A0 (`prereg/amendments/A0_decision_rules.md`): HELD. It was required "before any H-R result is opened", but the H-R result was computed, opened and reported on 2026-11-21 (run `HR-none-f431f35-20261121T081116Z`, `results/HR_gate.md`, NO-GO under the frozen rule). See the G0 report to the human.
- **Amendments committed:** none. Their commit hashes will be recorded here.
- **H-R job state:**
  - The confirmatory H-R gate run finished at 08:31 UTC: `results/HR_gate.json`, commit a16e158.
  - Still running: the `replicator` review of it (subagent, R bootstrap in `scratch/replicate/`, writing `results/review/replicator.md`). Not touched.
  - Saved: the `stats-reviewer` report (`results/review/stats_reviewer.md`: 7 violations, none decision-changing).
  - Not yet run: the skeptic.
  - Replicator finished 10:16 UTC: `results/review/replicator.md`, scripts in `scratch/replicate/`.
    - 110 of 116 rows PASS, including every gating number, the hypothesis flags and the decision (NO-GO).
    - The 6 FAILs are all split-half reliability or disattenuated ρ (reporting-only). They are Monte Carlo variation in the undefined-split rate for pythia-2.8b: 32 vs 41 of 200 splits.
    - Both review reports move to `reports/gates/G1/` at G1.

## 0. Hardware now

| item | value | source |
|---|---|---|
| GPU | none (`nvidia-smi`: command not found; `reports/hw.json` gpus []) | live check 2026-11-20 |
| CPU / RAM | 4 cores / 15 GB, no swap; ~11 GB in use by the running pythia-2.8b S5 job | `free -g` |
| Disk | 12 GB free after the approved deletion of `cache/hf/hub/blobs/91/91cf95c5…` (5.7 GB pythia-2.8b main weights; the 0.5 MB llama-tokenizer blob in the same folder was kept) | `df -h`, 2026-11-20 13:35 UTC |
| Memory cap | 14.3 GB for this session (cgroup); S5 holds ~12 GB, so only one extra job at a time, with oom_score_adj 1000 | `memory.limit_in_bytes` |
| Tier | CPU. Every run so far was on CPU, after the human said "OK CPU G1" and "do everything on cpu" | `reports/GATE_G1.md` |

Largest disk items (none deleted; candidates for P0 "free disk", to be approved before deletion):

| path | size | what it is | needed later? |
|---|---|---|---|
| `cache/hf/local/EleutherAI--pythia-2.8b--step32000` | 5.7 GB (pytorch_model.bin) | current S5 checkpoint; the chain deletes it when the revision finishes | in use now |
| `cache/zoo/pythia-1.4b` | 4.9 GB | S7/S9 weight deltas (ROME/MEMIT/AlphaEdit/LoRA) | yes (re-evaluating zoo models, S7b) |
| `cache/hf/hub/blobs/44/44c573fa…` | 2.9 GB | pythia-1.4b `main` weights | yes |
| `.venv` | 1.9 GB | environment | yes |
| `cache/hf/hub` pythia-410m / 70m | 0.9 / 0.45 GB | tests | yes |

## 1. Gates and what they concluded

| gate | rule (`configs/prereg.yaml`) | result | outcome | human reply | report / run_id |
|---|---|---|---|---|---|
| G1 | partial R^2 of log1p(EXACT cooc) on causal_final >= 0.10, negative slope, in >= 2 of {pythia-1.4b, pythia-2.8b, OLMo-2-7B} | pythia-1.4b 0.001 [-0.028, 0.028]; pythia-2.8b -0.018 [-0.056, 0.033]; OLMo-2-7B MISSING | **NO-GO** (0/2 run models pass) | "GO G1" (override; NO-GO stands as the prereg result) | `reports/GATE_G1.md`; `G1-none-3d0e3e5-20261110T233528Z` |
| G2 | Spearman(inserted freq, depth) < -0.5 on facts learned in all seeds | -0.130 (p 0.5735), N = 21 | **FAIL** | "GO G2" | `reports/GATE_G2.md`; `G2-none-1e14c66-20261115T142350Z` |
| G3 | fact-level AUROC >= 0.8 on non-adaptive ROME/MEMIT | s_maha 0.823 [0.797, 0.848], N+ 1123, N- 276 | **PASS on point estimate; CI lower bound < 0.8; pass driven by the confidence residual, not depth** | "GO G3" | `reports/GATE_G3.md`; `S8-pythia-1.4b-aae6507-20261118T123031Z` |
| A2 (amendment 2) | within-relation partial R^2 of log1p(EXACT cooc) on half_prob_depth >= 0.10 and slope < 0 (WEAK >= 0.05), in >= 2 of {pythia-1.4b, pythia-2.8b, OLMo-2-7B} | OLMo-2-7B -0.026 [-0.052, 0.014], slope +0.0056 [-0.0003, 0.0111]; pythia-1.4b 0.006 [-0.060, 0.015], slope +0.0130 [0.0047, 0.0174]; pythia-2.8b -0.014 [-0.047, 0.016], slope +0.0114 [0.0033, 0.0167]; N 3900 rows each | **NO-GO** (0/3 PASS, 0/3 WEAK; slope positive in all 3 models and all 21 sensitivity fits) | waiting | `reports/GATE_A2.md`; `A2-none-a7dfeb5-20261121T065218Z` |

Important caveats already in the reports:
- G2 was run on a CPU-scaled model (10.5M parameters, 8 layers, 10M-token stream x 4 passes), not the 160M / 5B-token spec. 18 of the 21 facts learned in all seeds are in the top frequency bin (`reports/GATE_G2.md`).
- In G3, depth residual alone scores below chance: s_abs_r_causal 0.397 [0.358, 0.439], s_r_causal 0.344. The confidence-vs-frequency residual alone scores 0.884 [0.862, 0.903], which is above the combined s_maha (`reports/GATE_G3.md`).
- By construction, causal_final resolves exactly when the model's top-1 answer is correct; on memit100 the censored-vs-correct crosstab is diagonal (`reports/S7.md`). Depth exists only for correctly answered rows, about 20% of rows on clean Pythia (`reports/GATE_G1.md`).

## 2. What has run (by stage)

| stage | status | key numbers | report / run_id |
|---|---|---|---|
| S0 setup | done | 12/12 tests (S0). Suite now 27/27 on pythia-70m (2026-11-19, after the revision-loading fix) | `reports/S0_S2.md`; `S0-pythia-70m-8e025e4-20261106T193847Z` |
| S1 facts | done | 5,200 facts, 26 relations x 200; SANSKRITI 2,619 cloze facts kept of 21,853 MCQ items | `reports/S0_S2.md`; `S1-none-7ce9c25-20261106T000136Z`, `S1b-none-40f14b3-20261105T213843Z` |
| S2 counts | done | EXACT phrase counts (amendment_1): Pile (EXACT), OLMo-mix (EXACT), DCLM (PROXY). CNF windows w32 / w100 / w500 also stored. Pile zero fraction 0.445 | `S2x-none-5516178-20261108T042549Z`, `S2x-none-dc68830-20261117T145502Z`; CNF `S2-none-4534b8f-20261106T105913Z` (w100), `S2-none-ea2fa06-20261106T175613Z` (w32/w500); audit `reports/count_audit.csv` |
| S3 depth | done, 1300-fact subsample (26 x 50) | pythia-1.4b correct@1 0.185; pythia-2.8b 0.206; 3900 rows each | `S3-pythia-1.4b-b9a353d-20261108T064941Z`, `S3-pythia-2.8b-be99060-20261109T021915Z` |
| S3b depth (amendment 2, GPU) | done 2026-11-21, human-run GPU session (RTX PRO 6000 Blackwell; branch gpu-olmo-run merged ff at 5a0f36e) | half_prob_depth + causal_final + logit lens, fp32, 1300 facts x 3 templates = 3900 rows per model, 0 NaN; correct@1 OLMo-2 0.363, pythia-1.4b 0.185, pythia-2.8b 0.206. Pythia GPU rows match CPU S3 (correct@1 3900/3900, causal_final on all resolved rows) | `S3b-OLMo-2-1124-7B-923945f-20261121T061237Z`, `S3b-pythia-1.4b-a7dfeb5-20261121T063528Z`, `S3b-pythia-2.8b-a7dfeb5-20261121T064110Z`; `reports/A2_PRIMARY_gpu_20261121T065217Z.md`, `reports/env_gpu.md` |
| S4 transfer / controls | partial (exploratory) | TOST, held-out families, minimal pairs, SANSKRITI slice, LRE nested model on Pythia; transfer models MISSING | `reports/S4.md`; `S4stats-none-f6c16ee-20261112T183909Z` |
| S5 checkpoints | running | pythia-1.4b 9 revisions done (interim report). pythia-2.8b: 4 earlier runs invalid (loaded main weights; moved to `results/S5_invalid/`); rerun with shard-only loading: step1000, step2000, step4000 (correct@1 0.104, run `S5-pythia-2.8b_step4000-148a280-20261120T090122Z`), step8000 done (N 1524 rows, correct@1 0.231, causal_final resolved 352; pythia-1.4b step8000: 0.172, 262; run `S5-pythia-2.8b_step8000-daedcdd-20261120T160100Z`); step16000 done (N 1524, correct@1 0.318, causal_final resolved 485; pythia-1.4b step16000: 0.243, 371; run `S5-pythia-2.8b_step16000-2dddca9-20261120T224143Z`). step32000: the Hub branch has no shards and its model.safetensors is main's (sha ab496f1c); the guard stopped the chain at 05:09:46Z (no rows computed). Fix: `resolve_weights` now loads the distinct pytorch_model.bin (sha 521d9e00) in that case (load_mode `local_bin`); checked bin != main on 3 tensors and loaded params == bin; tests in `tests/test_revisions.py`. Relaunched 05:13Z (run dir `S5-pythia-2.8b_step32000-c894487-20261121T050945Z`, created before the fix; weights_shard0.json records local_bin). step64000-128000 have single distinct model.safetensors (no clash). The S4T chain started Gemma at 05:10Z when S5 stopped; I stopped it (0 chunks) and it now waits for `S5CPU DONE` | `reports/S5.md` (INTERIM); `S5stats-none-74f0e77-20261115T233904Z` |
| S6 / G2 | done (CPU scale) | see G2 | `reports/GATE_G2.md` |
| S7 zoo | done (pythia-1.4b) | rome_single, memit100/1000, alphaedit100/1000, lora50/200/1000, synthdoc50; all efficacy >= 0.90 | `reports/S7.md`; `S7-pythia-1.4b-f468c95-20261116T183628Z`; `zoo/manifest.json` |
| S8 detector | done | see G3 | `reports/S8.md` |
| S9 attacks | done | A1 s_maha 0.904, A2 0.820, A3 0.732 (vs twins rome_single 0.911, synthdoc50 0.626) | `reports/S9.md`; `S9-pythia-1.4b-aae6507-20261118T124110Z`, `S9score-pythia-1.4b-b70eba4-20261118T212041Z` |
| S10 figures | not started | | |

## 3. Running now

| job | state | ETA (UTC) |
|---|---|---|
| `scripts/run_s5_cpu.sh` (log `results/s5_cpu.out`, snapshot `results/logs/`) | pythia-2.8b step16000 done (1524 rows, correct@1 0.318); step32000 relaunched 05:13Z after the stale-main fix (load_mode local_bin), 5/21 chunks at 06:53Z (~20 min/chunk); then 64000, 96000, 128000 (~7.2 h each) | step32000 ~12:15 on 21 Nov; all ~10:00 on 22 Nov |
| `scripts/run_s4t_cpu.sh` | waits for `S5CPU DONE` in the S5 log (changed 2026-11-21 after it started Gemma early when S5 failed; stopped with 0 chunks); then gemma-3-4b-pt causal-only on 1300 facts (bf16, PROXY counts). Runtime not measured | 22-25 Nov |
| keep-alive | watcher + scheduled check-ins (~every 2 h); container restarted 3 times in 2 days, each time resumed from chunks | |

## 4. Status against the evidence bar (new brief, 2026-11-20)

### Claim 1 (regularity)
| item | status | numbers / source |
|---|---|---|
| a. partial R^2, relation cluster bootstrap | done for 2 Pythia models; both ~0 | `reports/GATE_G1.md` |
| b. survival HR | done; HR > 1 but mixes "resolves at all" with "resolves earlier" | 1.254 [1.159, 1.357] (1.4b), 1.273 [1.171, 1.384] (2.8b), `reports/GATE_G1.md` |
| c. minimal pairs | done, exploratory; 5 of 6 tests null; one small p (2.8b one-per-token, N 39, p 0.0046, uncorrected) | `reports/S4.md` |
| d. within-fact checkpoint dynamics | pythia-1.4b done (interim); 2.8b running; OLMo-2 MISSING (no GPU) | acquisition HR 1.020 [0.977, 1.064]; depth minus final depth: +0.116 at step 4000, about 0 from step 32000, `reports/S5.md` |
| e. EXACT counts, two families incl. OLMo-2-7B | MISSING: only Pythia (one family). OLMo-2-7B needs a GPU | |
| f. PROXY transfer | MISSING: Llama-3.1-8B, Qwen3-8B need a GPU; Gemma-3-4B queued on CPU | `reports/S4.md` |
| g. depth adds over confidence and LRE (nested) | LRE nested done (log cooc partial R^2 given faithfulness 0.0009); nested model vs logprob/margin not run | `reports/S4.md` |

### Claim 2 (causality)
| item | status |
|---|---|
| 160M, 3 seeds, Spearman < -0.5 | FAIL at CPU scale (10.5M model); spec scale MISSING (needs a GPU) |
| answer-token distribution and subject token length matched across bins | matching was built into the fact generator (`notes/s6_plan.md`); a per-bin balance table is not in any report: MISSING |

### Claim 3 (detector)
| item | status |
|---|---|
| beats confidence x rarity on matched-count set (S7b) | MISSING: S7b not built. On the G3 pool s_maha 0.823 vs s_conf_rarity 0.659, but depth alone 0.397 |
| within (count decile x confidence tercile) strata | not run |
| benign fine-tunes x3 (clean models + negative control) | not run |
| held-out method; MEMIT primary, AlphaEdit separate | per-model and held-out-method AUROCs reported separately (`reports/S8.md`); the prereg G3 pool pools rome_single + memit100 + memit1000 |
| A1-A3 | done; A3 as built (LoRA on 60 synthetic docs/fact) does not target the law-predicted depth for the fact's actual EXACT count: "A3 fix" not done |
| baselines conf, perp, conf x rarity, LCF, Youssef AdaBoost | done (LCF MISSING for A1-A3) |
| two-hop depth gap, >= 300 edited + 300 clean | MISSING: no two-hop prompts built |
| 7B replication from a second family | MISSING: no GPU |

### P5-P7
| item | status |
|---|---|
| SANSKRITI | 2,619 cloze facts (drop reasons in `reports/sanskriti_conversion.json`); 300-item slice on pythia-1.4b: 64 resolved rows of 900, 77% zero cooc, slope n.s. (`reports/S4.md`). Detector on SANSKRITI edits: not run |
| robustness (5% re-run, windows 32/100/500, causal vs lens, raw vs normalized, EXACT vs PROXY on same model) | counts for w32/w100/w500 exist; CNF-predictor sensitivity and measure agreement in G1; the rest not run |
| novelty sweep (notes/related.md) | not done |

## 5. P0 items "from my last review"
I find no record of an earlier review in this repo (`notes/`, `reports/`, git log) or in this session's transcript. None of these items is done: disk freeing (candidates listed in section 0), extended G3 report, S7b matched-count set, benign fine-tunes, A3 fix, two-hop sample.

How `results/HOLD_S5` was removed: the S8/S9 chain created it so S5/S4T would wait while S8/S9 used the RAM (commit `3276e8f`). `scripts/run_s8s9_cpu.sh` deliberately did not remove it at the end. I removed it by hand at 2026-11-19T13:38:14Z, 33 s after the human's "GO G3" (13:37:41Z), and recorded it in `reports/GATE_G3.md` ("Human decision") and in `results/s5_cpu.out` ("RELAUNCH after GO G3 (container restart; HOLD_S5 removed)"). Commits `6122817`, `b08df91`.

## 6. MISSING (consolidated)
- OLMo-2-1124-7B: S5 checkpoint dynamics; G1 (old measure, causal_final) not re-fitted on the S3b OLMo rows (the S3b run has causal_final, so it can be done on CPU if wanted). S3 depth for OLMo now exists (S3b, amendment 2).
- Llama-3.1-8B, Qwen3-8B transfer (no GPU); Gemma-3-4B queued on CPU.
- S6 at spec scale (160M, 5B tokens); per-bin balance table for S6.
- Tuned-lens depth (no pretrained lens for pythia-1.4b/2.8b; none trained). Patchscope and causal_subj_onset: < 30 resolved rows.
- S7b matched-count set; benign fine-tunes; stratified detector analysis; two-hop gap; A3 fix; LCF for A1-A3; model-level AUROC (one clean model).
- 7B zoo / replication.
- Robustness items in P6 except those listed above; novelty sweep; S10 figures; paper; release.

## 6b. Work done 2026-11-20 (human's 5-item request; P0 list superseded)
| item | result | report / run_id |
|---|---|---|
| 1. delete orphaned blob | done (5.7 GB) | – |
| 2. causal_final audit | resolved == correct@1 by construction (last-block identity); mechanics correct; carriers alone never predict the object; proposed correctness-free measure A (half-probability depth), NOT adopted, needs approval + prereg amendment_2 | `reports/AUDIT_causal_depth.md`; `AUDIT-pythia-410m-92ee9d9-20261120T134212Z`, `AUDIT-pythia-1.4b-341c906-20261120T135225Z`, `AUDITsum-none-be31f9e-20261120T142742Z` |
| 3. Claim 1 re-analysis (exploratory) | counts predict correctness (OR 1.24 / 1.32); depth-cooc Spearman is between-relation (within-relation -0.040 / -0.055, n.s.); survival HR among resolved rows ~1; tuned lens MISSING | `reports/C1_reanalysis.md`; `C1re-none-3cee850-20261120T141401Z` |
| 4. P1 compute estimate | OLMo-2-7B S3+G1 3-7 A100-h (1300 facts) incl. tuned lens, >= 40 GB; Claim 2 3 seeds 31-46 A100-h, >= 24 GB (estimates, not measurements) | `reports/P1_compute.md` |
| 5. gate notes | GO-despite-NO-GO/FAIL recorded in GATE_G1/G2; G3 signal = confidence residual, depth alone 0.397 | `reports/GATE_G1.md`, `GATE_G2.md`, `GATE_G3.md` |

## 6c. Work done 2026-11-20, second request (amendment 2, FCL, OLMo GPU script)
| item | result | where |
|---|---|---|
| 1a. prereg amendment 2 | half_prob_depth headline; primary test = within-relation partial effect (cooc split into relation mean + within deviation; relation random intercept + slope on the within term); controls log_subj, obj_logprob_final, n_answer_tokens, n_subject_tokens; g1 thresholds. Committed before any computation on gate models | `configs/prereg_amendment_2026-11-20.yaml`, commit c0a7825 |
| 1b. compute on S3 rows? | NOT possible: S3 stored per-layer patched **ranks** only (`final_rank_curves`), no patched probabilities. Live rerun needed. Done on GPU by the human on 2026-11-21 (S3b runs, see section 2); no CPU rerun | this file, section 7 |
| 2. FCL re-check | WAITING for the path to the FCL code and TCBench-2K data (not on this machine) | – |
| 3. OLMo GPU script | `scripts/olmo_gpu_run.sh` + `requirements-gpu.txt`; code path `run_depth --halfprob`; test `stats/amend2.py`; inputs `data/amend2_inputs.parquet` (1300 facts, EXACT piletrain + olmo-mix covariates, no NaN). Dry run on pythia-70m CPU (300 facts) passed end to end: pytest 7/7, depth pass, primary test + report. GPU-only branch run by the human on 2026-11-21 (`reports/env_gpu.md`); result `reports/GATE_A2.md` | `reports/A2_PRIMARY_DRYRUN.md`; `S3bdry-pythia-70m-3bd6894-20261120T165137Z`, `A2dry-none-3bd6894-20261120T165531Z` |
| 4. Claim 2 | on hold until the OLMo result; the OLMo result is in (GATE A2: NO-GO) | – |
| 5. GATE A2 (2026-11-21) | branch gpu-olmo-run merged; results complete (3900 rows x 3 models, 0 NaN, 0 bootstrap failures, no MISSING sensitivity); point estimates reproduced on CPU to 6 decimals; outcome NO-GO | `reports/GATE_A2.md`; `A2-none-a7dfeb5-20261121T065218Z` |

## 7. Next open item
GATE A2 is open: waiting for the human's "GO A2" or "PIVOT <option>" on `reports/GATE_A2.md` (NO-GO under the amended prereg). Also waiting: FCL code + TCBench-2K path. Claim 2 on hold. S5 keeps running; S4T Gemma waits for S5 DONE. Nothing else runs.
