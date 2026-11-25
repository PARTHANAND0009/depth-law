# GATE G4: paper setup (P2 paper; ARR January 2027 → ACL 2027)

STATUS: AWAITING GO G4. No paper text has been written.

## 1. Items
| # | item | file(s) | state |
|---|---|---|---|
| 1 | P2 robustness simulation (preregistered, non-selecting) | plan `analysis/p2/robustsim_plan.md` (committed before the run), code `analysis/p2/p2_robustsim.R`, output `results/P2robust/`, report `reports/p2/P2_robustsim_report.md`, RESULTS.md section 9 | done (800/800; two container restarts, resumed from checkpoints; ledger NOTEs) |
| 2 | Skeptic follow-up (subject-position patching + relation:object term) | not run; in RESULTS.md section 8 (future work), `paper/outline.md` (Limitations), `claims/claims.md` | done |
| 3 | Venue rules and ACL AI policy (5 lines each, official sources) | `reports/paper/venue_rules.md` | done |
| 4 | Claims with macros, scope, status; positioning against the six papers | `claims/claims.md`; `scripts/make_numbers.py` → `paper/numbers.tex` | done (revised after reviews) |
| 5 | 3 titles + 150-word abstract | `reports/paper/titles_abstract.md` | done (revised after reviews) |
| 6 | Outline with page budget, figures, tables | `paper/outline.md` | done |
| 7 | Figure 1 (script + render, numbers from results files) | `src/depthlaw/figs/fig1_p2.py` → `paper/figs/fig1_p2.{pdf,png,json}`; caption draft `paper/figs/fig1_caption.md` | done |
| 8 | Dataset release plan and data card | `reports/paper/data_card.md` | done (licences to confirm by the human) |
| 9 | Reviews: claim-auditor, novelty-scout | `reports/gates/G4/{claim-auditor,novelty-scout}.md` (verbatim), `responses.md` | both REVISE; fixes applied; not re-reviewed (robustness additions not reviewed) |

## 1b. Robustness simulation result (non-selecting; cannot change any decision)
Source `reports/p2/P2_robustsim_report.md` (N = 100 per condition, 8 conditions, 300 bootMer resamples; truths A/B × L 24/36 × carriers 3/2, MNAR missingness ≈ 0.58).

| quantity | range over conditions | nominal |
|---|---|---|
| ICC(1) CI coverage | 0.79–0.89 | 0.95 |
| ICC(1) bias | −0.034 to −0.022 | 0 |
| ICC(1) misses: truth above / below CI | 126 / 4 (of 800) | 20 / 20 |
| diff CI coverage | 0.87–0.95 | 0.95 |
| diff lower bound > 0 when true diff = 0 (single measure) | 0.05–0.12 | 0.025 |

Reading: the fact-share interval errs low, so the licensed "above zero" is conservative under these conditions. The single-measure H1 interval test is liberal (2–5× nominal) when the truth is diff = 0; the full H1 condition (D1, D4 and MoM all agree) was not simulated. The Llama H1 result must be reported with this caveat. No decision, threshold or CI method changes (prereg section 4). Macros `\ptRob*`.

## 2. Review verdicts
| reviewer | verdict | summary |
|---|---|---|
| claim-auditor | REVISE | 6 blocking wording/scope findings (abstract "wording exceeded ... in only one model" misread the point estimates; correct-only scope; licensed-sentence wording; rank-1 note overgeneralised; "at most" read as a bound; titles 1–2 implied unlicensed claims). No number disagreed with its macro. All addressed (`responses.md`). |
| novelty-scout | REVISE | No central claim already published; combination NEW. Prompt dependence of localisation is known (Benz anecdotally, Chen at neuron level, Elhelo for behaviour with a 10-paraphrase ANOVA): must not be framed as a discovery. claims.md mischaracterised Benz (it has a 3-phrasing causal-tracing example), understated Chen, overclaimed the Elhelo delta. All corrected. |

## 3. Where the human's arc differs from what is licensed (details in `claims/claims.md`)
- (i) "does not set depth" → "adds almost nothing to marginal R² (upper bounds < 0.02)"; a survival model in the same data finds a small association; H3 was not blind.
- (ii) "relation identity does not set depth (preregistered null)" → H1 (a positive test) failed with small adjusted shares; this is not a confirmed null; relation orderings are moderately shared across families.
- (iii) "fact identity explains about 0.3 to 0.4 ..., wording most of the rest" → licensed: "The fact share is above zero." Estimates 0.28–0.42 (fact component includes answer-token identity) and 0.55–0.68 (paraphrase-related, mostly fact × paraphrase interaction); "wording most of the rest" as a finding is not licensed (H1 met in one family).
- (iv) "4 to 8 paraphrases needed" → "estimated for G = 0.8" (estimation only).
- (v) methods note, EXPLORATORY audit, scoped to the final-token patch; not a contribution, not in the abstract.
- (vi) S5 incomplete (pythia-2.8b 7/9 revisions; OLMo MISSING); no numbers cited.

## 4. Decisions for the human
1. **Integrity incident:** frozen `config/required_macros.json` was rewritten indirectly (additive, +130 P2 entries; commit 21692bb). Restore or accept: `reports/pending_frozen_changes/required_macros_P2/README.md`.
2. Title choice (recommended: 1).
3. Data release licences (CounterFact, PopQA, LRE; Llama 3.1 terms; infini-gram counts): `reports/paper/data_card.md`.
4. Whether to add "(three further preregistered models had too few correct answers)" to the abstract (+9 words; claim-auditor A2).

## 5. MISSING
- S5 (exploratory) incomplete; relaunched 2026-11-25 14:43 UTC by `scripts/p2_robustsim_run.sh` under the standing authorization (ledger NOTE); running.
- H-R secondary outcome logit-diff onset: PENDING (GPU; not run).
- P2: Qwen3-8B, pythia-1.4b, pythia-2.8b MISSING (insufficient data); H4 cross-family part MISSING.
