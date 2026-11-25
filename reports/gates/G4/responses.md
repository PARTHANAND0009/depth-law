# G4 responses to reviewers (paper setup)

Reviews (verbatim, not edited): `claim-auditor.md` (REVISE; 6 blocking wording findings, 0 numeric errors), `novelty-scout.md` (REVISE; no central claim already published; 3 mischaracterisations). Both audited the versions at commit `21692bb`. Revised files: `claims/claims.md`, `reports/paper/titles_abstract.md`, `scripts/make_numbers.py` (derived range macros; `paper/numbers.tex` regenerated through `scripts/log_run.py`). No result, threshold or prereg file changed. The revised files were not re-reviewed.

## Claim-auditor
| # | sev | response |
|---|---|---|
| A1 | B | Fixed. The abstract now says paraphrase-related shares exceeded the fact share "by the preregistered test in one model"; it no longer says wording exceeded the fact share in only one model (point estimates exceed it in both). |
| A2 | B | Fixed in part. Abstract: "in a separate study ... on the prompts each model answers correctly"; "at the prediction position" scopes the readout. The MISSING models, cell counts, PROXY covariate and conditioning are stated in claims.md and go in the body (section 5.1); the 150-word limit does not hold them all. If the human wants the MISSING models in the abstract, the simplest addition is "(three further preregistered models had too few correct answers)" (+9 words). |
| A3 | B | Fixed. The licensed sentence is quoted verbatim; the estimate sentence says the fact-level shares "include answer-token identity". claims.md (iii) adds the GO G2 meaning. |
| A4 | B | Fixed by removal. The rank-1 note is out of the abstract; claims.md (v) is scoped to the final-token patch and labelled EXPLORATORY. Note on the premise: S3 stored two measures, `causal_subj` (subject position) and `causal_final` (final token); the audit and all H-R/S5 depths use the final-token patch (`src/depthlaw/depth/causal.py` docstring), so the derivation does not apply to `causal_subj`, as claims.md now says. |
| A5 | B | Fixed. Abstract: "the relation-level share was small (≤ `\hrIccMax`; upper bounds ≤ `\hrIccHiMax`)" with new macros; claims.md (ii) calls ICC_rel an adjusted share, not variance explained, and keeps H2 raw (orderings ρ 0.52/0.60, p < 0.01) with the paper text (section 4). H2 raw is not in the abstract (length); it is in the body and the preregistered-results list. |
| A6 | N | Partly. "point estimates ≤ ... all upper 95% bounds below 0.02". The survival association and the not-blind disclosure go in section 4 of the body (claims.md (i) requires both). Not added to the abstract (length). |
| A7 | N | Fixed. "estimates 4 (OLMo) and 8 (Llama) paraphrases for a generalizability coefficient of 0.8"; "reliable per-fact depth" removed. The Llama CI [6, 13] and the assumptions go in the body. |
| A8 | N | Fixed. New macros `\ptIccRangeLo/Hi`, `\ptWordingRangeLo/Hi`, `\hrIccMin/Max`, `\hrIccHiMax`, `\hrDRsqMax`, `\hrDRsqHiMax`, `\ptNullRatioMin`, `\ptNFacts`. |
| A9 | N | The abstract no longer characterises the composition of the paraphrase share. The EXPLORATORY split stays in Figure 1 (labelled) and claims.md. |
| A10 | N | Fixed: "In a separate study"; no numbers are compared across studies. |
| A11 | N | Accepted: both disclosures (H3 not blind; G1 values known before P2) go in the body. |
| T1 | B | Fixed: "How Much of Answer-Readout Depth Is Fact-Level? Two Preregistered Studies" (recommended). |
| T2 | B | Fixed: "Paraphrase Sensitivity of Final-Position Readout Depth: A Preregistered Variance Decomposition in Two Model Families". |
| T3 | N | Fixed: "One Fact, Many Readout Depths: Preregistered Evidence from Two Model Families". |
| C1 | N | Fixed (heading and wording: marginal R², relation-centred, not a within-relation share). |
| C2 | N | Fixed ("H1 failed in all three models; upper bounds descriptive; no upper-bound criterion in the prereg"). |
| C3 | N | Kept; the H2 and correct-only caveats stay attached to (ii). |
| C4 | N | Fixed: claims.md has a table of every preregistered test and estimate with its result. |
| C5 | N | Fixed in the scope table. |
| C6 | N | Fixed: S5 digits removed until macros exist. |
| C7 | N | Fixed: Hase row now states the estimated paraphrase-related share with macros. |
| C8 | N | Fixed with `\ptIccRangeLo/Hi` and `\ptNullRatioMin`. |

## Novelty-scout
| item | response |
|---|---|
| (i) PARTIALLY KNOWN; equivalence-bounded null NEW | Accepted. Bajpai et al. 2411.10813 added to positioning (opposite direction, different measure); Merullo kept. The suggested Bajpai-style convergence analysis is not run (no new analysis at this gate). |
| (ii) NEW as a share; ordering PARTIALLY KNOWN | Accepted; Hochman row updated (no statistic reported, one prompt per fact). |
| (iii) qualitative message PARTIALLY KNOWN; quantification NEW | Accepted. claims.md now has a "Framing" note: prompt dependence is not presented as a discovery; Benz, Chen and Elhelo are cited as precedents. |
| (iv) NEW for depth measures; method borrowed | Accepted: G-theory cited as borrowed; Meloux et al. 2510.00845 added. A bootstrap interval for G(k) already exists for n′ (`\ptNprimeLo/Hi`, parametric bootstrap); a facts × paraphrases bootstrap is not added. |
| (v) PARTIALLY KNOWN; methods note | Accepted: labelled "methods note, not a contribution"; removed from the abstract. |
| Benz mischaracterised | Fixed: section 4.3 (one fact at layers 16, 12, 20 under three phrasings) cited as the closest anecdotal precedent. |
| Chen understated | Fixed: query-tied localisation across ParaRel paraphrases. |
| Elhelo delta overclaimed | Fixed: 10 paraphrases + two-way ANOVA precedent acknowledged; delta limited to readout-depth outcome, preregistered fact-share null, D-study. |
| Hochman additions | Added. |
| Gupta "TunedLens" | Changed to "probe-based lens". |
| Title/abstract risks | Titles reworded (see T1–T3); "at most" now explicitly point estimates with upper bounds; "reliable per-fact depth" removed. |
| UNVERIFIED items (ZF443JePxe, 2609.04047, 2603.00883, 2604.18389, 2602.14080) | Not cited. |
| New citations (2411.10813, 2510.00845) | To be verified by citation-verifier at G5 before any related-work text uses them. |
