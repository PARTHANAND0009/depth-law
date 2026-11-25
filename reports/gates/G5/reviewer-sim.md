ARR SIMULATION: "How Much of Answer-Readout Depth Is Fact-Level? Two Preregistered Studies" (long paper)

I read these files and judged the paper as submitted: /home/user/depth-law/paper/main.tex, /home/user/depth-law/paper/appendix.tex, /home/user/depth-law/paper/numbers.tex, /home/user/depth-law/paper/generated/{hrvar,sens}.tex and /home/user/depth-law/paper/figs/fig1_p2.png. For context only I also read /home/user/depth-law/reports/p2/RESULTS.md, /home/user/depth-law/prereg/P2_prompt_vs_fact.md (§5–6) and /home/user/depth-law/prereg/HR_revised.md (B7–B9). The build log says the PDF is 12 pages; the main text ends on p.5. I made no changes to any file.

=====================================================================
REVIEWER 1: Interpretability expert
=====================================================================
**Summary.** The paper defines D1, a "readout depth". The prompt's final-token residual at layer l is patched into the final token of three carriers ("X is associated with", …). D1 is the first layer from which the object's first-token probability stays at or above half its final value. Study 1 (Pythia-1.4B/2.8B, OLMo-2-7B; 1,300 facts × 3 templates; all rows) finds:
- the relation share of D1 is 0.013–0.060, so preregistered H1 fails;
- within-relation exact co-occurrence adds ΔR²m ≤ 0.0016, with upper bounds ≤ 0.0104 < 0.02 (H3 passes).

Study 2 (300 facts × 10 designed frames; only Llama-3.1-8B and OLMo-2-7B pass inclusion; correct cells only) splits within-relation D1 variance as follows:
- fact share: 0.31 and 0.42;
- paraphrase-related share: 0.65 and 0.55;
- n′ for G = 0.8: 8 and 4 paraphrases.

The only preregistration-licensed headline is "the fact share is above zero."

**Strengths.**
1. It asks a measurement question the field really needs answered: how much of a layer-wise depth belongs to the fact and how much to the prompt. Using generalizability theory and a decision study is a good idea that fits the problem.
2. Figure 1 is persuasive. Same facts, same order, two models, with visible spread across paraphrases.
3. The paper is careful about what is measured: a readout at the prediction position, not storage, not the subject position.
4. It openly states that answer-token identity is folded into the fact component.

**Weaknesses (most severe first).**
1. **The construct may not be what it claims.**
   - A final-token patch into a carrier's final token asks when the source's last position holds enough to make the carrier emit the object. That depends on how compatible the carrier is with the source state, not only on the fact.
   - At l = L−1 the carrier outputs exactly the source distribution, so the normalizer is shared. Below that, D1 mixes "the answer has been moved to the last position" with "the carrier's later layers can still use this state."
   - The paper does not say whether X in a carrier is the literal subject string. If it is, the carrier can recall the fact itself at late layers.
   - Figure 1 shows a strong floor: many OLMo cells sit exactly at layer ~18, and Llama clusters at 15–17. That looks like a carrier- or architecture-imposed threshold more than a fact property.
2. **"Paraphrase-related" variance is really prompt-instance variance.** The fact×frame component (the largest, 0.34–0.47) contains any prompt-specific idiosyncrasy of the source state. This includes measurement noise that the three carriers share, because all carriers receive the same source state. Calling it "fact-specific sensitivity to phrasing" (§6) is an interpretation, not a finding.
3. **Absolute scale is never reported.** All shares are of a within-relation variance that, judging from Figure 1, is a few layers out of 32. Readers cannot tell whether "65% paraphrase-related" means 1 layer or 6 layers. That matters for the practical recommendation.
4. **The correctness criterion is narrow.** "Correct" means the top-1 next token equals the object's first token. That throws out ~55–60% of cells (1,221/3,000 for Llama; 1,355/3,000 for OLMo) and three of five models. Qwen3-8B with only 125 qualifying facts suggests the criterion or the frames (articles, leading spaces, Q/A formatting) fail rather than the model's knowledge. Two-model scope weakens every family-level statement.
5. **Study 1 uses all rows, mostly wrong ones.** The paper's own audit shows 3,180 of 3,900 Pythia-1.4B rows are censored and wrong. §3 says D1 "means something different" on wrong prompts, which is why Study 2 restricts to correct cells. Study 1's equivalence result therefore mostly describes a quantity the authors consider uninterpretable.
6. **No subject-position or storage-oriented measure, and no relation×object term.** Both are deferred to future work. Without them the title's "fact-level" means "constant within fact, answer token included."

