G5 CLAIM AUDIT (read-only; no files edited)

LIMITS: Bash blocked my first two calls (a hook, "shell write touching a frozen path"). A plain `python3 /home/user/depth-law/scripts/check_numbers.py` then ran and printed "check_numbers: ok". I did not rebuild main.pdf and did not read RESULTS.md, GATE_G2.md or the reference list. I checked the ledger only by counting 4 hits for the two figure scripts; I did not inspect their entries. I did not open G4/claim-auditor.md or responses.md, so I cannot say whether the G4 findings were all addressed.

## Findings (B = blocking, N = non-blocking)

| id | sev | location | quoted text | problem | fix |
|---|---|---|---|---|---|
| F1 | B | main.tex:256 | "passed in \ptRobDiffLoPosMin--\ptRobDiffLoPosMax{} of datasets whose true difference was zero (nominal \ptRuleNullP" | Wrong macro. \ptRuleNullP is 0.01, the fact-share null threshold. The nominal one-sided rate for a 95% interval is 0.025, as in claims.md, GATE_G4 s1b and appendix.tex:85 ("a fortieth"). The text understates the liberality (0.05–0.12 against 0.025, so 2–5 times, not 5–12 times) and misreports the nominal. | Use a 0.025 macro (add to make_numbers.py) or write "one fortieth". |
| F2 | B | main.tex:277-278, 286; contribution bullet main.tex:73 | "Single-prompt depths are noisy estimates of a fact-level quantity." "should average over paraphrases" "We recommend averaging depth over paraphrases before comparing facts, relations or models." "estimates how many paraphrases a per-fact depth needs" | This is the prereg s6 sentence "A single prompt is a poor estimate...; it takes N paraphrases". It needs H1 and n'≥8 in ≥2 families. \ptClaimSinglePromptPoor = not licensed (H1 holds in 1 of 2 families; Llama n'=8, OLMo n'=4). GO G2 licensed only "The fact share is above zero." The recommendation also extends to relations, models and checkpoints, none of which were tested. "needs" is the wording claims.md says to replace with "estimated for G=0.8". | Remove or hedge as an EXPLORATORY, non-licensed suggestion ("if one wants G=0.8 under these two models, the estimate is 8 and 4 paraphrases"). Drop the recommendation to compare across relations, models and checkpoints. Change "needs" to "estimated for G = 0.8". |
| F3 | B | main.tex:285 (Conclusion) | "Readout depth at the prediction position has a fact-level component above zero; in our estimates most of the within-relation variance ... is paraphrase-related (confirmed by the preregistered test in one of two models)" | The licensed sentence is stated as a general property of readout depth. The licensing covered only Llama-3.1-8B and OLMo-2-7B, correct cells only, 10 designed frames, and a fact component that includes answer-token identity. The conclusion drops all of these. "confirmed" drops the G4-required caveat that the test is liberal in simulation (the abstract has it). "most of the variance" is not licensed (ptClaimHOne = not licensed). | Rewrite: "In Llama-3.1-8B and OLMo-2-7B, on correctly answered prompts, the fact share is above zero (including answer-token identity); the paraphrase-related share is estimated higher, but the H1 test held in one model only and was liberal in simulation." |
| F4 | B | Paper omits several preregistered P2 rule outcomes (claims.md "must all appear" table, G4 C4). \ptClaimNoFixedLayer, \ptClaimSinglePromptPoor, \ptClaimModelDep, \ptClaimFactUnexplained and \ptClaimWordingTogether never appear in main.tex or appendix.tex (grep: no match outside numbers.tex). | | Reported only indirectly: H1-alt "held in neither", H1 not family-level, tf-resid negative. Never stated for no-fixed-layer (ICC D1 upper 0.370 and 0.487, against the <0.15 rule), single-prompt-poor, the conflict rule, or the "facts have a depth frequency and relation don't explain" rule. Two of these are not mentioned at all. Under the audit rule, an unreported preregistered test means BLOCK. | Add a table, "Preregistered headline rules and outcomes", listing all 6 rules (5 not licensed, 1 licensed) using the \ptClaim* macros. |
| F5 | B | main.tex:38, 71; abstract and contribution 1 | "the relation-level share was small (\le \hrIccMax ...)" | The relation share is small only on all rows. The non-gating variants in generated/hrvar.tex are far larger: correct rows only 0.139 / 0.371 / 0.178 (Pythia-2.8B's 0.371 is above the 0.30 H1 threshold as a point estimate); single-template fits up to 0.542. claims.md (ii) says to qualify "does not matter" with these. Study 1 depth is also computed on wrong prompts, where the paper itself says D1 "means differently". Neither point is in the abstract or the intro. | Add "(all rows; correct-only rows: 0.139–0.371, non-gating)" or equivalent in the abstract and the Study 1 results. Also state that Study 1 rows include incorrect answers. |
| F6 | N | main.tex:67 | "tests whether depth is set by the relation or by pretraining co-occurrence" | Causal verb "set" for a variance-partition result. claims.md forbids "sets". | "depends on" or "is associated with". |
| F7 | N | main.tex:59 | "What has not been measured is how much of a layer-wise depth is fact-level at all" | Priority claim. G4 novelty-scout says prompt dependence is known and only the preregistered quantification is new. Elhelo et al. 2026 already does a paraphrase variance decomposition (of behaviour). | "To our knowledge, no preregistered variance decomposition of a patching-based readout depth exists." |
| F8 | N | main.tex:56 | "A depth measured on one prompt is treated as a property of the fact." | Uncited assertion about the literature. | Cite or soften. |
| F9 | N | main.tex:71 | "changes the marginal \Rsq of depth by at most \hrDRsqMax" | "at most" reads as a bound. claims.md says "point estimates of at most", with upper CI bounds ≤0.0104. The bullet omits that H3 was not blind and that the survival model finds a small association. | "by point estimates of at most ...". Add "H3 not blind". |
| F10 | N | main.tex:72 | contribution 2 | Scope missing. No mention of correct cells, two families, or that the fact component includes answer-token identity. | Add scope. |
| F11 | N | main.tex:274 | "A readout depth measured on one prompt contains a fact-level part that is above zero." | Under the heading "What the licensed sentence says", but with no model scope or correct-cells scope. | Add "in Llama-3.1-8B and OLMo-2-7B, on correct prompts". |
| F12 | N | main.tex:274 | "In both included models the estimated paraphrase-related share is larger than the estimated fact share" | True for the point estimates (0.649 > 0.310; 0.546 > 0.422). In OLMo the D1 difference CI includes 0 (-0.004). | Add "(OLMo D1: interval includes zero)". |
| F13 | N | main.tex:279 | "the exact-count result bounds the explained variance, not the association: the survival model sees a small effect in the opposite direction" | Reasonable. The survival model is non-gating, which the paper says, but the HR is reported without a label saying it is preregistered. The "opposite direction" comparison is to a hypothesis the paper never stated. | State the hypothesis explicitly, or drop the comparison. |
| F14 | N | main.tex:200-201 | "\llama{} (\ptIncFactsLlama{} facts) and \olmo{} (\ptIncFactsOlmo)" and Table 2 "\ptNFactsLlama / \ptNCellsLlama" | Inclusion counts (196, 205 facts with ≥2 correct paraphrases) differ from the analysed fact counts (222, 219) with no explanation. Which facts enter the model is unstated. | Explain the 196 against 222 difference. |
| F15 | N | main.tex:214 | H1-alt definition | Omits the preregistered MoM condition "MoM diff < 0 under both measures" (prereg s5). | Add. |
| F16 | N | main.tex:263 | "keep the D1 fact share between \ptSensIccDOneMin{} and \ptSensIccDOneMax" | The minimum (0.231) comes from the "correct under all frames" set, which has only 14 Llama and 30 OLMo facts. "without the one influential relation" appears without introduction. The sentence also says "All preregistered sensitivities". | Name the small sets and give the facts N. Define "one influential relation" (manufacturer). |
| F17 | N | main.tex:268 | "so 'above zero' is conservative here" | The licensed sentence rests on the null test, not the interval. The null was mildly liberal (0.020 at p<0.01). Coverage of the interval is indirect evidence for the test. | Say so, and refer to the null calibration. |
| F18 | N | main.tex:209 | "log co-occurrence (PROXY: DCLM-baseline counts" | Labelled PROXY. It is not said that the same DCLM count is used for OLMo (whose own corpus is OLMo-mix; exact counts exist). | State this. |
| F19 | N | Fig. 1 caption (main.tex:47-50) | bold title "The same fact is read out at different depths under different paraphrases" | The 40 facts were selected (2 per relation, most paraphrases correct in both models), so they are not representative. The caption says "chosen by the number of paraphrases correct" but not that the choice is non-random. The carrier-level segment of the right-top bar is not mentioned. No error bars exist. Intervals are cited only in the text. The bar is drawn as a short marker. | Add "(selected, not random)". Mention the carrier-level segment. Say that intervals are in Table 2. |
| F20 | N | main.tex:66 / Table 1 caption (156) | Table 1 caption | N rows are in the table. Fig. 2 caption gives no N and says "intervals ... \ptCiLevel\%" (matches the script, 2000 resamples). Table 1 has no CI for \DRsq. | Add "N=3900 rows per model" to the Fig. 2 caption. |
| F21 | N | main.tex:310 (Acknowledgements) | "Every claim was checked at human gates." | G5 had not yet taken place when this was written. | "Claims were reviewed at gates G1–G4; G5 pending." |
| F22 | N | appendix.tex:40 | "the incident is recorded as a write-once deviation file" | summary.json shows INC-2026-11-25-required-macros is not installed ("installed": false, "staged for the human, APPLY_guard.sh"). The file is still in reports/pending_frozen_changes. The appendix says "all entries are generated", and \intNDeviations=3 counts it. | Say "staged, pending installation" or install it before submission. |
| F23 | N | appendix.tex:51 | "which is why the installed hook fails \intTestHookOldFail{} of the new cases" | Matches summary.json (15 failures of 25). The staged hook patch is not yet applied. The appendix says "Both ... unchanged" and "guard (i) blocks frozen edits", which holds only after the patch. | State that the hook patch is pending. |
| F24 | N | appendix.tex:67-68 | "The replicator agent independently recomputed the headline numbers ... at both result gates and passed. A human read every gate report" | summary.json has replicator PASS for G1 and G2 only. G3 and G4 had no replicator, and G4 and G5 are not "result gates". "Every gate report" cannot be verified from the files I read. | Name the gates (G1, G2). |
| F25 | N | main.tex:105-108, Study 1 | EXPLORATORY labelling | Present for the audit and the correct-only note. The Study 1 secondary outcomes (hrvar: rank-1 onset, p≥0.1 onset) are called preregistered and non-gating in the hrvar caption. I could not check that against the HR prereg. | Confirm against HR_revised.md. |
| F26 | N | Fig. 2 | not a defect | Plotted values match numbers.tex (0.040 [0, 0.119]; 0.013 [0, 0.075]; 0.060 [~0, 0.123]; ΔR² −0.0003/0.0012/0.0016 with upper 0.0037/0.0084/0.0104; n_boot 2000, N=3900). | None. |

Banned words: none found in paper/*.tex ("novel" appears only in reviews.tex as the reviewer name "novelty-scout"). The words conserved, universal, determines and causes are absent. "set" appears once as a causal verb (F6).

Scope and labelling checks:
- Correct cells only: stated in the abstract, Table 2 caption and Limitations.
- Final-position readout: stated in the abstract, intro and Limitations.
- Answer-token identity: in the abstract, Fig. 1, Results, Discussion and Limitations. It is missing from the bullet in the contribution list (F10) and from the Conclusion (F3).
- Two families: stated in the abstract and Limitations.
- PROXY: stated in the Model paragraph and Limitations.
- H3 not blind: in Results and Limitations. Missing from the abstract and contribution 1 (F9).
- G4 abstract requirements: both present (three further preregistered models had too few correct answers; the H1 test was liberal in simulation, so the one-model result is weak).
- EXPLORATORY labels: the fact × paraphrase split, the rank-1 audit and H4 are labelled in the text, in the Fig. 1 caption and in the appendix.
- Figure sources and ledger entries: fig1_p2.py and fig2_hr_forest.py exist and read only results files. The ledger has 4 mentions of the two scripts; I did not inspect them.
- Study 2 relation share (0.081 and 0.128) and the HR relation ordering across families are mostly reported (ρ is in Study 1 results).

## Macro-usage check
- F1 is the only wrong-macro finding.
- \ptIccRangeLo/Hi (0.282–0.422) is the D1/D4 range over 2 models, as its comment says. It is used as "of within-relation variance" in the abstract. This is fine.
- \ptWordingRange (0.546–0.678) matches D1 OLMo and D4 Llama.
- \ptNullRatioMin 5.6 = 0.310/0.055, the minimum; OLMo gives 0.422/0.046 = 9.2.
- \ptRobIccMissAbove/Below (126/4 of 800) is used in the appendix and main text consistently with coverage 0.79–0.89.
- The \ptRobDiffLoPos range is used correctly except for the nominal macro in F1.
- \ptSensIccDOneMin/Max is derived over all sets including the 14-fact set (F16).
- D4 macros are used as D4 in Table 2.
- No D1/D4 confusion found.
- \hrIccMax/\hrIccHiMax/\hrDRsqMax match the per-model values (0.060, 0.123, 0.0016).
- \hrSurvPOlmoSeven (3.3e-07) is the largest of the three p values, so "all p ≤" is correct.
- \hrNBootRel is 2000 and \ptNBoot is 1000. The captions use each in the right place.

## Integrity appendix check (summary.json, deviations, pending dir)
- Freeze commits and sha256 prefixes match summary.json: 7725c5b / 7d4bcceb5e5b7193; ff119ca / 493b2c3c079d2167. Both unchanged.
- Ledger: 147 entries, 65 runs (33 confirmatory, 32 exploratory), 82 notes, 7 non-zero exits, 0 frozen violations. These match the macros.
- Guard tests: 11/0, 25/0, 13/0, old hook 10 pass and 15 fail. The paper's "fails 15 of the new cases" matches.
- 21 frozen files and 19 reviews match.
- D-A0 and D-P2 are installed; the incident is not (F22).
- The deviation text for D-P2 (copy via the GitHub branch, no measurement change) matches the file.
- The incident narrative matches INC-...md (329→459 entries, commit 21692bb, detected after about a minute, restore blocked, GO G4 accepted).
- I did not read protect_frozen.diff, DEVIATIONS_append.txt or APPLY_guard.sh.

## Numbers checked against numbers.tex and sources
- Study 1 abstract and results: ICC_rel 0.040/0.013/0.060; upper 0.119/0.075/0.123; ΔR² −0.0003/0.0012/0.0016; upper 0.0037/0.0084/0.0104 (all below 0.02); ρ 0.519/0.597 (perm p 0.0028/0.0011); survival HR 0.934/0.936/0.966; odds ratio 1.384/1.433/1.283.
- Study 2: fact share D1 0.310 [0.242, 0.370] and 0.422 [0.347, 0.487]; D4 0.282 and 0.373.
- Wording share: D1 0.649/0.546; D4 0.678/0.612.
- Diff D1 Llama 0.339 [0.220, 0.474] (H1 met); OLMo 0.124 [−0.004, 0.272] (not met).
- Null p 0.0010 at its floor; max null 0.055/0.046.
- n' = 8 [6, 13] and 4 [3, 5]. G ceilings 0.957 and 0.990.
- Cells 1221 and 1355; facts 222 and 219; included 196 and 205; missing models 125, 91 and 93.
- Calibration: 0.020 at p<0.01 (N=200), power 0.46.
- Robustness: 800 simulations, coverage 0.79–0.89, bias −0.034 to −0.022.
- Cross-model ρ 0.373 (N=190), disattenuated 0.463.

VERDICT: BLOCK
