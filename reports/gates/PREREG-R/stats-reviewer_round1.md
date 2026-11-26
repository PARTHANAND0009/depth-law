PREREG-R review of `/home/user/depth-law/reports/pending_frozen_changes/P2R/A_P2R_new_families.md` (read-only; the only thing I ran was p2r_combine.py on synthetic inputs in the scratchpad)

**Bottom line.** The wrapper really does run the frozen analysis. The problems are elsewhere: the four-family summary script crashes when both new models are MISSING; the summary's design is not disclosed fully enough; the wording rules leave some outcomes uncovered; and two statements in the amendment are not true as written. All of these are fixable before the freeze.

## Findings

### BLOCKING

**1. `p2r_combine.py` crashes if both P2R models are MISSING, and it reports the wrong G_ceiling when the two calls use different nc.**
- **Crash:** `p2r_combine.py:28` takes `nc = min(P2 nc, P2R nc)`. A P2R call with no included model writes `n_carriers_used = 0`, so `decide()` divides by zero at `analysis/p2/p2_analysis.py:414` (G_ceiling for Llama and OLMo).
  - Reproduced with `/tmp/claude-0/-home-user-depth-law/79d106ca-74b7-5e19-8ef3-6880f992c1ff/scratchpad/fake_p2r_missing.json`: `ZeroDivisionError`.
- **Wrong value:** if P2R falls back to nc = 2, the P2 models' G_ceiling is recomputed with nc = 2. Llama shows 0.937 instead of the frozen 0.957 (`results/P2analysis/correct/p2_decision.json`).
  - Reproduced with `/tmp/claude-0/-home-user-depth-law/79d106ca-74b7-5e19-8ef3-6880f992c1ff/scratchpad/out_fake_p2r_one_nc2.json`.
- `p2r_test.py` tests neither the MISSING case nor an nc mismatch.
- `combine()` checks only `set == "correct"`. It does not check `gating is True` or `test is False`, and it does not pin which P2 results file is used.
- **Decision impact:** a crash means no four-family summary in a realistic scenario (see the power section). The G_ceiling error affects a reported number only, not a rule.
- **Fix:**
  - Keep each call's own nc for per-model quantities: copy each model's G_ceiling from its own call's `p2_decision.json`, or call `decide()` per call and merge only the family counts.
  - Treat an nc of 0 as "no included models".
  - Refuse inputs that are not gating or are `--test` outputs.
  - Pin the sha256 of `results/P2analysis/correct/p2_results.json` in the amendment.
  - Add tests for: both MISSING, one MISSING, and nc 2 vs 3.

**2. The four-family summary (§5(b), line 54) is partly decided in advance, and for H1 it lowers the bar. Neither is disclosed. §5(d), line 62 ("No further correction") is wrong for the summary.**
- **"The fact share is above zero":** already licensed by Llama and OLMo (null p = 0.001 in both). The summary licenses it whatever P2R shows.
- **H1-dependent rules:** Llama already meets H1 with n′ = 8. So one new family meeting H1 licenses "H1 holds" and "A single prompt is a poor estimate…" in the summary.
  - Confirmed with the synthetic input above: Gemma included, Mistral MISSING → both sentences are licensed.
- **Error rate:** if H1 is false in both new models, the chance of a false summary licence is about 1 − 0.975² ≈ 0.05. P2's design figure was about 0.006.
- **Fix:**
  - State these facts explicitly in §0 and §5(b).
  - Rule that a sentence licensed only by (b) never appears in the abstract or a headline, and is reported only as a per-family tally: "k of 4 families; 2 seen before this amendment".
  - Correct §5(d).

**3. The wording rules in §5(c) (lines 56–60) do not cover every outcome. This leaves room to choose wording after seeing P2R data.**
- Not covered:
  - both models included and both fail the fact-share null;
  - one model MISSING while the other passes or fails;
  - the outcomes of H1, H1-alt and the other headline rules in the replication call;
  - what happens to the paper's existing P2 sentence if the replication fails.
- **Fix:** write an exhaustive outcome table now: {pass, fail, MISSING} × {pass, fail, MISSING} for each rule, with the exact sentence for each cell, including how the existing P2 sentence is then qualified.

**4. Two provenance statements are false or unsupported.**
- **Commit hash (line 21):** the amendment says the commit hash is "recorded … in each run's meta.json". It is not.
  - `run_p2.py:92` writes `provenance()` (`src/depthlaw/io.py:57-60`), which records `hf_revision: "main"` only.
  - `lm.weights` (the LFS sha256s of the weight files) is never written by `run_p2`.
  - Runbook step 8 prints the hash to the console only, not to a file.