**Questions to authors.**
- Q1. Is X in the carriers the subject string? What is the carrier-only answer prior, and does D1 move when that prior is high?
- Q2. What fraction of cells sit at the modal layer (the ~18 floor in OLMo)? Is D1 near-constant below some layer for structural reasons?
- Q3. Within-relation SD of D1 in layers, per component?
- Q4. How many Qwen3 failures are near-misses: object in the top-k, or preceded by " the" or whitespace?
- Q5. Does the fact share change if each paraphrase is patched into a carrier sharing its syntactic frame?

**Missing references.**
- Geva et al. 2021 / 2022 (FFN as key-value memories / promoting concepts).
- nostalgebraist 2020 (logit lens).
- Din et al. 2024 (Jump to Conclusions).
- Lad et al. 2024 (stages of inference).
- Biran et al. 2024 (Hopping Too Late).
- Nanda et al. 2023 (Fact Finding).
- Haviv et al. 2023 (memorized idioms, early vs late layers).
- Wendler et al. 2024 (latent language via logit lens).

**Typos / presentation.**
- "ICC(1)" is not the Shrout–Fleiss ICC(1). It is a covariate-conditional share of the carrier-averaged score; rename it or define it.
- The "den" notation and the rt/ft/fc abbreviations are hard to parse.
- Figure 1's caption is a paragraph.
- Table 2 reports 222 facts, the text reports 196 included facts, and neither explains the difference.

**Scores.** Soundness 2.5 / Excitement 2 / **Overall 2.5** (borderline Findings) / Confidence 4.

**Limitations & ethics/AI disclosure.**
- Limitations is mostly adequate: subject position, answer-token identity, correct-only, designed frames, two families.
- It omits the D1 floor/discreteness, the first-token correctness criterion, and Study 1's majority-wrong rows.
- The AI-use disclosure is unusually explicit and compliant.

=====================================================================
REVIEWER 2: Statistics / methodology
=====================================================================
**Summary.** Two preregistered mixed-model studies, as above. Study 1 is an equivalence-style test on ΔR²m (bound 0.02, relation-cluster bootstrap over 26 relations) plus a non-gating discrete-time survival model. Study 2 is a crossed random-effects decomposition (REML), with:
- parametric bootstrap intervals;
- a parametric null for the fact share;
- simulation-based coverage checks;
- a D-study.

**Strengths.**
1. A real preregistration with frozen code. Pass/fail rules are applied mechanically. Failures (H1, H2, H1 in OLMo) are reported as failures.
2. Calibration and robustness simulations are reported even when unflattering:
   - fact-share coverage 0.79–0.89, erring low;
   - single-measure H1 test liberal, 0.05–0.12 vs nominal 0.025;
   - null slightly liberal, 0.020 at α = 0.01.
3. Sensitivities include all cells, new facts only, leave-one-frame-out and template covariates. The fact share is stable across them, 0.231–0.464 (D1).
4. Exploratory analyses are labelled as such.

**Weaknesses (most severe first).**
1. **The confirmatory payload is nearly trivial.** The fact-share null (fact variance = 0) is rejected at the bootstrap floor, and the observed share is ≥ 5.6× the null maximum. With a point estimate of 0.31 and CI [0.24, 0.37], nobody doubted this. The informative contrast is wording − fact:
   - not established in OLMo (D1 CI [−0.004, 0.272]);
   - established in Llama only through a test the authors show is liberal.
