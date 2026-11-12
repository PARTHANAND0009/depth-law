# GATE G1

Source of every number: `results/G1/G1-none-3d0e3e5-20261110T233528Z/g1.json` (run_id `G1-none-3d0e3e5-20261110T233528Z`).

## Decision rule (configs/prereg.yaml g1 + amendment_1)
PASS = partial R^2 >= 0.1 with negative slope on causal_final; WEAK = >= 0.05; GO needs >= 2 PASS models.

| model | count index (label) | partial R² | outcome |
|---|---|---|---|
| EleutherAI/pythia-1.4b | piletrain (EXACT) | 0.001 | FAIL |
| EleutherAI/pythia-2.8b | piletrain (EXACT) | -0.018 | FAIL |

PASS models: 0 (need 2). Gate models not run: olmo-2-1124-7b. **Outcome: NO-GO**

## Per model × measure

| model | measure | N resolved / censored | N fit | partial R² [CI] | slope [CI] | p (Holm) | HR [CI] | best shape (AIC) |
|---|---|---|---|---|---|---|---|---|
| EleutherAI/pythia-1.4b | causal_final | 720 / 3180 | 720 | 0.001 [-0.028, 0.028] | 0.0024 [-0.0075, 0.0103] | 1.0000 | 1.254 [1.159, 1.357] | linear |
| EleutherAI/pythia-1.4b | patchscope_depth | MISSING: fewer than 30 resolved rows (25) | | | | | | |
| EleutherAI/pythia-1.4b | tuned_lens_depth | MISSING: fewer than 30 resolved rows (0) | | | | | | |
| EleutherAI/pythia-1.4b | logit_lens_depth | 720 / 3180 | 720 | -0.003 [-0.052, 0.027] | 0.0017 [-0.0038, 0.0058] | 1.0000 | 1.227 [1.144, 1.316] | logistic |
| EleutherAI/pythia-1.4b | causal_subj_onset | MISSING: fewer than 30 resolved rows (0) | | | | | | |
| EleutherAI/pythia-2.8b | causal_final | 804 / 3096 | 804 | -0.018 [-0.056, 0.033] | 0.0029 [-0.0083, 0.0146] | 1.0000 | 1.273 [1.171, 1.384] | logistic |
| EleutherAI/pythia-2.8b | patchscope_depth | 39 / 3861 | 39 | 0.015 [-0.444, 0.067] | 0.0249 [-0.0001, 0.0373] | 1.0000 | 0.981 [0.807, 1.193] | linear |
| EleutherAI/pythia-2.8b | tuned_lens_depth | MISSING: fewer than 30 resolved rows (0) | | | | | | |
| EleutherAI/pythia-2.8b | logit_lens_depth | 804 / 3096 | 804 | -0.001 [-0.044, 0.013] | -0.0012 [-0.0056, 0.0029] | 1.0000 | 1.247 [1.157, 1.345] | logistic |
| EleutherAI/pythia-2.8b | causal_subj_onset | MISSING: fewer than 30 resolved rows (0) | | | | | | |

CIs: cluster bootstrap over relations (n_boot = 1000); HR = discrete-time cloglog hazard ratio per unit log1p(exact cooc), relation-clustered SEs. Holm across models × measures.

## Controls and sensitivities (headline measure)

| model | override median | Spearman(headline, override) | share equal | CNF-predictor partial R² | +override covariate partial R² | exact vs CNF Spearman (non-approx, N) |
|---|---|---|---|---|---|---|
| EleutherAI/pythia-1.4b | 0.708 | 0.723 | 0.351 | 0.008 | -0.027 | 0.773 (221) |
| EleutherAI/pythia-2.8b | 0.594 | 0.798 | 0.250 | -0.004 | -0.004 | 0.773 (221) |

## Measure agreement (fact-level Spearman)

**EleutherAI/pythia-1.4b**: causal_final|patchscope_depth 0.44; causal_final|logit_lens_depth 0.10; patchscope_depth|logit_lens_depth 0.31
**EleutherAI/pythia-2.8b**: causal_final|patchscope_depth 0.02; causal_final|logit_lens_depth 0.28; patchscope_depth|logit_lens_depth 0.25

## 5 example facts per frequency decile (headline depth, template mean)

**EleutherAI/pythia-1.4b**

