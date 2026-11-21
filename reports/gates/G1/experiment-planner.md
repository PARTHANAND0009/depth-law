<!-- EXPLORATORY (post hoc, not preregistered). experiment-planner subagent (.claude/agents/experiment-planner.md), fresh context, 2026-11-21. Saved verbatim by the main session; not edited. -->
Experiment plan at gate G1 (depth-law). Nothing was run and no files were written.

## Where things stand (sources read)
- Gate outcome is AMBIGUOUS (`reports/gates/G1/GATE_G1.md`). The stats-reviewer said REVISE: with fact share measured as within-relation ICC(1), the result would be PASS-FACT in 2 of 3 models. The skeptic said BLOCK: OLMo's "prompt > fact" result rests on one template, `company_ceo` "{} is led by its CEO,".
- Part 0a (`analysis/exploratory/E-depthvar/EXPLORATORY_post-hoc_not-preregistered__PART0A_REPORT.md`):
  - In OLMo, the D1 diff stays above 0 in all 26 leave-one-relation-out fits, but its minimum is 0.009 (the fit without `company_ceo`).
  - The self-readout test was inconclusive: the lens readout is late for all 3 `company_ceo` templates.
- Carrier facet (B7c in the report): carrier 0.005–0.044, fact:carrier 0.000–0.005, template:carrier 0.012–0.076. Carrier readout noise is small. The skeptic estimates that 64–81% of the residual is fact × template structure.
- `prereg/` contains only HR_revised.md, DEVIATIONS.md (empty) and HASH.txt. There are no amendments.
- No abstract exists (`paper/` has only models.tex). "Abstract wording" below therefore means the candidate claims in `claims/claims.md`.

## Measured GPU timings (S3b on the same GPU type: fp32, 3 carriers, 3900 rows = 52 chunks)
| model | total s | s/row | source |
|---|---|---|---|
| OLMo-2-1124-7B | 1245 | 0.319 | results/S3b/S3b-OLMo-2-1124-7B-923945f-20261121T061237Z/log.jsonl |
| pythia-2.8b | 630 | 0.162 | results/S3b/S3b-pythia-2.8b-a7dfeb5-20261121T064110Z/log.jsonl |
| pythia-1.4b | 317 | 0.081 | results/S3b/S3b-pythia-1.4b-a7dfeb5-20261121T063528Z/log.jsonl |

- Session overhead in that run: about 5 min from session start (06:08) to the first model start (06:12:43). Gaps between models were 1–2 min (`reports/env_gpu.md` plus run_id timestamps).
- Model download time was never logged: MISSING.

---

## E1 (rank 1): P2_prompt_vs_fact, the human's plan with seven changes. CONFIRMATORY (new amendment committed before any data)

**Decision it changes.** Claims 1–3 in `claims/claims.md` are EXPLORATORY now. The result would replace them with one confirmatory sentence, and it also decides how claim 5 (the co-occurrence null) is read:
- **Fact-driven:** "Causal depth is a stable property of the fact across 10 wordings (within-relation ICC(1) = x [CI]) in ≥2 families, yet within-relation co-occurrence does not predict it." The null becomes informative.
- **Wording-driven:** "Final-position causal depth is mostly a property of prompt wording. A single-template depth is not a fact-level quantity." The paper becomes a critique of the measure, and the depth-law null is partly explained by this.
- **Template/readout artifact:** "Apparent wording effects come from a few frames whose final token does not cue the answer. With final-token class controlled, depth is a fact property." This adds a methods recommendation.

**Changes I recommend before the amendment is committed:**
1. **Add `(1|fact:template)`, `(1|carrier)` and `(1|frame:carrier)` to the long-format model.**
   - In the planned formula, fact × wording interaction falls into the residual together with carrier-level noise. This is the conflation the skeptic flagged as issue 7.
   - In E-depthvar, template:carrier (0.012–0.076) was larger than fact:carrier (0.000–0.005). `(1|fact:carrier)` may go singular and could be dropped.
2. **Treat fact+subject as one unit unless the design separates them.**
   - `(1|subject)` and `(1|fact)` are identified only if subjects recur across relations, and the replicator found them confounded.
   - Either prereg their sum as the fact term, or deliberately choose subject-sharing relations.
3. **Make final-token class a crossed frame factor**, for example frames ending in a predicate word vs ending in punctuation.
   - The artifact explanation predicts this fixed effect absorbs most of σ²_frame.
   - Also prereg a leave-one-frame-out check of the decision.
