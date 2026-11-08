# G1 DRY RUN (not a gate result)

Source of every number: `results/G1/G1dry-none-f4171a0-20261108T001848Z/g1.json` (run_id `G1dry-none-f4171a0-20261108T001848Z`).
Dry run on a test model / subsample. It checks the pipeline end to end; it is NOT the G1 decision.


## Decision rule (configs/prereg.yaml g1 + amendment_1)
PASS = partial R^2 >= 0.1 with negative slope on causal_final; WEAK = >= 0.05; GO needs >= 2 PASS models.

| model | count index (label) | partial R² | outcome |
|---|---|---|---|
| EleutherAI/pythia-410m | piletrain (EXACT) | 0.040 | FAIL |

PASS models: 0 (need 2). Gate models not run: pythia-1.4b, pythia-2.8b, olmo-2-1124-7b. **Outcome: NO-GO**

## Per model × measure

| model | measure | N resolved / censored | N fit | partial R² [CI] | slope [CI] | p (Holm) | HR [CI] | best shape (AIC) |
|---|---|---|---|---|---|---|---|---|
| EleutherAI/pythia-410m | causal_final | 108 / 792 | 108 | 0.040 [-0.058, 0.096] | 0.0105 [-0.0017, 0.0198] | 0.1257 | 1.168 [1.056, 1.292] | linear |
| EleutherAI/pythia-410m | patchscope_depth | MISSING: fewer than 30 resolved rows (5) | | | | | | |
| EleutherAI/pythia-410m | tuned_lens_depth | MISSING: fewer than 30 resolved rows (0) | | | | | | |
| EleutherAI/pythia-410m | logit_lens_depth | 108 / 792 | 108 | -0.051 [-0.091, 0.025] | 0.0014 [-0.0098, 0.0153] | 0.8528 | 1.171 [1.061, 1.292] | linear |
| EleutherAI/pythia-410m | causal_subj_onset | MISSING: fewer than 30 resolved rows (0) | | | | | | |

CIs: cluster bootstrap over relations (n_boot = 50); HR = discrete-time cloglog hazard ratio per unit log1p(exact cooc), relation-clustered SEs. Holm across models × measures.

## Controls and sensitivities (headline measure)

| model | override median | Spearman(headline, override) | share equal | CNF-predictor partial R² | +override covariate partial R² | exact vs CNF Spearman (non-approx, N) |
|---|---|---|---|---|---|---|
| EleutherAI/pythia-410m | 0.750 | 0.558 | 0.481 | 0.004 | -0.021 | 0.814 (48) |

## Measure agreement (fact-level Spearman)

**EleutherAI/pythia-410m**: causal_final|logit_lens_depth 0.28

## 5 example facts per frequency decile (headline depth, template mean)

**EleutherAI/pythia-410m**

