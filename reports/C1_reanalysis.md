# Claim 1 re-analysis on existing S3 data (EXPLORATORY, not pre-registered)

Requested by the human 2026-11-20. No new model runs.

- **Source of every number:** `results/C1re/C1re-none-3cee850-20261120T141401Z/c1.json` (run_id `C1re-none-3cee850-20261120T141401Z`, script `src/depthlaw/stats/c1_reanalysis.py`).
- **Inputs:** S3 runs `S3-pythia-1.4b-b9a353d-20261108T064941Z` and `S3-pythia-2.8b-be99060-20261109T021915Z`, 1300 facts × 3 templates = 3900 rows each.
- **Counts:** log1p of EXACT Pile phrase co-occurrence (v4_piletrain_llama, `count_label` EXACT).
- **CIs:** relation-cluster bootstrap with 1000 resamples for OLS slopes; relation-clustered SEs for the GLMs.

## Key result
1. **Counts behave.** The odds of a correct answer rise with log co-occurrence in both models, with and without controls:
   - pythia-1.4b: OR 1.24 per log1p unit;
   - pythia-2.8b: OR 1.32.
2. **The raw negative depth-cooc correlation is between-relation.**
   - Raw row-level Spearman: pythia-1.4b -0.170 (N 720 resolved rows); pythia-2.8b -0.126 (N 804).
   - Within relations: -0.040 (p 0.28) and -0.055 (p 0.12).
   - With relation fixed effects the OLS slope is about 0, CI includes 0.
   - Adding log subject count alone reverses the slope's sign.
3. **The survival HR > 1 is entirely "answers correctly".**
   - On all rows (unresolved censored): HR 1.254 [1.159, 1.357] (pythia-1.4b) and 1.273 [1.171, 1.384] (pythia-2.8b).
   - Restricted to resolved rows: 0.979 [0.914, 1.049] and 0.993 [0.924, 1.067].
4. **Tuned-lens depth: MISSING** (no lens; 0 resolved rows). Logit-lens depth gives the same pattern.

Under causal_final, frequency predicts whether a fact is answered, not how early it resolves (`reports/AUDIT_causal_depth.md`).

## 1. Raw Spearman, depth vs log1p(EXACT cooc), resolved rows

| model | measure | row level rho (p, N) | fact mean rho (p, N facts) | within relation, demeaned rho (p, N) |
|---|---|---|---|---|
| pythia-1.4b | causal_final | -0.170 (4.3e-06, 720) | -0.136 (0.0063, 402) | -0.040 (0.28, 720) |
| pythia-2.8b | causal_final | -0.126 (0.00034, 804) | -0.103 (0.032, 436) | -0.055 (0.12, 804) |
| pythia-1.4b | logit_lens_depth | 0.055 (0.14, 720) | 0.008 (0.88, 402) | -0.012 (0.76, 720) |
| pythia-2.8b | logit_lens_depth | -0.118 (0.00077, 804) | -0.174 (0.00025, 436) | -0.022 (0.54, 804) |

Row-level p-values treat the 3 templates of a fact as independent, so they are optimistic. The fact-level column does not have this problem.

## 2. OLS slope of causal_final on log cooc, adding the prereg controls one at a time

Slope per log1p unit, with a 95% relation-cluster bootstrap CI (1000 resamples, all succeeded). "partial R²" is the OLS R² with log cooc minus the R² without it.

| step | pythia-1.4b slope [CI] | partial R² | pythia-2.8b slope [CI] | partial R² |
|---|---|---|---|---|
| log cooc only | -0.0030 [-0.0069, 0.0015] | 0.0068 | -0.0050 [-0.0136, 0.0023] | 0.0128 |
| + relation FE | 0.0001 [-0.0027, 0.0032] | 0.0000 | -0.0031 [-0.0072, 0.0023] | 0.0028 |
| + log_subj (alone) | **+0.0045** [-0.0049, 0.0118] | 0.0060 | **+0.0076** [-0.0036, 0.0143] | 0.0108 |
| + log_obj (alone) | -0.0030 [-0.0063, 0.0014] | 0.0071 | -0.0062 [-0.0107, -0.0002] | 0.0195 |
| + n_answer_tokens (alone) | -0.0030 [-0.0060, 0.0020] | 0.0070 | -0.0056 [-0.0113, 0.0016] | 0.0162 |
| + log_answer_first_token_freq (alone) | -0.0029 [-0.0068, 0.0014] | 0.0064 | -0.0050 [-0.0140, 0.0021] | 0.0127 |
| + n_subject_tokens (alone) | -0.0025 [-0.0066, 0.0022] | 0.0038 | -0.0044 [-0.0139, 0.0036] | 0.0078 |
| cumulative: log_subj + log_obj | 0.0031 [-0.0055, 0.0108] | 0.0027 | 0.0023 [-0.0061, 0.0085] | 0.0009 |
| cumulative: all 5 prereg controls | 0.0037 [-0.0053, 0.0122] | 0.0037 | 0.0018 [-0.0058, 0.0083] | 0.0006 |
| all 5 controls + relation FE | 0.0076 [-0.0015, 0.0144] | 0.0107 | 0.0062 [-0.0013, 0.0126] | 0.0047 |