| decile | subject | object | relation | exact cooc | depth | correct |
|---|---|---|---|---|---|---|
| 0 | Chi Herculis | Hercules | constellation | 0 | MISSING | 0.00 |
| 0 | thyssenkrupp AG | Ulrich Lehner | company_ceo | 0 | MISSING | 0.00 |
| 0 | Theta Pegasi | Pegasus | constellation | 0 | 0.819 | 1.00 |
| 0 | Semirechye Oblast | Almaty | capital | 0 | MISSING | 0.00 |
| 0 | Uber Technology | Dara Khosrowshahi | company_ceo | 0 | MISSING | 0.00 |
| 1 | Pomponius Mela | geography | field_of_work | 0 | 0.778 | 0.33 |
| 1 | William Rees-Mogg | BBC | employer | 0 | MISSING | 0.00 |
| 1 | James George Frazer | folklore | field_of_work | 0 | 0.660 | 0.67 |
| 1 | Whiteshell Laboratories | Canada | country | 0 | MISSING | 0.00 |
| 1 | Test Drive Le Mans | Atari | developer | 0 | MISSING | 0.00 |
| 2 | Amy Stoch | actor | occupation | 0 | MISSING | 0.00 |
| 2 | Clio Goldsmith | French | native_language | 0 | MISSING | 0.00 |
| 2 | Jean-Marie Pardessus | French | native_language | 0 | 0.731 | 1.00 |
| 2 | Matthieu Chedid | guitar | instrument | 0 | MISSING | 0.00 |
| 2 | Chris Speed | jazz | music_genre | 0 | MISSING | 0.00 |
| 3 | Theodore Haak | London | place_of_death | 0 | MISSING | 0.00 |
| 3 | Giulio Bisegni | Frascati | place_of_birth | 0 | MISSING | 0.00 |
| 3 | Kalyan Kumar | Bangalore | place_of_death | 0 | MISSING | 0.00 |
| 3 | Tusculanae Disputationes | Latin | original_language | 0 | MISSING | 0.00 |
| 3 | Fox Butterfield | Lancaster | place_of_birth | 0 | MISSING | 0.00 |
| 4 | Brian Steen Nielsen | midfielder | sport_position | 0 | MISSING | 0.00 |
| 4 | Hans Cornelis | association football | sport | 0 | MISSING | 0.00 |
| 4 | Iowa Wild | ice hockey | sport | 0 | MISSING | 0.00 |
| 4 | TV Rain | Natalya Sindeyeva | company_ceo | 2 | MISSING | 0.00 |
| 4 | Edward Hitchcock | Massachusetts | place_of_death | 1 | MISSING | 0.00 |
| 5 | Khanty-Mansi Autonomous Okrug | Russian | official_language | 3 | 0.722 | 0.33 |
| 5 | Frank Strazzeri | jazz | music_genre | 3 | 0.625 | 0.33 |
| 5 | Dave Darling | composer | occupation | 2 | MISSING | 0.00 |
| 5 | Novartis | Joseph Jimenez | company_ceo | 3 | MISSING | 0.00 |
| 5 | Staver | Chicago | headquarters | 3 | MISSING | 0.00 |
| 6 | Aarau | German | official_language | 6 | 0.583 | 1.00 |
| 6 | HFS Plus | Apple | manufacturer | 4 | MISSING | 0.00 |
| 6 | Mithat Bayrak | Turkish | native_language | 6 | 0.722 | 0.33 |
| 6 | Henryk Sienkiewicz | Poland | citizenship | 4 | 0.681 | 0.67 |
| 6 | Marvin Stamm | trumpet | instrument | 7 | MISSING | 0.00 |
| 7 | Nikolay Nekrasov | Russian | native_language | 9 | 0.662 | 1.00 |
| 7 | Narciso Yepes | guitar | instrument | 10 | MISSING | 0.00 |
| 7 | Jamie Cullum | jazz | music_genre | 11 | 0.847 | 0.33 |
| 7 | Lena Valaitis | Germany | citizenship | 18 | MISSING | 0.00 |
| 7 | Rosneft | Moscow | formation_location | 19 | MISSING | 0.00 |
| 8 | Saint Pierre and Miquelon | French | official_language | 51 | 0.759 | 1.00 |
| 8 | Elvis Presley | guitar | instrument | 45 | 0.688 | 0.67 |
| 8 | Thomas de Waal | journalist | occupation | 56 | MISSING | 0.00 |
| 8 | Kiribati | South Tarawa | capital | 83 | MISSING | 0.00 |
| 8 | Robert Scoble | Microsoft | employer | 26 | MISSING | 0.00 |
| 9 | Windows XP | Microsoft | manufacturer | 8838 | 0.657 | 1.00 |
| 9 | Gambro | Lund | formation_location | 575 | MISSING | 0.00 |
| 9 | LGA 775 | Intel | manufacturer | 154 | MISSING | 0.00 |
| 9 | Iceland | Reykjavík | capital | 4742 | 0.667 | 1.00 |
| 9 | Windows 8 | Microsoft | developer | 5921 | 0.634 | 1.00 |
**EleutherAI/pythia-2.8b**

