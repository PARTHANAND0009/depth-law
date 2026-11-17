# S9 plan (CPU): adaptive attacker. 2026-11-17, written before any S8 result or S9 code is run.

Threat model: the attacker knows the detector (notes/s8_plan.md), including the clean depth law
fitted by S8 (detect/features.Calibration on clean pythia-1.4b rows) and the EXACT Pile counts.
Base model, requests, controls and evaluation are the S7 ones (first 100 requests for A1/A2,
first 50 for A3; same 5 seeded controls per edit as rome_single). Nothing here changes a
pre-registered threshold; G3 is on the NON-adaptive models (S8). S9 results are reported beside it.

Predicted depth for a request: d_hat = Calibration.fit_causal applied to (relation, x), x =
log1p(EXACT Pile count of subject + NEW object) (data/s7_cf_counts_exact.parquet or
data/counts_exact.parquet for true-new). l_hat = clip(round(d_hat * 24) - 1, 0, 23).

## A1 layer matching (ROME, single edits)
- Pilot: 10 pilot requests (first 10 of the S7 pilot list), ROME at layers {3, 5, 8, 11, 14, 17},
  measure the edited fact's causal_final depth (mean over templates, censored -> 1.0).
  Fit nothing; tabulate mean depth per layer.
- Rule: for each of the 100 requests, edit at the pilot layer whose mean depth is closest to d_hat
  (ties -> lower layer). Second-moment stats for any new layer: same 60k FineWeb-Edu tokens.

## A2 depth-regularized edit loss (ROME layer 5, single edits)
- v* loss += lambda * mean_{l in (5, l_hat)} softplus(LL_l(target first token) - log(1e-3)),
  LL_l = log-softmax of the logit lens (final norm + unembed) of block l's output at the last
  prompt token, bare prompt only. lambda = 1. Same steps/lr/KL/wd/clamp as S7 ROME.
  Goal: the object must not be decodable before the predicted layer.

## A3 frequency spoofing (synthetic-doc LoRA)
- As synthdoc50 but 60 docs per fact (all 20 doc templates x 3 fact templates; synthdoc50 used
  10), i.e. 6x the exposure, so the fact can look like a higher-frequency fact. Same LoRA
  settings and stop rule.

## Measured per attack
- Efficacy (template 0 rank 1) and paraphrase efficacy; collateral = control correct@1 at
  template 0 minus the clean model's (N controls stated); compute = wall-clock seconds per edit
  (or per model for A3) on this CPU.
- Detection: S8 scores (s_maha primary, baselines, LCF) with the S8 populations; fact-level
  AUROC with bootstrap CI. Keep rule for reporting: an attack below 0.90 efficacy is reported
  with its efficacy (AUROC on its successful edits only, primary population).

## Resources
- A1 pilot ~1.7 h; A1 100 edits ~3 h; A2 100 edits ~3.5 h; A3 ~2 h + eval ~1.5 h. S5/S4T stay
  on hold (results/HOLD_S5) until G3.

## Addendum (2026-11-17, before any S9 run)
- A2 early stop: stop when mean target prob > 0.9 AND the penalty < 0.1 (S7 ROME stops on the
  probability alone; with the penalty that would end before the penalty is optimised). Max steps
  stay 25. If 25 steps pass without both, the edit is kept as is and its efficacy is measured.
- tau = log(1e-3); layers = 6 .. l_hat-1 (block outputs after the edited layer 5 and before the
  predicted layer); if l_hat <= 6 the penalty is empty and A2 equals S7 ROME for that request.
