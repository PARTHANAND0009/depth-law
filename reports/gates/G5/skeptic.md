G5 hostile review of the paper draft: /home/user/depth-law/paper/main.tex, appendix.tex and numbers.tex (read-only; I edited nothing)

**Scope.** I read main.tex, appendix.tex, numbers.tex, claims/claims.md, prereg/HR_revised.md, prereg/P2_prompt_vs_fact.md, reports/p2/RESULTS.md, reports/p2/P2_robustsim_report.md, results/HR_gate.json, results/P2analysis/correct/*, paper/figs/fig1_p2.json, paper/generated/*.tex and the G1, G2 and G4 reviews. A few numbers below are my own checks of existing result files. They are marked [reviewer scratch, EXPLORATORY], are not logged runs, and must not go into the paper.

## Number check
Every macro used in main.tex and appendix.tex resolves to a source-commented value in numbers.tex. I spot-checked these against results/HR_gate.json, results/P2analysis/correct/p2_results.json, reports/p2/P2_robustsim_report.json and the null-calibration values; all match.
- The derived robustness numbers are right: 126 / 4 misses out of 800, ICC coverage 0.79–0.89, diff lower bound > 0 in 0.05–0.12.
- The null ratio is right: 0.310 / 0.055 = 5.6.
- Both prereg sha256 values match the frozen commits (7725c5b, ff119ca).

**Exceptions:**
- **N1 (minor, wrong number), main.tex:256.** "(nominal \ptRuleNullP)" renders as nominal 0.01. The one-sided nominal rate for a 95% interval's lower bound is 0.025, which is what appendix.tex:85 ("a fortieth"), RESULTS.md §9 and P2_robustsim_report.md say. Fix: use a 0.025 macro.
- **N2 (major, untrue integrity statement), appendix.tex:67.** The appendix says "The replicator agent independently recomputed the headline numbers from raw result files at both result gates and passed." This is not what happened.
  - The G1 replicator (reports/gates/G1/replicator.md, line 1) replicated the EXPLORATORY E-depthvar shares. Nothing in reports/gates/ replicates Study 1 (HR_gate.json: ICC_rel, ΔR², survival HR, OR).
  - The G2 replicator (reports/gates/G2/replicator.md, around lines 8–11) reused the frozen `p2_fit`/`p2_shares` R code and says "bootMer and the 1000-dataset null were not rerun".
  - So the null p behind the only licensed sentence, and all of Study 2's confidence intervals, were never independently recomputed.
  - Fix: state exactly what was replicated, or run a replicator on HR_gate.json and on the null.
- **N3 (minor to major, untrue disclosure), main.tex:304.** "Compute: one GPU session for Study 2 and CPU for everything else." Study 1's depth data come from GPU runs: results/S3b/*/log.jsonl start events show "device": "cuda:0", and HR_revised.md:34 calls them "amendment-2 GPU runs". Fix the sentence.

## Findings

**F1. MAJOR (borders on fatal for Study 1). Study 1's depth is measured mostly on wrong prompts, a regime the paper itself says changes what D1 means.**
- **Where:** main.tex:38, 108, 113, 120, 127, 279.
- **What the paper says:** at :108, "D1 is defined on wrong prompts too, but its meaning differs there". Study 2 therefore restricts to correct cells.
- **What Study 1 does:** it uses all rows (:113). Only 720, 804 and 1414 of 3900 rows are correct (HR_gate.json main.n_correct), so 64–82% of rows are wrong. For those rows the curve is half of the gold object's tiny final probability.
- **Evidence that the sign flips by regime:**
  - Study 1's fixed effect for obj_logprob_final is +0.135, +0.109 and +0.091 (more confident means later readout).
  - On Study 2's correct cells, between-fact r(D1 mean, logprob mean) within relation is −0.29 (Llama) and −0.18 (OLMo) [reviewer scratch, EXPLORATORY].