4. **Prereg the analysis set.** Primary should be all cells; half_prob_depth is defined for every row, as in the H1 analysis. Correct cells should be secondary.
   - The skeptic showed the sign of OLMo's diff flips between all cells (about −0.05) and correct cells (+0.199).
   - S3b correct@1 was only 0.363 for OLMo. Qwen3/Llama accuracy is MISSING.
5. **Use outcome bands with a precision target instead of one cut at 0.5.**
   - E-depthvar's single-template ICC(1) range, 0.37–0.64, straddles 0.5. A rule like "lower CI ≥ 0.5" will probably give AMBIGUOUS again.
   - Example bands: <0.3 wording, 0.3–0.6 mixed, >0.6 fact. The human sets the numbers.
   - With only 10 frame levels, the frame variance is what limits the CI width. The simulation should report the expected ICC(1) half-width at E-depthvar-like components, and compare 300 facts × 10 frames against roughly 200 × 15 at equal GPU cost.
6. **Use facts never measured before.** `data/facts.parquet` has 200 facts per relation and only 50 per relation were used in S3b. Pick the 20 relations by a rule written down before data, not by their E-depthvar influence.
7. **Run Pythia on the GPU, not the CPU.**
   - The pythia-1.4b weights blob is 2.9 GB and pythia-2.8b is 5.7 GB (PROGRESS section 0). Both exceed the 1.8 GB CPU cap unless weights are streamed layer by layer.
   - On the GPU they cost about 4 + 8 min.
   - Consider OLMo before Llama: claim 3 (the only directional wording > fact result) is OLMo-only and cannot be confirmed or refuted without OLMo.
   - Check Llama gated access before renting; a failed download still burns billed minutes.

**Predicted outcomes**
| hypothesis | variance pattern in P2 |
|---|---|
| fact-driven (leading for Pythia) | within-relation ICC(1) above about 0.6. σ²_frame and σ²_fact:template small. Fact means correlate across models within relation (E-depthvar range 0.11–0.51). |
| wording-driven (shared wording computation) | frame + relation:frame + fact:frame > fact+subject. Frame BLUPs correlate across models. The order/form/length factors explain much of σ²_frame. Result is stable to leave-one-frame-out. |
| carrier/template artifact | σ²_frame is heavy-tailed, sitting in 1–2 frames that flip the decision when left out. The final-token class absorbs it. Outlier frames differ by model (the `company_ceo` outlier was OLMo-only). Carrier terms stay small, as in B7c. |
| my expectation | mixed: single-paraphrase ICC(1) about 0.35–0.6, frame share concentrated in punctuation-final frames, especially in OLMo. |

**Cost.** Rows are 300 facts × 10 paraphrases = 3000 per model. All GPU times are estimates scaled from the S3b s/row above.
| model | GPU min | basis |
|---|---|---|
| Qwen3-8B | about 18–25 | OLMo s/row × (8/7 nominal size). Upper end allows for more layers and a larger vocabulary for the per-layer lens. Not measured. |
| Llama-3.1-8B | about 18–22 | OLMo s/row × 8/7. Not measured. |
| OLMo-2-7B | about 16 | 0.319 s/row × 3000 |
| pythia-2.8b / 1.4b | about 8 / 4 | 0.162 and 0.081 s/row |

- **Qwen3 + Llama:** about 36–47 min of compute, plus about 5 min setup and 1–2 min per model switch, plus downloads (unmeasured).
  - INR 240 buys about 69 min, so this is tight. The 2-carrier fallback is likely to trigger.
- **All 5 models:** about 64–75 min of compute plus about 12 min overhead plus downloads. This needs the INR 500 top-up (total about 214 min), which is the human's call. It is well under the 20 GPU-hour ask threshold.
- **GPU memory:** an 8B model in fp32 is about 32 GB by parameter count × 4 bytes, which fits in 96 GB.
- **CPU:**
  - Bootstrap-coverage simulation: about 3–11 core-hours, or 1–4 h wall with 3 R workers, assuming about 100 simulation reps × 199 resamples and 0.5–2 s per lmer fit (an estimate). E-depthvar's 42-min main run is the reference point.
  - Confirmatory fits: about 2–6 h.
  - Peak RAM: E-depthvar's largest process was 258 MB and its build peaked at 516 MB, so this stays under 1.8 GB. Run one heavy job at a time. Note S5 needs about 11.9 GB if the human relaunches it.
