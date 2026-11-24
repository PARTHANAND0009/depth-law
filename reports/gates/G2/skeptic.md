<!-- skeptic subagent, fresh context, 2026-11-24, gate G2 (P2 results). Scope: P2 only. Read-only: no repo file was edited, no model was refitted and no bootstrap was run. Saved verbatim by the main session; not edited. The scratch scripts it cites were copied to results/G2_skeptic_scratch/ (EXPLORATORY; not logged runs). -->
# G2 skeptic report: P2 (prompt vs fact in causal resolution depth)

**Bottom line.** The analysis follows the preregistration, and every number I checked matches its results file. My objection is to interpretation. The quantity measured is the depth at which the answer becomes readable at the prompt's final position, not where a fact lives. The "wording" share that drives H1 is mostly a fact × paraphrase interaction, and a neutral prefix alone reproduces most of it. The one licensed sentence ("The fact share is above zero") was close to certain before the data came in. It is also confounded with answer-token identity, and the prereg model has no term to separate the two. None of this changes a gating flag in `p2_decision.json`. All of it changes what a reader may take from the results.

**Labelling of my own numbers.** Numbers marked [scratch] are my own reviewer computations. They are EXPLORATORY, not logged runs, and must not go into RESULTS.md or the paper. I computed them from `results/P2analysis/correct/long_*_correct.csv`, `fit_*_correct_D*.json` and `materials/facts_v1.jsonl`. The scripts are in `/tmp/claude-0/-home-user-depth-law/79d106ca-74b7-5e19-8ef3-6880f992c1ff/scratchpad/skep/` (a1.py to a8.py).

## Number check (no finding)
I checked these RESULTS.md values against the JSON files:
- **§2:** inclusion counts.
- **§3:** every ICC(1), wording, diff and n′ value with its CI; the MoM diffs; the shares of total variance; the null p and the null quantiles.
- **§3 secondary outcomes:** ICC(1) and diff for D2 and D3.
- **§5:** H3 (ρ 0.373, k̄, G(k̄), 0.463).
- **§6:** every sensitivity row (rows/facts, ICC(1) D1 and CI, diff D1 and D4 and CIs, MoM diffs, singular flags) and every lofo min–max.

Sources: `results/P2analysis/{correct,new226,all,all10,nomanufacturer,tcov,lofo}/p2_results.json` and `correct/p2_decision.json`.

All match to 3 dp. The replicator had already recomputed §2–§5 from the raw runs. I found no number without a source file, except the INR spend, which is labelled as a human figure.

## Findings

### 1. The construct is readout depth at the prediction position, not "where a fact lives". Severity: major
- **What is patched.** `src/depthlaw/p2/run_p2.py:112` patches `states[:, -1]`, the residual at the final token of the fact prompt, into the final token of each carrier. That token is "is", "of" or ":" in "A:". The project's own causal depth (CLAUDE.md S3; `src/depthlaw/depth/causal.py:3`) patches the subject's last token instead. The prereg is explicit about the final token, so this is not a deviation, but the title and question ("a fact's causal resolution depth") borrow the subject-position term.
- **The carriers add almost nothing.** Carrier-level variance, (fc + e)/nc, is 0.015–0.041 of den [scratch, from `fit_*_D1/D4.json` vc]. In 67% (Llama) and 75% (OLMo) of cells, all three carriers give an identical D1 [scratch]. So the "causal carrier patch" is in effect the source's final-position residual run through the remaining layers, which is close to a lens readout.
- **Why wording dependence is expected.** At the prediction position, the time at which the answer becomes readable depends on attention routing from the subject: how far away it is, the syntax, and which token is final. That is wording-dependent almost by construction.
- **What the design cannot separate.** It cannot tell "the fact's storage depth varies with wording" from "storage is fixed, but extraction to the final position varies with wording".
- **Required.** Scope every claim to "answer-readout depth at the final position". The phrase "where a fact lives" is not licensed.

### 2. H1 ("wording > fact") rests on the fact × paraphrase interaction, which a neutral prefix reproduces. Severity: major
- **Splitting den.** I split den into three parts [scratch, from vc]:

  | model, measure | fact | systematic wording (rt + frame) | ft |
  |---|---|---|---|
  | Llama D1 | 0.310 | 0.177 | 0.473 |
  | Llama D4 | 0.282 | 0.306 | 0.372 |
  | OLMo D1 | 0.422 | 0.203 | 0.343 |
  | OLMo D4 | 0.373 | 0.327 | 0.285 |

  Systematic wording is below the fact share in 3 of 4 fits. The prereg's own "wording shifts every fact together" quantity is negative in both models: −0.323 and −0.168 (RESULTS §3). So Llama's H1 holds because ft is counted on the wording side.
