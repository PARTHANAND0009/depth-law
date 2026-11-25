G5 round 2 claim audit. Read-only. Files: /home/user/depth-law/paper/main.tex, appendix.tex, numbers.tex, generated/*.tex.

LIMITS
- The Bash hook blocked my first multi-path commands ("shell write touching a frozen path"). I used Read, Grep and Glob for anything touching prereg, results or the ledger.
- I did not re-read paper/main.pdf. I did not re-read reports/gates/G5/{skeptic,reviewer-sim,novelty-scout}.md in full. For their items I relied on responses.md.
- The ledger lines are too long to display. I confirmed only that fig3_audit.py (ledger line 163-164), g5_expl.py (line 160) and g5_expl_object.R (line 161) have entries.

1. check_numbers.py
Output: `check_numbers: ok`.

2. Round-1 findings F1-F26
| F | status | note |
|---|---|---|
| F1 | FIXED | \ptNominalOneSided = 0.025 is used at main.tex:310. appendix.tex:85 says "a fortieth". |
| F2 | PARTLY | "Single-prompt depths are noisy" and the "should average" recommendation are gone. See R2-3 and R2-6 (G(1), "needs", recommendation). |
| F3 | FIXED | The Conclusion is scoped (two models, correct prompts, one-of-two test, liberal test). The new "about half is answer identity" is R2-4. |
| F4 | FIXED for the P2 rules | Table 4 lists all six rules with \ptClaim* outcomes. A different preregistered omission is new: R2-1. |
| F5 | FIXED | The abstract says "all prompts (most answered incorrectly)" and "pooled over templates". main.tex:146 and :157 give the template-alone and correct-only variants. |
| F6 | FIXED | "depends on" (main.tex:68). |
| F7 | FIXED | "To our knowledge, no preregistered study…" (main.tex:61). |
| F8 | PARTLY | main.tex:59 still has "A depth measured on one prompt is then read as a property of the fact" with no cite. The §6 quotes show one prompt per fact, not this reading. See R2-9. |
| F9 | FIXED | "point estimates of at most … (not blind)". |
| F10 | FIXED | Scope added to contribution 2. |
| F11 | FIXED | |
| F12 | FIXED | OLMo's lower bound of −0.004 is stated at main.tex:309. |
| F13 | FIXED | |
| F14 | FIXED | main.tex:225-226 gives 196 facts with ≥2 correct paraphrases against 222 facts in the fit. |
| F15 | FIXED | H1-alt now includes the MoM condition. |
| F16 | PARTLY | Sets are named with N, and manufacturer is named. The text still says "the only influential relation in the sample" (main.tex:345). The prereg says "the only Part-0a influential relation". Restore "Part-0a" or "in the earlier decomposition". |
| F17 | FIXED | main.tex:350. |
| F18 | FIXED | "PROXY count from DCLM-baseline for both models". |
| F19 | FIXED | Fig. 1 caption says "selected, not sampled", names the carrier-level segment, and points to Table 3. |
| F20 | FIXED | |
| F21 | PARTLY | main.tex:406: "Claims were checked at human gates, the last before submission included." G5 has no verdict yet. Reword, or edit after GO G5. |
| F22 | FIXED | appendix.tex:40 says staged and pending. |
| F23 | FIXED | appendix.tex:51. |
| F24 | PARTLY | appendix.tex:67 now names G1 and G2. "Reproduced the EXPLORATORY variance shares" is generous: the G1 replicator reported MoM and REML shares differing by more than 0.02 in 26 of 48 shares, though it passed. "A human read every gate report" (appendix.tex:68) is not checkable from files. |
| F25 | FIXED | HR prereg Part A line 15 and B1 list the secondary outcomes. |
| F26 | n/a | |

3. New findings (B = blocks, N = non-blocking)
| id | sev | location | quoted text | problem | fix |
|---|---|---|---|---|---|
| R2-1 | B | main.tex §4, Table 1, appendix.tex App. C | (absent) | The preregistered H2 controlled item "Report split-half reliability and disattenuated rho" (HR_revised.md Part A line 20, B6) is not reported. \hrSplitHalf* (0.929, 0.897, 0.943) and \hrDisatt* (0.555, 0.649) exist in numbers.tex but appear in no .tex file, so check_numbers cannot catch it. Also missing: the preregistered "pythia-1.4b vs 2.8b is reported" (\hrRhoPyOneFourPyTwoEight = 0.832), the frailty SD and frailty-BLUP Spearman (B9), and the H2 ρ bootstrap CIs (\hrRhoLo*, \hrRhoHi*). The H2-controlled CI-lower and ρ-gap criteria are not shown either, only pass flags. | Add split-half r_SB, disattenuated ρ, the Pythia-pair ρ, and the frailty items to Table 1 or Appendix C, using the existing macros. If a quantity was not run, write MISSING. |
| R2-2 | B | main.tex:325, :369 | "mostly sensitivity of individual facts to any small change of the prompt, not a few systematic frame effects"; "most of that variance reflects how individual facts respond to small prompt changes" | Contradicted by the paper's own numbers. Fact×paraphrase is 0.473/0.343 against systematic 0.177/0.203 under D1. Under D4 it is 0.372/0.285 against 0.306/0.327. OLMo D4 systematic exceeds fact×paraphrase (fact×paraphrase is 47% of the paraphrase share). main.tex:321 itself says the dominant part "depends on the measure". The H4 frame-mean range (1.26 and 1.61 layers) is as large as the fact SD (1.06 and 1.29 layers) that the same paragraph gives for scale, so "small on average" and "not systematic" are not shown. The RMS pair differences (Table 6) have no noise baseline (discreteness and fact×carrier variance), so "small edits move depth as much as large ones" is unanchored. | Restrict to D1 ("under D1, about two thirds…; under D4 the split reverses for OLMo"). Drop "mostly" in the Discussion. State that the frame-mean range is comparable to the fact SD. Add a noise baseline or hedge. |
| R2-3 | N | main.tex:362-364 (§6) | "the relative generalizability of one prompt's depth, read from the preregistered G(k) curve, is 0.38 … roughly half or more … does not carry over to other paraphrases"; "should report how many paraphrases were averaged" | This is the unlicensed sentence "a single prompt is a poor estimate" in other words (condition not met: H1 in 1 of 2 families, n′ is 8 and 4). It is not labelled EXPLORATORY, although the macro is \explGOne from g5_expl.py (not from the preregistered output), and it gives a practice recommendation although the human asked for no new claims. The disclaimer sits one sentence later. | Label it EXPLORATORY, give G(1) as an estimate only, and delete or soften the recommendation. |
| R2-4 | N | main.tex:378 | "and about half of it is answer identity (EXPLORATORY)" | There is no macro for "half". Only point estimates exist (object.json). D1 gives 0.153/0.310 = 49% and 0.245/0.422 = 58%. D4 gives 35% and 78%. The fact (+object) and object terms sum to 0.339 and 0.451, not to the frozen 0.310 and 0.422. Convergence warnings are not disclosed: OLMo D4 object fit "failed to converge" and the OLMo D4 object+logprob fit is singular (Table 5 values). | Say "under D1, point estimates 0.153 and 0.245 against 0.310 and 0.422". Add a note on the non-converged and singular fits to the Table 5 caption. |
| R2-5 | N | main.tex:155, :372 | "clearly non-zero but small"; "non-zero but a fraction of a layer" | OLMo's interval is [−0.001, 0.140], which includes zero. The unit is per log1p of within-relation co-occurrence (HR B7), not "log". The slope is conditional on obj_logprob_final. | "non-zero in both Pythia models; OLMo's interval touches zero". Say log1p. |
| R2-6 | N | main.tex:333 | "needs 11 and 6 paraphrases … needs 10 and 4" | "needs" was the wording claims.md says to replace with "estimated for G = 0.8". | "is estimated at". |
| R2-7 | N | main.tex:371 | "large when each template was fitted alone" | The range is 0.134-0.542 (templates A to C). Only some fits are large. | "up to 0.54". |
| R2-8 | N | main.tex:147 | "This template dependence is the same prompt dependence that Study 2 measures." | Different rows (all vs correct), different variance object (relation×template vs fact×frame), different models. Identity is not shown. | "is of the same kind". |
| R2-9 | N | main.tex:59, :360-361 | "is then read as a property of the fact"; "which is what their questions need"; "They do bear on per-fact or per-relation readings"; later "does not transfer to other measures" | Uncited attribution of intent to other papers. "Do bear" conflicts with the non-transfer disclaimer in :363. | Cite or soften to "may bear". |
| R2-10 | N | main.tex:154 | "which co-occurrence also predicts" (final log-probability) | The evidence is the correctness odds ratio, not a log-probability association. | Say "predicts correctness". |
| R2-11 | N | main.tex:132 | "agreement with a logit-lens onset" | The lens onset is never defined. Spearman is −0.14, 0.17 and 0.27 (N = 720, 804, 1,414). | Add a one-line definition. |
| R2-12 | N | main.tex:400 | "(one GPU, fp32)" | The Study 1 precision is not shown in the files I read. UNVERIFIED. | Verify against the S3b run logs or drop "fp32" for Study 1. |
| R2-13 | N | abstract, main.tex:43 | "estimates 4 (OLMo) and 8 (Llama) paraphrases" | The scope is missing: relative coefficient, D1, correct cells. | Add "relative, D1". |
| R2-14 | N | §6 quotes, main.tex:357-359 | quotations | I checked them against the PDFs. Meng et al. App. B.1: verbatim ("We use the text up to but not including the object … we randomly sample 1000 of these texts"). Geva et al. §3: verbatim ("a data sample for each model, resulting in 1,209 queries for GPT-2 and 1,199 for GPT-J"). Hochman et al. §6 Data: verbatim ("select 2,000 prompts for which the target attribute is a single token and this token is correctly predicted by the model"). The gloss "one query per triplet" is not in Geva and is an inference. UNVERIFIED as a quotation. | Drop or hedge the gloss. |

4. EXPLORATORY traceability
- All `expl*` macros trace to results/G5expl/expl.json or object.json. I checked these values against the JSON: pairs RMS and N, n_distinct 47 and 47, modal share and layer, facts ≥8 and single, H4, D4 split, n′ (Φ and D4), G(1) 0.377 and 0.529, slopes and intervals, relation×template shares, lens ρ and N, worked example (D1 15.33 and 16, rank-1 onset 15 of L = 24), object refits, GPU minutes (57.7 and 36.5).
- \explSdFact/Ft/WordLayers, \explSysWordShare and \explFtShare are labelled EXPLORATORY but computed from results/P2analysis/correct/p2_results.json, not G5expl. I recomputed two of them from the variance components and they match. The label is right; the source path differs.
- Audit counts (720/0/0/3180 and 804/0/0/3096) trace to results/C1re c1.json and sum to 3900 per model.
- The H4 numbers come from results/P2analysis/h4 via g5_expl.py. They are labelled EXPLORATORY in the text and in the Table 6 caption.
- Labels present: the worked example, the audit counts, §3.3, the relation×template breakdown, the slope, the object refit, the pair table, the D4 split, the n′ variants and the SD in layers. Missing: the §6 G(1) (R2-3).
- The claim "OLMo passes H1 in three non-gating sensitivity sets" is correct per the p2_decision.json files: all, new226 and nomanufacturer are true; all10 and tcov are false.
- Macro use: no D1/D4 or model mix-ups found. Specific checks: \ptRuleNullP is used only for the null threshold, \ptNominalOneSided for the nominal rate, and the \ptNullRatioMin arithmetic is correct.

5. Other checks
- Banned words: none in main.tex, appendix.tex or generated/*.tex. "novelty-scout" appears only as the reviewer name in reviews.tex. "conserved", "universal", "determines" and "causes" are absent.
- Required abstract content (GO G4): present. It says three further preregistered models had too few correct answers, that the H1 test was liberal in simulation, and that it failed narrowly in the other model. The licensed sentence is stated only for the two models.
- Figures: Fig. 3 comes from src/depthlaw/figs/fig3_audit.py, with ledger entries and plotted values in fig3_audit.json. Those match expl.json and the macros. It is a single selected fact (3 carriers, no error bars). The caption does not say how the fact was chosen: the script takes the first fact by id with template 0 correct and template 1 wrong. Add that to the caption. Fig. 1 and Fig. 2 were not re-audited: the captions are fixed per F19-F20 and I did not re-check their values.
- Appendix A: the freeze, guard and ledger statements are consistent with the round-1 checks. Open points are F21, F24, and the unverifiable "human read every gate report".

VERDICT: BLOCK
Reason: R2-1 is a preregistered report item (split-half reliability, disattenuated ρ, the Pythia-pair ρ) that is absent from the paper. The fix is cheap, since the macros already exist. R2-2 (the Discussion overstates the paraphrase decomposition) is also blocking until fixed. All other items are non-blocking. After R2-1 and R2-2 are fixed, I expect REVISE-level items R2-3 to R2-14 and the F8, F16, F21 and F24 leftovers to be the remainder.
