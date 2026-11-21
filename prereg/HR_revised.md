# Preregistration: revised H-R (relation-driven depth)

- **Status:** frozen at the commit recorded in `prereg/HASH.txt`. Any later deviation goes to `prereg/DEVIATIONS.md` with its reason and a UTC timestamp.
- **Written on:** 2026-11-21. The data files for this analysis were not opened for this request before this file was committed (see "Disclosure").
- **Structure:**
  - Part A is verbatim from the human's instruction of 2026-11-21.
  - Part B is the operationalization, written by Claude before data access to resolve ambiguities in Part A. Where B and A conflict, A governs and the conflict is a deviation.
  - Part C is a disclosure of prior exposure to related data.

---

## Part A. Verbatim (human instruction, 2026-11-21)

Hypotheses and thresholds:
- Outcome: half-probability depth as l/L (primary). Secondary: absolute p=0.1 onset, stable rank-1 onset (correct facts), logit-diff onset vs relation-matched distractor.
- Fact covariates: answer token count, model log prior of object first token (mean over 10 generic prefixes), object final logprob, subject token count, subject-to-final distance, template.
- Relation covariates: log object cardinality k, n distinct objects, first-token collapse rate, relation accuracy, mean final logprob.
- H1: lmer depth ~ fact covariates + (1|relation) + (1|relation:template) + (1|subject). ICC_rel >= 0.30 per model AND relation-cluster bootstrap (2000) 95% CI lower bound >= 0.15.
- H2 raw: Spearman of relation BLUPs per cross-family pair >= 0.7, permutation p < 0.01 (10000 relation shuffles).
- H2 controlled: residualize relation BLUPs on relation covariates within model; partial Spearman >= 0.5 with bootstrap 95% CI lower bound > 0.2 for every cross-family pair; observed rho minus rho of covariate-only predicted orderings >= 0.15. Report split-half reliability and disattenuated rho.
- H3: within-relation log co-occurrence delta R^2 95% CI upper bound < 0.02 per model; report correctness odds ratio.
- Cross-family pairs: Pythia vs OLMo, and any pair involving a new family. Pythia-1.4b vs 2.8b is reported but does not count.
- Decision: GO if H1, H2 raw, H2 controlled, H3 all pass; PARTIAL if H2 raw passes and H2 controlled fails; NO-GO if H2 raw fails in any cross-family pair.

Robustness (from STEP 2 of the instruction):
- Run H1, H2 raw, H2 controlled, H3, plus robustness: correct-only, incorrect-only, collapse>25% excluded, whole-word-object subset, thresholds 0.25/0.75, per template, per carrier, discrete-time survival with relation frailty.
- Recompute secondary outcomes from cached per-layer curves; if curves are missing, write a GPU job script (do not run) and mark those outcomes PENDING.

---

## Part B. Operationalization (Claude, written before data access)

### B0. Data
- **Existing rows (amendment-2 GPU runs), one row per fact × template:**

  | model | run dir |
  |---|---|
  | EleutherAI/pythia-1.4b | `results/S3b/S3b-pythia-1.4b-a7dfeb5-20261121T063528Z/depth.parquet` |
  | EleutherAI/pythia-2.8b | `results/S3b/S3b-pythia-2.8b-a7dfeb5-20261121T064110Z/depth.parquet` |
  | allenai/OLMo-2-1124-7B | `results/S3b/S3b-OLMo-2-1124-7B-923945f-20261121T061237Z/depth.parquet` |

- **Facts:** `data/facts_g1cpu.parquet` (1300 facts = 26 relations × 50), templates 0-2.
- **Asserted before analysis:** 3900 rows per model, 26 relations, 3 templates per fact.
- **Filter:** none for the primary analyses (no correctness filter).
- **Revision:** all models at `main`. Each model is fitted separately.
- **Families:** Pythia (pythia-1.4b, pythia-2.8b) and OLMo (OLMo-2-1124-7B).
  - The cross-family pairs that count are pythia-1.4b vs OLMo-2 and pythia-2.8b vs OLMo-2.
  - No new family is analysed in this gate.

