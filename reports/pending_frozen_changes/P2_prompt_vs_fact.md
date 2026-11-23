<!-- STAGED DRAFT for the human. Intended path: prereg/P2_prompt_vs_fact.md. Claude cannot write prereg/
     (permission deny rule Edit(prereg/**), protect_frozen.py, pre-commit). The human installs it, commits it
     before any P2 GPU data exists, and records the commit in prereg/HASH_P2.txt / PROGRESS.md. -->
# Preregistration P2: prompt vs fact in causal resolution depth

- **Status:** DRAFT 2026-11-21, revised 2026-11-22 and 2026-11-23 after the PREREG gate reviews (stats-reviewer rounds 1 and 2; human decisions of 2026-11-22 and 2026-11-23). Written before any P2 data exist. No P2 model run has been made; only pythia-70m plumbing runs (5 facts × 2 paraphrases) and synthetic-data tests.
- **Freeze:** this file is committed and tagged `prereg-P2` before the GPU session.
- **Decision text:** sections 1–9, as written. Deviations go in `prereg/deviations/` as `D-P2-<session UTC>-<n>.md`, with reason and UTC time, written before any rerun (section 9).

## 0. Disclosure (data seen before this file)
- **G1 / E-depthvar (EXPLORATORY):** variance shares of D1/D4 on S3b rows of pythia-1.4b, pythia-2.8b and OLMo-2-7B (3 templates per relation, 26 relations, correct cells).
  - Fact+subject 0.29–0.48 of total, template-main 0.05–0.37, residual 0.12–0.24, relation 0.09–0.33.
  - Within-relation ICC(1) 0.37–0.64.
  - The OLMo wording advantage drops to 0.009 without `company_ceo` (`reports/gates/G1/GATE_G1.md`, `analysis/exploratory/E-depthvar/*PART0A_REPORT.md`).
- **Earlier preregistered and exploratory results** on these models: H-R gate (`results/HR_gate.md`), amendment 2 (`reports/GATE_A2.md`), C1 re-analysis.
- **Fact overlap:** 74 of the 300 P2 facts were among the 1300 facts analysed in G1 (their 3 old templates differ from the P2 paraphrases). All 300 are primary; the 226 facts not analysed in G1 form a preregistered sensitivity set (section 3; list `materials/facts_v1_not_in_G1.json`, sha256 bce491a37d1f61713727233c4226a399d4eae67605648266f8c38e03c2688079).
- **Excluded relations:** `company_ceo` was excluded by the prespecified first-token rule (`materials/SAMPLING_RULES_v1.md`: 45% of its pool fails the distinct/contentful first-token rule). It drove OLMo's G1 result: leaving it out moved the OLMo D1 diff from 0.199 to 0.009 (Part 0a). P2 therefore cannot test that relation.
- **New data:** nothing from Qwen3-8B or Llama-3.1-8B has been run or seen.

## 1. Design (materials frozen with this file)
| item | file | sha256 |
|---|---|---|
| facts: 300 = 20 relations × 15, 5 per co-occurrence tercile (DCLM EXACT phrase counts, labelled PROXY), seed 20261121, rules `materials/SAMPLING_RULES_v1.md` | `materials/facts_v1.jsonl` | 0f596cd7385a318b9f2d8bea84d5d8cf483ee62c9333fa3bec0ecd60d9f1bfe3 |
| paraphrases: 10 per relation = 8 shared frames + 2 lexical variants | `materials/paraphrases_v1.jsonl` | dd481a359860bcb4a8cfec6ed6e85a35904dfcc42b7042a4278d030c1c707548 |
| carriers: `{} is associated with` (existing) + `{} is linked to`, `A word that goes with {} is` (new) | `materials/carriers_v1.jsonl` | dea5a8910cb356d8b42c8d91f09db9cecb646a924bba23e9ea3b07578258aadd |

- **Frames:** the 8 frames are order (subject-first / relation-first) × form (cloze / "Q: …? A:") × length (short / long). The long version adds the shared neutral clause "According to reference sources, ".
- **Prompt checks:** every prompt ends where the next token is the answer's first token. Subject appears exactly once and the answer string is absent in 3000/3000 prompts (`materials/paraphrases_v1_report.md`).
- **Models, in order, one GPU session** (rented RTX Pro 6000 Blackwell 96GB, fp32; balance about INR 740 after the human's INR 500 top-up; minute budget floor(740/207.36·60) − 15 = 199): Qwen/Qwen3-8B, meta-llama/Llama-3.1-8B, EleutherAI/pythia-1.4b, EleutherAI/pythia-2.8b, allenai/OLMo-2-1124-7B.
- **Pilot gate:**
  - The first 20 facts (2 chunks) of Qwen3-8B run first with 3 carriers.
  - Measured seconds per unit project the full cost of all five models.
  - If the projection exceeds the remaining budget, the fallback order below is applied, and logged as a deviation, before the rest of the session.
  - Per-model checks are also made before each later model. They compare the remaining minutes with that model's static upper estimate (`scripts/p2_gpu_run.sh`, UP3/UP2):
    - a model that does not fit with 3 carriers runs with 2;
    - a model that does not fit with 2 is skipped.
  - Any model may be skipped this way, including one early in the order (e.g. Llama or pythia-2.8b) while a later, smaller model still runs.
  - A failed Llama-3.1-8B access check also skips Llama.
  - A model that crashes or fails the done-check is MISSING (incomplete).
  - Every such case writes a deviation file before the step.
    - File names carry the session's UTC start time (`D-P2-<UTC>-<n>.md`), so a later session never overwrites an earlier record.
    - Deviation files and the session log are copied off the instance after every deviation, after the pilot projection, after every model and at the hard stop (`SYNC_DEST/_session_<UTC>/`, `rsync --mkpath`, rsync ≥ 3.2.3).
    - The result of each copy is logged.
  - The driver logs the git revision with a dirty flag, and stops if the materials' sha256 differ from the table above.
- **One run per model:**
  - The run analysed for a model is its **first run that passes the completeness rule**.
  - A later run replaces it only through a committed deviation that names the run_id it replaces.
  - The analysis refuses two runs of the same model in one call.
- **Measurement** (`src/depthlaw/p2/run_p2.py`):
  - For each fact × paraphrase, write the final-token residual at the output of every block into the final token of each carrier (filled with "X").
  - Store p(object first token) as float16 and its rank as int16 at the carrier's final position, for every layer.
- **Compute fallback order** (if the projected cost exceeds the minute budget):
  1. Drop to 2 carriers (drop carrier 2). Chunks already run with 3 carriers keep them. The carriers analysed follow the nc rule of section 3.
  2. Drop Llama-3.1-8B.
  - Each step is logged as a deviation before continuing.
- **Hard stop:** at the minute budget (`scripts/p2_gpu_run.sh` arms an auto-stop). A partly run model is reported as MISSING (incomplete).
- **Completeness rule:** one rule, `completeness()` in `analysis/p2/p2_analysis.py`. The driver's done-check (`scripts/p2_done_check.py`) calls the same function. A model is analysed only if all of these hold; otherwise it is MISSING (incomplete) and excluded:
  - its run dir has a `manifest.json` with every checksum ok;
  - the last `log.jsonl` event is a successful `done` covering all 300 facts;
  - all 300 × 10 fact × paraphrase cells have behaviour rows and curves;
  - no p value is NaN;
  - every cell has carriers 0..k−1 with k ≥ 2, and all curves have the same number of layers.
  - A resume (e.g. after the pilot) sets any earlier `manifest.json` aside, so a pilot manifest cannot stand in for a complete run.
  - The checksums are recomputed at analysis time, so a copy damaged after the run is caught.
- **Run identity** (the gating call): every `start` event of a run must name the model it is given for, with dtype float32, and every meta file must record revision main. Otherwise the call is refused.
- **Session stop flag:** the budget timer writes a session-specific flag (`STOP_P2_<session UTC>`), so a flag left by an earlier session cannot skip models in a later one.

## 2. Outcomes
- **Primary D1, per carrier:** l\* = min l with p(l') ≥ 0.5·p(L−1) for all l' ≥ l; value (l\*+1)/L.
- **Required robustness, D4:** 1 − mean_l min(1, p_l/p_final).
- **Secondary:**
  - D2: stable p ≥ 0.1 onset; censored if the final p < 0.1.
  - D3: stable rank-1 onset; censored if not rank 1 at the last layer.
  - Censored D2/D3 rows are dropped from their fits, not modelled as censored.
- **Undefined D1/D4:** if the final p is 0 (float16 underflow), D1 and D4 are undefined for that curve, because every layer would pass p ≥ 0.5·0. The curve is dropped from D1/D4 fits. The count is reported per model, with the count of curves whose final p < 1e-4, where the float16 threshold is coarse. This matters mainly for the all-cells sensitivity.
- **Carrier averaging:** shares are reported on the carrier-averaged scale (section 4).

## 3. Inclusion
- **Primary:** correct cells, i.e. (fact, paraphrase) where the model's top-1 next token on the paraphrase is the object's first token.
- **Minimum data** (human decision 2026-11-22 on review item 11). A model enters the confirmatory analysis only if, among its correct cells:
  - ≥ 150 of the 300 facts have ≥ 2 correct paraphrases; and
  - those facts cover ≥ 15 of the 20 relations.
  - Otherwise the model is MISSING (insufficient data) for every set.
- **Selection caveat:** selecting correct cells makes inclusion depend on the model's behaviour, which can bias the components. The all-cells and all-10 sensitivities address this in part.
- **Which models and carriers** (human decision 2026-11-23 on round-2 finding 4).
  - The confirmatory call (`--set correct`) is given one entry for each of the five models of section 1: its run (section 1), or `MODEL=none` if it has no run, which makes it MISSING (not run).
  - The call is refused unless it names exactly those five models and uses 1000 bootstrap resamples and 1000 null datasets. The `--test` flag lifts these checks for synthetic runs only, and marks every output non-gating.
  - A model is **included** only if it passes the completeness rule (section 1) **and** the minimum-data rule above. Otherwise it is MISSING and excluded.
  - **nc = the smallest carrier count among the included models.** A MISSING model has no effect on nc. nc is written to `p2_results.json`.
  - Every sensitivity call passes `--primary <confirmatory output dir>`. It reuses that call's nc, and it is refused unless its `--runs` are the same as the confirmatory call's.
  - Sensitivity outputs are marked `"gating": false`. Only `--set correct` decides the claims of sections 5–6.
- **Sensitivities (preregistered; reported, not gating; code frozen, `--set` values in brackets):**
  - the 226 facts not analysed in G1, correct cells (`new226`);
  - all cells, every fact × paraphrase correct or not (`all`);
  - facts correct under all 10 paraphrases (`all10`);
  - `manufacturer` dropped, the only Part-0a influential relation in the sample (`nomanufacturer`);
  - the template-covariate model of section 4 (`tcov`);
  - leave-one-frame-out of the decision quantities: point estimates of ICC(1), diff and MoM diff for D1 and D4, with each of the 10 frames dropped in turn (`lofo`).

## 4. Model
- **Formula,** fitted on carrier-level rows (fact × paraphrase × carrier) by REML with lme4 convergence checks ON (`calc.derivs = TRUE`); singular fits and warnings are logged:
  `y ~ n_answer_tokens + n_subject_tokens + log_cooc_proxy + answer_prior + carrier + (1|relation) + (1|frame) + (1|relation:template) + (1|fact) + (1|fact:template) + (1|fact:carrier) + residual`
- **Covariates:**
  - The four covariates are fact-level and z-scored within model × set.
  - `carrier` is a fixed effect with 2–3 levels.
  - answer_prior is the object first-token log-prob on the carriers alone, averaged over the carriers used.
  - n_subject_tokens is the subject's token count as it appears in the fact's 10 paraphrases, averaged: no leading space at the start of a prompt, a leading space after a word. (Changed before freezing, after stats-reviewer round 3, item 13: before, it was always counted with a leading space.) n_answer_tokens counts the object with a leading space, as it follows the prompt.
  - Template-level covariates (template length and subject-to-final distance, in tokens) are not in the primary model, because they would remove wording variance by construction. They go in the `tcov` sensitivity model.
  - **ICC(1) is conditional on these covariates.** It is the share of variance in depth not explained by frequency, length, answer prior and carrier. It is not directly comparable with the unconditional G1 values in section 0 (0.37–0.64), and H1-alt's 0.5 is not to be read against them.
- **Frames as a random factor:** the 10 frames are a 2×2×2 factorial plus two lexical variants, not exchangeable draws, and their variance has 9 df. The wording share describes variation over frames like these.
- **Changes from the human's original formula** (proposed by Claude, accepted by the human 2026-11-22, written before any data):
  - `relation:template` is fitted as relation × frame. Each paraphrase id is one of the 10 frames shared by all relations, so the two terms are the same factor.
  - `(1|fact:template)` is added. Without it, the fact × wording interaction (G1's "residual") is pooled with carrier-level noise; the G1 skeptic and stats-reviewer flagged that conflation. The combined residual is also reported.
  - `(1|subject)` is dropped. All 300 subjects are distinct, so subject and fact are the same factor and cannot both be estimated (the G1 replicator found them confounded).
- **Change after stats-reviewer round 1** (accepted by the human 2026-11-22, before any data): a `carrier` fixed effect is added.
  - Without it, a systematic difference between carriers would be absorbed into fact:carrier variance and would lower ICC(1) and the wording share.
  - Fixed effects do not enter the shares. That the CI-method selection below still applies with this fixed effect and the four covariates is an **assumption**: the CI-method simulations had neither covariates nor a carrier effect. The robustness simulation below fits the frozen formula.
  - A carrier × relation interaction would still be absorbed into fact:carrier (Limitations).
- **Shares** (within relation, carrier-averaged; nc = number of carriers):
  - den = fact + rt + frame + ft + fc/nc + e/nc.
  - **Primary fact share = within-relation ICC(1) = fact / den.**
  - Wording share = (rt + frame + ft) / den; diff = wording − ICC(1).
  - The share of total variance (relation included) is also reported for every component.
  - G(k) = fact / (fact + ft/k + fc/nc + e/(k·nc)), for the same k paraphrases for every fact.
  - Φ(k) adds (rt + frame)/k.
  - n′ = min k with G(k) ≥ 0.8. If G(k) < 0.8 for every k ≤ 30, n′ is undefined.
    - As k grows, G(k) tends to the ceiling fact/(fact + fc/nc), which is set by carrier noise that paraphrases cannot average out.
    - An undefined n′ therefore does **not** meet the "it takes N paraphrases" rule (section 6), and the ceiling is reported. This was changed before freezing, after stats-reviewer round 3, item 3: before, an undefined n′ was coded 31 and counted as ≥ 8.
    - The bootstrap CI of n′ still codes an undefined value as 31, for reporting only.
  - Template + frame minus residual = (rt + frame − ft − e/nc) / den. The "residual" here is the combined fact × paraphrase residual on the carrier-averaged scale (ft + e/nc).
- **Estimators:**
  - REML primary.
  - Henderson-III method-of-moments sensitivity (`analysis/p2/p2_mom.py`; its algebra is unbiased in self-test).
  - **What MoM estimates.**
    - The input is carrier-averaged cell means of y, after y is residualised by OLS on carrier-level rows on the same four covariates and the carrier fixed effect (`mom_cells`).
    - On this scale MoM's fact component is fact + fc/nc and its residual is ft + e/nc; den is the same as REML's.
    - So MoM ICC(1) is not the REML ICC(1), and **MoM diff is not the REML diff**. In expectation, MoM diff = REML diff + (e − fc)/(nc·den).
    - The check is therefore not symmetric:
      - when fc > e, the MoM condition for H1 is harder than the REML one;
      - for H1-alt, REML ICC(1) ≥ 0.5 implies in expectation MoM diff ≤ −2·fc/(nc·den) < 0, so the MoM condition is nearly redundant there.
    - The MoM components were checked on carrier-level synthetic data with fc, a carrier shift and a covariate (`analysis/p2/p2_test_mom.py`, 200 replicates): fact + fc/nc and ft + e/nc were recovered with relative bias ≤ 0.05.
    - The diff offset itself is smaller than that test resolves: predicted +0.0135; mean MoM diff 0.204 against a predicted 0.216 and a REML diff of 0.203.
  - MoM diff is computed from the **raw** (untruncated) components. Negative raw components are truncated at 0 only for the reported shares, so truncation cannot flip the sign of diff. If the raw denominator is ≤ 0, MoM is MISSING. (Changed before freezing, after stats-reviewer round 3, item 2.)
  - MoM is used only as a **direction check on diff** (wording − fact):
    - H1 needs MoM diff > 0;
    - H1-alt needs MoM diff < 0;
    - both under D1 and D4.
  - REML/MoM agreement applies to H1 and H1-alt only.
- **Failed fits and refits** (human decisions 2026-11-22 on review item 10, and 2026-11-23 on round-2 finding 3):
  - boundary (zero) variance estimates are accepted and reported;
  - singular fits and convergence warnings are reported and do not change any rule;
  - a fit with more than 5% failed bootstrap refits in its ICC(1) or diff column is MISSING; a fit that errors is MISSING.
  - **Each rule is evaluated on the fits it uses.** A rule whose inputs are MISSING is MISSING for that model, and that model does not count toward it. The model stays included for its other rules:

    | rule | inputs |
    |---|---|
    | H1, H1-alt | REML D1 and D4 fits, MoM D1 and D4 |
    | "no fixed layer" | REML D1 |
    | n′ | REML D1 |
    | template + frame vs residual | REML D1 |
    | "fact share > 0" | the parametric fact-share null, which refits D1 itself |

    - The rules that also need H1 or H1-alt are MISSING whenever H1 or H1-alt is.
    - A MoM failure makes H1 and H1-alt MISSING for that model, not false.
  - H3 pairs with a MISSING D1 fit are MISSING.
  - The fits are written to `p2_results.json` before any decision is computed.
- **CIs:** parametric `bootMer` (`type = "parametric"`, `use.u = FALSE`), 1000 resamples, 95% percentile intervals (quantiles 0.025 and 0.975); `analysis/p2/p2_analysis.R` with `boot=param`.
  - The selection rule: coverage ≥ 0.90 and |bias| ≤ 0.05 for ICC(1) and diff in both simulated conditions.
  - The simulations used the P2 layout (300 facts, 20 relations, 10 frames), with these simplifications:
    - Gaussian y;
    - 50% of fact × paraphrase cells missing completely at random;
    - nc = 3;
    - no covariates and no carrier effect;
    - true values of ICC(1) 0.372 / 0.709 and diff 0.206 / −0.461, away from the decision boundaries.
  - 500 resamples were used in the simulations and 1000 in the analysis; more resamples only reduce Monte Carlo error in the interval ends.
  - The simulations fitted with `calc.derivs = FALSE`, which changes only the convergence warnings, not the estimates.
  - **How it was chosen (two looks, both on record).**
    - v1 (`reports/p2/P2_bootsim_report.md`, 60 simulations per condition, 100 resamples) compared the two-way cluster bootstrap with parametric `bootMer`. No method met the rule.
      - v1's prespecified tie-break had preferred the two-way bootstrap, which under-covered (0.733–0.917).
      - Parametric `bootMer` missed narrowly: diff coverage was 0.883 in the edepthvar_like condition (Monte Carlo SE sqrt(0.883·0.117/60) = 0.041).
      - The 100 resamples add Monte Carlo noise to v1's interval ends.
    - v2 (`analysis/p2/bootsim_v2_plan.md`, committed before launch) was a second look proposed after that near-miss and approved by the human on 2026-11-22. It tested parametric `bootMer` only: 120 simulations per condition, 500 resamples, a new seed base (20261122), the same two conditions and the same thresholds. It evaluated 95% and then 97.5% intervals, with the rule fixed in advance.
    - v2 result (`reports/p2/P2_bootsim_v2_report.md`): the 95% intervals passed in both conditions, so the 95% level is used.
      - ICC(1) coverage 0.958 and 0.925; diff coverage 0.950 and 0.933 (Monte Carlo SE 0.018–0.024).
      - |bias| ≤ 0.006.
      - One-sided misses at 95%, out of 120 per condition (edepthvar_like, fact_dominant), computed from `results/P2sim_v2/p2_bootsim_v2.json`; nominal is 3/120 per side:
        - truth below the lower bound: ICC(1) 4 and 5 (the error that matters for H1-alt); diff 1 and 3 (the error that matters for H1);
        - truth above the upper bound: ICC(1) 1 and 4; diff 5 and 5.
      - Pooled v1 + v2 parametric diff coverage in edepthvar_like: (53 + 114)/180 = 0.928.
  - **Caveats.**
    - The method was chosen at the second look, and the second look gave two chances to pass (95%, then 97.5%).
    - Coverage of 0.925 (Monte Carlo SE 0.024) in the fact_dominant condition is below the nominal 0.95. It does not establish coverage ≥ 0.90: one-sided 1.96 SE below is about 0.88.
    - A parametric bootstrap tested on data from its own model mainly checks the implementation, and the simplifications above were not tested.
- **Robustness simulation** (human approval 2026-11-22; non-selecting; reported next to the results; it cannot change the CI method or any decision):
  - parametric `bootMer` 95% coverage of ICC(1) and diff, fitting the frozen formula (four covariates and the carrier fixed effect), with:
    - D1 discretised to (l\*+1)/L, L = 24 and 36;
    - missingness tied to correctness (cells more likely missing when the latent depth is late);
    - nc = 2 and nc = 3, with a carrier shift;
    - true values near the boundaries: ICC(1) 0.4–0.5 and diff ≈ 0.
  - Its code is written and committed before it runs. It runs only when no other heavy job is running, and it does not delay the freeze or the GPU session.
- **Fact-share null: parametric bootstrap** (`analysis/p2/p2_null.R`, `p2_null_fns.R`; set correct; D1). H0: fact variance = 0, with every other component as estimated.
  - **null model:** the primary model of this section without `(1|fact)`. It keeps the covariates, the carrier fixed effect and every other random term, including `(1|fact:carrier)` and `(1|fact:template)`. Fitted by REML;
  - **simulation:** 1000 datasets from the null model (lme4 `simulate`, new random effects and residuals, seed 20261121);
  - **statistic:** the full primary model is refitted on each simulated dataset (lme4 `refit`), and its fact share ICC(1) gives the null distribution. The observed statistic is the primary fit's ICC(1);
  - **p** = (1 + #{null ICC(1) ≥ observed}) / (1 + number of successful refits). Failed refits are dropped and their number is reported;
  - the null's fits use `calc.derivs = FALSE` for speed, which changes only convergence warnings, not estimates;
  - "fact share > 0" is accepted for a model only if p < 0.01. The sentence needs this in ≥ 2 families (section 6). The null gates only that sentence.
  - **Change made before freezing, after stats-reviewer round 3** (human decision 2026-11-23, before any P2 data). It replaces the shuffled-fact null.
    - That null permuted fact labels within relation × paraphrase cells. This also removed fact:carrier, so it tested fact = fact:carrier = 0, not fact = 0.
    - The p-value formula, the p < 0.01 threshold and the headline sentence are unchanged.
  - **Calibration and power** (`analysis/p2/p2_null_calib.R`, `results/P2null_calib/`; filled in below before freezing): **[calibration results]**
- **Multiple comparisons:** no further correction is applied.
  - Within a model, H1 and H1-alt are conjunctions (D1 and D4, REML and MoM), i.e. intersection-union tests.
  - Across models, a claim needs at least 2 of up to 4 families.
  - There is no family-wise control across the headline sentences.
  - Round 1's rough estimate of a false claim from ≥ 2 one-sided false passes among 5 models at α = 0.025, assuming independence, was about 0.006.
- **Seed:** 20261121 everywhere.

## 5. Hypotheses (per model; a claim needs ≥ 2 model families)
- **H1 (wording):** wording share > ICC(1), with the 95% CI of the difference excluding 0, under D1 **and** D4, and the MoM difference > 0 under both.
- **H1-alt (fact):** ICC(1) ≥ 0.5 with lower 95% CI ≥ 0.4, under D1 and D4, and the MoM difference < 0 under both.
  - **Change made before freezing, after stats-reviewer round 1** (human decision 2026-11-22, before any P2 data). The MoM condition was "MoM ICC(1) ≥ 0.5" and is now "MoM diff < 0".
  - Reason: MoM's fact component includes fact:carrier/nc and its input had no covariate adjustment, so MoM ICC(1) is a different quantity from the REML ICC(1), and a 0.5 threshold on it would not mean the same thing. MoM is kept as a direction check only.
  - The REML thresholds of H1 and H1-alt are unchanged.
- **Other changes that affect H1 and H1-alt** (same review batch, human decisions 2026-11-22 and 2026-11-23, before any P2 data):
  - the REML model has a `carrier` fixed effect (section 4);
  - the MoM input is residualised on the covariates and the carrier fixed effect; before, it was raw carrier-averaged cell means;
  - "≥ 2 models" became "≥ 2 families";
  - each rule is evaluated on the fits it uses (section 4).
- **Families and claims** (human decision 2026-11-22 on review item 4):
  - "≥ 2 models" means ≥ 2 models from ≥ 2 families. The families are Qwen3, Llama-3.1, OLMo-2 and Pythia; pythia-1.4b and pythia-2.8b count as one family.
  - Only models that are not MISSING, and whose inputs for that rule are not MISSING, count.
  - Within one family, a model meeting H1 and another meeting H1-alt count toward both, including for the conflict rule.
  - A model name outside these families is refused by the analysis.
  - **Conflict rule:** if H1 and H1-alt each hold in ≥ 2 families, no headline sentence that depends on H1 or H1-alt is used. The result is reported as model-dependent, with per-model shares.
- **Description bands for fact ICC(1)** (human, 2026-11-22). These describe the point estimate with its CI and are not a decision rule:
  - < 0.15: prompt-dominated;
  - 0.15–0.4: mixed;
  - 0.4–0.7: moderately fact-stable;
  - > 0.7: fact-stable.
- **H2 (estimation):** ICC(1) [CI] and n′ for G = 0.8 [CI].
- **H3 (estimation):** cross-model Spearman ρ of fact-level mean depth (D1, correct set), raw and disattenuated approximately by sqrt(G(k̄_x)·G(k̄_y)).
  - k̄ is the mean number of correct paraphrases per fact in that model, because correct-set fact means average fewer than 10 paraphrases.
  - Spearman disattenuation by G is an approximation, used for estimation only.
- **H4 (EXPLORATORY):**
  - order and form effects: frame fixed effects replacing (1|frame) in a separate fit, with point estimates (`--set h4`);
  - whether the wording share is larger in Qwen3-8B / Llama-3.1-8B / OLMo-2-7B than in Pythia.

## 6. Headline wording rules (enforced by claim-auditor; primary set; computed in `p2_decision.json`)
Every rule needs ≥ 2 families, counting only models that are not MISSING. The rules that depend on H1 or H1-alt are void under the conflict rule (section 5).
- **"There is no fixed layer where a fact lives":**
  - condition: ICC(1) upper 95% CI < 0.15, under D1;
  - does not depend on H1 or H1-alt.
- **"A single prompt is a poor estimate of a fact's depth; it takes N paraphrases":**
  - condition: H1 holds, and n′ is defined and ≥ 8 (D1, point estimate; an undefined n′ does not count; section 4);
  - N is reported per model with its CI.
- **"Wording shifts every fact's depth together":**
  - condition: H1 holds, and (rt + frame) − (ft + e/nc) > 0 (D1, point estimate; the residual is the combined fact × paraphrase residual of section 4).
- **"Facts have a depth that frequency and relation do not explain":**
  - condition: H1-alt holds.
- **"The fact share is above zero":**
  - condition: parametric fact-share null p < 0.01 (section 4).
- Otherwise: report the estimated shares and n′ as an intermediate result.

## 7. Code (frozen with this file)
- Analysis:
  - `analysis/p2/p2_model.R`
  - `analysis/p2/p2_analysis.R`
  - `analysis/p2/p2_null.R`
  - `analysis/p2/p2_null_fns.R`
  - `analysis/p2/p2_bootsim_fns.R`
  - `analysis/p2/p2_mom.py`
  - `analysis/p2/p2_analysis.py`
- Measurement and session:
  - `src/depthlaw/p2/run_p2.py`
  - its dependencies `src/depthlaw/depth/causal.py`, `src/depthlaw/depth/common.py` and `src/depthlaw/io.py`
  - `scripts/p2_gpu_run.sh`
  - `scripts/p2_done_check.py`
- Test only:
  - `analysis/p2/p2_fake_run.py`
  - `analysis/p2/p2_test_e2e.py`
  - `analysis/p2/p2_test_mom.py`
  - `analysis/p2/p2_null_calib.R`
  - `analysis/p2/p2_null_calib_run.sh`
- `p2_analysis.py` refuses:
  - a materials sha256 that differs from section 1;
  - a model outside the four families;
  - a duplicate model or a duplicate run dir;
  - any `--boot` other than `param`;
  - in the gating call, the checks of section 3 (the five models, 1000 resamples and null datasets) and of section 1 (run identity).
- Run order after the GPU session:
  1. `p2_analysis.py <out> --runs <MODEL=RUN_DIR or MODEL=none for each of the five models> --set correct` (gating).
  2. Then, with `--primary <out>` and the same `--runs`: `new226`, `all`, `all10`, `nomanufacturer`, `tcov`, `lofo`, `h4` (not gating).
- Simulation v1: `analysis/p2/p2_bootsim.R` → `results/P2sim/p2_bootsim.json` (no method passed).
- Simulation v2 (selection): `analysis/p2/p2_bootsim_v2.R` → `results/P2sim_v2/p2_bootsim_v2.json`; report `analysis/p2/p2_bootsim_v2_report.py` → `reports/p2/P2_bootsim_v2_report.md`.

## 8. Related work (for citation-verifier)
- **Prior work on where and how facts are processed:**
  - Causal tracing / activation patching is used to localise factual recall. Hase et al. (2301.04213) show that localisation does not reliably predict where editing works.
  - Hochman, Shapira, Goldberg (2606.21345) find redundant, non-contiguous retrieval paths and "significant rank discordance between models" in per-relation path length.
  - Gupta et al. (2510.18871) show the first token of multi-token answers needs more depth.
  - Agarwal (2609.17537) finds relation information becomes causally active before entity information.
  - Rohweder et al. (2610.27241) predict linear relational decodability from the subject representation alone.
  - Chen et al. (2405.14117), Elhelo et al. (2606.27237) and Benz et al. (2607.01000) are required citations. **Their content is to be verified by citation-verifier; it is not characterised here.**
- **P2's question:** to our knowledge, none of these estimates how much of a fact's causal depth is a property of the fact versus the prompt wording. The closest adjacent work is Elhelo et al. (2606.27237; task-specific encoding of a fact) and Agarwal (2609.17537; eight prompt families).

## 9. Deviations
`prereg/deviations/D-P2-<session UTC>-<n>.md` (and `D-P2-<session UTC>-budget.md` at the hard stop): write-once, with reason and UTC time, committed before any rerun. Deviations written outside the GPU driver follow the same pattern with the UTC time of writing.

## 10. Known limitations (descriptive; not decision text)
Recorded from the PREREG reviews (stats-reviewer rounds 1–3). None of these changes a decision rule. Fixes to code that does not compute a decision quantity are listed in `analysis/p2/POST_FREEZE_FIXES.md`.
- **CI method:**
  - It was selected on simplified simulations (section 4) and at a second look.
  - The carrier fixed effect and the covariates were not in those simulations.
  - Coverage of the fact_dominant ICC(1) interval was 0.925.
- **Selection on correctness:** inclusion by correct cells can bias the components (MNAR). The all-cells and all-10 sensitivities address this in part.
- **Frames:** the 10 frames are a designed set (9 df), so the wording share generalises only to frames like these.
- **Carrier × relation:** a carrier × relation interaction would be absorbed into fact:carrier, and so into den as fc/nc.
- **MoM:**
  - It estimates fact + fc/nc and ft + e/nc. Its diff differs from the REML diff by (e − fc)/(nc·den) in expectation, which the synthetic test could not resolve.
  - The carrier-level MoM test failed at 20 replicates (frame variance, −0.23, Monte Carlo noise) and passed at 200. Both runs are in the ledger.
- **Fact-share null:**
  - Failed refits are dropped without a failure threshold. If all refits fail, p = 1, which is conservative.
  - Its calibration was checked at B = 100 simulated datasets per replicate. The analysis uses 1000.
- **n′:** when G(k) has a ceiling below 0.8, set by carrier noise, n′ is undefined and only the ceiling is reported.
- **H3:** disattenuation by G(k̄) is approximate.
- **Multiple comparisons:** there is no family-wise control across the headline sentences.
- **Session tests:**
  - The patch-identity test runs on pythia-70m only. On the rented models, the stored data allow a post-hoc check: p at the last layer = exp(obj_first_logprob).
  - The driver's hard-stop path was not exercised in the dry runs.
  - The driver's dry runs used one real model (pythia-70m), plus a second model that cannot load, to test the crash path.
- **Proxy frequencies:** log_cooc_proxy is a DCLM phrase count (PROXY), not the pretraining corpus of every model.