2. **Interpretive statements go beyond the licensed results.** The prereg marks "A single prompt is a poor estimate of a fact's depth" as not licensed. §6 nevertheless states "Single-prompt depths are noisy estimates of a fact-level quantity" and recommends averaging. "Most … is paraphrase-related" (Conclusion) holds for point estimates only: OLMo D1 wording CI is [0.482, 0.619].
3. **The exploratory split is reported for D1 only, and it reverses under D4.** The fact×paraphrase vs systematic-wording claim ("most … is fact-specific") is shown for D1:
   - Llama 0.473 vs 0.177; OLMo 0.343 vs 0.203.
   - Under D4 the same file gives Llama 0.372 vs 0.306 and OLMo **0.285 vs 0.327**, i.e. the opposite direction.
4. **Outcome model fit.** A Gaussian LMM is fitted to a discretized outcome ((l*+1)/32) with visible floor clumping. Normality-based parametric bootstrap intervals and nulls inherit the misspecification. The robustness sim does discretize, which helps, but it does not show the observed floor. An ordinal or cloglog-type check is missing.
5. **Selection.** Correct-only analysis means MNAR selection on the outcome's support. Facts have 1–10 correct frames, so fact effects and fact×frame are estimated from unbalanced, outcome-dependent subsets. The D-study then assumes "the same exchangeable paraphrases for every fact." The paper admits this, but n′ should be called optimistic, not just "estimation only."
6. **Study 1 inference.**
   (a) ΔR²m is negative in one model (−0.0003). It is a difference of ML fits whose variance components shift, so it is not a clean effect-size measure.
   (b) A percentile cluster bootstrap with 26 clusters under-covers. The 0.02 bound is not justified as a smallest effect of interest.
   (c) The survival model (prereg B9) has relation frailty only. The three templates per fact and the subjects are unmodelled, and every row has an event (no censoring). So "small, clear association … p ≤ 3.3e-07" uses anti-conservative Wald p-values on what is really an ordinal model of D1.
   (d) The analysis pools correct and wrong rows. Co-occurrence predicts correctness (OR 1.28–1.43), and the paper says D1 means something different on wrong rows. So the co-occurrence slope is confounded by mixture composition. Correct-only ΔR² point estimates (0.0004 / 0.0082 / −0.0006) have no CIs. With ~800 correct rows per Pythia model, the 2.8B upper bound may exceed 0.02.
7. **CI-method selection.** It was done at a second look with 120 simulations per condition. Coverage of 0.925 vs 0.95 is within roughly one Monte Carlo SE. Fine, but describing it as "below nominal" in the Limitations implies more precision than 120 simulations support.

**Questions.**
- Q1. Why not report a TOST-style 90% interval for H3, and how was 0.02 chosen?
- Q2. Report the correct-only H3 bootstrap CI (exploratory).
- Q3. Survival model with fact- and template-level frailty: does p remain small?
- Q4. Is G relative (fact×frame error) or absolute (with frame main effects)? Which components enter G(k)?
- Q5. The ICC denominator divides (fc+e) by n_c. Report the single-carrier share too.
- Q6. In the sims, diff bias is about +0.03 toward H1. Should the Llama H1 estimate be shrunk accordingly?

**Missing references.**
- Shrout & Fleiss 1979.
- Cronbach et al. 1972 (G-theory origin).
- Lakens 2017 (equivalence testing / TOST).
- van Miltenburg et al. 2021 ("Preregistering NLP research", NAACL). Notably absent for a paper titled around preregistration; nosek2018prereg is in refs.bib but never cited.
- Card et al. 2020 (power in NLP).
- Dror et al. 2018.

**Typos / presentation.**
- Abstract ranges pool D1 and D4 without saying so.
- "p is at its floor" should give the floor (1/1001).
- Survival HR CIs are shown for one model only in the text.