N = 720 rows (pythia-1.4b) and 804 rows (pythia-2.8b).

**Which control removes the effect.**
- **The OLS slope CI includes 0 even before any control** in both models, so there is no clustered-robust effect to remove.
- **The negative Spearman sign goes away with two terms:**
  - relation fixed effects, which bring the slope to about 0;
  - the subject's own corpus count (log_subj), which alone reverses the sign to positive in both models.
- **The other controls barely move the slope:** object count, answer tokens, answer first-token frequency, subject tokens.
- **One CI excludes 0:** pythia-2.8b with log_obj alone, -0.0062 [-0.0107, -0.0002]. It is one of 20 uncorrected intervals per model.

## 3. Discrete-time survival (cloglog), causal_final
HR is per log1p unit of cooc. Relation-clustered SEs. Layer baseline in 12 bins.

| model | rows | controls | HR [95% CI] | p | events |
|---|---|---|---|---|---|
| pythia-1.4b | all 3900 (3180 censored) | none | 1.249 [1.149, 1.358] | 1.9e-07 | 720 |
| | all 3900 | prereg | 1.254 [1.159, 1.357] | 1.9e-08 | 720 |
| | resolved only (720) | none | 1.019 [0.989, 1.051] | 0.22 | 720 |
| | resolved only (720) | prereg | 0.979 [0.914, 1.049] | 0.55 | 720 |
| pythia-2.8b | all 3900 (3096 censored) | none | 1.270 [1.163, 1.386] | 9.5e-08 | 804 |
| | all 3900 | prereg | 1.273 [1.171, 1.384] | 1.3e-08 | 804 |
| | resolved only (804) | none | 1.035 [0.976, 1.098] | 0.25 | 804 |
| | resolved only (804) | prereg | 0.993 [0.924, 1.067] | 0.85 | 804 |

- **On all rows, censoring is the same as answering wrongly** (`reports/AUDIT_causal_depth.md`). A higher hazard therefore mostly means "more likely to be answered".
- **Among answered rows, the timing hazard does not depend on cooc.**
- The "resolved only" rows were added by me; they were not in the request.

## 4. Logistic regression: correct@1 on log1p(EXACT cooc) (sanity check)

| model | covariates | odds ratio [95% CI] | p | N rows |
|---|---|---|---|---|
| pythia-1.4b | log cooc only | 1.282 [1.153, 1.425] | 4.2e-06 | 3900 |
| | + relation FE | 1.310 [1.215, 1.413] | 2.3e-12 | 3900 |
| | + prereg controls + relation FE | 1.242 [1.157, 1.334] | 2.0e-09 | 3900 |
| pythia-2.8b | log cooc only | 1.317 [1.181, 1.469] | 7.6e-07 | 3900 |
| | + relation FE | 1.353 [1.250, 1.464] | 7.5e-14 | 3900 |
| | + prereg controls + relation FE | 1.316 [1.183, 1.463] | 4.6e-07 | 3900 |

The counts carry the expected signal for knowing a fact, so the null on depth is not a broken-count artifact.

## 5. Tuned-lens depth, and logit-lens depth as the available lens
- **tuned_lens_depth: MISSING.** There are 0 resolved rows in both models: no pretrained tuned lens exists for pythia-1.4b/2.8b and none was trained (`reports/S0_S2.md`). Training one is a new model run, outside this request.
- **logit_lens_depth (same S3 rows):**
  - Raw Spearman is +0.055 (pythia-1.4b, p 0.14) and -0.118 (pythia-2.8b, p 0.00077).
  - Within relations it is -0.012 and -0.022.
  - Relation FE slopes: 0.0012 [-0.0008, 0.0041] and -0.0008 [-0.0042, 0.0019].
  - Survival on all rows: HR 1.227 [1.144, 1.316] (pythia-1.4b) and 1.247 [1.157, 1.345] (pythia-2.8b), with controls.
  - Survival on resolved rows only: 1.002 [0.977, 1.028] and 1.008 [0.986, 1.030].
  - Full step table in c1.json.
- **The logit lens has the same censoring structure as causal_final.** Its depth rule also requires rank 1 at the last layer (`reports/S7.md`).

## What this does and does not show
- **It shows:** on the two Pythia models, EXACT co-occurrence predicts whether a fact is answered (OR ~1.25-1.35 per log1p unit). Among answered rows, it does not predict the causal_final or logit-lens depth once relation is accounted for.
- **It does not test** depth on unanswered facts. Neither current measure is defined there. Measure A in `reports/AUDIT_causal_depth.md` would be.
- **Scope:** one model family (Pythia), 26 relations, 1300 facts. No OLMo-2.