- **Neutral-prefix test.** Frames 1, 3, 5 and 7 differ from frames 0, 2, 4 and 6 only by the prefix "According to reference sources, ", so they are near-null paraphrases. After removing relation × frame means, I compared the within-fact RMS change in D1 for three kinds of frame pair [scratch, a8.py]:

  | model | length (neutral prefix) | order | form |
  |---|---|---|---|
  | Llama | 1.41 layers (N = 384) | 1.54 (N = 338) | 1.50 (N = 307) |
  | OLMo | 1.08 layers (N = 511) | 1.29 (N = 444) | 1.74 (N = 395) |

  D4 shows the same pattern.
- **Reading.** Most of the "wording" variance is fact-specific sensitivity to any perturbation. That is instability of a single-prompt measurement, not an effect of meaningful wording content.
- **Required.** Report ft separately from rt + frame wherever the "wording share" appears. Any "prompt wording matters more than the fact" reading is misleading.

### 3. The only licensed sentence is nearly foreknown and is confounded with answer identity. Severity: major
- **Foreknown.** Prereg §0 discloses G1 within-relation ICC(1) of 0.37–0.64 on OLMo-2-7B. The null's 99th percentile is 0.043 (Llama) and 0.034 (OLMo), against observed ICC(1) of 0.310 and 0.422 (`correct/p2_results.json` null). Almost any item-level measurement would reject this null.
- **Objects are shared.** 186 of the 300 facts share their object with another fact in the same relation [scratch]. Continent, instrument and music_genre have 3 distinct objects among 15 facts. The model has no `(1|relation:object)` term, so answer-token variance loads onto `(1|fact)`. `answer_prior` is a single linear covariate and does not absorb it.
- **Permutation test.** Shuffling object labels within relation, on fact means of facts with ≥ 2 correct paraphrases [scratch, a4.py]:
  - OLMo: p = 0.0005 for D1 and for D4;
  - Llama: p = 0.026 for D4 and p = 0.23 for D1.
- **Size.** A crude object ICC among fact means within relation is about 0.54 (D1) and 0.67 (D4) for OLMo, and 0.28 and 0.20 for Llama [scratch, a3.py].
- **Required.** The sentence should read "fact-level variance, which includes answer-token identity, is above zero". It does not support "facts have their own depth". H1-alt, the claim that would, failed in both models.

### 4. The fact share depends on the measure, and D1 and D4 are not independent checks. Severity: major
- **Range.** ICC(1) runs from 0.172 to 0.406 (Llama) and from 0.275 to 0.422 (OLMo) across D1–D4 (RESULTS §3).
- **The model ordering flips.** Under D1, OLMo is more fact-stable (0.422 vs 0.310). Under D2, Llama is (0.406 vs 0.275).
- **D1 and D4 share one curve.** Both are computed from the same curve relative to p_final. Their cell-level Spearman is 0.80 (Llama) and 0.88 (OLMo) [scratch]. So "under D1 and D4" is weak corroboration.
- **Reading.** The share is a property of the threshold definition as much as of facts. No cross-model comparison of fact-stability is licensed.

### 5. All the variance sits in a band about two layers wide. Severity: minor
- **Range of D1.** D1 has 22–23 distinct values. Its interquartile range is about 2 of 32 layers in both models [scratch].
- **Component sizes.** The fact SD is 1.06 layers (Llama) and 1.30 layers (OLMo). The ft SD is 1.31 and 1.17 layers (from vc × 32).
- **Reading.** The paper decomposes ±1-layer differences on a one-layer grid. State the absolute scale next to every share.

### 6. Only two models, both high-knowledge, with the same answer tokenization. Severity: major for external validity; changes no flag
- **Who was excluded.** The minimum-data rule excluded Qwen3-8B, pythia-1.4b and pythia-2.8b by behaviour (RESULTS §2).
- **The two included models tokenize answers identically.** Llama-3.1-8B and OLMo-2-7B have the same first-token id for 300 of 300 objects (`materials/facts_v1.jsonl`). So the "≥ 2 families" requirement is weaker than it looks for any token-driven effect.
- **Consequence.** Every claim is unanimous by necessity, and nothing generalises beyond 7–8B models that know these facts.

### 7. OLMo sits at the boundary; there is no heterogeneity test, and the check on CI coverage was not run. Severity: minor
- **The boundary.** OLMo's D1 diff CI is [−0.004, 0.272]. The stats-reviewer estimates the Monte Carlo SE of the interval end at about 0.006.
- **No test of model difference.** No between-model test was preregistered, and the diff CIs overlap: Llama [0.220, 0.474], OLMo [−0.004, 0.272]. "H1 in Llama, not in OLMo" must not be read as a difference between models.
- **The relevant check is MISSING.** The preregistered robustness simulation (discretised D1, missingness tied to correctness, truths near the boundary) is MISSING (RESULTS §7). That is exactly the regime of this result. D1 is also bounded and right-skewed: the 1st, 50th and 99th percentiles are layers 12, 16 and 24 for Llama [scratch]. Gaussian parametric-bootstrap coverage on such data is unverified.