- **"Stop if main moved" (line 21):** this is not automatic. Step 8 prints `MOVED` and relies on the human reading it, and "the human decides" is not prespecified.
- **Fix:**
  - In step 8, write a JSON file into the sync dir with `model_info().sha` and the weight-file LFS sha256s (`weight_files()` in `src/depthlaw/depth/common.py:38`), and correct the text of line 21.
  - Prespecify the rule: if only non-weight files changed (same LFS sha256), proceed; otherwise exit non-zero before the driver starts.

**5. The disclosure of what was done before the amendment is incomplete (review item 3).**
- **Third tokenizer:** a Mistral-7B-v0.3 tokenizer was loaded and is not mentioned.
  - HF cache `/root/.cache/huggingface/hub/models--mistralai--Mistral-7B-v0.3`, snapshot caa1feb…, created 2026-11-25 20:19:24Z alongside Gemma; v0.1 followed at 20:21:34Z.
  - Line 10 says Claude loaded "only their tokenizers", i.e. only the two chosen models'.
- **Tokenizer check was run outside the CPU memory rule:** `p2r_tokcheck.py` ran outside the ledger. Since the Gemma tokenizer fails at 1.8 GB, it must also have run above the standing CPU cap, while the background job was running. This breach is not disclosed.
- **Output not quoted:** line 36 says the tokenizer check output "is quoted" in `GATE_PREREG-R.md`. That report (line 27) gives a prose summary only, with no counts.
- **Overstated claim:** the check uses only paraphrase 0 of each relation (`p2r_tokcheck.py:19`), yet the amendment and gate report say it holds "for all 300 facts". It holds for 300 facts × 1 frame, not all 10 frames.
- **Fix:**
  - List every tokenizer and model loaded, with UTC times and results, and say why v0.1 was chosen over v0.3. If the reason is that v0.3 has no official knowledge-QA numbers, say so.
  - Disclose the cap breach.
  - Extend the check to all 10 paraphrases, re-run it through `log_run.py`, and quote the actual counts before installing.

### NON-BLOCKING

**6. The wrapper is faithful to the frozen analysis (review item 1).**
- `family()` and `main()` read `TOKMAP` and `PREREG_MODELS` when called, so the rebinding works.
- The R and MoM code has no model-specific constants or layer counts (searched).
- `decide()`, inclusion, nc, `n_boot`/`n_null`, materials and run-identity checks are the frozen ones.
- The substring family matching gives gemma2 and mistral correctly.
- Two minor points:
  - Covariates come from the CPU-cached tokenizers (`local_files_only`). Their snapshots match the pinned commits; record those snapshot hashes in the output.
  - With two families the conflict rule can never trigger, because H1 and H1-alt need opposite MoM signs within a model. State this.

**7. The exploratory scripts cannot run "unchanged" (§6, line 67).** `analysis/g5/g5_expl.py:31-32` hard-codes Llama and OLMo, L = 32, and the path `results/P2analysis/correct`; Gemma has 42 layers. **Fix:** write and hash the P2R variant (models, L, paths) before any data, and describe what was changed.

**8. Install script.** `APPLY_P2R.sh` does not check that `analysis/p2r/*` and the runbook are committed at the tag; they are only staged now. The runbook and the exploratory scripts are not in the `.sha256` file. If the code is missing at the tag, runbook step 6 fails on the paid GPU. **Fix:** add `git ls-files --error-unmatch` and `git diff --quiet HEAD --` checks, and hash the runbook too.

**9. Budget and GPU type: there is a real risk that the money runs out before Mistral finishes.**
- **Slower GPU:** P2 ran on an RTX PRO 6000 Blackwell; P2R plans an H100. In fp32 (no TF32) the H100 has roughly 67 TFLOPS (SXM) or about 51 (PCIe), against roughly 120 for the Blackwell.
- **Timing estimate:** P2's measured times were Qwen 16.3, Llama 16.3 and OLMo 13.8 min (`results/logs/p2_gpu_run_20261124T162942Z.log`). Scaling by parameters × layers gives about 21 min (Gemma) and 13 min (Mistral) on the Blackwell, but about 35–45 and 22–30 min on an H100. The runbook's 60–70 min total is likely optimistic.
- **Driver projection (`scripts/p2_gpu_run.sh:113,122`):** Mistral is projected at Gemma's rate (relative factor defaults to 1.0), about 1.27× too high. This pushes toward the 2-carrier fallback.
- **Per-model checks inert:** the per-model upper estimates default to 0 (`:145-147`), so the per-model skip never fires. A short budget therefore ends with Mistral cut off by the hard stop: MISSING (incomplete).
- **Misleading deviation files:** the fallback-2 branch (`:134-136`) and the Llama access check (`:77-79`, `:93-95`) write "Llama-3.1-8B not run" deviations that mean nothing in P2R.
- **Fix:**
  - Rent the same GPU type as P2, or raise the budget.
  - Use `SKIP_ENV=1` in step 10, since the driver otherwise rebuilds the venv and reruns pip (`:70-72`).
  - State that "Llama not run" deviation files from the P2R session are no-ops.

