<!-- stats-reviewer subagent, fresh context, 2026-11-24, gate G2 (P2 results). Scope: P2 only, as instructed by the launching agent. No repo file was edited. -->
# G2 stats-reviewer report: P2 (prompt vs fact)

**Bottom line:** the gating analysis was run as preregistered, and every decision in `p2_decision.json` follows the frozen rules. Nothing I found changes a gating decision or the one licensed headline ("the fact share is above zero"). `RESULTS.md` needs fixes before G2:
- one preregistered item is neither reported nor marked MISSING;
- one preregistered sensitivity is reported incompletely;
- some fit diagnostics are missing;
- the OLMo H1 non-result and H3 need interpretive caveats.

## What I verified (no finding)
**Prereg integrity**
- sha256 of `prereg/P2_prompt_vs_fact.md` = 493b2c3c…4662f, matching `prereg/HASH_P2.txt`.
- Tag `prereg-P2` = ff119ca.
- `git diff prereg-P2 HEAD -- prereg materials` shows only the added deviation file.

**Frozen code**
- `git diff prereg-P2 HEAD -- analysis/p2 src scripts/p2_gpu_run.sh scripts/p2_done_check.py` shows one change: the new, non-frozen `analysis/p2/p2_results_md.py`.
- The ledger input sha256 of `p2_analysis.py` (98653d9c…) equals `git show prereg-P2:analysis/p2/p2_analysis.py`.
- The working copies of the `.R` files and `p2_mom.py` have mtimes from 2026-11-21 to 2026-11-23, all before the freeze at 2026-11-24 04:35. So the dirty-tree runs used the frozen versions, but see finding 12.

**Gating call** (ledger line 107)
- Five `--runs`, exactly the prereg models.
- `--n-boot 1000 --n-perm 1000`, seed 20261121, `--set correct`, no `--primary`.
- nc = 3, written to `p2_results.json`.
- Run identity and completeness were enforced in code (`p2_analysis.py:308-320`). The replicator checked them independently.

**Sensitivity calls**
- All six non-gating sets and h4 pass `--primary results/P2analysis/correct` with identical `--runs`.
- They reuse nc = 3 (`p2_analysis.py:286-294`, `:321-324`).
- Their outputs are `gating: false`.

**H4 labelling**
- Ledger tag is "EXPLORATORY P2 analysis: set h4 (H4)", with status EXPLORATORY.
- RESULTS.md:3 and :123 label it EXPLORATORY.

**Operational changes cannot change any number**
- `--cores 3 → 4` only affects scheduling. `bootMer` draws all nsim responses up front with `simulate()` in the master process after `set.seed(20261121)` (`p2_analysis.R:35-37`; checked in the deparsed lme4 1.1.35.1 `bootMer`), then fits them with `mclapply`.
- The null also simulates first (`simulate(m0, nsim, seed=seed)`, `p2_null_fns.R:23`), then refits with `mclapply`.
- Relaunches skip only sets whose `p2_decision.json` exists, and rerun an interrupted set from scratch with the same seed.
- `correct` ran once (ledger 107). The ledger has no other real-data gating call.

**GPU session**
- 5/5 models complete with 3 carriers, no fallback, 0 session deviations.
- `D-P2-20261124T044034Z-0.md` was committed at 15:55Z, before the session started at 16:29Z. It changes only the off-instance copy mechanism.
- The driver's budget input (161 min, from INR 610.12) is lower than the prereg's "about 199". It was never binding: 58 min were used.

**Rule implementation** (`p2_analysis.py:398-466`) matches prereg §4–§6:
- the per-rule input dependencies;
- MoM MISSING when its raw denominator is ≤ 0 (`p2_mom.py:64-68`);
- the conflict rule voiding only the H1/H1-alt-dependent sentences;
- Pythia 1.4b/2.8b counted as one family (`TOKMAP`).

## Findings

### 1. The preregistered robustness simulation was never run and is not reported or marked MISSING
**Severity: should-fix.**
- **What the prereg requires:** prereg §4 (lines 191-197) requires a non-selecting robustness simulation "reported next to the results". It covers:
  - discretised D1;
  - correctness-linked missingness;
  - a carrier shift;
  - truths near ICC(1) 0.4–0.5 and diff ≈ 0.
