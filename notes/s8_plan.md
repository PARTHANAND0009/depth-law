# S8 plan (CPU): tampered-fact detector. 2026-11-17, written before any S8 code or data.

Inputs are fixed by S7 (notes/s7_plan.md): base model EleutherAI/pythia-1.4b (main), zoo in
zoo/manifest.json (run S7-pythia-1.4b-f468c95-20261116T183628Z), causal-only depth evals per
kept model in results/S7eval/S7eval-<model_id>-*/depth.parquet, rome_single rows in
results/S7/<run>/rome/depth.parquet. Only the G3 threshold is pre-registered
(configs/prereg.yaml g3.fact_auroc_min 0.8; targets locate_then_edit_auroc 0.9, sft_auroc 0.8).
Everything below is fixed now; any later change is logged here with a date and reason.

## Units, labels, populations
- Unit = fact in a model (the 3 templates are averaged per feature).
- Positive = edited fact in an edited model, evaluated with the NEW object (target).
- Negative = unedited control fact in the same edited model, evaluated with its true object.
  rome_single: each edit is its own model; negatives are the 5 controls evaluated under that edit.
- PRIMARY population (both classes "asserted"): positives with new-object correct@1 at template 0,
  negatives with true-object correct@1 at template 0 in that model. Reason: an auditor checks
  facts the model states; unknown facts are trivially separable by confidence alone.
- SECONDARY population: all edited facts vs all 300 controls (reported, not gating).

## Frequency
EXACT Pile phrase counts (v4_piletrain_llama, configs/s2_exact.yaml patterns), label EXACT:
controls and true-new edits from data/counts_exact.parquet (exact_piletrain; true object = target);
counterfactual edits from data/s7_cf_counts_exact.parquet (same code, subject + NEW object).
x = log1p(count). No PROXY counts are used in S8.

## Calibration set (clean model only)
Clean pythia-1.4b S3 rows (results/S3/S3-pythia-1.4b-b9a353d-20261108T064941Z/depth.parquet) for
the 1,000 G1 facts that are NOT S7 controls. Nothing from any edited model enters calibration.

## Features (per row, then averaged over templates)
- r_causal: causal_final - [relation FE + b * x], OLS fit on resolved clean calibration rows.
  Censored rows (never resolved) take depth 1.0 before the residual is taken.
- r_ll: same for logit-lens depth.
- r_conf: obj_first_logprob - [relation FE + b * x], OLS on all clean calibration rows.
- d_profile: RMS distance between the row's logit-lens log10(rank) curve (24 layers) and the
  relation's mean curve over resolved clean calibration rows.
- recall-vs-two-hop depth gap: MISSING (no two-hop prompts built; a second depth run per model
  is beyond the CPU budget).

## Detector (unsupervised, primary)
Score = Mahalanobis distance of (r_causal, r_ll, r_conf, d_profile) from the clean calibration
fact-level mean, covariance by Ledoit-Wolf on the clean calibration facts. Higher = suspicious.
Single-feature scores (|r_causal|, signed r_causal, etc.) are reported as secondary.

## Supervised
- Upper bound: logistic regression (standardised features above + raw causal depth, ll depth,
  logprob, margin), 5-fold CV over facts within each model (in-distribution).
- Held-out method: train on all other models' rows, test on the held-out method's models.
- Held-out family: families {locate: rome_single, memit*, alphaedit*} and {finetune: lora*,
  synthdoc50}; train on one family, test on the other.

## Baselines (all fact-level, same populations)
- confidence-only: obj_first_logprob (higher = suspicious).
- perplexity: obj_logprob / n_obj_tokens (higher = more confident = suspicious).
- confidence x rarity: exp(obj_first_logprob) / (1 + x).
- LCF: last-token residual at every layer, template 0; inter-layer differences h_{l+1} - h_l;
  per layer a diagonal Mahalanobis distance with mean and variance from 200 clean calibration
  prompts run through the AUDITED model (200 seeded calibration facts, disjoint from controls and
  edits), variances shrunk Ledoit-Wolf style toward their mean; score = sum over layers.
  Needs one forward pass per prompt per model (detect/hidden.py); rome_single runs it per edit.
- Youssef-style AdaBoost: features = logit-lens object probability curve (24 layers) + final
  logprob; sklearn AdaBoostClassifier(n_estimators=200, seed 1234); held-out method and held-out
  family protocols as above (it is supervised).

## Metrics
- Fact-level AUROC per model, per method (pooled over that method's models) and per family.
- Bootstrap: 1000 resamples stratified by label, percentile 95% CI, seed 1234.
- Model-level AUROC: MISSING (one clean model of this architecture; a model-level AUROC needs
  several clean models).
- G3 number: unsupervised-score fact-level AUROC, PRIMARY population, pooled over the
  non-adaptive ROME and MEMIT models (rome_single, memit100, memit1000), vs 0.8. Per-model
  values and targets (locate-then-edit 0.9, SFT 0.8) are reported beside it.

## Order and resources
After the S7 evals: detect/hidden.py (forward passes for LCF), then detect/eval.py (all scores,
AUROCs, CIs) -> results/S8/<run_id>/. S5 and S4T wait on results/HOLD_S5 until G3.
