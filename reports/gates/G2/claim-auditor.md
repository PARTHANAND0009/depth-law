<!-- claim-auditor subagent, fresh context, 2026-11-24, gate G2 (P2 results), on reports/p2/RESULTS.md (version at e7d21f4) against prereg/P2_prompt_vs_fact.md sections 3-6 and 10, results/P2analysis/correct/p2_decision.json and the ledger. Saved verbatim by the main session; not edited. -->
CLAIM AUDIT, Gate G2 (P2 results). Object: /home/user/depth-law/reports/p2/RESULTS.md. Checked against prereg/P2_prompt_vs_fact.md §3–6 and §10, results/P2analysis/correct/p2_decision.json, and the ledger.

Method notes:
- Bash was blocked by a frozen-path hook, so I did not run any script. I used Read and Grep only.
- Each number in §§3–5 of RESULTS.md that I compared matches p2_decision.json: ICC(1), diff, MoM diff, n′, ceiling, null p, H3 ρ, k̄, G(k̄) and the 0.463 disattenuated value.
- I did not re-check the sensitivity, lofo, share-of-variance or scale numbers against their JSON files.
- The ledger has RUN entries for the correct-set analysis call, the sensitivity calls (line 105 onward) and the generator `analysis/p2/p2_results_md.py` (line 119).
- The deviation file named in RESULTS.md line 3 exists: `/home/user/depth-law/prereg/deviations/D-P2-20261124T044034Z-0.md`.

## Headline-sentence check (item 1)

No sentence in RESULTS.md asserts an unlicensed §6 headline. The §4 table (lines 94–101) correctly shows every rule except `fact_share_gt0` as False. Nothing says "no fixed layer", "it takes N paraphrases", "wording shifts together" or "facts have a depth that frequency and relation do not explain".

Several places let a reader infer an unlicensed sentence, or leave a licensed one unqualified.

| line | sentence or row | rule it breaks | required change |
|---|---|---|---|
| 52, 58 | Bold "**H1** … **True**", and "H1 holds" for Llama only | §5/§6: H1 supports a claim only in ≥2 families, and only Llama has it. A bare "H1 holds" beside the sensitivities invites reading it as a wording-over-fact finding. | Reword to "H1 condition met in Llama only (1 of 2 included families); no H1-dependent sentence is licensed". Drop the bold from the True. |
| 54 | "n′ for G = 0.8 (D1) [CI]: 8 [6, 13] / 4 [3, 5]" | §4: n′ is estimation only. §6 licenses "it takes N paraphrases" only with H1 and n′ ≥ 8 in ≥2 families. Llama's 8 reads as support. | Add a note: "Estimation only (H2). Llama n′ = 8 does not license 'it takes N paraphrases'; the rule fails (single_prompt_poor = False)." |
| 54 | Same row | §4: n′ is for k paraphrases where all facts share the same k, and the G ceiling is reported next to it. | Mention that n′ assumes all facts have the same k, in the table note. |
| 56 | "(rt + frame) − (ft + e/nc), share of den: −0.323 / −0.168" | §6: the "wording shifts together" rule needs this > 0 and H1. It is negative in both models. | Add "negative in both models; the rule is not met". This also keeps the line from being read as supporting the fact-specific reading of H1-alt. |
| 59–61 | Wording split D1/D4 and "scale D1: SD in layers" rows | §4 reports shares and the combined residual. It does not preregister the split of ft/den versus (rt+frame)/den, or SD in layers. These rows also contain unescaped pipes, so the markdown table is malformed. | Label these rows EXPLORATORY (not preregistered). Fix the pipes. Do not interpret the split. |
| 43, 48 | "ICC(1) band D1: moderately fact-stable" (OLMo) | §5: bands describe the point estimate together with its CI. OLMo's CI [0.347, 0.487] straddles the 0.4 cut-off between "mixed" and "moderately fact-stable". "Fact-stable" wording also echoes H1-alt, which fails. | Add "descriptive band, not a decision rule; CI spans 'mixed' and 'moderately fact-stable'; H1-alt fails in both models". |
| 66–76 | Share of total variance table (relation included) | §4: this is preregistered, so ok. The "fact" share of 0.285 / 0.368 is not the primary fact share. | Say "not ICC(1); relation included". |
| 78–87 | Secondary outcomes D2, D3: the diff CIs exclude 0 in both models | §2 and §5: D2/D3 carry no hypothesis, and censored rows are dropped from their fits. The row counts (3564 vs 3663) already show the drop, but the text does not. | Add "secondary, descriptive; no H1 evaluated; censored D2/D3 rows dropped (row counts differ)". |
| 101 | fact_share_gt0 = True; null p = 0.001 | §4: the null is accepted at p < 0.01. 0.001 is the floor of 1000 simulations, 1/1001, and this is the one licensed sentence. The calibration caveats are missing from this report: the test is mildly liberal at fc = 1 (0.020 at p < 0.01), it has power 0.46 at fact share 0.10, and it is conditional on the covariates. | Report p as "≤ 0.001 (floor of 1000 null datasets)". State the licensed sentence verbatim: "The fact share is above zero (parametric null p < 0.01 in 2 of 2 included families)". Add the §10 caveats. Say that this sentence does not imply that the fact share is large or fixed. |
| 94–100 | The False rows | A False here means "not licensed". It does not mean the opposite claim is shown (for example, "no fixed layer = False" is not "a fixed layer exists"). | Add one sentence saying this, plus "otherwise: report shares and n′ as an intermediate result (§6)". |
| 118–129 | Sensitivity table with H1 and H1-alt columns | The preamble at line 116 disclaims them. But the table shows H1 = True for both families in new226, all and nomanufacturer, a pattern a reader will read as "H1 holds in ≥2 families" (§3: a sensitivity cannot establish or rescue a claim). | Drop the H1 and H1-alt columns, or relabel them "flag (non-gating; not evidence)". Add a sentence that the confirmatory H1 is met in only 1 family. |
| 124–125 | all10 rows | Llama has 14 facts and OLMo 30. | State the tiny N and that the intervals are very wide. Singular fit in Llama D1. |
| 131–138 | lofo | Point estimates only, as the prereg specifies. No problem. | None. |
| 140 | H4 labelled EXPLORATORY, points to `fixef`, the second part MISSING | Compliant. | None. |