- **Agent effort:** about 2–3 days: 200 frame instances written and checked, fact and relation selection rule, amendment, simulation, adapting `run_depth --halfprob` to the templates file, analysis, and reviews.
- **Timeline:** finishable by about Dec 1–3. That is before both the Dec 25 cutoff (ARR Jan 4 minus 10 days) and the Jan 4 cutoff (ICML abstract Jan 14 minus 10 days).

**Stop rules**
- **Before renting:**
  - If no bootstrap method reaches coverage ≥ 0.90 for ICC(1) in the simulation, do not rent.
  - If the expected ICC(1) CI is too wide to separate the preregistered bands, do not rent.
  - In either case, redesign the frame/fact split once; if it still fails, choose "write the paper now".
- **During the GPU session:**
  - A model is done at 3000 rows with 0 NaN.
  - After each model, compare billed minutes with the remaining balance and apply the preregistered fallback order (2 carriers, then drop the last-ranked model) before starting the next.
  - No reruns except chunk-resume after a crash.
- **After data:** one preregistered analysis, and the category is reported as it comes out. Any added model, frame or analysis is labeled EXPLORATORY.

---

## E2 (rank 2): finish the skeptic's tests on existing data, CPU only. EXPLORATORY

**Content:**
- Leave-one-template-out jackknife (56/60/72 template levels in set i).
- Two-stage relation → template → fact bootstrap, or parametric bootstrap, for the diff and for ICC(1). This also serves as the dry run of E1's code.
- D1 ≥ (L−1)/L treated as censored.
- Template final-token class as a fixed effect.
- An attenuation bound on the H3 null (ΔR² upper bound 0.0104 for OLMo, `results/HR_gate.md`) using fact-mean reliability.

**Decision it changes:**
- Claim 3 is either kept ("OLMo: wording ≥ fact, robust to template sampling") or rewritten to "no family difference distinguishable".
- Claim 5 gains or loses the sentence "the null is not explained by unreliable depth".
- The GATE_G1 category does not change. The stats-reviewer found that wider CIs can only remove exclusions.

**Predicted outcomes:**
- Wording-driven: the OLMo diff stays above 0 with the two-stage CI excluding 0 under every left-out template.
- Fact-driven or artifact: the two-stage CI includes 0. Leaving out the `company_ceo` template gives a diff near 0 (the relation-level drop already gave 0.009). Under the artifact explanation, final-token class absorbs most of OLMo's template-main share.
- My expectation: claim 3 is downgraded.

**Cost:** 0 GPU. About 1–3 CPU hours (estimate based on the 42-min E-depthvar run). Peak RAM under 0.6 GB (build peak 516 MB). Agent effort about 0.5 day.

**Stop rule:** log the criterion before running, as Part 0a did. One pass with no added variants. Stop and report MISSING after 4 CPU hours.

**Limit:** it re-analyses data already seen and cannot be confirmatory. It does not settle the gate by itself, so it ranks below E1. Part (b) is needed by E1 anyway.

---

## Rejected
- **S6 at spec scale (Claim 2):** estimated 31–46 A100-h (`reports/P1_compute.md`). Over budget.
- **OLMo S5 checkpoint dynamics:** about 8 × 21 min, roughly 166 min estimated from S3b. That uses nearly the whole topped-up budget and does not touch G1.
- **Gemma / Llama / Qwen H3 replications:** more nulls of the same kind.
- **Recomputing the G1 rule with the ICC(1) denominator:** that is a threshold change after seeing data and is not allowed.

## Files
- /home/user/depth-law/PROGRESS.md
- /home/user/depth-law/reports/gates/G1/GATE_G1.md
- /home/user/depth-law/reports/gates/G1/skeptic.md
- /home/user/depth-law/reports/gates/G1/stats-reviewer.md
- /home/user/depth-law/reports/gates/G1/responses.md
- /home/user/depth-law/analysis/exploratory/E-depthvar/EXPLORATORY_post-hoc_not-preregistered__PART0A_REPORT.md
- /home/user/depth-law/analysis/exploratory/E-depthvar/EXPLORATORY_post-hoc_not-preregistered__REPORT_EXPLORATORY.md
- /home/user/depth-law/claims/claims.md
- /home/user/depth-law/prereg/HR_revised.md
- /home/user/depth-law/results/HR_gate.md
- /home/user/depth-law/results/S3b/*/log.jsonl
- /home/user/depth-law/reports/env_gpu.md

RECOMMEND: E1