- **What exists:** no code, no output and no ledger entry. The only mention is PROGRESS.md:79. RESULTS.md §7 (lines 125-129) does not list it.
- **Why it matters:** this is exactly the regime of OLMo's D1 diff (finding 6).
- **Could it change a decision?** No: the prereg says it cannot change the CI method or any decision.
- **Fix:** list it as "MISSING: not run", or run it with code committed first, and report it.

### 2. The `lofo` sensitivity is reported incompletely
**Severity: should-fix.**
- Prereg §3 (line 95) defines lofo as point estimates of ICC(1), diff and MoM diff, for D1 **and** D4.
- RESULTS.md:118-121 (generator `p2_results_md.py:154-173`) omits ICC(1) D4 and MoM diff D4. Both are present in `results/P2analysis/lofo/p2_results.json`.
- My read of that file, for orientation only (the generator must emit these, not this review):
  - Llama: ICC(1) D4 0.250–0.310, MoM diff D4 0.360–0.462;
  - OLMo: ICC(1) D4 0.356–0.414, MoM diff D4 0.201–0.296.
- **Could it change a decision?** No (non-gating).

### 3. Singular fits and convergence warnings in the sensitivity sets are not reported
**Severity: should-fix.**
- Prereg §4 (line 148): "singular fits and convergence warnings are reported".
- RESULTS.md reports them for `correct` only (line 56). The sensitivity table (lines 103-114) omits these:
  - convergence warnings "max|grad| = 0.00317 / 0.00295 (tol 0.002)" in Llama D4 for `new226` and for `all`;
  - singular fits (frame variance 0) in OLMo D1 `all` and Llama D1 `all10`.
- **Could it change a decision?** No (non-gating; the rules ignore singularity).

### 4. `RESULTS.md` does not say that the H4 cross-family comparison is MISSING
**Severity: note.**
- Prereg §5 (lines 258-260) has a second H4 part: is the wording share larger in Qwen3/Llama/OLMo than in Pythia?
- Both Pythia models and Qwen3 are MISSING, so this part cannot be evaluated. RESULTS.md:123 and §7 do not say so.
- **Could it change a decision?** No (EXPLORATORY).

### 5. The decisions follow the prereg as written
**Severity: note (confirmation).**

**Inclusion.** Qwen3 (125 facts with ≥ 2 correct paraphrases), pythia-1.4b (91) and pythia-2.8b (93) are all below 150. They are MISSING (insufficient data) for every set, which is correct under §3. The replicator reproduced the counts.

**H1 per model**
- Llama is True: diff lower bounds are 0.220 (D1) and 0.259 (D4); MoM diffs are 0.392 and 0.406.
- OLMo is False: the D1 diff CI is [−0.004, 0.272]. Its D4 and MoM conditions pass.

**H1-alt** is False in both models: ICC(1) < 0.5 for D1 and D4.

**Family-level claims**
- H1 holds in {llama31} only, so H1 and every H1-dependent sentence are False.
- H1-alt holds in no family, so the conflict rule is not triggered and "model-dependent" is False.
- "No fixed layer" is False: the ICC(1) D1 upper bounds are 0.370 and 0.487.

**Null.** p = 1/1001 in both models, with 0 failed refits, so "fact share > 0" is True in 2 families.

**H3** is computed on 190 common facts.

All of these match prereg §3–§6 and the per-rule dependencies of §4.

### 6. OLMo's H1 failure is a boundary non-rejection within bootstrap Monte Carlo error
**Severity: should-fix (interpretation).**
- **How big the Monte Carlo error is:** with B = 1000, the 2.5% percentile has an approximate Monte Carlo SE of sqrt(0.025·0.975/1000)/φ(1.96) × SD_boot. With SD_boot ≈ (0.272 + 0.004)/3.92 ≈ 0.070, that gives about **0.006**. This is my approximation; the bootstrap draws were not saved.
  - The lower bound of −0.004 is therefore about 0.7 Monte Carlo SE below 0.
  - Another seed would give a positive bound with probability on the order of 25%.
- **What a flip would change:**
  - OLMo H1 would become True, and "H1 holds in ≥ 2 families" (§5) would become True.
  - No §6 headline sentence would change: OLMo's n′ = 4 < 8, and tf − resid < 0 in both models.
- **What the rest of the evidence says:** every other indicator points toward wording > fact in OLMo:
  - the D1 and D4 point estimates (0.124, 0.239);
  - both MoM diffs;
  - all 10 lofo drops (diff D1 0.037–0.150);
  - every sensitivity point estimate.