- **Correct-only results differ:** the relation share on correct rows is 0.139, 0.371 and 0.178 (\hrIccCorrectOnly*). For Pythia-2.8B the point estimate is above the 0.30 H1 threshold. These numbers appear only in an appendix table.
- **Alternative explanation:** the "small relation share" and the survival "later with more co-occurrence" come from noise in wrong rows and the confidence coupling, not from readout.
- **Fix without new experiments:**
  - Put the correct-only variants next to every Study 1 headline.
  - Scope the abstract sentence at :38 to "all rows, mostly incorrect".
  - Drop or qualify the substantive reading of the survival HR at :279 ("opposite direction to frequent facts resolve earlier").
  - Run an EXPLORATORY survival fit on correct rows only, from existing data.

**F2. MAJOR. "Relation-level share small" hides a relation × template share about as large as the subject share.**
- **Where:** main.tex:38, 71, 120.
- **Evidence:** HR_gate.json main.vc as shares of random variance:

| model | relation | relation × template | subject |
|---|---|---|---|
| Pythia-1.4B | 0.04 | 0.29 | 0.31 |
| Pythia-2.8B | 0.01 | 0.29 | 0.36 |
| OLMo-2-7B | 0.06 | 0.30 | 0.33 |

- **Per-template refits:** with one template, the relation share is 0.13–0.54 (\hrIccTemplate*, appendix hrvar).
- **Reading:** the relation effect is large but template-specific. That is the same prompt-dependence Study 2 studies, yet the paper never connects the two.
- **Also:** ICC_rel is conditional on obj_logprob_final, which is a readout of the same patched curve. That covariate absorbs relation-level confidence differences (relation accuracy varies).
- **Fix:** report the rt share and the per-template ICCs in the main text, and rephrase the claim as "relation main effect, pooled over templates".

**F3. MAJOR. The co-occurrence equivalence bound (H3) adjusts for a mediator and uses a metric that can be negative.**
- **Where:** main.tex:38, 71, 118, 123, 128.
- **Mediator:** H3 controls obj_logprob_final. Co-occurrence → confidence → D1 is the obvious pathway, and confidence is itself predicted by co-occurrence (OR 1.28–1.43).
- **Metric:** the ΔR² point estimate is negative in Pythia-1.4B (−0.0003). Yet the co-occurrence slope in the same model is clearly nonzero: cooc_coef 0.0061, SE 0.0016, z ≈ 3.8 (HR_gate.json main). Pythia-2.8B gives z ≈ 3.8 and OLMo z ≈ 1.9. So the marginal-R² change does not measure what the term contributes.
- **Data mix:** the bound is also computed mostly on wrong rows (F1).
- **"At most":** the wording at :71 is a point-estimate maximum; the bounds reach 0.0104.
- **Fix without new experiments:**
  - Report the slope in layers per log1p unit with its CI. Using Pythia-1.4B's L = 24 (per the G1 replicator), 0.0061 is about 0.15 layers per unit, which is genuinely small; that is the honest equivalence statement.
  - Add an EXPLORATORY fit without obj_logprob_final.
  - Report the correct-only ΔR² (0.0004, 0.0082, −0.0006) with bootstrap CIs.

