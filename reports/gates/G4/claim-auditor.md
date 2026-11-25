<!-- claim-auditor subagent, fresh context, 2026-11-25, gate G4 (paper setup), on claims/claims.md and reports/paper/titles_abstract.md (versions at commit 21692bb). Saved verbatim by the main session; not edited. -->
G4 claim audit (read-only). Objects: /home/user/depth-law/claims/claims.md and /home/user/depth-law/reports/paper/titles_abstract.md.

## 0. Script output
`python3 scripts/check_numbers.py` printed: `check_numbers: ok`. The first two Bash calls were refused by a hook ("shell write touching a frozen path"). A later identical call ran and returned ok. The script confirms the macro file is consistent with its sources. I did not rely on it alone (section 2).

## 1. Findings
Severity: B = BLOCKING (fix before GO G4 and before any paper text), N = non-blocking. Location is claims.md section or the abstract/titles file. Sentence quotes are abbreviated.

| # | Sev | Location | Sentence | Rule broken | Required change |
|---|---|---|---|---|---|
| A1 | B | Abstract | "…but wording exceeded the fact share in only one model." | Misstates the macros. Wording share is larger than the fact share in both models by point estimate: D1 `\ptWordingDOneLlama` 0.649 vs `\ptIccDOneLlama` 0.310, and `\ptWordingDOneOlmo` 0.546 vs `\ptIccDOneOlmo` 0.422. What differs is the preregistered H1 condition. It needs the D1 and D4 CIs of diff to exclude 0 and both MoM diffs > 0. It was met in Llama (`\ptHOneLlama`) and not in OLMo (`\ptHOneOlmo`; D1 diff CI lower bound `\ptDiffDOneLoOlmo` = -0.004). Family-level `\ptClaimHOne` is "not licensed". | Replace with "The preregistered condition that paraphrase-related variance exceeds the fact share held in one of the two models (family-level claim not licensed)." Or drop the clause. |
| A2 | B | Abstract, P2 sentences | "300 facts × 10 designed paraphrases … the fact share is above zero; … 0.28–0.42 of within-relation variance" | Omits that depth is defined only on correctly answered cells. The analysed sets are `\ptNCellsLlama` 1221 and `\ptNCellsOlmo` 1355 of 3000 cells (222 and 219 facts), not 300 × 10. Also omits: 3 of 5 preregistered models (Qwen3, Pythia-1.4B, Pythia-2.8B) are MISSING (insufficient data); the frequency covariate is PROXY (DCLM); the estimate is conditional on four covariates and a carrier effect; and the readout is at the final position. This is the correct-only omission the audit rules flag. | State "on cells each model answers correctly (N facts, N cells)" and "two of five preregistered models met the data rule". Say the fact share is final-position readout depth, conditional on covariates. |
| A3 | B | Abstract | "the fact share is above zero; it was estimated at 0.28–0.42 …" | The licensed sentence (P2 sec 6, human GO G2) is "The fact share is above zero." RESULTS.md section 4 adds that the fact component includes answer-token identity (no relation × object term in the frozen formula; skeptic G2 finding 3: 186 of 300 facts share an object within relation). The abstract and titles 1 and 3 read as "the fact has its own depth", which the GO G2 decision and RESULTS section 4 exclude. | Quote the licensed sentence verbatim. Add "fact-level variance, including answer-token identity". Keep the estimates in a separate sentence, labelled as estimates. |
| A4 | B | Abstract, last sentence; claims (v) | "rank-based causal depth exists only for correctly answered prompts" | Overgeneralised. The derivation holds for the final-token patch only. The project's own S3 causal depth patches the subject last token, and the derivation was not shown there. The audit is EXPLORATORY (C1re, Pythia-1.4B and 2.8B). The licensing table says "the abstract states the derivation", but the abstract has no EXPLORATORY label. | Say "with final-position patching, rank-1 depth exists only for correct prompts (exploratory audit, Pythia)". Mark it EXPLORATORY in the abstract or move it out. |
| A5 | B | Abstract, H-R sentence | "relation identity explained at most `\hrIccOlmoSeven` [0.060]" | Numerically the maximum of the per-model point ICCs (0.040, 0.013, 0.060), so it is accurate as a point-estimate summary. It is incomplete in three ways. (a) Upper CIs reach 0.119, 0.075, 0.123. "At most" can be read as a bound when it is a point-estimate maximum. (b) It is an adjusted ICC (covariates include `obj_logprob_final`, a readout of the same patched curve), with a subject random effect. It is not "variance explained". (c) The preregistered relation test H2 (raw cross-family relation ordering) is omitted. H2 raw FAILED, giving `\hrDecision` NO-GO. The orderings are positively shared: ρ `\hrRhoPyOneFourOlmo` 0.519 and `\hrRhoPyTwoEightOlmo` 0.597, permutation p 0.0028 and 0.0011. | Write "point estimates of the covariate-adjusted relation share were 0.013–0.060 (upper 95% bounds ≤ 0.123)". Add one clause that cross-family relation orderings were correlated but below the preregistered 0.7 (H2 raw failed). |
| A6 | N | Abstract | "co-occurrence added at most `\hrDRsqOlmoSeven` [0.0016] explained variance" | Accurate as the max of the point estimates (-0.0003, 0.0012, 0.0016). The upper bounds are 0.0037, 0.0084 and 0.0104, all below 0.02, so the parenthesis is right. Selective: the same data give survival HR 0.934, 0.936 and 0.966 (p < 1e-6) and correctness OR 1.28–1.43. H3 was NOT blind (HR prereg Part C). The abstract does not say so, though the licensing table says "disclosed in paper". | Add "small within-relation association in the survival model" or "does not rule out small effects". Keep the not-blind disclosure in the paper body, and consider a short clause in the abstract. Say "marginal R², within-relation (relation-centred) co-occurrence". |
| A7 | N | Abstract | "A decision study estimates 4–8 [`\ptNprimeOlmo`–`\ptNprimeLlama`] paraphrases for a reliable per-fact depth." | "estimates" is acceptable (the human's "needed" was rightly softened). Missing: "reliable" means G = 0.8 for a relative, within-relation, correct-cells coefficient; the Llama CI is [6, 13]; the value is model-dependent; it assumes exchangeable frames like the 10 designed ones. `\ptClaimSinglePromptPoor` is "not licensed". "per-fact depth" presupposes depth is a fact property. | "…estimates 4 (OLMo) and 8 (Llama) paraphrases for a generalizability coefficient of 0.8 (model-dependent; Llama CI 6–13)". |
| A8 | N | Abstract | "0.28–0.42", "0.55–0.68", "300 facts × 10" | Literal digits. The paper rule is that numbers come from numbers.tex. The ranges are derived and have no macro. The bracketed macros show the range endpoints, which are right: min is `\ptIccDFourLlama` 0.282, max is `\ptIccDOneOlmo` 0.422; wording min is `\ptWordingDOneOlmo` 0.546, max is `\ptWordingDFourLlama` 0.678. | Add macros for the ranges, or write the four endpoint macros. |
| A9 | N | Abstract | "paraphrase-related variance at 0.55–0.68" | Wording share = rt + frame + fact × paraphrase (ft). Most of it is ft: `\explFtShareLlama` 0.473 and `\explFtShareOlmo` 0.343, against systematic wording `\explSysWordShareLlama` 0.177 and `\explSysWordShareOlmo` 0.203. "Wording shifts together" is negative (`\ptTfResidLlama` -0.323, `\ptTfResidOlmo` -0.168). The abstract may read as "paraphrase effect". | "…of which most is fact-specific sensitivity to paraphrase (fact × paraphrase interaction; exploratory split)". Mark the split EXPLORATORY. |
| A10 | N | Abstract | Two studies in one paragraph | H-R and P2 differ in models, facts, templates and correctness filter (claims.md scope table is correct). Putting "relation ≤ 0.060" beside "fact 0.28–0.42" invites comparing numbers from different estimands. The H-R relation share is over all rows with a subject effect. The P2 fact share is within relation, correct cells only. | Add "in a separate study" and "(not comparable)". Do not compare the numbers in prose. |
| A11 | N | Abstract | "two preregistered studies" | Accurate. Disclosures: H3 not blind; P2 sec 0 lists G1 ICC(1) 0.37–0.64 on the same models, so "fact share above zero" was foreseeable (skeptic G2 finding 3). | State both disclosures in the paper body. |
| T1 | B | Title 1 | "How Much of a Fact's Readout Depth Belongs to the Fact?" | "belongs to the fact" suggests facts have a depth, which GO G2 does not license (RESULTS sec 4: "does not say … that facts have their own depth"; H1-alt not met in either model). It is also circular wording. | e.g. "How Much of Answer-Readout Depth Is Fact-Level? Two Preregistered Studies". Or drop "belongs to". |
| T2 | B | Title 2 | "Fact or Phrasing? … Where Language Models Read Out Answers" | "Where" reads as localisation, and skeptic finding 1 says "where a fact lives" is not licensed. "Fact or Phrasing?" implies a verdict on wording vs fact, which H1 does not license at family level. "Language Models" is generic for 2 families. | Reword: "A Preregistered Variance Decomposition of Final-Position Readout Depth in Two Model Families". |
| T3 | N | Title 3 | "One Fact, Many Depths: Paraphrase Sensitivity of Causal Readout Depth in Language Models" | Closest to the data (estimated fact × paraphrase variance is large). Still "in Language Models" overgeneralises (2 families, correct cells), and it drops the H-R null half of the paper. | "… in Two Model Families". Add a subtitle for scope. Of the three, this is the safest. |
| C1 | N | claims (i) permitted wording | "marginal R² … raised … by at most 0.0016" under the heading "explains almost none of the within-relation variance" | The H3 ΔR² is a Nakagawa marginal R² over total modelled variance (HR prereg B7). It is not a share of within-relation variance. | Heading: "adds almost nothing to marginal R²". |
| C2 | N | claims (ii) permitted wording | "below the preregistered 0.15 floor for a relation effect" | Misdescribes the prereg. H1 passes only if ICC ≥ 0.30 and the CI lower bound ≥ 0.15 (HR B4). It is a positive test with a pass floor, not an equivalence test with a 0.15 ceiling. "Upper bound < 0.15" is true (0.119, 0.075, 0.123) but is not a preregistered criterion. | "H1 failed in all three models; the upper 95% bounds were 0.119, 0.075, 0.123 (descriptive)". |
| C3 | N | claims (ii) heading | "(ii) Relation identity explains little" | Acceptable. The human's "preregistered null" is not: H1 failing is not a confirmed null, H2 raw failed with ρ 0.52–0.60 (p < 0.003), and correct-only ICC reaches 0.371 for Pythia-2.8B (non-gating). claims.md already lists these under "Not permitted". Keep them. | No change, except that the paper must carry the H2 and correct-only caveats wherever (ii) appears. |
| C4 | N | claims, missing items | Not in claims.md or the abstract | Preregistered tests that must appear in the paper. HR: H2 raw and H2 controlled (all FAIL; only mentioned in passing in (ii)). P2: H3 cross-model ρ = `\ptHThreeRho` 0.373, disattenuated `\ptHThreeDisatt` 0.463 (estimation); the "no fixed layer" rule (False; ICC upper not < 0.15); "wording shifts together" (not met); "fact depth unexplained"/H1-alt (not met); the null-calibration and power caveats (included). H4 and the P2 robustness simulation (MISSING). | Add a "preregistered results list" to claims.md covering every H and rule with result and status, including negatives. At paper stage all must appear. |
| C5 | N | claims scope table | "audit (v): Pythia-410M, 1.4B, 2.8B" | The (v) macros (`\explAudit*`) come from c1.json, which holds only 1.4B and 2.8B. 410M is from a separate AUDIT run (AUDITsum). The tables are not identical. | Say "numbers cited: 1.4B and 2.8B (c1.json); 410M in AUDITsum". |
| C6 | N | claims (vi) | "Spearman −0.030, HR 1.020 [0.977, 1.064]" | No macro, and S5 is incomplete. Not checkable against numbers.tex. EXPLORATORY label is correct. | Keep out of the abstract. Add macros once S5 completes. Do not cite the digits before then. |
| C7 | N | claims positioning | "we … find the prompt-specific part large (iii)" (Hase row) | The prompt-specific part is wording share = rt + frame + ft. "Large" rests on the not-licensed H1 and on an ft interaction the skeptic reads as sensitivity to any perturbation (neutral-prefix control). | "estimate the paraphrase-related share at 0.55–0.68, mostly fact × paraphrase interaction". |
| C8 | N | claims (iii) | "0.28–0.42" range; "observed ≥ 5 × null max" | Derived values without macros (also in the abstract). The ratios check out (5.6 and 9.2). | Add macros for derived ranges, or cite the endpoint macros. |

Correctly handled in claims.md (no change needed):
- It refuses "frequency does not matter" and "does not set / does not affect depth" without bounds. It gives the survival HR and correctness OR.
- It refuses "wording matters more than the fact". "Wording most of the rest" is flagged as not licensed and misleading.
- It refuses "it takes N paraphrases".
- H-R and P2 are separated by the study scope table.
- Final-position readout is stated, and "where a fact is stored" is explicitly disclaimed.
- EXPLORATORY labels on the wording split, the audit and S5 are correct.
- The S6 FAIL is "not cited as causal evidence".
- EXACT vs PROXY is labelled (H-R Pile and OLMo-mix EXACT; P2 DCLM PROXY, covariate only).
- Correct-only is stated for P2.

Labels:
- (i) CONFIRMATORY not blind, (ii) CONFIRMATORY (H1 FAIL), (iii) licensed sentence CONFIRMATORY, (iv) CONFIRMATORY estimation: all correct per prereg.
- (v) derivation plus EXPLORATORY audit: correct.
- (vi) EXPLORATORY: correct.
- The abstract table's label for the "only one model" clause, CONFIRMATORY per-model result, is acceptable only if the sentence is rewritten as in A1.

Banned-word grep over claims.md, titles_abstract.md and paper/*.tex: no hits. The only match is "novelty.md", a file name.

## 2. Numbers checked
Every item below was compared against the macro and, where noted, its source JSON.

**H-R, `results/HR_gate.json` (run HR-none-f431f35-20261121T081116Z)**
- Per-model relation ICC: 0.040, 0.013, 0.060. The OLMo value 0.0596 matches `main.icc_rel` in the JSON.
- ICC upper bounds: 0.119, 0.075, 0.123.
- H3 ΔR²: -0.0003, 0.0012, 0.0016.
- H3 ΔR² upper bounds: 0.0037, 0.0084, 0.0104. All are < 0.02 and `h3_pass` is true in all three models.
- `h1_pass` is false in all three models, decision NO-GO. Threshold block: icc 0.3, icc_lo 0.15, rho 0.7, dr2_hi 0.02.
- Survival HR: 0.934 [0.917, 0.952], 0.936 [0.919, 0.954], 0.966 [0.953, 0.979]. These agree with the JSON `hr_cooc`.
- Correctness OR: 1.384, 1.433, 1.283.
- N: 3900 rows per model; 1300 facts × 3 templates; 26 relations.
- H2 raw ρ: 0.519 (p 0.0028) and 0.597 (p 0.0011). Pythia-1.4B vs Pythia-2.8B ρ is 0.832 (same family, does not count).
- So "at most 0.0016" and "at most 0.060" are accurate point-estimate maxima. Both need the qualifiers in A5 and A6.

**P2, `results/P2analysis/correct/p2_decision.json` and `p2_results.json`**
- Llama: ICC D1 0.310 [0.242, 0.370]; D4 0.282; wording D1 0.649, D4 0.678; n′ = 8 [6, 13]; G ceiling 0.957; null p 0.000999.
- OLMo: ICC D1 0.422 [0.347, 0.487]; D4 0.373; wording D1 0.546, D4 0.612; n′ = 4 [3, 5]; G ceiling 0.990.
- Flags: Llama H1 true, OLMo H1 false, H1-alt false in both. `p2_decision.json` shows Qwen3 and both Pythia models as MISSING (insufficient data).
- Variance shares of total sum to 1.000 for Llama. Within-relation check: 0.285/(1 − 0.081) = 0.310, and 0.368/(1 − 0.128) = 0.422.
- Cells: 1221 × 3 = 3663 rows and 1355 × 3 = 4065 rows. These match the macros and the claims.md "of 3000".
- The abstract and claims.md ranges 0.28–0.42 and 0.55–0.68, and the n′ endpoints 4 and 8, match the macros.
- The EXPLORATORY split (0.177 / 0.473 and 0.203 / 0.343) and the "wording shifts together" values (-0.323, -0.168) match.

**Calibration, `results/P2null_calib/`**
- `null_fc1_nc3.json`: rejection 0.02 at p < 0.01 and 0.095 at p < 0.05, n = 200. Matches.
- `power_icc010.json`: power 0.46 at p < 0.01 and 0.84 at p < 0.05, n = 100. Matches.

**Audit, `results/C1re/C1re-none-3cee850-20261120T141401Z/c1.json`**
- Pythia-1.4B: 720 resolved and correct, 0 resolved and wrong, 0 censored and correct, 3180 censored and wrong. Pythia-2.8B: 804 / 0 / 0 / 3096. Matches the macros and claims.md.
- The c1.json label is "EXPLORATORY (not pre-registered)".

**Other**
- G2 S6 FAIL: Spearman -0.130, N = 21 (PROGRESS.md). Matches claims.md.
- "Only 'The fact share is above zero.' is licensed" matches the RESULTS.md section 4 and the ledger NOTE "GO G2 (human): P2 decided".
- Abstract length: about 146 words, counting each macro as one word.

**Not checkable**
- S5 numbers in claims (vi) have no macro. See C6.
- The `\ptRob*` robustness values are MISSING (simulation unfinished). claims.md says so.

No number in claims.md or the abstract disagrees with its macro. The faults are in wording, scope and omissions, not in arithmetic.

VERDICT: REVISE