- **The recorded decision stands.** The seed and B are preregistered, and a rerun with another seed would be a forking path. It must not be done.
- **Required wording for the gate report:** OLMo's result is "H1 not established (CI lower bound −0.004)". It is not evidence for fact dominance or for between-model heterogeneity, and the family-level H1 = False is fragile to Monte Carlo error.
- **Could it change a decision?** It could change the §5 family-level H1 status under a different seed. It cannot change any §6 headline.

### 7. Every family-level claim rests on exactly two models, chosen by a behaviour-dependent rule
**Severity: note.**
- **Two included models make every claim unanimous:** with only Llama-3.1-8B and OLMo-2-7B included, "≥ 2 families" means both models must agree.
- **The Pythia family is entirely absent.** The included models are the two that know the most facts, so every result is conditional on high-knowledge 7–8B models.
- **The false-claim estimate no longer applies:** the prereg's rough false-claim estimate (~0.006, §4 line 229) assumed 5 models. It does not describe this configuration.
- **Effect on the one True claim:** it is robust (finding 9).
- **What the gate report should say:** scope any statement to these two models.
- **Could it change a decision?** No.

### 8. Selection on correctness (MNAR) and the disagreeing sensitivities do not undermine the gating result
**Severity: note.**

**Size of the selection.** Correct cells are 1221/3000 (Llama) and 1355/3000 (OLMo). Facts with a single correct paraphrase are kept. That follows the prereg; the ≥ 2 threshold is a model-inclusion rule only.

**OLMo H1 by sensitivity set**
- It holds in `new226`, `all` and `nomanufacturer`, and fails in `correct`, `tcov` and `all10`.
- These failures do not show that selection drives the result:
  - `tcov` adds template covariates that remove wording variance by construction (prereg §4, line 105), so a lower diff there is expected.
  - `all10` has 14 (Llama) and 30 (OLMo) facts. Its CIs span about 0.6, and one fit is singular, so it is uninformative.
  - `all` includes incorrect cells, where D1 is measured relative to a tiny final p. 369 and 372 curves have p_final < 1e-4, where the float16 threshold is coarse. Its estimand therefore differs.

**Direction of the evidence**
- H1-alt fails in every set.
- The ICC(1) point estimates (0.23–0.44) never approach 0.5.
- So no sensitivity suggests that selection hides fact dominance.
- The `new226` result for OLMo (H1 True without the 74 G1-overlap facts) is noted but not interpretable as preregistered.

**Could it change a decision?** No: sensitivities are non-gating.

### 9. The null's mild liberalness is immaterial here
**Severity: note.**
- Observed ICC(1) is 0.310 (Llama) and 0.422 (OLMo).
- The null maximum over 1000 datasets is 0.055 and 0.046; the null 99th percentiles are 0.043 and 0.034.
- p sits at its floor, 1/1001.
- A size inflation of 0.020 vs 0.010 (prereg §4, line 221; §10, line 338) cannot matter at a margin of more than 5× the null maximum.
- **Could it change a decision?** No.

### 10. H3 is an approximate point estimate with known biases and no uncertainty; the replicator's ambiguity is real
**Severity: should-fix (caveats).**

**a. Which k̄ is used.** k̄ is computed over each model's full included fact set (`p2_analysis.py:367`): 5.50 and 6.19. ρ is computed on the 190 common facts, where k̄ is 5.86 and 6.67 (my computation from `long_*_correct.csv`). The prereg wording ("mean number of correct paraphrases per fact in that model") allows either reading. The code's reading gives a slightly larger correction.

**b. Bias in the disattenuation.**
- G(k) assumes the same k paraphrases for every fact. In the correct set, each fact mean averages a different paraphrase subset, of size 1–10.
- As a result:
  - frame and rt variance enter the fact-mean error;
  - G is concave in k (Jensen).
- G(k̄) therefore overstates the reliability of the fact means, and the disattenuated 0.463 is under-corrected.

**c. Scale mismatch.** ρ pools across relations, but G is a within-relation quantity.
- Reviewer scratch computation (EXPLORATORY; not a logged run; not for RESULTS or the paper): the relation-demeaned ρ is 0.33, and the ρ of relation means over 20 relations is 0.19.

**d. No interval.** None was preregistered.
- Reviewer scratch percentile bootstraps (EXPLORATORY, same status as above): about [0.23, 0.50] when resampling facts, and about [0.16, 0.56] when resampling relations.