| decile | subject | object | relation | exact cooc | depth | correct |
|---|---|---|---|---|---|---|
| 0 | Chi Herculis | Hercules | constellation | 0 | MISSING | 0.00 |
| 0 | thyssenkrupp AG | Ulrich Lehner | company_ceo | 0 | MISSING | 0.00 |
| 0 | Theta Pegasi | Pegasus | constellation | 0 | 0.719 | 1.00 |
| 0 | Semirechye Oblast | Almaty | capital | 0 | MISSING | 0.00 |
| 0 | Uber Technology | Dara Khosrowshahi | company_ceo | 0 | 0.969 | 0.33 |
| 1 | Pomponius Mela | geography | field_of_work | 0 | 0.594 | 0.33 |
| 1 | William Rees-Mogg | BBC | employer | 0 | MISSING | 0.00 |
| 1 | James George Frazer | folklore | field_of_work | 0 | MISSING | 0.00 |
| 1 | Whiteshell Laboratories | Canada | country | 0 | MISSING | 0.00 |
| 1 | Test Drive Le Mans | Atari | developer | 0 | MISSING | 0.00 |
| 2 | Amy Stoch | actor | occupation | 0 | MISSING | 0.00 |
| 2 | Clio Goldsmith | French | native_language | 0 | MISSING | 0.00 |
| 2 | Jean-Marie Pardessus | French | native_language | 0 | 0.542 | 1.00 |
| 2 | Matthieu Chedid | guitar | instrument | 0 | MISSING | 0.00 |
| 2 | Chris Speed | jazz | music_genre | 0 | MISSING | 0.00 |
| 3 | Theodore Haak | London | place_of_death | 0 | MISSING | 0.00 |
| 3 | Giulio Bisegni | Frascati | place_of_birth | 0 | MISSING | 0.00 |
| 3 | Kalyan Kumar | Bangalore | place_of_death | 0 | MISSING | 0.00 |
| 3 | Tusculanae Disputationes | Latin | original_language | 0 | 0.729 | 0.33 |
| 3 | Fox Butterfield | Lancaster | place_of_birth | 0 | MISSING | 0.00 |
| 4 | Brian Steen Nielsen | midfielder | sport_position | 0 | MISSING | 0.00 |
| 4 | Hans Cornelis | association football | sport | 0 | MISSING | 0.00 |
| 4 | Iowa Wild | ice hockey | sport | 0 | MISSING | 0.00 |
| 4 | TV Rain | Natalya Sindeyeva | company_ceo | 2 | MISSING | 0.00 |
| 4 | Edward Hitchcock | Massachusetts | place_of_death | 1 | MISSING | 0.00 |
| 5 | Khanty-Mansi Autonomous Okrug | Russian | official_language | 3 | 0.703 | 0.67 |
| 5 | Frank Strazzeri | jazz | music_genre | 3 | 0.656 | 0.33 |
| 5 | Dave Darling | composer | occupation | 2 | MISSING | 0.00 |
| 5 | Novartis | Joseph Jimenez | company_ceo | 3 | MISSING | 0.00 |
| 5 | Staver | Chicago | headquarters | 3 | MISSING | 0.00 |
| 6 | Aarau | German | official_language | 6 | 0.521 | 0.33 |
| 6 | HFS Plus | Apple | manufacturer | 4 | MISSING | 0.00 |
| 6 | Mithat Bayrak | Turkish | native_language | 6 | 0.785 | 1.00 |
| 6 | Henryk Sienkiewicz | Poland | citizenship | 4 | 0.646 | 0.33 |
| 6 | Marvin Stamm | trumpet | instrument | 7 | MISSING | 0.00 |
| 7 | Nikolay Nekrasov | Russian | native_language | 9 | 0.538 | 1.00 |
| 7 | Narciso Yepes | guitar | instrument | 10 | MISSING | 0.00 |
| 7 | Jamie Cullum | jazz | music_genre | 11 | 0.531 | 0.33 |
| 7 | Lena Valaitis | Germany | citizenship | 18 | MISSING | 0.00 |
| 7 | Rosneft | Moscow | formation_location | 19 | MISSING | 0.00 |
| 8 | Saint Pierre and Miquelon | French | official_language | 51 | 0.542 | 1.00 |
| 8 | Elvis Presley | guitar | instrument | 45 | 0.708 | 0.33 |
| 8 | Thomas de Waal | journalist | occupation | 56 | MISSING | 0.00 |
| 8 | Kiribati | South Tarawa | capital | 83 | MISSING | 0.00 |
| 8 | Robert Scoble | Microsoft | employer | 26 | MISSING | 0.00 |
| 9 | Windows XP | Microsoft | manufacturer | 8838 | 0.580 | 1.00 |
| 9 | Gambro | Lund | formation_location | 575 | MISSING | 0.00 |
| 9 | LGA 775 | Intel | manufacturer | 154 | MISSING | 0.00 |
| 9 | Iceland | Reykjavík | capital | 4742 | 0.566 | 1.00 |
| 9 | Windows 8 | Microsoft | developer | 5921 | 0.521 | 0.67 |

