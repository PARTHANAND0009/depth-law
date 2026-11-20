# Audit of causal_final (EXPLORATORY)

Requested by the human 2026-11-20.

## Key result
**causal_final resolves if and only if the model's own top-1 answer is the object. This holds by construction:**
- The measure patches the fact prompt's final-token residual at block l into the carrier's final token.
- At the last block (l = L-1), the patched state is the source's final residual. The carrier then outputs the source's own logits.
- The rule "rank 1 for all l' >= l" therefore requires rank 1 at the last block, which is the definition of correct@1.

So every causal_final depth is conditional on a correct answer, and every censored row is a wrong answer.

The audit confirms this with:
- live runs on pythia-410m (220 facts) and pythia-1.4b (20 hand facts);
- pythia-1.4b's S3 fp32 rows for the 200 random facts.

The patch mechanics are correct, and the carriers alone never predict the object.

The proposed replacement measure is in the last section. **No S3 rerun until the human approves it.**

## Runs
| what | run_id | model / dtype | facts |
|---|---|---|---|
| live audit | `AUDIT-pythia-410m-92ee9d9-20261120T134212Z` | pythia-410m, bf16 | 20 hand + 200 random (1 + 3 templates: 620 fact x template, 1860 x carrier) |
| live audit | `AUDIT-pythia-1.4b-341c906-20261120T135225Z` | pythia-1.4b, bf16, weights disk-offloaded | 20 hand |
| S3 rows, no new run | `S3-pythia-1.4b-b9a353d-20261108T064941Z` | pythia-1.4b, fp32 | the same 200 random facts (600 rows) |
| summaries | `AUDITsum-none-be31f9e-20261120T142742Z` | – | `results/AUDITsum/AUDITsum-none-be31f9e-20261120T142742Z/summary.json` |

- **Random facts:** `data/facts_g1cpu.parquet`, `sample(200, random_state=1234)`.
- **Hand facts:** `configs/hand_facts.yaml`.
- **Why bf16 / offload:** the S5 job holds 12 GB of the 14.3 GB memory cap.
- **Why no live pythia-1.4b run on the random facts:** it would take about 4 h offloaded. The S3 fp32 rows already store the per-layer patched ranks and the unpatched logit-lens ranks.

## 1. correct x resolved, per carrier
Carriers:
- 0 = "X is associated with"
- 1 = "Speaking of X, the first thing that comes to mind is"
- 2 = "X:"

Resolved = rank 1 for all l' >= l on that carrier.

| model / set | carrier | correct & resolved | correct & censored | wrong & resolved | wrong & censored | N |
|---|---|---|---|---|---|---|
| pythia-410m hand | 0, 1, 2 (each) | 15 | 0 | 0 | 5 | 20 |
| pythia-410m random | 0, 1, 2 (each) | 72 | 0 | 5 | 523 | 600 |
| pythia-1.4b hand (live) | 0, 1, 2 (each) | 18 | 0 | 0 | 2 | 20 |
| pythia-1.4b random (S3 fp32) | 0, 1, 2 (each) | 115 | 0 | 0 | 485 | 600 |
| pythia-1.4b, all 1300 G1 facts (S3) | all carriers | 720 | 0 | 0 | 3180 | 3900 |
| pythia-2.8b, all 1300 G1 facts (S3) | all carriers | 804 | 0 | 0 | 3096 | 3900 |

The last two rows come from `results/C1re/C1re-none-3cee850-20261120T141401Z/c1.json`.

- **The table is identical for every carrier.** Resolution is decided at the last block, which does not depend on the carrier.
- **The 5 "wrong & resolved" rows on pythia-410m are bf16 ties.**
  - These are 5 facts × 3 templates: f01047 Italy, f01181 India, f02304 Moscow, f03134 French, f03404 Russian.
  - In each, the object's rank is 1 under `rank_of` (no logit strictly greater), but argmax returns an equal-scoring token (" the" or " West").
  - In fp32 (S3) there are no such rows.

## 2. Mechanics checks
| check | pythia-410m | pythia-1.4b (hand) |
|---|---|---|
| source read position, causal_subj: decoded prompt up to the read index ends with the subject | 620/620 | 20/20 |
| source read position, causal_final: final prompt token (e.g. " is") | as designed (amendment_1); examples in summary.json | same |
| carrier write position, causal_final: final carrier token (" with", " is", ":") | yes, all 3 carriers | yes |
| carrier write position, causal_subj: placeholder token ("X", " X", "X") | yes | yes |
| hook writes the source vector exactly: max abs diff at the write position, mid block | 0.0 (150 checks) | 0.0 (60) |
| hook leaves other positions unchanged: max abs diff vs unpatched carrier at that block | 0.0 (both positions) | 0.0 |
| last-block identity: max abs logit diff, patched carrier vs source | 0.0625 (bf16; median 0.0039); object rank equal in 1860/1860 | 0.031; 60/60 |

**Note on the request.** The request asked to verify that the patch reads the subject's last token. The headline causal_final reads the **final** prompt token by design (prereg amendment_1, 2026-11-07). The original subject-last-token patch (causal_subj) resolved on 0 rows on both gate models (`reports/GATE_G1.md`). Both read positions are verified above.

## 3. Carriers alone (placeholder "X", unpatched)
| model | carrier | object at rank 1 | object in top 10 | median object rank | carrier's own top-1 |
|---|---|---|---|---|---|
| pythia-410m (N 620) | 0 | 0.000 | 0.000 | 10782 | " the" (620/620) |
| | 1 | 0.000 | 0.000 | 4208.5 | " that" (620/620) |
| | 2 | 0.000 | 0.000 | 21391 | "\n" (620/620) |
| pythia-1.4b (N 20) | 0 | 0.000 | 0.000 | 9524 | " the" |
| | 1 | 0.000 | 0.000 | 2431.5 | " the" |
| | 2 | 0.000 | 0.000 | 14898.5 | "\n" |

