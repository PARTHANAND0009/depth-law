# EXPLORATORY (post hoc, not preregistered) — E-depthvar plan

- **Status:** written 2026-11-21 before any E-depthvar statistic was computed.
- **Labels:** every file in this directory starts with the filesystem-safe prefix `EXPLORATORY_post-hoc_not-preregistered__`. Every figure title, table header and ledger entry starts with "EXPLORATORY (post hoc, not preregistered)".
- **Not confirmatory.** Nothing here is a confirmatory test.

## Disclosure: what is already known before this plan
- **Variance components already seen.** The revised H-R gate (`results/HR_gate.md`, run `HR-none-f431f35-20261121T081116Z`) fitted D1 (half_prob_depth) on all 3900 rows per model.
  - Model: 5 fact covariates + `(1|relation) + (1|relation:template) + (1|subject)`; no `(1|fact)`.
  - Known: σ²_relation, σ²_relation:template, σ²_subject and σ²_residual. The relation ICC was ≤ 0.06 in all three models; the relation:template, subject and residual components were of similar size.
  - Known: per-template-only relation ICCs of 0.13–0.54, the H-R robustness tables, and the cross-model Spearman of relation BLUPs.
- **Consequence.** The D1 decomposition on all rows is not blind, and the G1 rule's D1 comparison on correct cells is partly predictable from it. No variance decomposition on correct cells, D2–D4, the D-study, the fact-level cross-model ρ, or any null or simulation has been computed.

## Data
- **Rows:** the S3b fp32 GPU rows (1300 facts × 3 templates = 3900 rows per model, 26 relations).
  - `results/S3b/S3b-pythia-1.4b-a7dfeb5-20261121T063528Z/depth.parquet`
  - `results/S3b/S3b-pythia-2.8b-a7dfeb5-20261121T064110Z/depth.parquet`
  - `results/S3b/S3b-OLMo-2-1124-7B-923945f-20261121T061237Z/depth.parquet`
- **Stored curves:** per carrier (3 carriers, `configs/s3.yaml`), the patched object first-token log-prob for every layer (`final_logprob_curves`) and its rank (`final_rank_curves`).
  - Also stored: `carrier_alone_obj_logprob` (object first-token logprob on the carrier with no fact), `obj_first_logprob`, `correct_at1`.
  - All of D1–D4 can be computed from these, so no rerun is needed.
- **Covariates:**
  - `data/facts_g1cpu.parquet` (subject, object, template text), `data/amend2_inputs.parquet` (token counts, EXACT co-occurrence).
  - Offline tokenizers for template length and subject-to-final distance.
- **No model is loaded.**

## B1. Depth definitions
Per carrier c, p_c(l) = exp(logprob) at layer l (0-based); L = n layers. Each definition is normalized as (l+1)/L.

