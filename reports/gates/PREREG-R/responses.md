# PREREG-R responses (stats-reviewer round 1, `stats-reviewer_round1.md`, REVISE)

Revised: `reports/pending_frozen_changes/P2R/A_P2R_new_families.md` (revision 2), `analysis/p2r/p2r_combine.py`, `analysis/p2r/p2r_test.py` (16/16, ledger), `analysis/p2r/p2r_tokcheck.py` (all 10 frames; ledger; `results/P2R/tokcheck.json`), new `analysis/p2r/p2r_weights_check.py` and `materials/p2r_weights_pinned.json` (ledger), `reports/p2r/GPU_RUNBOOK_P2R.md`, `reports/pending_frozen_changes/P2R/APPLY_P2R.sh`. No P2R model has been run.

| # | sev | response |
|---|---|---|
| 1 | B | Fixed. `combine()` takes per-model quantities from each call's own `p2_decision.json` (own nc), computes family claims with the frozen `decide()` on the union and checks that its rule flags equal the per-call flags; an nc of 0 is handled; non-gating and `--test` inputs are refused; the P2 files are pinned by sha256 (in the code and in amendment §3). New tests: both MISSING, one MISSING, nc 3 vs 2, test input refused, real pinned P2 files. |
| 2 | B | Fixed. §0 and §5(b) state that the summary is partly decided in advance (fact share already licensed by Llama/OLMo; Llama already meets H1 with n′ = 8) and its higher error rate; rule: a sentence licensed only by (b) never appears in the abstract or a headline and is reported as a per-family tally. §5(e) corrected. |
| 3 | B | Fixed. §5(c) has an exhaustive 3 × 3 outcome table (PASS/FAIL/MISSING per family) with the exact sentence for every cell for the primary target, including how the existing P2 sentence is qualified, and the rule for all other headline rules (sentence only if both pass). |
| 4 | B | Fixed. Weight provenance: `p2r_weights_check.py pin` recorded the main commits and every safetensors LFS sha256 (`materials/p2r_weights_pinned.json`, ledger). On the instance `check` writes the observed values into the session files and exits non-zero on any weight change; the runbook does not start the driver after that. §1 now says `meta.json` records only `main`. |
| 5 | B | Fixed. §0 lists every tokenizer and model loaded with UTC times (including Mistral-7B-v0.3 and why it was not chosen, and the two random test models), discloses the first check's breach (outside the ledger, above the CPU cap, next to S5), and §3 quotes the ledger re-run on all 10 frames: 3000/3000 pairs agree for both tokenizers, 0 bare-space, 0 shared first tokens. |
| 6 | N | Stated in §5(a) (conflict rule cannot trigger with two families). Tokenizer snapshot hashes: the analysis loads the cached tokenizers; recording their snapshot hashes in the output is not added to the frozen code (noted). |
| 7 | N | Fixed by scope: the only preplanned EXPLORATORY P2R analysis is the answer-identity refit (`g5_expl_object.R`, generic, unchanged, hashed). Frame-pair and H4 analyses are not preplanned for P2R. |
| 8 | N | Fixed. `APPLY_P2R.sh` refuses unless every P2R file, the runbook, the pinned weights and the tokenizer-check output are committed and clean, and hashes them all into the `.sha256`. |
| 9 | N | Fixed. P2 ran on an RTX PRO 6000 (P2 log); the runbook now requires the same GPU type (no substitution without a deviation), uses `SKIP_ENV=1`, gives a projection scaled from P2's measured times, and states that "Llama not run" deviations from this session are no-ops. |
| 10 | N | Fixed in the runbook: both automatic stops are OS shutdowns; the first time one fires the human checks the dashboard and pauses by hand; the manual stop rule always applies. |
| 11 | N | Resolved without a cap change: with the tokenizer cached, the Gemma tokenizer loads under the standing 1.8 GB cap (the ledger re-run's peak RSS was 522 MB). No raise is requested. |
| 12 | N | Fixed. §4: a model MISSING (incomplete) may be rerun once, in a second session, only if decided and committed before anyone opens its partial chunks; MISSING (insufficient data) is never rerun. The runbook forbids opening partial chunks. |
| 13 | N | Fixed. §0 says Qwen3's P2 failure motivated the criterion (P2 data); §1 lists unchecked candidates and states the scope (high-knowledge base models); §0 discloses the empty gemma-3-4b-pt S4 run ("no Gemma-family outputs"). |
| 14 | N | Checked: transformers 5.22.1 defaults to `eager` for Gemma-2, which applies the softcapping (50.0), on a randomly initialised config. The runbook records the implementation and versions on the instance and pauses unless `eager`. |
| 15 | N | §7 now ties "paper unchanged" to the state committed at the tag. Committing is blocked until the human installs the pre-commit fix (`APPLY_precommit_fix.sh`); `APPLY_P2R.sh` refuses until the files are committed. |
| 16 | N | Fixed. §5(d): cross-call H3 pairs are not reported; only the Gemma–Mistral pair, per the frozen code. |
| Power | – | Noted in the gate report: the main risk is a MISSING model (about 0.3–0.45 by the reviewer's judgement), not statistical power. A third prespecified model in a fixed order would lower it; that needs the human's agreement and budget, and is offered as a decision. |

# Round 2 responses (`stats-reviewer_round2.md`, REVISE)

Revised: amendment revision 3, `analysis/p2r/p2r_weights_check.py` (pin / check-hub / check-cache) and re-pinned `materials/p2r_weights_pinned.json` (ledger), `analysis/p2r/p2r_combine.py`, `analysis/p2r/p2r_test.py` (all pass, ledger), `reports/p2r/GPU_RUNBOOK_P2R.md`, `reports/pending_frozen_changes/P2R/APPLY_P2R.sh`. Attention check logged (ledger NOTE). No P2R model has been run.

| # | sev | response |
|---|---|---|
| 1 | B | Fixed. Pins now cover every `*.safetensors` (LFS sha256) plus `config.json`, `generation_config.json`, `tokenizer.json`, `tokenizer.model`, `tokenizer_config.json`, `special_tokens_map.json` (blob id): Gemma 14 files, Mistral 8. Runbook: `check-hub && download`; then `check-cache` compares `refs/main` and the cache blob names of the downloaded files; step 10 is `export HF_HUB_OFFLINE=1` and `check-cache ... && driver`. Amendment §1/§4 and runbook D: a session without matching `weights_observed*.json` (empty `differences`) makes both models MISSING (not run). Local `check-cache --only-present` test OK (9 files, ledger). |
| 2 | B | Fixed. §5(c) names locations L1–L5 (abstract sentence, contribution 2, Study-2 results paragraph, Discussion paragraph, Conclusion first sentence) at the tag, gives the exact text and placement for every cell, keeps both qualifiers, lists five fixed MISSING reasons, keeps the abstract H1 clause scoped to P2 in every cell, and maps PASS/FAIL/MISSING to decision-file predicates (`None` or status ≠ ok = MISSING; an H1-dependent rule with H1 `None` = MISSING). |
| 3 | B | Fixed. §4: the P2R gating call runs exactly once, after all sessions have ended and the rerun decision is committed; no P2R analysis of any kind before that; the rerun decision is made from session logs only. |
| 4 | B | Fixed. §7: once a session has started, its §5(c) outcome is reported in every later version whatever the date; a Dec-20 submission without it carries a fixed Limitations sentence. |
| 5 | N | Fixed. §4: the rerun rule covers MISSING (not run, the session stopped before it); a code fix needs a committed deviation first and must leave P2 outputs unchanged (frozen pytest and pythia-70m smoke run). |
| 6 | N | Fixed. `combine()` compares each decision file's full `per_model` with `decide()` on its own results and nc; adds `families_per_rule`; cross-references corrected. Tests added (inconsistent decision file refused). |
| 7 | N | Fixed. `APPLY_P2R.sh` runs the test through `log_run.py`, commits with an explicit pathspec, and checks and hashes `paper/main.tex`, `appendix.tex`, `numbers.tex`. |
| 8 | N | Fixed. §1 cites `modeling_gemma2.py:352`; the check is logged as a ledger NOTE. |
| 9 | N | Fixed. §5(b): "wording shifts together" and H1-alt sentences need two new families; only "H1 holds" and "it takes N paraphrases" can be licensed by one. §2: `new226` runs as frozen and is only a 226-fact subset. |

# Round 3 responses (`stats-reviewer_round3.md`, REVISE)

Revised: amendment revision 4; `analysis/p2r/p2r_weights_check.py` (index files pinned; `check-cache` re-hashes bytes on disk) and re-pinned `materials/p2r_weights_pinned.json` (Gemma 15, Mistral 9 files; ledger); `results/P2R/cachecheck_test.json` (ledger, OK, 9 files; a scratch test with one altered byte under the correct blob name exits 1); runbook; `APPLY_precommit_fix.sh`.

| # | sev | response |
|---|---|---|
| N1 | B | Fixed. §5(c): the abstract gets a fixed short sentence S per cell (11–20 words) inserted after the P2 sentence, and the decision-study sentence is removed in **every** cell. Word count with real model names, whitespace-counted as at the tag: 186–195 for every cell (≤ 200). Reasons appear only outside the abstract. All other abstract sentences verbatim. |
| N2 | B | Fixed. No existing L1/L2/L4/L5 sentence is edited; the replication enters only as an added sentence (S or Lg), so EXPLORATORY clauses stay about Llama/OLMo. P2R refit results appear only in the L3 replication paragraph, labelled EXPLORATORY. |
| N3 | N | Fixed. Each other rule is decided on its own predicates in both new families, independently of the primary cell; licensed sentences go to L3 only. |
| N4 | N | Fixed. "All other abstract sentences stay verbatim", naming the fact-share-estimate sentence and the H1 clause. |
| N5 | N | Fixed. §1: absent or non-empty provenance files → both models `=none` with the fixed reason "its model files differed from the preregistered ones" or (new) "its model files could not be verified"; reasons are read, never chosen. |
| N6 | N | Fixed. §4: a gating call that writes no `p2_decision.json` is re-run with identical code, inputs and seed; all attempts logged; only the one that wrote the decision counts. |
| N7 | N | Fixed. Runbook step 3 writes RATE to `~/p2r_rate.txt`; step 10 reads it and the driver starts only if `B > 0` (`python3 -c "assert float('$B') > 0" && check-cache && driver`). |
| N8 | N | Fixed. Manual stop rule names `FILES CHANGED` and `DIFFERENT:`; section D requires `hub_observed.json` too. |
| N9 | N | Fixed. `*.safetensors.index.json` pinned; `check-cache` re-hashes the bytes on disk (sha256 / git blob sha1) in addition to blob names; amendment says loading itself is not hashed again. |
| N10 | N | Fixed. §4 code-fix procedure: deviation first; loading/device code only; frozen pytest and the driver's pythia-70m smoke command through the ledger with exit 0 and identical outputs between the code at `prereg-P2R` and the fix; new tag `prereg-P2R-fix1` with sha256 before the second session. |
| N11 | N | Fixed. `APPLY_precommit_fix.sh` commits with an explicit pathspec (pre-commit script and ledger only). |
| N12 | N | Fixed. §7 names the Limitations sentence as the only exception (G6 changes never touch L1–L5). |

# Round 4 responses (`stats-reviewer_round4.md`, REVISE)

Revised: amendment revision 5; `analysis/p2r/p2r_weights_check.py` (`check-hub` at the pinned commit; new `set-ref`); runbook (pinned-commit download, `set-ref`, section E for a second session); `APPLY_P2R.sh` (paper-state check). New ledger entries: `check-hub` test at the pinned commits (OK, 24 files, `results/P2R/hubcheck_test.json`), negative cache test (FILES CHANGED, exit 1, `results/P2R/cachecheck_negtest.json`), positive cache test re-run (OK, 9 files). `set-ref` tested on a scratch cache (writes refs/main; refuses when the pinned snapshot is absent; not logged, scratch only).

| # | sev | response |
|---|---|---|
| A | B | Fixed. S replaces the decision-study sentence as the abstract's **last** sentence; Lg is the **last** sentence of the Discussion paragraph and goes after the Conclusion's second sentence, before "Code, materials…"; Lg stays at the end of contribution 2. No unchanged P2 sentence follows an added sentence. |
| B | B | Fixed. FAIL is worded "the preregistered test did not show …" in every Lg and S (R2, R4, R5); the rule is stated in §5(c), citing P2 §6 (estimates reported as intermediate result in the L3 table). New S counts with real names: 186–197 words (≤ 200). |
| C | N | Fixed. Exact L3 sentences for H1 and H1-alt given; the four rules use their P2 §6 sentences, all with a fixed prefix. |
| D | N | Fixed. `check-hub` compares the file ids at the pinned commit (main recorded for information only); download uses `revision=<pinned commit>`; `set-ref` points refs/main at it for offline loading; `check-cache` unchanged. |
| E | N | Fixed. Negative test logged in the ledger; amendment cites the three test outputs. |
| F | N | Fixed. §5(d): P2R sensitivity sets in the appendix, per model, P2 format, license nothing. |
| G | N | Fixed. `APPLY_P2R.sh` asserts a 199-word abstract ending with the decision-study sentence and each anchor string exactly once; passes on the current paper. |
| H | N | Fixed. Every Lg carries "which includes answer-token identity"; every added sentence carries "on correctly answered prompts". |
| I | N | Fixed. Limitations sentence stays; one fixed sentence is added after it (R1–R5 and R6 variants). |
| J | N | Fixed. Runbook section E: second session at `prereg-P2R-fix1` (with the fix's sha256 check) or `prereg-P2R`, budget from the rerun note, only the named models, branch `p2r-gpu-session-2`. |

# Round 5 responses (`stats-reviewer_round5.md`, PASS; non-blocking findings fixed)

Round 5 passed. Its non-blocking findings were fixed in amendment revision 6, the runbook and `APPLY_P2R.sh`; a round-6 confirmation review covers the final text. No P2R model has been run.

| # | sev | response |
|---|---|---|
| N1 | N | Fixed. Runbook step 8: the attention check runs with `HF_HUB_OFFLINE=1` (reads the checked snapshot; cannot move refs/main). |
| N2 | N | Fixed. §5(c) "Two further fixed edits" (ii): the Limitations parameter sentence becomes "at most nine billion parameters (eight in \SOne and in the original \STwo models)" iff Gemma-2-9B is PASS or FAIL. Anchor added to the APPLY check. |
| N3 | N | Fixed. L3 paragraph placed immediately before `\subsection{Robustness simulation (non-selecting)}`; fixed edit (i): §6's "in our two models" becomes "in \llama{} and \olmo" in every cell. Both anchors (and "Agreement across models", "Decision study") added to the APPLY check, which passes on the current paper. |
| N4 | N | Fixed. §5(c) "Nothing else": no other P2R outcome text anywhere; L3 contains only the listed items; the appendix holds only the sensitivity tables. |
| N5 | N | Fixed. §5(b) states "at least about 0.05 (nominal) … possibly up to about 0.2", citing the simulated 0.050–0.120 single-measure pass rate. |
| N6 | N | Fixed. The qualifier rule applies to sentences that state a result; R6 and the Limitations sentences are named as stating none. |
| N7 | N | Fixed. H1-alt L3 sentence states the condition (point estimate ≥ 0.5, lower 95% bound ≥ 0.4, D1 and D4). |
| N8 | N | Fixed. §4 and runbook D: `check-cache --only-present` through the ledger right before the gating call; must be OK. |
| N9 | N | Fixed. Runbook step 8b runs the frozen `test_patching_identity`, `test_patching_changes_output` and `test_final_patch_last_layer_equals_source` on each new model via `DEPTHLAW_TEST_MODEL` (outputs synced); a failing model is not run (MISSING "it was not run", rerun-eligible); the driver runs only passing models; §3 states that no other validity check is applied after the data. |
| N10 | N | Fixed. `APPLY_P2R.sh` requires the three test outputs committed and hashes them. |
| N11 | N | Fixed. §1: a failed provenance check voids only the models run in that session. |

# Round 6 responses (`stats-reviewer_round6.md`, REVISE)

Revised: amendment revision 7; `APPLY_P2R.sh` (anchors, macro check, `paper/models.tex` committed and hashed); `paper/main.tex` (abstract: `\llama{} and`, a rendering fix with no change of words); `paper/models.tex` (two name macros, `\GemmaTwoNineB`, `\MistralSevenB`). Paper rebuilt: check_numbers ok, verify_bib ok, 14 pages, abstract still 199 words.

| # | sev | response |
|---|---|---|
| F1 | B | Fixed. The four-family tally is an L3 item in every cell (including R6): one table (rows: the five P2 §6 rules, H1, H1-alt; condition, families meeting it, k of four) introduced by one fixed sentence; no other sentence about the summary. |
| F2 | N | Fixed. §3 session: `MODELS=` the models that passed the patching tests, Gemma first; the test loop runs once per session; a failed or absent `arch_test` file → `=none`, "it was not run"; arch-test failure added to the §4 rerun list and to the reason definition in §5(c). |
| F3 | N | Fixed. Fixed edit (iii) in every cell: "is not licensed in \llama{} and \olmo{} (Table~\ref{tab:rules})" and the caption "Only the first sentence is licensed (\llama{} and \olmo{})." Anchors added to the APPLY check. |
| F4 | N | Fixed. Abstract `\llama{} and` (renders "Llama-3.1-8B and"); APPLY anchor updated; edit (i) written "in \llama{} and \olmo{}"; section named "What this implies for single-prompt depths". No other macro-spacing case in main.tex or appendix.tex (all other uses are followed by `{}`, punctuation, or `\xspace` macros). |
| F5 | N | Fixed. H1-alt sentence uses `$\ge$ \ptRuleAltIcc`, `\ptCiLevel\%`, `\ptRuleAltIccLo`; Limitations sentences use `Section~\ref{sec:p2}`; model names via the new macros; every number through `numbers.tex`. Stated as spelling rules only. |
| F6 | N | No change needed. |
| F7 | N | Fixed. "(at most eight in the original \STwo models, seven in \SOne)"; applies if Gemma-2-9B was run in a session (any status except "it was not run" or a model-file reason). |

# Round 7 (`stats-reviewer.md`, PASS)

No blocking findings. Non-blocking N1–N5 are not applied, so the PASS covers the exact text (amendment sha256 6e10c8f7…f7d17c). They are listed in `GATE_PREREG-R.md` section 6 as optional edits for the human at GO PREREG-R.

# GO PREREG-R (human, 2026-11-26)

Approved with all five optional edits N1–N5 (amendment revision 8: N2 fixed captions and item order in L3, N3 single tally format, N4 fixed edit (iv), N5 "nominal sizes"; runbook section D: N1). No other change after the round-7 PASS.