The carriers do not predict the object on their own.

## 4. Per layer: patched object rank next to the unpatched readouts
Shares are over fact x template x carrier rows. "Unpatched logit lens" is the source prompt's own residual at block l, read with the final norm and unembedding.

**pythia-1.4b, 200 random facts (S3 fp32), L = 24**

| block | correct: share patched obj rank 1 | correct: median patched rank | correct: unpatched logit-lens rank 1 | wrong: share patched rank 1 | wrong: median patched rank |
|---|---|---|---|---|---|
| 0 | 0.000 | 3507 | 0.000 | 0.000 | 6236 |
| 6 | 0.000 | 85 | 0.000 | 0.000 | 833 |
| 12 | 0.046 | 7 | 0.000 | 0.002 | 101 |
| 18 | 0.875 | 1 | 0.374 | 0.008 | 31 |
| 21 | 0.930 | 1 | 0.122 | 0.004 | 28 |
| 22 | 0.968 | 1 | 0.061 | 0.003 | 29 |
| 23 | 1.000 | 1 | 1.000 | 0.000 | 29 |

N = 345 correct, 1455 wrong (fact x template x carrier).

**pythia-410m, 220 facts (bf16), L = 24**

| block | correct: share patched rank 1 | correct: share patched top-1 = model's unpatched top-1 | wrong: share patched rank 1 | wrong: share patched top-1 = model's unpatched top-1 |
|---|---|---|---|---|
| 0 | 0.000 | 0.000 | 0.000 | 0.373 |
| 12 | 0.023 | 0.019 | 0.001 | 0.714 |
| 18 | 0.916 | 0.908 | 0.013 | 0.898 |
| 23 | 1.000 | 1.000 | 0.009 | 1.000 |

N = 261 correct, 1599 wrong.

The full curves for every block are in summary.json (`per_layer`).

What the curves show:
- **Wrong rows.** From block ~18 on, the patched carrier reproduces the model's own (wrong) top-1 in ≥ 0.90 of rows. The object stays at median rank ~30-60, so it can never "resolve".
- **Correct rows.** The object reaches rank 1 around block 18 under the patch, while the unpatched logit lens at the same block shows it at rank 1 in only 0.37 of rows.

So causal_final carries information beyond the logit lens, but only on correct rows.

## 5. Does the diagonal hold by construction? Yes.
- **What causal_final is:** "the earliest block from which the final-token state already commits the model's own top-1 answer, given that the answer is the object".
- **Its censoring is a correctness filter.** Every causal_final fit (G1, S4, S5, S8) is a fit on correctly answered rows only:
  - 18.5% of rows on pythia-1.4b;
  - 20.6% of rows on pythia-2.8b.
- **The survival hazard ratio for causal_final** therefore mixes "answers correctly" with "resolves earlier". `reports/C1_reanalysis.md` separates the two.

## 6. Proposed depth measure that does not require correctness (not adopted; needs approval)
Computed on the 410m audit sample only (`summary.json`, 200 random facts, 600 fact x template rows).

| measure | definition (per carrier, then mean over 3 carriers; normalized (l+1)/L) | share of rows defined | median depth, correct (N 72) | median, wrong | Spearman with causal_final (resolved, N 77) | Spearman with source object logprob (N) |
|---|---|---|---|---|---|---|
| **A: half-probability depth** (recommended) | first block l with p_patch(obj, l') >= 0.5 x p_patch(obj, L-1) for all l' >= l | 1.000 | 0.750 | 0.694 | 0.545 | 0.371 (600) |
| B: half-gain depth (logprob, the human's example) | gain(l) = logp_patch(obj, l) - logp_carrier-alone(obj); first l with gain(l') >= 0.5 x gain(L-1) for all l' >= l; undefined if gain(L-1) < ln 2 | 0.958 (correct 1.000, wrong 0.953) | 0.250 | 0.292 | 0.463 | -0.231 (588) |

Why A rather than B:
- **B's "half its final value" is not defined for a raw logprob** (it is negative), so B needs the carrier baseline.
- **On the log scale, half the gain is reached early (median block 6 of 24).** It is reached as soon as the object leaves the tail of the vocabulary (rank ~10^4 to ~10^2), so B mostly measures that coarse step.
- **A tracks where the answer's probability actually forms.** It agrees more with causal_final on resolved rows (0.545 vs 0.463) and is defined for every row, correct or not.

Caveats for A, to be handled in the analysis plan before any rerun:
1. **A is anchored to the model's final-layer probability.** It measures when the object's probability forms relative to its own final level, not whether the answer is right.
2. **A correlates with confidence:** Spearman 0.371 with the source object logprob. Any depth-vs-frequency fit with A must include object logprob (and margin) as covariates. This is the Claim 1g nested test.
3. **When p_final is tiny, A can be driven by noise.** A sensitivity version should drop rows where p_patch(obj, L-1) <= p_carrier-alone(obj).
4. **Adopting A changes the headline measure,** which needs a dated prereg amendment_2 (human approval) before any S3 rerun.
5. **Cost:** A needs the patched object logprob at every block. The causal-only S3 path already computes these logits (no extra forwards), so a rerun costs the same as S5 per fact.

## MISSING
- MISSING: live pythia-1.4b audit on the 200 random facts (about 4 h with weights offloaded, because S5 holds the RAM). The S3 fp32 rows were used instead for the 2x2 and per-layer ranks.
- MISSING: measures A and B on pythia-1.4b. Their per-block patched logprobs need a live run, because S3 stored ranks only.