## Run facts

- EleutherAI/pythia-1.4b: rows 3900, facts 1300, errors 0, correct@1 0.185, layers 24, depth runs S3-pythia-1.4b-b9a353d-20261108T064941Z
- EleutherAI/pythia-2.8b: rows 3900, facts 1300, errors 0, correct@1 0.206, layers 32, depth runs S3-pythia-2.8b-be99060-20261109T021915Z

## Agent notes (added after the run; no thresholds changed)

- **Scope.** This G1 was run on CPU, as approved by the human with "OK CPU G1". It covers a 1300-fact subsample: 26 relations × 50 facts, split recorded in `data/splits/g1_cpu_subsample.json`.
- **OLMo-2-1124-7B: MISSING.** It does not fit in CPU RAM on this tier. Pre-registration requires ≥ 2 PASS models, and only 2 of the 3 gate models were run, so a GO would have required both to pass. Neither did: 0/2 PASS.
- **Heavy zero mass in EXACT counts.** These numbers come from `results/S2/S2x-none-5516178-20261108T042549Z/summary.json` (run_id `S2x-none-5516178-20261108T042549Z`, N = 5200, the full fact set, not the 1300-fact subsample):

  | index (label) | zero_frac | median |
  |---|---|---|
  | piletrain (EXACT) | 0.445 | 2 |
  | olmo-mix (EXACT) | 0.356 | 11 |
  | dclm (PROXY) | 0.371 | 11 |

  In the example table above, deciles 0–4 all have cooc ≤ 2. log1p(cooc) is therefore concentrated at 0 for about half the facts, which limits the spread of the predictor.
- **Heavy censoring.** The headline measure is censored for:
  - pythia-1.4b: 3180 of 3900 rows (correct@1 = 0.185);
  - pythia-2.8b: 3096 of 3900 rows (correct@1 = 0.206).

  Depth exists only for the roughly 20% of rows where the fact resolves. Among those resolved rows, the slope CIs include 0 for both models.
- **Hazard ratio.** The survival HR per unit log1p(cooc) is above 1 with CIs excluding 1 in both models:
  - pythia-1.4b: 1.254 [1.159, 1.357];
  - pythia-2.8b: 1.273 [1.171, 1.384].

  The per-layer hazard combines "resolves at all" with "resolves earlier", so this does not show earlier resolution.
- **Negative partial R² values.** These are differences between two separate fits, with and without log cooc, and can fall below 0. Read them as about 0. The statsmodels "invalid value encountered in sqrt" warnings in `results/g1_cpu.out` indicate that some of these fits hit a boundary or near-singular random-effect covariance.
- **Missing and weak measures:**
  - tuned lens: no pretrained lens exists for these models;
  - causal_subj_onset: 0 resolved rows in both models;
  - patchscope: 25 resolved rows in pythia-1.4b (MISSING) and 39 in pythia-2.8b.

  Agreement between causal_final and logit_lens is low: Spearman 0.10 (pythia-1.4b) and 0.28 (pythia-2.8b).
- **Decision.** This is for the human. I have not started any further stage. Reply `GO G1` or `PIVOT <option>`.

## Human decision

2026-11-12: the human replied **"GO G1"**, overriding the pre-registered NO-GO outcome above. The NO-GO stands as the pre-registered result and is not changed. S4 proceeds; see `notes/s4_plan.md`.