| decile | subject | object | relation | exact cooc | depth | correct |
|---|---|---|---|---|---|---|
| 0 | Ikki Kajiwara | Japan | citizenship | 0 | 0.750 | 0.33 |
| 0 | Hewlett Packard Enterprise | Antonio Neri | company_ceo | 0 | MISSING | 0.00 |
| 0 | Giuseppe Angeli | Italy | citizenship | 0 | 0.778 | 0.33 |
| 0 | Kingdom of Essex | London | capital | 0 | MISSING | 0.00 |
| 0 | Gambacorta Peak | Antarctica | continent | 0 | MISSING | 0.00 |
| 1 | Vernayaz | Switzerland | country | 0 | MISSING | 0.00 |
| 1 | Dawa River | Somalia | country | 0 | MISSING | 0.00 |
| 1 | Asian Highway Network | Turkey | country | 0 | MISSING | 0.00 |
| 1 | Bigourdan Fjord | Antarctica | continent | 0 | MISSING | 0.00 |
| 1 | Nikolaus Joseph von Jacquin | chemistry | field_of_work | 0 | MISSING | 0.00 |
| 2 | Tata Steel Europe | London | headquarters | 0 | MISSING | 0.00 |
| 2 | Mercer Ellington | trumpet | instrument | 0 | MISSING | 0.00 |
| 2 | Deacon Blue | Glasgow | formation_location | 0 | MISSING | 0.00 |
| 2 | Beshara | Birmingham | formation_location | 0 | MISSING | 0.00 |
| 2 | Kiersten Warren | actor | occupation | 0 | MISSING | 0.00 |
| 3 | Europa riconosciuta | Italian | original_language | 0 | MISSING | 0.00 |
| 3 | The Kwicky Koala Show | CBS | original_network | 0 | MISSING | 0.00 |
| 3 | La verbena de la Paloma | Spanish | original_language | 0 | MISSING | 0.00 |
| 3 | Schilder-boeck | Dutch | original_language | 0 | MISSING | 0.00 |
| 3 | Al-Ala'a Al-Hadrami | Islam | religion | 0 | MISSING | 0.00 |
| 4 | The Jean Arthur Show | CBS | original_network | 1 | MISSING | 0.00 |
| 4 | Vytautas | Christianity | religion | 0 | MISSING | 0.00 |
| 4 | Vladimir Bekhterev | Russian | native_language | 1 | 0.778 | 1.00 |
| 4 | 107 Piscium | Pisces | constellation | 1 | MISSING | 0.00 |
| 4 | Lord Henry FitzGerald | London | work_location | 0 | 0.611 | 0.67 |
| 5 | Johannes Goropius Becanus | physician | field_of_work | 3 | MISSING | 0.00 |
| 5 | Staver | Chicago | headquarters | 3 | MISSING | 0.00 |
| 5 | Kapuso Mo, Jessica Soho | Philippines | country_of_origin | 3 | MISSING | 0.00 |
| 5 | Red Hat | Matt Hicks | company_ceo | 3 | MISSING | 0.00 |
| 5 | Syed Ahmed Khan | Islam | religion | 1 | 0.639 | 0.33 |
| 6 | Ivan Sechenov | physiology | field_of_work | 7 | MISSING | 0.00 |
| 6 | Doug Raney | guitar | instrument | 6 | 0.639 | 0.33 |
| 6 | Dhwani | India | country_of_origin | 5 | MISSING | 0.00 |
| 6 | Lodhi dynasty | Delhi | capital | 8 | 0.861 | 0.33 |
| 6 | Rudolf Hess | Berlin | work_location | 6 | MISSING | 0.00 |
| 7 | Robert Dougall | BBC | employer | 8 | MISSING | 0.00 |
| 7 | OSRAM Licht AG | Munich | formation_location | 10 | MISSING | 0.00 |
| 7 | Internet Explorer Mobile | Microsoft | developer | 14 | 0.736 | 0.67 |
| 7 | John Mitchel | Ireland | citizenship | 11 | MISSING | 0.00 |
| 7 | Erich Mendelsohn | Berlin | work_location | 10 | MISSING | 0.00 |
| 8 | Georgians | Azerbaijan | country | 43 | MISSING | 0.00 |
| 8 | Xsan | Apple | developer | 41 | MISSING | 0.00 |
| 8 | Brandon University | Canada | country | 60 | 0.833 | 0.33 |
| 8 | Eric Frenzel | Germany | citizenship | 64 | MISSING | 0.00 |
| 8 | Marc Cheverie | goaltender | sport_position | 28 | MISSING | 0.00 |
| 9 | Agos | Turkey | country_of_origin | 72 | MISSING | 0.00 |
| 9 | Mario franchise | Nintendo | developer | 116 | 0.750 | 0.33 |
| 9 | Monica Niculescu | Romania | citizenship | 80 | 0.778 | 0.33 |
| 9 | Greece | Athens | capital | 55598 | 0.958 | 0.33 |
| 9 | Drew Brees | quarterback | sport_position | 6615 | 1.000 | 0.33 |

## Run facts

- EleutherAI/pythia-410m: rows 900, facts 300, errors 0, correct@1 0.120, layers 24, depth runs S3dry-pythia-410m-f4171a0-20261107T230649Z
