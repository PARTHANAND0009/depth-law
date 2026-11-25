# Paper outline: ACL 2027 long paper (ARR January 2027 cycle)

Limit: 8 pages of content (review version); Limitations, Ethics and references after the conclusion do not count; appendices after references do not count (rules: `reports/paper/venue_rules.md`). Template: official ACL style files, unmodified, anonymized (`\usepackage[review]{acl}`). Numbers only via `paper/numbers.tex`; model names via `paper/models.tex`. Claims and their status: `claims/claims.md`. Working title: candidates in `reports/paper/titles_abstract.md`.

## Main text (8.0 pages)
| § | section | pages | content | claims | display items |
|---|---|---|---|---|---|
| – | Abstract | – | 150 words, licensed sentences only | i–v | – |
| 1 | Introduction | 1.0 | question (fact vs prompt as the source of a layer-wise depth); why it matters (depth used to localise, edit, detect); two preregistered studies; contributions list; scope sentence (final-position readout, not storage) | i–iv | **Fig. 1** (top of p. 2, full width) |
| 2 | Related work | 0.6 | localisation vs editing (Hase 2023; Chen 2024); depth use (Gupta 2025); retrieval paths (Hochman 2026); query dependence (Elhelo 2026; Agarwal 2026); frequency and representations (Merullo 2025); tools (Benz 2026) | positioning | – |
| 3 | Measuring readout depth | 0.9 | final-token patch into neutral carriers; D1 (half of final probability), D4, rank-1 depth; derivation that rank-1 depth is defined only for correct prompts (EXPLORATORY audit numbers) | v | **Fig. 2** (patch schematic + audit 2×2, half column) |
| 4 | Study 1: frequency and relation (H-R prereg) | 1.4 | design (3 models, 2 families, EXACT counts, 1300 facts × 3 templates, all rows); H1 relation ICC; H2 cross-family orderings; H3 ΔR²; disclosure of prior exposure; survival model as non-gating contrast; correctness OR | i, ii | **Table 1** (H1, H2, H3 per model / pair with CIs); **Fig. 3** (forest plot of ΔR² and ICC_rel with preregistered bounds, half column) |
| 5 | Study 2: fact vs phrasing (P2 prereg) | 2.8 | 5.1 design (300 facts × 10 frames × 3 carriers, 5 models, inclusion rule, correct cells, frozen mixed model, CI method, parametric null) 1.1; 5.2 results: inclusion (3 MISSING), ICC(1), wording share, H1/H1-alt per model, the licensed sentence, n′ / D-study, H3 1.2; 5.3 sensitivities and robustness simulation (non-selecting) 0.5 | iii, iv | **Table 2** (P2 per model: ICC(1), wording, diff, MoM, H1/H1-alt, n′, null p); Fig. 1 referenced |
| 6 | Discussion | 0.9 | what the licensed sentence does and does not say (answer-token identity, conditional on covariates); fact × paraphrase interaction as the main non-fact component; implications for single-prompt depth claims; why the frequency and relation nulls are bounded, not absolute | i–iv | – |
| 7 | Conclusion | 0.4 | three sentences + release | – | – |

Total 8.0 pages including Fig. 1 (≈ 0.45 page), Fig. 2 (≈ 0.25), Fig. 3 (≈ 0.25), Table 1 (≈ 0.25), Table 2 (≈ 0.3).

## After the conclusion (not counted)
- **Limitations** (required; no new results): two included families in P2; correct-only scope and possible selection; readout at the final position only (subject position not patched: future work, skeptic G2); fact component includes answer-token identity (no relation × object term: future work); 10 designed frames; PROXY covariate in P2; CI coverage 0.925 in one simulated condition; null mildly liberal, power 0.46 at fact share 0.10; H-R not blind; S6 controlled-frequency pretraining underpowered; English only; ≤ 8B models.
- **Ethics statement**: models and data used (licences), no personal data beyond public-figure facts from public KBs, compute (GPU minutes, CPU), potential misuse (none specific).
- **Acknowledgements** (review version anonymized): AI-assistance disclosure per ACL policy: experiments, analysis code and drafting were done with Claude Code agents under the preregistrations and a guard harness; every claim was checked at human gates; the human author is responsible for all content; AI tools are not authors. Same disclosure in checklist item E1.

## Appendices (after references)
| app. | content |
|---|---|
| A | Preregistrations: HR_revised.md (frozen 7725c5b, hash) and P2_prompt_vs_fact.md (tag prereg-P2 = ff119ca, sha256 from HASH_P2.txt); verbatim decision rules and wording rules |
| B | Deviations: D-A0, D-P2-20261124T044034Z-0 (off-instance copy; no measurement change); unused H100 draft noted |
| C | Simulations: CI-method v1/v2 (coverage table), null calibration and power, robustness simulation (non-selecting) |
| D | P2 sensitivities: new226, all, all10, nomanufacturer, tcov, lofo; H4 (EXPLORATORY); D2/D3 secondary outcomes |
| E | H-R robustness variants and secondary outcomes (table); survival model |
| F | Materials: relations, the 10 frames, carriers, sampling rules, paraphrase generation |
| G | Reproducibility harness: guards, ledger, replicator and reviewer verdicts per gate (summary table), compute |
| H | Data card (`reports/paper/data_card.md`) |
| I | EXPLORATORY: S5 checkpoint dynamics (only if complete) |

## Figures and tables (all from results files; one script per figure in `src/depthlaw/figs/`, PDF + PNG + JSON of plotted numbers)
| item | script | inputs |
|---|---|---|
| Fig. 1 | `src/depthlaw/figs/fig1_p2.py` | `results/P2analysis/correct/long_*_correct.csv`, `fit_*_correct_D1.json` |
| Fig. 2 | `src/depthlaw/figs/fig2_patch_audit.py` (to write) | `results/C1re/.../c1.json` |
| Fig. 3 | `src/depthlaw/figs/fig3_hr_forest.py` (to write) | `results/HR_gate.json` |
| Table 1 | generated LaTeX from `paper/numbers.tex` macros | – |
| Table 2 | generated LaTeX from `paper/numbers.tex` macros | – |

## Schedule
- G4 setup: this file, claims, Figure 1, data card, reviews → AWAITING GO G4.
- G5 full draft by 2026-12-21 (after GO G4).
- G6 freeze by 2027-01-01 (after GO G5). Deadline 2027-01-04 23:59 AoE. Fallback ICML 2027 (Jan 22).
