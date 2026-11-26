PREREG-R round 6: stats-reviewer confirmation review of A_P2R_new_families revision 6. I edited no file and ran no analysis or model.

My instructions also asked me to compare results/*_gate.md with prereg/HR_revised.md. I did not do that, because your task replaced it (as in rounds 1–5).

**Bottom line:** all eleven round-5 findings (N1–N11) are fixed, two of them with small leftovers. Revision 6 adds one BLOCKING problem. The new "Nothing else" rule contradicts §5(b), so it is no longer settled whether, or where, the four-family summary the human asked for appears in the paper. That can be decided after the P2R data are seen. The fix is one added item in the L3 list. Seven further findings are NON-BLOCKING.

**Checked directly:**
- Amendment sha256 is `eb5747b60ffe…abc10d647`, as stated.
- The P2R scripts, the pin file and all four `results/P2R/*.json` files are unchanged since round 5: their hashes appear only in ledger lines 189–202, and there are no new entries.
- Frozen code (`scripts/p2_gpu_run.sh`, `src/depthlaw/depth/common.py`, `analysis/p2/p2_analysis.py`, `tests/`) has no change against tag `prereg-P2` apart from the new `tests/test_frozen_guard.py`.
- Every APPLY anchor (`APPLY_P2R.sh:31-44`) occurs exactly once in `paper/main.tex`.
- Section numbering: Results is §5.2 and L3 falls inside it.
- The step-8b tests read only "The capital of France/Japan" and a carrier from `configs/s3.yaml`, report pass or fail, and print no correctness or depth data on project materials. The driver's own pytest (`p2_gpu_run.sh:84`, `-k "identity or halfprob"`) needs only pythia-70m, which step 8 downloads, so it works offline.

**Abstract word count** (whitespace split, `main.tex:38-44`): 199 words. Removing the decision-study sentence (24 words) leaves 175.

| cell | S | total |
|---|---|---|
| R1 | 18 | 193 |
| R2 | 22 | 197 |
| R3 | 20 | 195 |
| R4 | 19 | 194 |
| R5 | 22 | 197 |
| R6 | 11 | 186 |

Every cell is at most 200 words and matches amendment `:63`.

## Round-5 findings
| # | status | evidence |
|---|---|---|
| N1 | FIXED | runbook `:54` (`HF_HUB_OFFLINE=1`; reads the snapshot that `set-ref` points to) |
| N2 | FIXED (wording error, see F7) | amendment `:80`(ii); APPLY `:44` |
| N3 | FIXED for placement | amendment `:65`; APPLY `:40-43`; edit (i) `:80`. The §6 scope is only partly fixed: see F3 |
| N4 | FIXED, but the new text contradicts §5(b): see F1 | `:81` |
| N5 | FIXED | `:50` (1−(1−0.12)² ≈ 0.23, so "about 0.2" holds) |
| N6 | FIXED | `:53` |
| N7 | FIXED (LaTeX problem, see F5) | `:78` |
| N8 | FIXED | amendment `:41`; runbook `:118` |
| N9 | FIXED (small gaps, see F2) | amendment `:35`; runbook `:67-78`, `:112`, `:117` |
| N10 | FIXED | APPLY `:19`, `:53` |
| N11 | FIXED | amendment `:20`; runbook `:117` |

## New findings
| # | class | where | finding | fix |
|---|---|---|---|---|
| F1 | **BLOCKING** | amendment `:51` (§5(b) rule), `:86` (§5(e)) vs `:65` (L3 item list) and `:81` ("Nothing else") | §5(b) requires the four-family summary in the results section as a tally, "k of 4 families (2 analysed before this amendment)". The new `:81` forbids any other P2R outcome text anywhere and says L3 holds only the items listed at `:65`, which do not include the tally. So whether the human-requested summary appears at all, and where, is left open. The authors could drop or keep it after seeing how it came out. Its placement is also unfixed: put anywhere in §5.2 other than L3, it would come before unscoped P2 sentences. The tally sentence is also not given exactly: it is unclear whether every rule is listed or only licensed ones, and what happens in R6. | Add to the L3 list at `:65`: "the four-family tally of 5(b): one fixed sentence per headline rule, '<rule sentence> (condition): k of 4 families (<families>; 2 analysed before this amendment)', for every rule and in every cell". |
| F2 | NON-BLOCKING | amendment `:29` vs `:35`; runbook `:90`, `:117`; amendment `:40`, `:53` | Step-8b rule gaps. (a) §3 still fixes `MODELS="google/gemma-2-9b mistralai/Mistral-7B-v0.1"` with "the pilot is Gemma's", but the runbook takes the model list from `~/p2r_models.txt`. (b) There is no rule for a model that runs although its `arch_test_*.txt` is missing or shows a failure: §3 says only that passing models are analysed. (c) The reason "it was not run" is defined as "the session stopped before it", and §4's rerun list does not name arch-test failure; only §3 does. (d) There is no rule against re-running the test loop after a failure. All of this happens before any data, from pass/fail only, so there is no outcome bias. One more point: a failure inside the hook code cannot be fixed under §4(2), which allows loading or device changes only, so such a model stays MISSING. | Change `:29` to "the models that pass the §3 tests, in this order". Add: "a model without a passing `arch_test` file is passed as `=none`, reason 'it was not run'; the test loop runs once per session". Add arch-test failure to the `:53` and `:40` definitions. |
| F3 | NON-BLOCKING | `main.tex:372`, `:298`; amendment `:78`, `:81` | L3 comes before §6. If the replication (a) licenses "it takes N paraphrases" (or the (b) tally counts it), the unedited `:372` "the preregistered sentence 'a single prompt is a poor estimate…' is not licensed (Table~\ref{tab:rules})" contradicts L3. `:81` forbids rewording it. The same tension applies, more weakly, to the `tab:rules` caption "Only the first sentence is licensed" at `:298`. | Make it a fixed edit in every cell: "…is not licensed in \llama{} and \olmo{} (Table~\ref{tab:rules})". |
| F4 | NON-BLOCKING | `main.tex:41` (L1, frozen verbatim), `:371`; `paper/models.tex`; amendment `:80`(i) | The model macros have no `\xspace`. The compiled `paper/main.pdf` already shows "Llama-3.1-8Band" in the abstract. Edit (i), "in \llama{} and \olmo" followed by " and on correct prompts", would render "OLMo-2-1124-7Band". L1 must stay verbatim (`:63`) and is untouchable until the gating call (`:94`), so this typo cannot be fixed later without a deviation. Edit (i) also calls `:371` a "Discussion sentence", but it is in §6, "What this implies for single-prompt depths". | Before the tag: fix `:41` (`\llama{} and`) and APPLY anchor `:31`; write edit (i) as "in \llama{} and \olmo{}"; correct the section name. |
| F5 | NON-BLOCKING | amendment `:78`, `:82`; `scripts/check_numbers.py:21-31`; `main.tex:9` | The fixed texts are not LaTeX-ready. In "lower 95% bound ≥ 0.4", the `%` comments out the rest of the line and `≥` is not defined under `inputenc` utf8. `check_numbers.py` flags 95, 0.5 and 0.4 here and "5.2" in "Section 5.2" as bare numbers. Making the text compile is a formatting choice after the data, with no change of content. "Section 5.2" is also hard-coded, so a G6 section change would make it wrong. | Give the LaTeX now: `\ptCiLevel\%`, `$\ge$`, the existing `\ptRule…` macros or `% allow-number`, and `\S\ref{sec:p2}` or a new label. |
| F6 | NON-BLOCKING | runbook `:67-78` | Step 8b loads each model in fp32 a second time (about 37 GB for Gemma), at about 1–3 minutes each, inside the INR 700 budget. That is acceptable. The only risk is a nondeterministic identity failure at atol 1e-4 (unlikely with eager attention and the same shapes), which would make a model MISSING before any data. | none needed |
| F7 | NON-BLOCKING | amendment `:80`(ii); `main.tex:139` | "(eight in \SOne and in the original \STwo models)" is inaccurate: Study 1's largest model is OLMo-2-1124-7B. Also, a Gemma that ran but was MISSING (too few correct answers) still leaves the text saying "at most eight". The rule is mechanical, so there is no bias. | Use "(at most eight in the original \STwo models, seven in \SOne)". |

Runbook, amendment and APPLY otherwise agree: the provenance file names, `set-ref`, offline loading, the sync paths, section E, the anchors and the hashed test outputs all match.

Files:
- /home/user/depth-law/reports/pending_frozen_changes/P2R/A_P2R_new_families.md
- /home/user/depth-law/reports/p2r/GPU_RUNBOOK_P2R.md
- /home/user/depth-law/reports/pending_frozen_changes/P2R/APPLY_P2R.sh
- /home/user/depth-law/paper/main.tex
- /home/user/depth-law/paper/models.tex
- /home/user/depth-law/paper/main.pdf
- /home/user/depth-law/scripts/check_numbers.py
- /home/user/depth-law/tests/test_depth.py
- /home/user/depth-law/tests/conftest.py
- /home/user/depth-law/scripts/p2_gpu_run.sh
- /home/user/depth-law/src/depthlaw/depth/common.py
- /home/user/depth-law/prereg/P2_prompt_vs_fact.md
- /home/user/depth-law/results/ledger.jsonl

VERDICT: REVISE