**e. The replicator's ambiguity.** Restricting to facts with ≥ 2 correct paraphrases gives ρ = 0.456 (N = 169) instead of 0.373.
- The implemented reading is literal and defensible.
- The gap is consistent with attenuation from single-paraphrase facts.
- Any restricted figure must be labelled EXPLORATORY.

**Fix.** RESULTS.md:97-100 should state (a) and (b) as caveats and say that no CI was preregistered.

**Could it change a decision?** No: H3 is estimation only.

### 11. Sensitivity rows show per-model H1 = True, and their non-gating decision files compute "H1 holds in ≥ 2 families" = True
**Severity: should-fix (wording).**
- The non-gating `p2_decision.json` files for `new226`, `all` and `nomanufacturer` compute `"H1_holds_(>=2_families)": true` (also visible in `results/P2analysis/run.out`).
- RESULTS.md:103-114 shows per-model H1 = True for both models in those sets.
- None of this licenses a claim (prereg §3, line 88). RESULTS.md:3 says only `correct` is gating, but §6 should state outright that sensitivity H1/H1-alt flags are descriptive and cannot establish or rescue a claim.
- **Could it change a decision?** No, unless it is misused.

### 12. Run labels and logging
**Severity: note.**
- **a. Ledger status labels.** `scripts/p2_run_analysis.sh:32` logs the six non-gating sensitivity runs with status `CONFIRMATORY` (ledger lines 111-116). The RESULTS.md generation is also logged as CONFIRMATORY (line 119). The prereg calls these sets "preregistered sensitivities, not gating". Suggest an appended ledger NOTE clarifying this, because the ledger is append-only.
- **b. Exit codes in `run.out`.** `scripts/p2_run_analysis.sh:28` prints `exit $?` after a `$(date …)` substitution, so it always prints 0. I tested this in bash. The real exit codes are in the ledger (all 0).
- **c. Unhashed analysis files.** The ledger hashes only `p2_analysis.py`, not the `.R` files or `p2_mom.py`. Integrity of those rests on mtimes plus the clean `git diff`. Hash all frozen analysis inputs next time.
- **d. H4 directory name.** The H4 output directory `results/P2analysis/h4/` has no EXPLORATORY in its name. H4 is preregistered as exploratory, so the CLAUDE.md filename rule may not strictly apply.
- **Could any of these change a decision?** No.

### 13. Is anything in `RESULTS.md` not permitted?
**Severity: note.**

**Nothing states a headline beyond the licensed one.** The only §6 sentence licensed is "The fact share is above zero" (line 95). Everything else is correctly an intermediate result.

**Two places need care in the gate report:**
- Line 41, the OLMo D1 band "moderately fact-stable". Its CI [0.347, 0.487] spans the 0.4 band edge, and D4 is "mixed" (line 46). Bands are descriptive (§5), so state the CI next to the band.
- Line 52, Llama's n′ = 8 [6, 13]. It must not be turned into "it takes 8 paraphrases": that needs 2 families.

**Could it change a decision?** No.

## Severity summary
- **Blocking:** none.
- **Should-fix:** 1, 2, 3, 6, 10, 11. All are reporting or interpretation fixes in `reports/p2/RESULTS.md`, `analysis/p2/p2_results_md.py` and the G2 gate text.
- **Note:** 4, 5, 7, 8, 9, 12, 13.

**Files referenced:**
- `/home/user/depth-law/prereg/P2_prompt_vs_fact.md`
- `/home/user/depth-law/prereg/HASH_P2.txt`
- `/home/user/depth-law/prereg/deviations/D-P2-20261124T044034Z-0.md`
- `/home/user/depth-law/reports/p2/RESULTS.md`
- `/home/user/depth-law/analysis/p2/p2_results_md.py`
- `/home/user/depth-law/analysis/p2/p2_analysis.py`
- `/home/user/depth-law/analysis/p2/p2_analysis.R`
- `/home/user/depth-law/analysis/p2/p2_null_fns.R`
- `/home/user/depth-law/analysis/p2/p2_mom.py`
- `/home/user/depth-law/scripts/p2_run_analysis.sh`
- `/home/user/depth-law/results/P2analysis/{correct,lofo,new226,all,all10,tcov}/`
- `/home/user/depth-law/results/P2analysis/run.out`
- `/home/user/depth-law/results/ledger.jsonl` (lines 104-119)
- `/home/user/depth-law/results/logs/p2_gpu_run_20261124T162942Z.log`
- `/home/user/depth-law/reports/gates/G2/replicator.md`

VERDICT: REVISE