**Scores.** Soundness 3 / Excitement 2 / **Overall 2.5** / Confidence 4.

**Limitations & ethics/AI disclosure.**
- Limitations is honest and specific: second-look CI selection, liberal null, non-blind H3, plan written after Study 1.
- It is missing: Study 1's majority-wrong rows, the survival model's clustering, and the Gaussian model on a discrete outcome.
- Compute disclosure ("one GPU session") is insufficient for checklist item C: give GPU type and hours.
- The AI disclosure is adequate.

=====================================================================
REVIEWER 3: Generalist NLP
=====================================================================
**Summary.** Layer-wise "where does the model know X" measurements depend on the prompt. Across 10 paraphrases, roughly 30–40% of within-relation variance in a final-position readout depth is fact-level and the rest is paraphrase-related. A second study finds that pretraining co-occurrence barely explains depth.

**Strengths.**
1. The practical message is useful to interpretability practitioners: average over paraphrases, and n′ ≈ 4–8 gives a concrete number.
2. Transparency is unusual: frozen plans, deviations, an integrity incident, released materials, licence analysis (CounterFact/LAMA CC BY-NC handled correctly).
3. The paper is careful not to overclaim in the Results section itself.

**Weaknesses (most severe first).**
1. **Low excitement relative to its framing.** The single licensed finding ("fact share > 0") is expected. The more interesting claim (wording dominates) holds in one of two models. Prompt sensitivity of localisation is already shown by Chen et al. 2024, Elhelo et al. 2026 and Benz et al. 2026, and in prompt-sensitivity work generally.
2. **Narrow scope.** Two models, English, 300 facts, 10 hand-designed frames, one depth definition. Three of five preregistered models were dropped by an inclusion rule that likely reflects the first-token criterion rather than the models.
3. **The two studies are loosely connected.**
   - Study 1 asks a different question (relation vs co-occurrence) on different models, facts and correctness regime, and reads like a negative-result add-on.
   - The interesting link goes undiscussed: relation share depends strongly on template (per-template ICC_rel 0.13–0.54, appendix), which is convergent evidence for Study 2.
4. **Under-used space.** The main text ends on p.5 of 8. Material a reader needs sits in the appendix or is absent: the absolute scale in layers, Study 1 correct-only results, the D4 split, the carrier definition, how the 300 facts were sampled, and what "new facts" means.
5. **The integrity appendix dominates.** Guard harness, Linux immutable attributes, a hook patch and AI-agent incidents are interesting meta-science, but it takes the space the science needs and may distract ACL reviewers. It reads as process documentation.
6. **"EXACT" counts.** For OLMo-2-1124-7B the olmo-mix-1124 index covers stage-1 only, not the mid-training mix. Co-occurrence within a token window is also a proxy for the fact being stated. "Exact counts in the models' own corpora" overstates this.

**Questions.**
- Q1. Why did Qwen3-8B answer so few?
- Q2. What would a practitioner gain in layers by averaging 8 paraphrases?
- Q3. How were the 10 frames chosen? Would naturally occurring paraphrases (e.g., ParaRel) give different shares?
- Q4. What is the anonymous code link? "Link added at submission" is not provided.

**Missing references.**
- Sclar et al. 2024 (prompt-format sensitivity).
- Mizrahi et al. 2024 (multi-prompt evaluation), the direct analogue of "average over paraphrases".
- Jiang et al. 2020 (How can we know what LMs know).
- Kang & Choi 2023 (co-occurrence and factual knowledge).
- Elazar et al. 2023 (causal effects of data statistics on factual predictions).
- Chang et al. 2024 (factual knowledge acquisition during pretraining).
- Allen-Zhu & Li 2023 (knowledge storage/extraction and paraphrase augmentation).

**Typos / presentation.**
- "licensed sentence" jargon in the Discussion will puzzle readers unfamiliar with the prereg.
- Table 2's "facts / cells 222/1,221" vs 196 included facts is unexplained.
- "the one influential relation" (manufacturer) and "new facts only" are unexplained in the main text.
- Related-work sentence on Merullo/Hernandez is garbled.