### 8. H3's cross-model agreement sits mostly at the relation and object level. Severity: minor
- **Breakdown** [scratch, a7.py]:

  | version | N | ρ |
  |---|---|---|
  | raw | 190 | 0.373 |
  | relation-demeaned | 189 | 0.327 |
  | relation-demeaned object means | 111 groups | 0.414 |
  | within relation:object | 113 | 0.194 |

  The last value covers only facts that share an object, and it is not disattenuated.
- **Reading.** The agreement that is left once relation and object are removed is weak. The disattenuation uses G built on a fact variance that includes object variance.

### 9. Position and confidence. Severity: minor
- **Position covariates.** In the `tcov` sensitivity (template covariates added), OLMo's diff D1 falls from 0.124 to 0.082 [−0.039, 0.230] (`tcov/p2_results.json`).
- **Within-fact correlations in OLMo** [scratch]:
  - D1 with prompt length: r = −0.27;
  - D1 with the cell's object log-prob: r = −0.26.
  - In Llama, both are about 0.
- **Reading.** Part of OLMo's ft and wording variance is "longer prompt or more confident cell → earlier readout". That is a mechanical explanation, not a semantic one.

### 10. Selection on correct cells. Severity: minor
- **How much is selected.** Correct cells are 1221/3000 (Llama) and 1355/3000 (OLMo).
- **Frames see different facts.** Per-frame counts of correct cells range from 65 to 179 (Llama) [scratch]. So each frame sees a behaviour-selected subset of facts.
- **The `all` sensitivity gives similar ICC(1).** Llama 0.344 (correct set 0.310); OLMo 0.406 (correct set 0.422).
- **Reading.** Selection probably does not drive the shares. It does mean the frame components are not estimated from the same facts.

## Strongest honest one-paragraph summary
In Llama-3.1-8B and OLMo-2-1124-7B, we patched the final-position residual of each prompt into neutral carriers. This measures the layer at which the answer becomes readable at the prediction position, for 300 facts × 10 paraphrases, restricted to correctly answered prompts. The three other preregistered models had too few such facts (MISSING). Conditional on four fact-level covariates, between-fact variance is 0.31 [0.24, 0.37] (Llama) and 0.42 [0.35, 0.49] (OLMo) of within-relation variance in D1. It is reliably above zero: null p = 0.001 in both, the smallest possible with 1000 null datasets. Most of the rest is fact-specific sensitivity to paraphrase, not a uniform shift by wording: wording-common minus residual is −0.32 and −0.17. Wording exceeded the fact component in Llama under both preregistered measures. In OLMo the D1 interval touched zero, and neither model showed fact dominance. One prompt therefore gives a noisy estimate of a fact's readout depth. Whether the between-fact component reflects the fact itself or the answer token, and whether any of this holds at the subject position, was not tested.

## Reviewer score
Reject as it stands. The narrow claim is sound. But the measurement does not address "where a fact lives", the "wording" component is mostly perturbation sensitivity, and the only licensed positive claim is near-trivial and confounded with answer identity.

## The one experiment most likely to change my assessment
Rerun the same 300 × 10 design on Llama-3.1-8B and OLMo-2-7B with subject-last-token patching, using a depth rule defined for that position (e.g. onset of half the maximum, since the top layers cannot move the subject state). Fit the frozen formula plus `(1|relation:object)`. This needs a new preregistration or amendment.
- If the fact share stays high at the subject position and survives the object term, while the final-position share does not, the paper has a real finding: storage is fact-stable and extraction is prompt-dependent.
- If the subject-position shares look like these, "depth is mostly prompt-specific" generalises.

The GPU session ran all five models in 58 min, so two models should cost under an hour.

**Files cited:**
- /home/user/depth-law/prereg/P2_prompt_vs_fact.md
- /home/user/depth-law/prereg/deviations/D-P2-20261124T044034Z-0.md
- /home/user/depth-law/reports/p2/RESULTS.md
- /home/user/depth-law/results/P2analysis/correct/p2_results.json
- /home/user/depth-law/results/P2analysis/correct/p2_decision.json
- /home/user/depth-law/results/P2analysis/correct/fit_{Llama-3.1-8B,OLMo-2-1124-7B}_correct_D{1,2,3,4}.json
- /home/user/depth-law/results/P2analysis/correct/long_{Llama-3.1-8B,OLMo-2-1124-7B}_correct.csv
- /home/user/depth-law/results/P2analysis/{new226,all,all10,nomanufacturer,tcov,lofo}/p2_results.json
- /home/user/depth-law/materials/facts_v1.jsonl
- /home/user/depth-law/materials/paraphrases_v1.jsonl
- /home/user/depth-law/src/depthlaw/p2/run_p2.py (line 112)
- /home/user/depth-law/src/depthlaw/depth/causal.py (line 3)
- Scratch scripts: /tmp/claude-0/-home-user-depth-law/79d106ca-74b7-5e19-8ef3-6880f992c1ff/scratchpad/skep/a1.py through a8.py

VERDICT: REVISE
