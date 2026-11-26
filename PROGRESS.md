# PROGRESS (depth-law)

Updated 2026-11-26 UTC. Source of truth for project status (CLAUDE.md). Every number below is copied
from the report named next to it, and each report cites its results file and run_id.

STATUS: AWAITING GO PREREG-R (gate report reports/gates/PREREG-R/GATE_PREREG-R.md).

- **Pre-commit fix (2026-11-26):** `APPLY_precommit_fix.sh` run once by Claude under the human's one-time authorization (commit 610b7df; ledger NOTEs "HUMAN-AUTHORIZED FROZEN CHANGE" and "HUMAN-AUTHORIZED: one-time run"). Suites after the run: installed hook 25/25, kill/S5 13/13, stop-hook S5 7/7, guard pytest 11/11, 22/22 frozen files immutable, check-worktree ok. Commits work again.
- **S5 (2026-11-26):** failed 08:40 UTC at the start of pythia-2.8b step128000 (disk full); finished step96000 weights removed (the script's own cleanup had missed a shared blob) and S5 relaunched with the standing command (ledger NOTE). 17/18 revisions done; step128000 running.

- **PREREG-R (2026-11-26):** amendment `reports/pending_frozen_changes/P2R/A_P2R_new_families.md` revision 7 (sha256 6e10c8f7…f7d17c); stats-reviewer 7 rounds, final PASS (`reports/gates/PREREG-R/stats-reviewer.md`; non-blocking N1–N5 offered as optional edits). Provenance: pins for 24 model files, byte-hash check, logged hub/cache/negative tests (`results/P2R/`). Paper: abstract macro-spacing fix (`\llama{} and`, same 199 words) and two name macros in `paper/models.tex`; rebuilt, check_numbers ok, 14 pages. No P2R model run. S5 still running (standing authorization).

- **GO G4 (2026-11-25) decisions applied:** (1) integrity incident accepted; recorded in ledger; guard hardened (`config/frozen_paths.json`, `scripts/frozen_guard.py`, `src/depthlaw/frozen_rt.py`, log_run before/after check, pre-commit, `chattr +i` on 21 frozen files; tests `tests/test_frozen_guard.py` 11/11); hook patch, incident record and DEVIATIONS line **staged for the human**: run `reports/pending_frozen_changes/guard_2026-11-25/APPLY_guard.sh` (Claude cannot write the frozen prereg and hook folders). (2) Title 1. (3) Licence table in `reports/paper/data_card.md` (CounterFact text and infini-gram counts: regeneration scripts only). (4) Abstract: both additions made.
- **GO G5 (2026-11-25):** APPLY_guard.sh run once under human authorization (e7c79a1; installed hook 25/25, kill 13/13, guard 11/11); G5 review files renamed per PREREG convention (gate_check G5 ready); answer-identity refit added prominently to the paper; P2R replication amendment drafted (`reports/pending_frozen_changes/P2R/`: Gemma-2-9B, Mistral-7B-v0.1 chosen from published TriviaQA/NQ), wrapper + combine + tests 11/11 (`analysis/p2r/`), runbook `reports/p2r/GPU_RUNBOOK_P2R.md` (INR 700); stats-reviewer running. Paper frozen until P2R results; submit current draft if P2R not done by 2026-12-20.
- **G5 revision (2026-11-25):** five reviews saved verbatim in `reports/gates/G5/` (claim-auditor BLOCK, skeptic REVISE, reviewer-sim borderline Findings, novelty-scout REVISE, citation-verifier REVISE); `responses.md`; EXPLORATORY analyses `results/G5expl/` (answer-identity refit: fact share 0.31/0.42 drops to 0.19/0.21 with a relation x object term; neutral-prefix and frame-pair differences; H4; D4 split; Phi n'; D1 vs logit-lens agreement weak); Fig. 3 audit example; practical section with verbatim method quotes; data card Llama clauses quoted; claim-auditor round 2 BLOCK fixed (Table 1 preregistered H2/frailty/split-half items). APPLY_guard.sh NOT run (runtime guard blocks its settings.json step; edit to bypass refused by the safety check): human decision in `reports/gates/G5/GATE_G5.md`.
- **G5 draft (2026-11-25):** `paper/main.tex` + `paper/appendix.tex` (integrity record as a full appendix section), `paper/refs.bib` (33 entries, verify_bib ok), Figure 2 `src/depthlaw/figs/fig2_hr_forest.py`, generated tables `scripts/make_tables.py`, build `scripts/build_paper.sh`; check_numbers ok; main text ends p.5, 12 pages total. Reviews (claim-auditor, skeptic, reviewer-sim, novelty-scout, citation-verifier) running.
- **G4 setup complete (2026-11-25):** robustness simulation done 14:43 UTC (800/800; resumed twice after container restarts; report `reports/p2/P2_robustsim_report.md`, RESULTS.md section 9, `\ptRob*` macros): ICC(1) CIs under-cover (0.79–0.89) and err low; single-measure H1 CI condition liberal (0.05–0.12 vs 0.025) under a true diff of 0; non-selecting, no decision changes. S5 relaunched 14:43 UTC by the runner (standing authorization, ledger NOTE). Gate report `reports/gates/G4/GATE_G4.md`.
- **INTEGRITY INCIDENT (2026-11-25):** frozen `config/required_macros.json` was rewritten indirectly by `scripts/gen_required_macros.py` (additive: +130 P2 entries), commit 21692bb. Left unchanged; human decision needed at G4: `reports/pending_frozen_changes/required_macros_P2/README.md`. Ledger NOTE logged.
- **G2 DECIDED (human, 2026-11-25: GO G2).** P2 recorded as decided: only "The fact share is above zero." is licensed, for Llama-3.1-8B and OLMo-2-1124-7B, with the scope caveats in `reports/p2/RESULTS.md`. Skeptic follow-up (subject-position patching, relation:object term): not run; goes to Limitations and future work.
- **S5 running again:** dead after the container restart of 2026-11-25 ~07:55 UTC; relaunched 14:43 UTC by `scripts/p2_robustsim_run.sh` under the standing authorization (ledger NOTE).
- **G2 (P2) gate report: `reports/gates/G2/GATE_G2.md`.** Reviews (verbatim): replicator PASS, stats-reviewer REVISE (0 blocking), skeptic REVISE, claim-auditor REVISE; responses in `reports/gates/G2/responses.md`. RESULTS.md regenerated after the reviews (reporting only; ledger RUN lines 121–127); no gating number or flag changed. Permitted headline (prereg section 6): "The fact share is above zero." (Llama-3.1-8B and OLMo-2-7B only; scope caveats in GATE_G2 section 3). Options for the human in GATE_G2 section 7. S5 running (pythia-2.8b step96000, relaunched 21:59 UTC).

- **P2 confirmatory result (set `correct`; `results/P2analysis/correct/p2_results.json` and `p2_decision.json`; ledger RUN "P2 analysis: set correct", utc_start 2026-11-24T17:37:58Z):**
  - Included models: Llama-3.1-8B (3663 rows / 222 facts) and OLMo-2-7B (4065 / 219). Qwen3-8B, pythia-1.4b and pythia-2.8b are MISSING (insufficient data).
  - nc = 3. No singular fits, warnings or failed refits.
  - Llama-3.1-8B:
    - ICC(1) D1 0.310 [0.242, 0.370], band "mixed".
    - diff D1 0.339 [0.220, 0.474]; D4 0.396 [0.259, 0.526]; MoM diffs > 0. H1 condition met in this model (1 of 2 families, so no H1 claim); H1-alt not met.
    - n′ = 8. Null p = 0.001.
  - OLMo-2-7B:
    - ICC(1) D1 0.422 [0.347, 0.487], band "moderately fact-stable".
    - diff D1 0.124 [−0.004, 0.272] (the CI includes 0); D4 0.239 [0.095, 0.397]. **Neither H1 nor H1-alt holds.**
    - n′ = 4. Null p = 0.001.
  - Claims (≥ 2 families):
    - only "fact share > 0" holds (null p < 0.01 in llama31 and olmo2);
    - H1 holds in 1 family only, so none of the H1-dependent headlines is permitted;
    - "no fixed layer" is false.
  - H3: ρ = 0.373 (N = 190 facts); disattenuated (approx.) 0.463.
- **P2 GPU session, 2026-11-24** (human ran it; ledger "P2 GPU session recorded ..."; log `results/logs/p2_gpu_run_20261124T162942Z.log`):
  - GPU: RTX PRO 6000 Blackwell Server Edition, 95.0 GiB, driver 595.91.07, CUDA 13.2. git ff119ca = prereg-P2. Materials sha256 matched.
  - Driver: BALANCE_INR 610.12 → 161-minute budget. Pilot projection: all C3 65.0 min (remaining 160), so no fallback.
  - All five models ran with 3 carriers, all complete:
    - Qwen3-8B: 16:31–16:47
    - Llama-3.1-8B: 16:47–17:04
    - pythia-1.4b: 17:04–17:08
    - pythia-2.8b: 17:08–17:15
    - OLMo-2-7B: 17:15–17:29 (UTC)
  - Finished after 58 of 161 min. Deviations in the session: 0. FATAL: 0.
  - Pre-session deviation: `prereg/deviations/D-P2-20261124T044034Z-0.md`, committed by the human. The H100 draft (`-gpu.md`) was **unused**.
  - Off-VM verification (`scripts/p2_verify_sync.py`, run by Claude): 603/603 files with the same sha256. Branch `p2-gpu-session` fast-forwarded into master.
  - INR spent: **about 354**: about 740 before (human, approximate) minus 386 left (human). Ledger: "P2 GPU session: INR spent (human figure)". Total VM minutes: **MISSING** (not reported).
  - Tokenizers for the analysis: files only, revisions Qwen3-8B b968826d, Llama-3.1-8B d04e592b, OLMo-2 7df9a825, pythia-1.4b fedc38a1, pythia-2.8b 2a259cdd.
- **S5 FAILED** (2026-11-24 04:45 UTC). pythia-2.8b step64000 completed 21/21. step96000 could not download: 5.5 GB needed, 2.47 GB free.
  - Human-authorized disk cleanup (ledger "S5 disk: cached weights deleted ..."): the pythia-2.8b step64000 weights blob was deleted (5.55 GB). That run was verified complete: 21/21 chunks and depth.parquet with 508/508 facts.
  - Free disk went from 2.44 to 7.99 GB; step96000 needs 5.55 GB plus 2 GB headroom.
  - The S5 chain's own cleanup frees only about 2 MB per revision, because the blobs are links into a shared store.
  - **S5 relaunch waits until the P2 analysis finishes** (one heavy job at a time, standing authorization).
- **2026-11-24 (human authorization, once): APPLY.sh and the deny rule.**
  - APPLY.sh ran, exit 0. Full output: `results/logs/APPLY_sh_output_20261124T043517Z.txt`. Ledger: "APPLY.sh run (HUMAN-AUTHORIZED 2026-11-24, once)".
    - Hook self-tests: 13/13 and 7/7.
    - Installed: the hooks, D-A0, `prereg/INDEX.md`, the P2 prereg (byte-identical to the staged file minus its header), `prereg/HASH_P2.txt`, the PREREG gate and `reports/gates/PREREG/` (7 files).
    - gate_check PREREG: ready. Commit and tag prereg-P2: ff119ca.
  - The `.claude/settings.json` deny rule `Edit(prereg/**)` was replaced by the seven entries the human gave (ledger ".claude/settings.json deny rule relaxed ...").
  - Machine restart at 04:32 UTC; S5 relaunched under the standing authorization.
- **Human decisions of 2026-11-23:**
  - GO with recommendations on round-2 findings 3, 4 and 6 (the message numbered them 1, 2, 3):
    - each rule is evaluated on the fits it uses;
    - nc = the smallest carrier count among complete, sufficient models, reused by sensitivity runs;
    - the first complete run per model is analysed, replaced only through a recorded deviation; deviation file names are timestamped.
  - The four definite fixes (round-2 findings 1, 2, 5, 7).
  - Then re-run all tests, including a forced fit failure, and run stats-reviewer round 3 in fresh context.
  - Round 3 is the last review before freezing:
    - BLOCKING only if a finding could change a decision (H1, H1-alt, the headline wording rules, or a model's inclusion);
    - everything else is NON-BLOCKING and goes to Limitations or a post-freeze fix list.
  - If round 3 has no BLOCKING findings: mark the prereg ready, set the status line to await GO for the PREREG gate, and stop. Otherwise stop and show only the BLOCKING findings.
- **Round-2 batch** (ledger "P2 round-2 batch (human GO 2026-11-23): applied"; `responses.md`). Tests (ledger "P2 round-2 batch: tests after the batch"):
  - MoM carrier-level test (new):
    - 20 replicates FAILED on frame variance (rel bias −0.23, Monte Carlo noise; 9 df per replicate);
    - 200 replicates PASS (all components within 0.05).
  - End-to-end v3: 44/44 pass (`results/P2fake_test_v3_20261123/`). It covers:
    - forced fit failures: output written; only the affected rules MISSING;
    - the nc rule;
    - `--primary`;
    - refusals.
  - Dry runs (10:19–10:21 UTC), all passed:
    - normal path;
    - fallback path, with timestamped deviations;
    - crash + second model + local nested SYNC_DEST: every sync ok (`results/P2dry/syncdest_listing_20261123T102036Z.txt`).

- **Human decisions of 2026-11-22 (third message):**
  - GO with recommendations on items 1, 2, 4, 5, 10, 11.
  - Null code written and frozen now; the p < 0.01 rule is kept.
  - The H1-alt MoM change is disclosed in the prereg.
  - Robustness simulation approved as non-selecting. It must not delay the freeze or the GPU run, and runs only when no other heavy job is running.
  - **S5 standing authorization:** after any restart, or if S5 is found dead, relaunch it with exactly `nohup setsid bash scripts/run_s5_cpu.sh >> results/s5_cpu.out 2>&1 < /dev/null &`, only when no other heavy job runs, and log each relaunch.
  - Plan: one batch, then re-test, then stats-reviewer round 2. If it passes, mark the prereg ready and stop at PREREG; on REVISE or BLOCK, stop and show the findings.
- **Machine restarts at 2026-11-22 15:19 UTC and 2026-11-23 09:48 UTC;** S5 relaunched under the standing authorization (ledger "S5 relaunch (HUMAN STANDING AUTHORIZATION 2026-11-22)"). After the 2026-11-23 relaunch S5 resumed pythia-2.8b step64000 at 9/21 chunks (its resume rewrote meta_shard0.json).
- **Batch applied** (ledger "P2 PREREG batch ..."). How each review item was applied: `reports/pending_frozen_changes/gate_reviews_P2/responses.md`.
- **Tests after the batch** (ledger "P2 PREREG batch: tests after the batch"):
  - MoM self-test: relative bias ≤ 0.013 on every component.
  - End-to-end synthetic test v2: 31/31 checks pass (`results/P2fake_test_v2_20261122/`; 19 min; peak RSS 561 MB; 1 core alongside S5). It covers:
    - MISSING (incomplete), including a pilot with a false "done" event;
    - MISSING (insufficient data);
    - fallback-1 nc = 2;
    - the planted carrier shift (0.05, recovered as 0.049);
    - families (pythia + llama);
    - the null, all 7 sensitivity sets, and the `--nc` guard.
  - Dry runs:
    - The first pair (15:58 UTC) exposed a bug in the new run_p2 `all_ok`: the manifest has 2 entries per chunk. The done-check failed correctly and wrote deviations.
    - After the fix, the second pair (16:00 UTC) passed: normal path with 0 deviations; fallback path with D-P2-1 and D-P2-2 written before the step. Done-check ok in both.
  - `completeness()` accepts the fixed dry-run dirs (nc 3 and 2) and rejects the 15:58 run.

- **Simulation v2 result (2026-11-22 14:37 UTC, `reports/p2/P2_bootsim_v2_report.md`; ledger "P2 CI-method simulation v2 report and selection"):**
  - Run: 1 h 36 min after the relaunch; peak RSS 340 MB; 240/240 ok; 0 failed refits.
  - Rule (a), 95% intervals: passes.
    - ICC1 coverage: 0.958 (edepthvar_like), 0.925 (fact_dominant).
    - diff coverage: 0.950 (edepthvar_like), 0.933 (fact_dominant).
    - Monte Carlo SE 0.018–0.024; |bias| ≤ 0.006.
  - Chosen: parametric bootMer with 95% percentile intervals. Written into section 4 of the staged prereg, with v1's failure and the second look disclosed.
- **GPU-script dry runs (2026-11-22 14:40 UTC, pythia-70m, CPU; ledger "EXPLORATORY P2 GPU-script dry run ..."), both exit 0:**
  - Normal path: `results/logs/p2_gpu_run_20261122T143942Z.log`.
    - pytest 2 passed; smoke ok; pilot chunk resumed by the full run.
    - done-check: checksums ok, 180 long rows, 0 NaN.
    - 56 s; peak RSS 892 MB.
  - Fallback path (BALANCE_INR=55, budget 0 min): D-P2-1 (2 carriers) and D-P2-2 (drop Llama) were written before the step.
    - 144 long rows: the pilot chunk has 3 carriers and the rest have 2.
    - `carriers_everywhere` returns 3 / 2 / 2 on these run dirs.
    - Test deviations are in `results/P2dry/deviations_test/`.
- **End-to-end synthetic test (2026-11-22 ~14:50 UTC; ledger "EXPLORATORY P2 end-to-end synthetic test ..."; `results/P2fake_test_20261122/`). Test only; not a result.**
  - Setup: two fake runs in the runner format (seeds 7 and 8). Run B has carrier 2 dropped after its 2-chunk pilot (fallback 1). `p2_analysis.py --set correct`, 20 parametric resamples.
  - Result:
    - n_carriers_used = 2; B's table has carriers 0–1 only.
    - All 8 REML fits ok: no singular fits, no warnings, 0 failed resamples.
    - REML and MoM agree in direction.
    - ICC1 (D1): 0.338 and 0.310; diff (D1): 0.241 and 0.301; bands "mixed".
    - Cross-model rho −0.10 (independent seeds).
  - Run: 59 s; peak RSS 518 MB.
- **PREREG gate reviews:**
  - Where they live:
    - Claude cannot write `reports/gates/PREREG/`: the deny rule `Edit(prereg/**)` also matches it.
    - The reviews and responses.md are therefore staged verbatim in `reports/pending_frozen_changes/gate_reviews_P2/`.
    - APPLY.sh copies them to `reports/gates/PREREG/`, runs `gate_check.py PREREG` and sets the status line.
  - citation-verifier:
    - Round 1 (fresh) returned REVISE.
    - Fixes:
      - Elhelo sentence reworded;
      - Section 8 says "does not reliably predict" and drops the unverified Meng mention;
      - "To our knowledge" hedge added, naming Elhelo and Agarwal as adjacent work.
    - Round 2 (fresh) returned PASS. Its label note was applied: the section 8 heading was renamed.
  - stats-reviewer, round 1 (fresh): REVISE. Saved verbatim as `stats-reviewer_round1.md`.
    - Blocking findings:
      1. MoM measures a different quantity.
      2. No carrier fixed effect.
      3. A partly run model is not marked MISSING.
      4. The multi-model claim rules are undefined.
      5. The shuffled-fact null and other sensitivities have no code.
    - Main claims checked in the code and confirmed. One-sided miss counts recomputed and confirmed.
    - `responses.md` answers all 20 findings:
      - DECIDE (human): 1, 2, 4, 5, 10, 11, each with a recommendation.
      - FIX (no hypothesis or threshold change): the rest, to be applied in one batch with the decisions.
      - Then: re-test, then a fresh stats-reviewer round 2.
  - APPLY.sh now refuses unless the status line reads "STATUS: AWAITING APPLY.sh, then GO PREREG". That line is set only when the prereg is ready.
- **Human decisions of 2026-11-22 (second message):**
  - CI method: option 2.
    - Plan `analysis/p2/bootsim_v2_plan.md` committed (875ba33) and logged as a SECOND LOOK before launch.
    - Simulation v2 (parametric only, 120 sims per condition, 500 replicates; 95% and 97.5% evaluated) running since 06:51 UTC under `results/P2sim_v2/`, with job checkpoints. About 6 h; slowed by sharing the CPU with S5.
      - Progress: 21/240 job files at 07:22 UTC; 83/240 at 08:57 UTC; 126/240 at 10:01 UTC; 160/240 at 10:57 UTC.
      - Worker restart at 13:00:49 UTC killed it at 163/240. Relaunched 13:01 UTC; it resumes from the job files. Next check-in 16:00 UTC.
  - **S5 DOWN since the 13:00 UTC restart** (needs the human):
    - pythia-2.8b step64000 has 7/21 chunks: `results/S5/S5-pythia-2.8b_step64000-02dca70-20261122T075405Z`.
    - The human's authorization covered one relaunch only.
    - Command: `nohup setsid bash scripts/run_s5_cpu.sh >> results/s5_cpu.out 2>&1 < /dev/null &`.
      - S5 finished pythia-2.8b step32000 and is on step64000 (ps, 08:57 UTC).
      - New job files appear while it runs and are committed periodically.
      - Check-in at 10:00 UTC (relaunch if dead).
  - Gate PREREG staged:
    - `reports/pending_frozen_changes/gates_PREREG.txt`.
    - APPLY.sh now also installs `prereg/P2_prompt_vs_fact.md`, `prereg/HASH_P2.txt` and tag prereg-P2. It refuses while the CI placeholder remains.
    - `hooks/proposed/pre-commit` allows those two files once (status A only).
  - S5 relaunched by human authorization at 06:52 UTC (ledger "S5 relaunch (HUMAN-AUTHORIZED)"). It resumed `results/S5/S5-pythia-2.8b_step32000-c894487-20261121T050945Z` with 18/21 chunks present.
  - Order after v2: GPU-script dry run, then the fake-run test, one heavy job at a time.
- **P2 A4 simulation result (2026-11-22, results/P2sim/p2_bootsim.json):**
  - Run: 60 sims × 2 conditions, 100 bootstrap replicates each; 1 h 09 min; peak RSS 300 MB; 0 errors; 0 singular fits.
  - Bias of the point estimator: within ±0.016 for every quantity (passes).
  - Two-way coverage:
    - edepthvar_like: ICC1 0.767, diff 0.733 (fails).
    - fact_dominant: ICC1 0.917, diff 0.900.
  - Parametric coverage:
    - edepthvar_like: ICC1 0.900, diff 0.883 (53/60; fails by one simulation).
    - fact_dominant: ICC1 0.950, diff 0.933.
  - Monte Carlo SE of a coverage near 0.90 at N = 60: 0.039.
  - The 7 parametric misses on diff (edepthvar_like): 4 above the truth, 3 below.
  - The 05:15 UTC check-in was deleted because the simulation had finished.

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
  - Done: A6 citation-verifier PASS (8/8 supported; `reports/gates/P2pre/citation-verifier.md`).
  - Pending: stats-reviewer on the prereg and simulation report.
  - Simulation restart: the first run was killed by a worker restart (seen 2026-11-22 03:43 UTC; nothing saved). It was relaunched at 03:44 UTC with per-job checkpoints (`results/P2sim/p2_bootsim.json.jobs/`), so it resumes after restarts. A check-in is scheduled for 05:15 UTC. Its log (`results/P2sim/p2_bootsim.out`) grows while it runs, so each stop sees an uncommitted change; it is committed periodically.
  - Also done:
    - `scripts/p2_gpu_run.sh` (budget auto-stop, fallback with pending deviations, done-check, rsync), dry-run on CPU.
    - `run_manifest.yaml` (experiment-planner RECOMMEND P2-B: INR 500 top-up, all five models).
    - Qwen3-8B has 36 layers and Llama-3.1-8B 32.
  - Human decisions of 2026-11-22, implemented (ledger "P2 decisions implemented"):
    - Top-up to INR ~740; all five models in one session; 199-minute budget; pilot gate kept.
      - `run_manifest.yaml` and `scripts/p2_gpu_run.sh` updated: the pilot is the first 20 facts of the first model with 3 carriers, then the session is projected. If needed, fallback 1 (2 carriers) and then fallback 2 (drop Llama), each with a pending deviation.
    - Sensitivity set `new226` (`materials/facts_v1_not_in_G1.json`) and the all-cells set.
    - ICC(1) description bands.
    - Formula-change reasons and the company_ceo disclosure added to the staged prereg.
    - The analysis uses carriers 0–1 for every model if any model fell back.
    - Not yet re-tested: driver dry run and fake-run test. These run after the simulation (one heavy job at a time).
  - Next:
    - When the simulation finishes: write the CI method into the staged prereg, or STOP if neither method meets coverage ≥ 0.90 with |bias| ≤ 0.05.
    - Re-run stats-reviewer.
    - Then the awaiting-GO status for the prereg install; the human runs APPLY.sh. Open problem: `gates.yaml` (frozen) has no gate named PREREG, so the stop hook rejects that status line. The human must add it or name the gate to use.

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