**F4. MAJOR (contribution level). The one licensed sentence, "The fact share is above zero", was nearly certain before the data.**
- **Where:** main.tex:39, 72, 248–252, 274, 285.
- **What the null rejects:** zero variance in a component that holds everything constant within a fact: answer-token identity, subject tokenisation, final confidence (not a covariate in Study 2, :209), and object prior beyond a linear term.
- **Foreknowledge:** the P2 prereg §0 records within-relation ICC(1) of 0.37–0.64 from G1 on the same kinds of rows, including OLMo-2-7B.
- **Size of the margin:** the null's 99th percentile is about 0.04 against observed 0.31 and 0.42 (G2 skeptic #3).
- **Shared answers:** 186 of 300 facts share their object with another fact in the same relation. Llama and OLMo have the same first-token id for 300 of 300 objects (G2 skeptic #3 and #6), so the "two families" requirement adds no independence for token-driven variance. Neither point is in the paper's Limitations.
- **Answer identity can be estimated now:** the paper says it "cannot separate the fact from its answer" (:275) and calls this "future work" (:294). With repeated objects in the existing data, an EXPLORATORY (1|relation:object) refit is possible today. The skeptic's crude object ICC among OLMo fact means was about 0.54.
- **Confidence:** [reviewer scratch, EXPLORATORY] between-fact r(D1, final logprob) within relation is −0.29 in Llama.
- **Fix without new experiments:**
  - Run and report EXPLORATORY refits with (1|relation:object) and with cell-level final log-prob (obj_first_logprob is in long_*_correct.csv).
  - Disclose the shared tokenisation.
  - Say plainly that the confirmatory result is close to a manipulation check.

**F5. MAJOR. The paraphrase-related share is mostly instability under any perturbation, not wording content; and H1's "weakness" is attributed to the wrong cause.**
- **Where:** main.tex:40, 255–258, 274, 285.
- **What the share contains:** the fact × frame part (ft) is 0.473 (Llama) and 0.343 (OLMo) of den, against 0.177 and 0.203 for systematic wording. The G2 skeptic (#2) found that pairs differing only by the neutral prefix "According to reference sources, " move D1 by about 1.1–1.4 layers RMS, similar to order or form changes. The paper does not report this.
- **Same source state, three carriers:** all carriers patch in the same source state, so ft collects every source-prompt idiosyncrasy. 67–75% of cells give identical D1 across all three carriers (skeptic #1).
- **The final token differs across frames** ("of", "is", ":"), so frame variance includes final-token identity.
- **Scale:** the fact SD is about 1.1–1.3 layers, on a grid of about 20 distinct D1 values (RESULTS §3 and my count). The paper never states the absolute scale in the main text.
- **The H1 "weak result" argument at :40 and :256 points to the wrong cause:**
  - Llama's D1 diff lower bound is 0.220.
  - In the simulation, the false-pass rate of 0.05–0.12 and the +0.03 bias in diff apply when the true diff is 0. They cannot plausibly produce a lower bound of 0.22.
  - The knife-edge is OLMo's failure (lower bound −0.004, Monte Carlo SE about 0.006). OLMo's H1 flag is True in the new226, all and nomanufacturer sensitivities (RESULTS §6).
  - The simulation also shows diff biased up by about 0.03 and ICC biased down by about 0.03. The paper reports "err low" for ICC but not the upward diff bias that favours the wording side.
- **Fix (text plus an existing-data EXPLORATORY analysis):** report the neutral-prefix comparison as a logged EXPLORATORY run, give absolute SDs in layers, and rewrite the H1 caveat.

**F6. MAJOR. Discussion and Conclusion use sentences the frozen wording rules do not license.**
- **Where:** main.tex:277–278, 285–286.
- **The prereg rules (§6):**
  - "A single prompt is a poor estimate of a fact's depth; it takes N paraphrases" is not licensed (p2_decision single_prompt_poor = False).
  - "Wording most of the rest" is flagged in claims.md:41 as not licensed and misleading.
- **What the paper says instead:**
  - ":277 Single-prompt depths are noisy estimates of a fact-level quantity" also presupposes that facts have a depth, which RESULTS §4 excludes.
  - ":278 / :286 should average over paraphrases ... how many" restates the unlicensed rule.
  - ":285 most of the within-relation variance of a single prompt's depth is paraphrase-related" is the unlicensed wording claim.
- **Fix:** report these as estimates only (prereg §6, "Otherwise"), or label the recommendation EXPLORATORY with its basis.

**F7. MAJOR. The decision-study numbers depend on the coefficient chosen and on facts the model cannot supply.**
- **Where:** main.tex:41, 50, 260, 278, 286.
- **Relative vs absolute coefficient:** n′ uses relative within-relation G, which leaves out rt and frame. The paper recommends averaging before comparing relations or checkpoints; that needs the absolute coefficient Φ, which the prereg also computes (§4) and which is in p2_results.json but not reported.
  - Llama D1 Φ(k): 0.759 at k = 8, 0.792 at k = 10, 0.805 at k = 11. So n′ = 11, more than the 10 frames available.
  - Llama D4: G reaches 0.8 at k = 9; Φ is 0.767 at k = 12.
  - Llama D3: G is 0.73 at k = 12.
  - OLMo D2 and D3: n′ = 8.
  - So "4 and 8" is specific to D1 and to relative G.
- **The model cannot supply that many paraphrases:**
  - Only 67 of 222 Llama facts (74 of 219 for OLMo) have 8 or more correct paraphrases [reviewer scratch, EXPLORATORY].
  - Mean correct paraphrases per fact is 5.5 (Llama).
  - 26 Llama facts have a single correct paraphrase, so for them fact and ft cannot be separated.
- **Fix:** report Φ-based n′ and n′ under D4, and state that n′ counts correct paraphrases, which most facts do not have.

**F8. MAJOR (disclosure). Prior exposure for Study 2 is understated.**
- **Where:** main.tex:298; appendix.tex:24.
- **What the paper says:** only "the Study 2 plan was written after Study 1's results were known".
- **What the prereg records (P2 §0) but the paper omits:**
  - The same variance decomposition had already been estimated (G1 E-depthvar) on OLMo-2-7B and both Pythias, with ICC(1) 0.37–0.64.
  - OLMo's wording advantage in G1 depended on company_ceo (0.199 → 0.009 without it).
  - company_ceo was then excluded from P2 by a sampling rule.
- G4 claim-auditor A11 asked for this disclosure in the body. Fix: add it.

**F9. MAJOR (validity, partly addressed). Convergent validity of "readout depth" is not shown.**
- **Where:** main.tex:62–64, 96–104.
- **What D1 measures:** onset relative to the source's own final probability, after running the patched state through the carrier's remaining layers. The carriers rarely change the outcome (F5), so D1 behaves like a lens convergence layer.
- **D1 and D4 are not independent checks:** both come from the same curve (cell Spearman 0.80 and 0.88, skeptic #4).
- **The measure changes the answer:** under D2 and D3 the fact shares reorder across models (Llama D2 0.406 vs OLMo 0.275; RESULTS §3).
- **Fix without new experiments:**
  - State that the fact share depends on the measure.
  - If S3 logit-lens curves exist for Study 1 rows, report EXPLORATORY agreement between D1 and lens onset.
  - Make the scope "readout at the final position" explicit in the title or abstract (it is already in the body at :63–64).

**F10. MAJOR for a top venue. Novelty is thin.**
- **Where:** :59, :84, :281–282.
- Prompt-dependent localisation is published: Chen 2024 (ParaRel, neuron level), Benz 2026 (layers 16/12/20 under rephrasing), and Elhelo 2026 (10 paraphrases, fact × task ANOVA). Meloux 2025 covers estimation variance of interpretability measures.
- What is left is preregistration, a near-certain null rejection (F4) and a measure-specific D-study (F7).
- ":59 What has not been measured is ..." is stronger than this supports.
- Bajpai 2024 and Meloux 2025 were added after G4 with "content to be verified by citation-verifier at G5" (claims.md:76). No G5 citation-verifier report exists.
- Fix: soften :59 and run the citation check.

**F11. MINOR.**
- **(a) OLMo counts:** :114 calls OLMo-2 counts "pretraining mix" EXACT. The index covers stage-1 pretraining only; the released model also saw mid-training data that was not counted.
- **(b) Abstract juxtaposition:** :38–40 places the Study 1 relation share (all rows, includes subject variance) next to Study 2 within-relation shares (correct cells). These are different estimands; :39 says "separate", but the side-by-side numbers still invite comparison.
- **(c) Robustness claim at :268:** "'above zero' is conservative" is inferred from interval coverage at truths of 0.36–0.48. The licensed sentence rests on the null test, not on the interval.

## Alternative explanations and whether the analysis that rules each out was run

| claim | most likely alternative | analysis that would rule it out | run? |
|---|---|---|---|
| fact share > 0 | answer-token identity, confidence, subject tokenisation | (1\|relation:object) plus cell-level final log-prob refit | no (data exist: long_*_correct.csv) |
| wording share 0.55–0.68 | single-prompt instability or final-token identity | neutral-prefix pairs; final-token covariate | only the skeptic's scratch computation; tcov partly (OLMo diff → 0.082 [−0.039, 0.230]) |
| H1 in Llama | weaker than stated: ft equals perturbation sensitivity | as above | no |
| relation share small (Study 1) | wrong-row noise; relation × template absorbs relation; conditioning on confidence | correct-only and per-template variants | yes (HR_gate.json variants), but they contradict the headline and appear only in the appendix |
| co-occurrence bound (H3) | conditioning on a mediator; wrong rows | fit without obj_logprob_final; correct-only with CI | no / point estimate only |
| survival HR < 1 | correctness and confidence coupling of the half-threshold | correct-only survival | no |
| n′ = 4 and 8 | choice of G over Φ, and of measure | Φ, D4 | computed in p2_results.json, not reported |

## Five most damaging issues, ranked
1. **F4:** the only confirmatory headline is close to a manipulation check, and the fact component is not separated from answer identity or confidence, although the existing data allow it.
2. **F1 + F2:** Study 1's "relation share small" and survival reading rest on 64–82% wrong rows and pooled templates. The paper's own correct-only (up to 0.371) and per-template (0.13–0.54) variants contradict the abstract framing.
3. **F6:** the Discussion and Conclusion state the unlicensed "single prompt is poor / average N paraphrases / wording most of the rest" sentences, in a paper whose selling point is frozen wording rules.
4. **N2 + F8:** integrity overstatements and omissions. The replicator claim is untrue for Study 1 and for the CIs/null; the earlier E-depthvar exposure and the company_ceo exclusion are not disclosed; and the compute statement is false (N3).
5. **F7 + F3:** both quantitative take-aways are fragile.
   - The D-study gives n′ = 11 under the Φ that the paper's own recommendation needs, and few facts have 8 correct paraphrases.
   - The co-occurrence "equivalence" is a marginal-R² change that conditions on a mediator, even though the slope has z ≈ 3.8.

## Reviewer score and the one experiment most likely to change my mind
- **Score:** reject as it stands. The bookkeeping is unusually careful, but the scientific claims are either near-trivial or framed beyond the data.
- **Experiment (no GPU needed):** an EXPLORATORY refit of the existing Study 2 correct-cell data with (1|relation:object) and cell-level final log-prob, plus a neutral-prefix-only wording share. If the fact share stays at 0.2 or more in both models after the object term, and ft is not reproduced by the neutral prefix, the licensed sentence becomes informative.
- **New-experiment version:** the G2 skeptic's subject-position patch on the same 300 × 10 design.

Key files:
- /home/user/depth-law/paper/main.tex
- /home/user/depth-law/paper/appendix.tex
- /home/user/depth-law/paper/numbers.tex
- /home/user/depth-law/results/HR_gate.json
- /home/user/depth-law/results/P2analysis/correct/p2_results.json
- /home/user/depth-law/results/P2analysis/correct/long_Llama-3.1-8B_correct.csv
- /home/user/depth-law/reports/p2/P2_robustsim_report.md
- /home/user/depth-law/reports/gates/G1/replicator.md
- /home/user/depth-law/reports/gates/G2/replicator.md
- /home/user/depth-law/reports/gates/G2/skeptic.md
- /home/user/depth-law/prereg/P2_prompt_vs_fact.md
- /home/user/depth-law/results/S3b/S3b-pythia-1.4b-a7dfeb5-20261121T063528Z/log.jsonl

VERDICT: REVISE