| def | per-carrier value | cell value |
|---|---|---|
| D1 | min l with p_c(l') ≥ 0.5·p_c(L−1) for all l' ≥ l (always defined) | mean over the 3 carriers (= stored half_prob_depth) |
| D2 | min l with p_c(l') ≥ 0.1 for all l' ≥ l; censored if p_c(L−1) < 0.1 | mean over carriers if all 3 are defined; otherwise censored. Sensitivity: a censored carrier gets (L+1)/L |
| D3 | min l with rank_c(l') = 1 for all l' ≥ l; censored if rank_c(L−1) ≠ 1 | as D2 (equals stored causal_final when defined) |
| D4 | 1 − mean_l min(1, p_c(l)/p_c(L−1)) | mean over carriers |

## B2. Inclusion
- **Correct cell:** `correct_at1` = the model's final top-1 token on the fact prompt equals the object's first token.
- **Counts:** per model, the number of facts correct under 3/3, 2/3, 1/3 and 0/3 templates.
- **Two analysis sets, both run:**
  - (i) all correct cells (unbalanced);
  - (ii) facts correct under all 3 templates (balanced).
- **Censoring:** for D2 and D3, report censoring rates per set, analyze uncensored cells, and run the censored-as-(L+1)/L sensitivity.

## B3. Variance components (per model × definition × set)
- **Model:** `depth ~ 1 + (1|relation) + (1|relation:template) + (1|subject) + (1|fact)`, fitted with lme4 REML via Rscript.
  - Templates are nested in relations, so "template main" = relation:template.
  - The residual is fact × template interaction plus measurement error; the two cannot be separated with one observation per cell.
  - Subject and fact are nearly confounded (one fact per subject, apart from a handful). "fact+subject" is the primary fact-level share; the split is reported but not interpreted.
- **Shares:** each σ² divided by the sum of all σ² including residual.
- **95% CIs:** 1000 cluster-bootstrap resamples of facts within relation.
  - Relations are kept; within each relation, facts are drawn with replacement together with all their cells.
  - Duplicate draws get new fact and subject labels.
  - Percentile CIs; seed 20261121. The bootstrap of the difference (template-main + residual) − (fact+subject) uses the same resamples.
- **ICC(1)** (within-relation, single template) = (σ²_f+σ²_s)/(σ²_f+σ²_s+σ²_rt+σ²_e).
  - ICC_rel, which leaves σ²_rt out of the denominator, is also reported.
- **D-study over k templates per fact (k = 1..30):**
  - Φ(k) = (σ²_f+σ²_s)/(σ²_f+σ²_s+(σ²_rt+σ²_e)/k), absolute.
  - G(k) = (σ²_f+σ²_s)/(σ²_f+σ²_s+σ²_e/k), relative: the same templates for every fact in a relation.
  - n′ = smallest k with Φ(k) ≥ 0.8, and likewise for G. CIs come from the bootstrap.
  - k > 3 extrapolates from 3 templates per relation and assumes new templates come from the same population.
- **ANOVA (method-of-moments) G-study cross-check.** Run on the balanced sets (all 3900 cells; set ii) as a within-relation facts × templates two-way design without replication, pooled across relations:
  - σ²_e = MS_res;
  - σ²_f = (MS_fact − MS_res)/3;
  - σ²_rt = (MS_tmpl − MS_res)/n̄_f;
  - σ²_rel from the between-relation mean square (n̄_f = mean facts per relation).
  - fact+subject cannot be split here, so it is reported as one fact component.

## B4. Wording-related variance
- Report share(relation:template) and share(residual) separately.
- State which of the two is larger for each model × definition, with bootstrap CIs.

## B5. Covariates (fixed effects added to B3, z-scored within model)
- **Covariates:**
  - template length in tokens (filled prompt length minus subject tokens);
  - subject-to-final distance (tokens after the subject's last token);
  - subject token count;
  - answer prior (mean over carriers of `carrier_alone_obj_logprob`);
  - final-layer log p(object) (`obj_first_logprob`);
  - log1p(EXACT co-occurrence) (Pythia: piletrain; OLMo-2: olmo-mix-1124; EXACT).
- **Fits:** all six jointly, and one at a time. Report each variance component's percent change from B3 (point estimates).

## B6. Cross-model agreement
- **Facts:** those correct under all 3 templates in all three models (strict). Sensitivity: facts correct under ≥ 1 template in each model, using the mean over correct templates.
- **ρ:** Spearman of fact-level mean depth for each model pair, raw and within-relation (relation means removed).
- **Disattenuated ρ** = ρ / sqrt(G_a(3)·G_b(3)), with G from each model's set-(ii) B3 fit.
- **CIs:** 1000 bootstrap resamples of facts. G is held at its point estimate inside the bootstrap; this is noted as a limitation.
- **Definitions:** D1 and D4.

## B7. Controls
- **(a) Shuffled-fact null.**
  - Permute fact IDs within relation × template cells, 1000 times, on the balanced sets.
  - Recompute the ANOVA fact share each time and report the null distribution (mean, 95th and 99th percentiles) next to the observed share.
- **(b) Planted-depth recovery.**
  - Simulate on each model's exact correct-cell design (set i: its facts, relations, templates and missing cells).
  - Latent midpoint m = relation + relation:template + fact + residual, with planted shares: fact ∈ {0.1, 0.3, 0.5, 0.7} × template-main ∈ {0.05, 0.2}. Relation share is fixed at 0.05; residual = 1 − the rest. The latent total variance and mean match the observed D1 depth.
  - Per carrier, a sigmoid curve on the model's layer grid: p(l) = p_fin·σ((l+1)/L − m)/s), with p_fin drawn from the observed final probabilities and s = 0.05.
  - Apply D1 and D4 and refit the B3 model with lme4 (50 simulations per condition).
  - Report the bias of the recovered fact+subject and template-main shares against the planted values.
  - 95% coverage: within-relation fact bootstrap (200 resamples) with the ANOVA estimator on the balanced version of the design (simulated facts with all 3 templates).
  - Pass if every mean recovered share is within ±0.05 of the planted one.
  - Recovery is in latent-share units: D1 and D4 are nonlinear in m, so exact equality is not expected.
- **(c) Carrier facet.** There are 3 carriers, so carrier is added as a facet on the long per-carrier data for D1 and D4 (correct cells).
  - Model: `(1|relation) + (1|rt) + (1|fact) + (1|subject) + (1|carrier) + (1|fact:carrier) + (1|rt:carrier)`.
  - Carrier has 3 levels, so its own variance is poorly estimated. The main use is the fact:carrier share.

## B8. Outputs
In this directory, every file prefixed:
- `tables/EXPLORATORY_post-hoc_not-preregistered__E-depthvar_components.csv`;
- figures: stacked variance shares per model × definition, D-study curves, and a strip plot of 40 seeded random facts (seed 20261121) showing their 3 template depths per model;
- `..._REPORT_EXPLORATORY.md`: numbers, CIs and limitations only.

## Execution
- **Runs:** through `scripts/log_run.py` (nice 10, `prlimit --as=1.8 GB`). Peak RSS is checked with `/usr/bin/time -v` on the heaviest script; target under 1.5 GB.
- **One heavy job at a time, alongside the S5 job.** S5 is not running at the time of writing and is not touched.

## G1 decision rule (from the human's instruction, copied before any result)
- **PASS-PROMPT:** all of the following.
  - In ≥ 2 of 3 models under D1, the (template-main + residual) share exceeds the (fact + subject) share, with the bootstrap CI of the difference excluding 0.
  - The same direction holds under D4.
  - The null and planted checks pass.
  - No unresolved blocking skeptic issue.
- **PASS-FACT:** (fact + subject) share ≥ 0.5 in ≥ 2 of 3 models under both D1 and D4.
- **AMBIGUOUS:** anything else.
- **Analysis set for the rule:** set (i), correct cells (the human's primary set); set (ii) is reported alongside.