### B1. Outcomes
- **Primary: `half_prob_depth`,** as stored. Per carrier c, l_c = min l with p_c(l') >= 0.5·p_c(L-1) for all l' >= l. The stored value is (l_c+1)/L (l is the 0-based block index), averaged over the 3 carriers in `configs/s3.yaml`. This is the prompt's "l/L" with 1-based layer numbering.
- **Secondary (non-gating),** recomputed from the stored per-layer curves (`final_logprob_curves`, `final_rank_curves`):
  - **`p01_onset`:**
    - Per carrier: min l with p_c(l') >= 0.1 for all l' >= l, normalized (l+1)/L. Defined only if p_c(L-1) >= 0.1.
    - Row value: the mean over carriers when all 3 are defined; otherwise missing.
  - **`rank1_onset`:** stable rank 1 from l to L-1 in all 3 carriers, mean of (l+1)/L. This is the stored `causal_final`, defined only on correct@1 rows.
  - **`logitdiff_onset`:**
    - Per carrier: min l with logit(object first token) − logit(distractor first token) > 0 for all l' >= l.
    - Distractor: the most frequent canonical object among the relation's 50 facts whose first token (model tokenizer) differs from this fact's object first token. Ties are broken alphabetically.
    - Distractor logits were never stored, so this outcome is **PENDING**. A GPU job script is written but not run.

### B2. Fact covariates (per model tokenizer)
- **`n_answer_tokens`:** token count of " " + object (column in `data/amend2_inputs.parquet`).
- **`log_prior`:** the mean over the 10 prefixes below of log softmax probability of the object first token at the prefix's final position. Computed with the same model at `main`, fp32, on CPU.
  - Prompts are tokenized exactly as the S3 prompts (`common.encode`).
  - The weights may be streamed layer by layer to fit in memory. The arithmetic is that of a standard forward pass; it is validated against a standard forward on pythia-70m and the max abs difference is reported.
  - Cached to `cache/hr/prior_<model>.parquet`.
  - Prefixes:
    1. `The`
    2. `It is`
    3. `This is`
    4. `The answer is`
    5. `I think it is`
    6. `Here is`
    7. `One example is`
    8. `Some people say`
    9. `The word is`
    10. `In the`
- **`obj_logprob_final`:** stored `obj_first_logprob` (unpatched fact prompt, last layer, final position).
- **`n_subject_tokens`:** column in `data/amend2_inputs.parquet`.
- **`subj_final_dist`:** (number of prompt tokens − 1) − subject last-token index, tokenized as in S3 (`common.subject_last_pos`).
- **`template`:** enters only through `(1|relation:template)`. Template ids are relation-specific, so there is no fixed template term.
- **Scaling:** continuous fact covariates are z-scored within model before fitting. This does not change ICC or ΔR².

### B3. Relation covariates (per model; the relation's 50 facts / 150 rows)
- **`log_k`:** log of the number of distinct canonical objects in the relation's full S1 pool (`data/facts.parquet`, 200 facts per relation). This is the "object cardinality".
- **`n_distinct`:** number of distinct canonical objects among the relation's 50 analysed facts.
- **`collapse_rate`:** share of the relation's 50 facts whose object first token (model tokenizer) equals the first token of a different canonical object among those 50 facts.
- **`rel_accuracy`:** mean correct@1 over the relation's 150 rows.
- **`rel_mean_final_logprob`:** mean `obj_first_logprob` over the relation's 150 rows.

### B4. H1
- **Model:** `lme4::lmer(y ~ n_answer_tokens + log_prior + obj_logprob_final + n_subject_tokens + subj_final_dist + (1|relation) + (1|relation:template) + (1|subject), REML = TRUE)`. `subject` is the subject string.
- **ICC_rel** = σ²_rel / (σ²_rel + σ²_rel:template + σ²_subject + σ²_resid). This is the adjusted ICC: fixed-effect variance is excluded.
- **Bootstrap:** 2000 relation-cluster resamples (26 relations drawn with replacement). A duplicated relation gets new labels for relation, relation:template and subject. Percentile 95% CI. Failed fits are counted and reported; the CI uses the successful fits.
- **Pass:** per model, ICC_rel >= 0.30 AND CI lower bound >= 0.15. H1 passes iff it passes in all 3 models.

### B5. H2 raw
- **BLUPs:** conditional modes of `(1|relation)` from each model's H1 fit (26 values).
- **ρ:** Spearman over relations.
- **Permutation p:** 10000 permutations of the relation labels of one model's BLUP vector. One-sided p = (1 + #{ρ_perm >= ρ_obs}) / 10001, since a positive association is predicted. The two-sided p is also reported.
- **95% CI:** 2000 relation bootstrap resamples of the paired BLUPs.
- **Pass:** per cross-family pair, ρ >= 0.7 AND one-sided p < 0.01.

### B6. H2 controlled
- **Residualization:** within each model, OLS of BLUP on [log_k, n_distinct, collapse_rate, rel_accuracy, rel_mean_final_logprob] + intercept, using that model's own covariates.
- **Partial ρ** = Spearman(residuals_A, residuals_B).
- **Covariate-only ρ** = Spearman(fitted_A, fitted_B).
- **95% CI for partial ρ:** 2000 relation bootstrap resamples, refitting both OLS models inside each resample.
- **Pass:** per cross-family pair, all three of:
  - partial ρ >= 0.5;
  - CI lower bound > 0.2;
  - (raw ρ − covariate-only ρ) >= 0.15.
- **Split-half reliability:**
  - Make 200 random splits of each relation's 50 facts into 25/25, keeping all templates of a fact together.
  - Fit the H1 model on each half and take the Spearman of the two halves' BLUPs.
  - Apply Spearman-Brown: r_SB = 2r/(1+r).
  - Report the per-model mean r_SB, with the 2.5/97.5 percentiles over splits.
- **Disattenuated ρ** = raw ρ / sqrt(r_SB,A · r_SB,B), not capped at 1.

### B7. H3
- **Predictor:** `cooc_within` = log1p(EXACT phrase cooc) − its relation mean, as in amendment 2.
  - EXACT index per model: Pythia `v4_piletrain_llama`; OLMo-2 `v4_olmo-mix-1124_llama`.
  - EXACT only; never pooled across indexes.
- **ΔR²:**
  - Fit the H1 model with and without `cooc_within` by ML (REML = FALSE).
  - ΔR² = marginal R² (Nakagawa-Schielzeth: var(fixed-part predictions) / (that + Σσ²_RE + σ²_resid)) of the model with the term minus the model without.
  - 95% CI from 2000 relation-cluster resamples.
- **Pass:** per model, the CI upper bound < 0.02. H3 passes iff it passes in all 3 models.
- **Correctness odds ratio** (reported, not gating):
  - Model: logistic regression `correct_at1 ~ cooc_within + n_answer_tokens + log_prior + n_subject_tokens + subj_final_dist + relation fixed effects`.
  - `obj_logprob_final` is excluded because correctness is a function of the final distribution.
  - OR per log1p unit; 95% CI from 2000 relation-cluster resamples.

### B8. Decision (frozen rule, applied mechanically)
- **H2 raw and H2 controlled** must hold in every cross-family pair (pythia-1.4b–OLMo-2, pythia-2.8b–OLMo-2).
- **NO-GO** if H2 raw fails in any cross-family pair.
- **PARTIAL** if H2 raw passes and H2 controlled fails.
- **GO** if H1, H2 raw, H2 controlled and H3 all pass.
- **Unassigned case:** if H2 raw and H2 controlled pass but H1 or H3 fails, the rule assigns no label. This is reported as "UNASSIGNED by the frozen rule (not GO)".
- **pythia-1.4b vs pythia-2.8b** is reported and does not count.

### B9. Robustness (non-gating)
- **What each variant reports:** point estimates of ICC_rel per model, raw and partial ρ and covariate-only ρ per pair with the one-sided permutation p (10000), and H3 ΔR² per model. No bootstrap CIs.
- **Variants:**
  - correct@1 rows only;
  - incorrect rows only;
  - relations with collapse_rate > 0.25 excluded, per model; pairs use the relations kept in both models;
  - whole-word-object subset: rows whose object first token, decoded and stripped, equals the object's first whitespace-delimited word;
  - outcome recomputed from the stored curves with frac 0.25 and frac 0.75 instead of 0.5;
  - per template: each template id alone, without the `(1|relation:template)` term;
  - per carrier: each carrier's `half_prob_depth_per_carrier` alone;
  - discrete-time survival with relation frailty (details below).
- **Survival model:**
  - Event layer per row = round(L · half_prob_depth), 1-based. Person-period rows run from layer 1 to the event layer.
  - Fit: `glmer(event ~ layer-bin factor (8 equal-width bins of normalized layer) + fact covariates + cooc_within + (1|relation), family = binomial(link = "cloglog"))`.
  - Report the relation frailty SD, the HR for cooc_within with a Wald 95% CI, and the Spearman of frailty BLUPs across model pairs.
- **Secondary outcomes** (`p01_onset`, `rank1_onset`): H1 ICC point estimate and H2 raw ρ with permutation p. Non-gating.

### B10. Software and seeds
- R 4.3.3 with lme4 1.1-35.1 (Ubuntu apt), and the Python 3.13 project venv.
- One seed, 20261121, for every bootstrap, permutation and split.
- Outputs: `results/HR_gate.json` and `results/HR_gate.md`, plus a run directory `results/HR/<run_id>/` with `log.jsonl`.

---

## Part C. Disclosure of prior exposure (Claude)
- **Seen before this file was written:**
  - **Amendment-2 gate (`reports/GATE_A2.md`, run `A2-none-a7dfeb5-20261121T065218Z`):** on the same three S3b runs, within-relation log cooc had a small positive slope on half_prob_depth and partial R² ≤ 0.006 in all 3 models.
    - It used different controls and a random slope.
    - H3 is therefore not a blind test; its direction and approximate size were known.
  - **Amendment-2 descriptives:** correct@1, median depth for correct vs wrong rows, Spearman with cooc and obj logprob.
  - **Earlier Pythia causal_final work** (G1, S4, S5, C1 re-analysis). `reports/S4.md` reports Spearman(relation mean causal_final depth, LRE faithfulness) = 0.253 over 26 relations for pythia-1.4b.
- **Not computed before this file, on any model:** relation-level orderings of half_prob_depth, ICCs, BLUPs, and any cross-model comparison of relation orderings.
- **Unknown:** whether the human, who ran the GPU session, looked at relation-level patterns.
- **Known limitation:** H2 uses one Pythia-vs-OLMo family contrast. The two Pythia pairs share OLMo and are not independent; n = 26 relations.
