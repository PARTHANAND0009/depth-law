# Design issue: the pre-registered headline depth measure is degenerate as specified

Source for every number below: `results/G0/G0-pythia-410m-21ffc75-20261105T214453Z/depth.parquet`
(run_id `G0-pythia-410m-21ffc75-20261105T214453Z`; pythia-410m, CPU, 100 random facts from
data/facts.parquet as of 21:27 UTC, template 0 only, 3 neutral carriers from configs/s3.yaml).

| measure (definition in code) | resolved / 100 | resolved among model-correct facts (N=15) | median depth (resolved) |
|---|---|---|---|
| causal_subj_stable (CLAUDE.md S3 spec, literal) | 0 | 0/15 | n/a |
| causal_subj_onset (first layer rank 1) | 0 | 0/15 | n/a |
| patchscope_depth (first source layer, stays correct) | 1 | 1/15 | 0.292 |
| causal_final (final-token patch, stays rank 1) | 15 | 15/15 | 0.750 (8 distinct values) |
| logit_lens_depth | 15 | 15/15 | 1.000 |

Model correct@1 on these 100 facts: 15/100.

## Why
1. **Subject-position patching cannot satisfy "rank 1 for all l' >= l".** A vector written at
   the subject token in block l only reaches the carrier's final position through attention
   in blocks > l. Near the top there are no blocks left, so late-layer patches always fail and
   the "stays rank 1 to the last layer" rule is never met. Under this definition the outcome
   is fully censored.
2. **Neutral carriers ("X is associated with") rarely elicit the specific object even when the
   information is present.** 0/15 correct facts reached rank 1 at any layer.
3. **Same-layer Patchscope shows the inverse pattern.** On the hand facts, extraction succeeds
   from early source layers (the patched vector is still close to the subject token, so the
   target prompt simply recomputes the fact) and fails at late ones. "First layer from which
   it stays correct" is therefore censored as well. See the hand-fact check on pythia-410m in
   the session log, e.g. France→Paris ok at layers 0–10 only.
4. **causal_final resolves, but clusters.** 6/15 facts sit at exactly 0.75 (block 18/24). That
   may be a model-level "context can no longer override" layer rather than per-fact
   resolution. Needs checking at scale before it carries a claim.

## Options (human decision before G1; prereg.yaml NOT changed)
A. **Window measure at the subject position:** keep subject patching with *relation-specific*
   carriers (Patchscope-style, target layer fixed early, e.g. block 0–2), and define depth as
   the *last* source layer whose state still lets the target recover the object. In the
   enrichment view, this is where the attribute stops being recomputed from identity and is
   carried by the representation. Requires a new definition and a prereg amendment.
B. **causal_final as headline** (well-defined, resolves every correct fact), with a
   carrier-override control: patch a *random other fact's* final state and record the layer
   where its object wins. Report depth relative to that model-level baseline.
C. **Keep the spec and accept censoring.** Then the discrete-time survival model carries G1
   alone. On this evidence that would yield no information (0 events).

Recommendation: B as headline, A as secondary, decided and written into prereg.yaml as a dated
amendment *before* any G1 data are fit.