## Traceability and MISSING (item 2)

| line | issue | required change |
|---|---|---|
| 148 | "INR about 354 (human figure; approximate)". This is not in any results file. It is only in PROGRESS.md line 36 and a ledger note. | Keep "MISSING" or mark it as not from results/. CLAUDE.md rule 1 says every reported number must be read from results/. Better to remove it from the results report. |
| 5 | "D1–D4 are read from p(object first token)". D3 is a rank-1 onset, read from the stored rank (§2). | Change to "D1, D2 and D4 from p; D3 from rank". |
| 3, 7–23 | Provenance is complete: run_ids, manifest sha prefixes and ledger RUNs. | ok |
| 30–34, 142–147 | MISSING items are marked correctly. Qwen3 and both Pythia are MISSING (insufficient data). | ok |
| 146 | The robustness simulation is MISSING and flagged as non-selecting. | ok |
| 64 | The p_final = 0 count covers all curves "before the inclusion set". This matches prereg §2. | ok |
| 113 | H3 is labelled "estimation only", with caveats and no CI. This matches §5. Add "D1, correct set". | Minor. |
| 3 | The sentence "all other sets are preregistered sensitivities (not gating)" is right. | ok |

## Descriptive and estimation-only status (item 3)

- H3 is correctly labelled estimation only.
- Bands, n′ and the sensitivities are only partly labelled. Bands and n′ are shown in the table with no "descriptive / not a test" status (see the rows above). The sensitivity disclaimer (line 116) is present but undercut by the flag columns.
- The `diff` CIs and the "H1 status in words" row make the primary results read like tests. State in the §3 header that H1 and H1-alt are the preregistered conditions, and that only §4 decides claims.

## Measurement description and caveats (item 4)

The description at line 5 matches prereg §1: final-token residual patched into the carriers' final token. The added note that the subject position is not patched is accurate and helpful.

Understated or missing relative to prereg §§3–4 and 10:
- Scope.
  - Only 2 families are included: Llama-3.1-8B and OLMo-2-7B. Qwen3 and Pythia are MISSING.
  - Every claim therefore needs both remaining families.
  - Nothing generalises beyond these two models.
- Correct-only scope.
  - Depth is defined only for facts the model answers correctly: cells where top-1 equals the object's first token, and only facts with ≥2 correct paraphrases enter the inclusion rule.
  - The report never says this in a caveat. "Set `correct`" is not explained.
  - The selection caveat (§3, MNAR) is also absent.
- ICC(1) is conditional on the four covariates (the frequency proxy, lengths and answer prior) and on the carrier fixed effect. It is not comparable with the G1 values.
- The wording share describes variation over these 10 designed frames only (9 df).
- The frequency proxy is a DCLM PROXY count.
- The CI method was chosen on simplified simulations, with coverage 0.925 in one condition.
- MoM diff differs from REML diff by (e − fc)/(nc·den). It is a direction check only.
- Nothing about frequency is tested in P2. Do not let any wording imply that frequency "does not matter".

Required change: add a Limitations block that restates the §10 caveats briefly.

No banned words found in RESULTS.md. I did not run the paper checker (no paper exists).

## Verdict reasoning

- No unlicensed headline is asserted, and the licensed sentence ("The fact share is above zero") is supported by the decision file.
- Nothing is fabricated, and all preregistered quantities are present: H1, H1-alt, n′, the null, H3, the sensitivities, lofo and H4.
- Fixable wording issues remain.
  - The sensitivity H1 flags and the "H1 holds" label risk inference.
  - The D3 description is wrong.
  - The INR figure has no results file.
  - The variance-split rows are unlabelled and mis-formatted.
  - The caveats on correct-only scope and the null are missing.

VERDICT: REVISE