**Scores.** Soundness 3.5 / Excitement 2 / **Overall 2.5** / Confidence 3.

**Limitations & ethics/AI disclosure.**
- Limitations is adequate and candid.
- The ethics statement is minimal but sufficient for the topic.
- The AI disclosure is compliant. "The human author" signals a single author but is not deanonymizing.
- Compute reporting is too vague.

=====================================================================
CLAIMS STRONGER THAN THE NUMBERS SUPPORT (paper text vs numbers.tex / results)
=====================================================================
1. **"At most" applies to point estimates, not the bound.**
   - Paper (Intro, contribution 1): "within-relation co-occurrence changes the marginal R² of depth by at most 0.0016 (upper bounds below 0.02)".
   - Numbers: 0.0016 is the largest point estimate (hrDRsqMax). The upper bounds reach 0.0104 (hrDRsqHiMax, results/HR_gate.json, run HR-none-f431f35-20261121T081116Z).
2. **"Relation-level share was small" holds only on all rows.**
   - Paper (Abstract): "the relation-level share was small (≤ 0.060; upper bounds ≤ 0.123)".
   - Same results file, preregistered variants: correct rows only ICC_rel = 0.139 / **0.371** / 0.178. Single templates go up to **0.504** (Pythia-2.8B) and **0.542** (OLMo).
   - §4 itself says "A failed positive test is not a confirmed null."
3. **"Most" fails at the interval level in OLMo.**
   - Paper (Conclusion): "in our estimates most of the within-relation variance of a single prompt's depth is paraphrase-related".
   - Numbers: OLMo D1 wording share 0.546 [**0.482**, 0.619] (results/P2analysis/correct/p2_results.json).
4. **The fact-specific vs systematic split is D1-only.**
   - Paper (§5 and §6): "Most paraphrase-related variance is fact-specific rather than shared across facts (exploratory split)".
   - Numbers: under D4, OLMo systematic 0.327 > fact×paraphrase 0.285; Llama 0.306 vs 0.372 (RESULTS.md §3, EXPLORATORY rows). Only the D1 values are in the paper.
5. **A preregistration-unlicensed headline is restated.**
   - Paper (§6 Implications): "Single-prompt depths are noisy estimates of a fact-level quantity."
   - Numbers: ptClaimSinglePromptPoor = "not licensed" (H1 holds in 1 of 2 families). This restates the prereg's unlicensed headline in different words.
6. **The recommendation extends past what was measured.**
   - Paper (§6): "Comparisons of depth across facts, relations or training checkpoints should average over paraphrases; the decision study gives … how many".
   - The D-study is within-relation, correct cells only, two models. No checkpoint data are reported (the checkpoint analysis is omitted, Appendix "Not reported").
7. **"Clear" association rests on anti-conservative p-values.**
   - Paper (§4): "a small, clear association … (all p ≤ 3.3e-07)".
   - The survival model (prereg B9) has relation frailty only. With 3 templates per fact and no fact or subject term, the Wald p-values are anti-conservative. There is also no censoring under D1.
8. **"Conservative" is claimed for the wrong procedure.**
   - Paper (§5.3): "the fact-share intervals err low, so 'above zero' is conservative here."
   - "Above zero" is decided by the null test, not the intervals. The null rejected 0.020 at α = 0.01 in calibration (ptCalFcOneNcThreeRejOne).
9. **"Exact" overstates OLMo coverage.**
   - Paper (§1/§4): "exact subject–object counts in the models' own corpora".
   - For OLMo-2-1124-7B the index is the stage-1 mix only. The approximation flag rate is not reported anywhere in the paper.

=====================================================================
META-REVIEW
=====================================================================
**Consensus.** The reviewers agree the paper is unusually transparent and statistically careful. They also agree its confirmatory yield is thin, its construct is under-validated, and its scope is two models.
- Overall scores: 2.5 / 2.5 / 2.5.
- Soundness: 2.5–3.5.
- Excitement: 2.

