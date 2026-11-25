G5 round-3 claim audit (read-only). Files: /home/user/depth-law/paper/main.tex, appendix.tex, numbers.tex.

scripts/check_numbers.py output: `check_numbers: ok`.
Note: my first Bash call, a compound command that also catted a file under reports/, was blocked by the hook. I re-ran the script alone and used Read and Grep for the rest.

**R2-1 (was BLOCK): FIXED.** Table 1 is at main.tex:159-193. Macros are correct and all exist in numbers.tex (checked by grep).
- Split-half reliability per model: \hrSplitHalf{PyOneFour,PyTwoEight,OlmoSeven} = 0.929, 0.897, 0.943 (main.tex:176).
- Frailty SD per model: \hrSurvFrailtySd* = 0.359, 0.392, 0.410 (main.tex:177).
- H2 rho with CI for 1.4B-OLMo, 2.8B-OLMo and 1.4B-2.8B (main.tex:180-182). The Pythia pair is marked with a dagger ("does not count") in main.tex:179 and :191. Its raw and controlled pass cells read "does not count" (main.tex:188).
- Partial rho (main.tex:183). Only its CI lower bound is shown (main.tex:184), which is what the criterion uses.
- rho minus covariate-only rho gap: \hrRhoGap* (main.tex:185).
- Disattenuated rho: \hrDisatt* = 0.555, 0.649, 0.911 (main.tex:186).
- Frailty-BLUP Spearman per pair: \hrRhoSurvFrailty* (main.tex:187).
- Two small points:
  - The caption does not state the H2 thresholds for partial rho (0.5), its lower bound (0.2) and the gap (0.15), although the \hrThrPRho, \hrThrPRhoLo and \hrThrRhoGap macros exist.
  - The caption gloss "Split-half rel.: reliability of the relation effects (H2)" I could not check against the prereg text. It is UNVERIFIED.

**R2-2 (was BLOCK): FIXED.** Both sentences I flagged are gone.
- main.tex:328 gives the D1 and D4 splits and says "in OLMo under D4 the systematic part is the larger one. Which part dominates depends on the measure."
- main.tex:331 states that the pair differences include measurement noise with no baseline. It says the frame-mean range (H4) is "comparable to the standard deviation of the fact effects".
- main.tex:332 says "Under D1, fact-specific sensitivity... is the larger part; systematic frame effects are not negligible, and under D4 they are as large." This is consistent with the split numbers.
- The Discussion at main.tex:376 reads "under D1 the larger part of it is fact-specific, under D4 not in OLMo (EXPLORATORY)". I checked this against the figures in my round-2 audit: D4 fact×paraphrase 0.372/0.285 against systematic 0.306/0.327. The wording holds for Llama and OLMo.
- main.tex:330, "Small edits move depth about as much as larger ones", is now hedged by the noise-baseline sentence that follows it. This is acceptable.

**R2-3: FIXED.** main.tex:369-371 labels the G(1) estimate EXPLORATORY and calls it "an estimate only". It says the "poor estimate" sentence is not licensed and that the estimate does not transfer. The recommendation shrinks to "reporting... how many paraphrases were used".

**R2-4: FIXED.** The "about half" wording is gone. main.tex:385 reports the object-term shares and the frozen fact shares as point values, labelled EXPLORATORY. The Table 5 caption (main.tex:303) discloses the non-converged OLMo D4 fit and the singular fit.

**R2-5: FIXED.** main.tex:155 now reads "non-zero in both Pythia models while OLMo's interval touches zero... per unit of within-relation log1p co-occurrence, given the covariates". main.tex:379 uses log1p.

**R2-6: FIXED.** main.tex:339 says "the estimated number of paraphrases per fact is…". The word "needs" is gone.

**R2-7: FIXED.** main.tex:146 gives the template-alone range \hrIccTemplateMin–Max. main.tex:378 says "up to \hrIccTemplateMax".

**R2-8: FIXED.** main.tex:147 now reads "is of the same kind as".

**R2-9: FIXED (minor residue).** main.tex:59 reads "easily read as a property of the fact, but it is also a property of the prompt". main.tex:368 reads "may bear". The claim "usually taken on one prompt per fact" (main.tex:58) and "typically use one prompt per fact" (main.tex:363) rest on three papers, so "usually" and "typically" are mild generalisations. Say "in the three studies we checked". Also, main.tex:365 has a stray ", (" before the section reference.

**R2-10: FIXED.** main.tex:154 now reads "co-occurrence predicts correctness (odds ratio…)".

**R2-11: FIXED.** main.tex:132 defines the logit-lens onset: the first layer from which the object stays rank one when the final position is decoded directly.

**R2-12: FIXED.** main.tex:407 says fp32. configs/prereg_amendment_2026-11-20.yaml:36 states "fp32 weights for every gate model", so Study 1 is covered.

**R2-13: PARTLY.** The abstract (main.tex:43) says "relative generalizability coefficient... under the primary depth", but not "correct prompts". The sentence just before it (main.tex:42) is also scoped to correct prompts only through main.tex:41. Add "on correct prompts" to main.tex:43. The contribution at main.tex:73 has the scope.

**R2-14: FIXED.** The Geva gloss "one query per triplet" is gone. The three quotations stand as quoted. Fix the stray comma at main.tex:365.

**F8: FIXED.** main.tex:59 is now softened and balanced with "but it is also a property of the prompt". The remaining uncited attribution is only "usually", see R2-9.

**F16: FIXED.** main.tex:352 now reads "the only relation flagged as influential in the earlier decomposition".

**F21: FIXED.** main.tex:413 now reads "Claims were checked at human gates." The "last before submission included" is gone. G5 has no verdict yet, but the sentence no longer claims it.

**F24: FIXED.** appendix.tex:67 now says "method-of-moments and REML shares differed noticeably for some components". It adds that the bootstrap intervals and null were not rerun and that no one recomputed the S1 results. The unverifiable "a human read every gate report" became "Each gate decision was made by the human author" (appendix.tex:68).

**New problems in the changed sentences (all non-blocking):**
1. main.tex:379 (Discussion) reports the co-occurrence slope ("at most a fraction of a layer") without the EXPLORATORY label. The slope is EXPLORATORY at main.tex:155. Add the label.
2. main.tex:43 (abstract) lacks the "correct prompts" scope (see R2-13).
3. main.tex:378 says "relation effects too depend on the prompt". The evidence is the template-alone ICC range, which is a non-gating preregistered variant. "Vary with the template" is safer than "depend".
4. Table 1 does not state the H2 thresholds for partial rho, its lower bound and the gap.
5. No banned words appear in the changed text. I did not re-run the full banned-word grep, only the changed passages.

VERDICT: PASS