**10. The two "independent" stops use the same mechanism.** Both the step-3 timer and the driver's stop (`:64`) are an OS `shutdown`. On a container-based rental, an OS shutdown may not stop billing, and the hard-stop path was never exercised (P2 prereg §10). **Fix:** in step 3, check that shutdown actually works, or use the provider's pause API; keep the manual dashboard stop as the rule.

**11. Raising the CPU memory cap to 3 GB (review item 6) risks the background job.**
- This machine has 16 GB of RAM, no swap, and about 4.1 GB available; the background S5 job (pythia-2.8b) is using 11.5 GB.
- The address-space cap applies per process and is inherited by each Rscript child (cores = 3). If memory runs out, the OOM killer would most likely kill the background job, which CLAUDE.md forbids touching.
- **Fix:**
  - First try staying under 1.8 GB with `RAYON_NUM_THREADS=1`, `TOKENIZERS_PARALLELISM=false` and `MALLOC_ARENA_MAX=2`.
  - If 3 GB is still needed, approve it only when no other heavy job is running, record peak memory in the ledger, and keep cores = 3.

**12. The rerun and second-session rule is open (§4, line 46).** **Fix:** prespecify that a model MISSING (incomplete) because of budget or a crash may be rerun once, in a second session, only if that is decided before anyone opens its partial chunks (they contain correct@1, which is outcome-relevant). A model MISSING for insufficient data is never rerun.

**13. Model choice (review item 4).**
- The rationale is legitimate: official sources only, and the two highest numbers.
- The candidate list is incomplete: InternLM2-7B, Phi-3-small, Falcon-7B, Baichuan2-7B and Yi-9B were not checked. The choice would probably not change.
- Using Qwen3's P2 inclusion failure to justify the knowledge-QA criterion is itself P2 data. That is acceptable, but say so plainly, and state the scope: high-knowledge base models.
- An S4 run of gemma-3-4b-pt started but produced no outputs (`results/S4/S4-gemma-3-4b-pt-c894487-20261121T051040Z/log.jsonl`, one start event). Disclose "no Gemma-family outputs seen".

**14. Gemma-2 attention may not match the trained model.** `load_lm` (`src/depthlaw/depth/common.py:106`) sets no attention implementation. Under transformers 5.22.1 the default may be sdpa, which may ignore Gemma-2's attention-logit softcapping; I could not verify this offline. **Fix:** check the default on the tiny-random Gemma2 config now, log it at the pilot, and disclose it as a limitation (the loader is frozen).

**15. "Paper unchanged until results" (§7) is not yet well defined.** The G5 item-4 edit to `paper/main.tex` is staged but not committed. **Fix:** commit it before the tag.

**16. H3 pairs across calls are dropped** (combine passes `{}`). Only Gemma–Mistral is reported. **Fix:** say whether the new-vs-old pairs (e.g. Gemma vs Llama) will be reported as estimates; the same facts make them computable from the long CSVs.

## Power and feasibility (review item 8)

These are judgement estimates, not computed results.

**Inclusion threshold:** ≥ 150 facts with ≥ 2 correct paraphrases, covering ≥ 15 relations. P2 counts: Llama 196 (TriviaQA 77.6), OLMo 205, Qwen3 125, Pythia 91 and 93.

| quantity | estimate | basis |
|---|---|---|
| P(Gemma-2-9B included) | about 0.85–0.9 | TriviaQA 76.6, close to Llama |
| P(Mistral-7B-v0.1 included), behaviour only | about 0.65–0.8 | TriviaQA 69.9; expected around 170–180 facts, a thin margin. Qwen3's failure shows benchmark accuracy is an imperfect predictor. |
| P(Mistral incomplete), session | about 0.1–0.2 | H100 fp32 speed (finding 9) |
| P(null p < 0.01), given inclusion | ≥ 0.95 per model | P2's null 99th percentiles were 0.034–0.043 (maxima 0.046–0.055), against observed ICC(1) of 0.31 and 0.42; the answer-identity refit still gave 0.19 and 0.21. A model fails only if its true fact share is below about 0.05. |
| P(primary target met in both new families) | about 0.5–0.65 | product of the above |
| P(at least one new model MISSING), making the replication inconclusive under the no-substitute rule | about 0.3–0.45 | product of the above |
| P(H1 in both new families) | about 0.2–0.3 | P2 found H1 in Llama only; OLMo missed on the D1 lower bound of −0.004 |

The main risk is a MISSING model, not low statistical power. If the human wants to lower that risk, one prespecified option is a third model in a fixed order, with the rule "the first two included families count", written before any data. That needs the human's agreement and more budget.

Note: my standing instructions also mention checking `results/HR_gate.md` against `prereg/HR_revised.md`. I did not do that, because your request replaced it.

VERDICT: REVISE