**THREE WEAKEST POINTS (most damaging first)**

**1. The confirmatory result is near-trivial, and the interpretive layer goes beyond it.**
- The only licensed finding, "fact share > 0", was never in doubt (ICC 0.28–0.42).
- Wording > fact is established in one of two models, through a test shown to be liberal.
- Yet the Discussion, Implications and Conclusion state the unlicensed claims: "single-prompt depths are noisy", "most … is paraphrase-related", "most … is fact-specific" (D1 only; it reverses for OLMo under D4).
- *Fix without new experiments:*
  - Reframe as an estimation paper: shares with CIs, n′, and G(1) ≈ 0.4–0.5.
  - Remove or explicitly mark as unlicensed the "noisy single prompt" and "most" sentences.
  - Report the D4 exploratory split next to D1.
  - Report absolute SDs in layers (already computed as exploratory values, ~1 layer per component).
  - State that "above zero" was expected.
- *Needs new experiments:* more families. Fixing the first-token correctness criterion (e.g., greedy multi-token match) so Qwen3 and Pythia are included would turn 1/2 into a real cross-family test.

**2. Construct validity of D1.**
- The final-token readout through carriers is discretized to 32 layers with visible floor clumping.
- "Paraphrase-related" variance is any prompt-instance variance, including measurement noise shared by the carriers.
- The fact component includes answer-token identity.
- The narrow first-token correctness criterion excludes ~55–60% of cells and 3 of 5 models.
- *Fix without new experiments:*
  - Define the carriers exactly (is X the subject?).
  - Report the share of cells at the modal or floor layer.
  - Add an exploratory ordinal-model sensitivity on the stored data.
  - Rename "wording share" to "prompt-level share" or justify the stronger name.
  - Add an exploratory refit with (1|relation:object) on the stored data, labelled as such.
  - Add these items to Limitations.
- *Needs new experiments:*
  - subject-position patching with a matching depth rule;
  - carriers that do not contain the subject;
  - alternative correctness criteria.

**3. Study 1 validity and coherence.**
- The analysis runs on all rows, ~80% of them wrong in Pythia (720 of 3,900 correct in 1.4B). The paper itself says D1's meaning differs in that regime.
- "Relation share small" is contradicted by the correct-only (0.371) and per-template (up to 0.54) variants.
- The survival "clear association" uses anti-conservative p-values.
- For OLMo, "exact" counts cover stage-1 only.
- Study 1 is weakly tied to the title question.
- *Fix without new experiments:*
  - Move the correct-only and per-template results into the main text and soften the abstract's "small".
  - Compute correct-only H3 bootstrap CIs on existing data (exploratory).
  - Describe the survival model as a relation-frailty ordinal model with a clustering caveat.
  - Report approx-flag rates and the stage-1 coverage.
  - Tie Study 1's template dependence to Study 2's wording result, or shorten Study 1.
- *Needs new experiments:* counts over OLMo-2's mid-training data. A correct-only H3 needs no new experiments; a properly powered one would need a design with more correct rows (larger models or easier facts).

**Limitations / ethics / AI disclosure.**
- Limitations is adequate and candid, but should add the three omissions above.
- Ethics is sufficient.
- AI-use disclosure is explicit and policy-compliant.
- Compute reporting is too vague for the Responsible NLP checklist.
- The code link is missing.

**Likely outcome.** Not accepted to the main conference. The scores (~2.5) are borderline for Findings: rigour and transparency count in its favour; the near-trivial licensed claim, two-model scope and unvalidated construct count against it. The most likely meta-recommendation is a resubmission to a later cycle, possibly with Findings as a fallback if the area chair weights the methodological contribution.

VERDICT: Borderline Findings / likely reject from Main (overall ≈ 2.5); revise and resubmit with the claim–license alignment, construct-validity reporting, and expanded model coverage.
