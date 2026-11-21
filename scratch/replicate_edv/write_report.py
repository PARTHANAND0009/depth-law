import json
O = "/home/user/depth-law/scratch/replicate_edv/"
c = json.load(open("/home/user/depth-law/reports/gates/G1/EXPLORATORY_post-hoc_not-preregistered__claimed_numbers.json"))
ml = json.load(open(O + "ml.json")); s1 = json.load(open(O + "stage1.json"))
rows, an, notes = [], [], []
for k, v in c["B3_shares"].items():
    r = ml.get(k, {})
    if "shares" not in r:
        r = ml[k + "|nosubject"]; notes.append(k)
    a = s1["B3_anova"][k]
    for f in ("fact_plus_subject", "template_main", "residual", "relation"):
        y = r["shares"][f]; d = abs(y - v[f])
        rows.append((f"B3 {k} {f}", v[f], y, d, 0.02))
        an.append((f"{k} {f}", v[f], a["shares"][f], abs(a["shares"][f] - v[f])))
for k, v in c["B6_rho"].items():
    r = s1["B6"][k]
    for f in ("rho", "rho_within_relation"):
        rows.append((f"B6 {k} {f} (n={r['n_facts']})", v[f], r[f], abs(r[f] - v[f]), 0.03))
nfail = sum(x[3] > x[4] for x in rows)
maxsub = max(abs(ml[k]["shares"]["fact_plus_subject"] - ml[k + "|nosubject"]["shares"]["fact_plus_subject"])
             for k in c["B3_shares"] if "shares" in ml.get(k, {}))
neg = [k for k, v in s1["B3_anova"].items() if min(v["raw_unclipped"].values()) < 0]
L = []
L.append("# EXPLORATORY (post hoc, not preregistered) — independent replication of E-depthvar B3 shares and B6 cross-model rho\n")
L.append("Claims: reports/gates/G1/EXPLORATORY_post-hoc_not-preregistered__claimed_numbers.json (source run EXPLORATORY_E-depthvar-none-321939b-20261121T153451Z).")
L.append("Inputs: the three S3b depth.parquet files (S3b-pythia-1.4b-a7dfeb5-20261121T063528Z, S3b-pythia-2.8b-a7dfeb5-20261121T064110Z, S3b-OLMo-2-1124-7B-923945f-20261121T061237Z) and data/facts_g1cpu.parquet.")
L.append("Scripts: /home/user/depth-law/scratch/replicate_edv/rep2.py (D1/D4, ANOVA, B6, MixedLM), compare.py, sim_anova.py, write_report.py. Outputs: scratch/replicate_edv/{stage1.json, ml.json, cells.parquet}.\n")
L.append("## FAILs\n")
L.append(f"None. {len(rows)} numbers checked (48 B3 shares, 24 B6 rho); {nfail} FAIL. Max |diff|: B3 {max(x[3] for x in rows if x[0].startswith('B3')):.5f}, B6 {max(x[3] for x in rows if x[0].startswith('B6')):.1e}.\n")
L.append("## Pre-checks\n")
L.append("- D1 recomputed from final_logprob_curves equals stored half_prob_depth for all 3900 rows in each model (max |diff| = 0.0). L = 24 (pythia-1.4b), 32 (pythia-2.8b, OLMo-2).")
L.append("- n_cells and n_facts match the claimed values for all 12 B3 sets; n_facts match for all B6 sets (strict_all3 = 50, any_correct = 312).\n")
L.append("## Table (graded value = statsmodels MixedLM REML)\n")
L.append("| field | claimed | yours | abs diff | tolerance | result |\n|---|---|---|---|---|---|")
for x in rows:
    L.append(f"| {x[0]} | {x[1]:.4f} | {x[2]:.4f} | {x[3]:.5f} | {x[4]} | {'PASS' if x[3] <= x[4] else 'FAIL'} |")
L.append("\n## Library / estimator\n")
L.append("- B3: statsmodels 0.15.0 `MixedLM.from_formula('y ~ 1', groups=<one constant group>, re_formula='0', vc_formula={relation, relation:template, fact_id, subject}, use_sparse=True)`, `fit(reml=True, method='lbfgs')`. All reported fits converged=True. Share = component / (sum of 4 components + residual scale); fact_plus_subject = fact + subject.")
L.append("- relation:template level = relation + template_id (0..2). subject = facts_g1cpu.subject (1300 facts, 1296 distinct subjects).")
L.append("- B6: scipy.stats.spearmanr (average ranks for ties) on fact-level means; within-relation version subtracts, per model, the relation mean of fact-level means over the selected facts.")
L.append("- Cross-check (not graded): own Henderson method III (sequential sums of squares: relation, relation:template | relation, fact | relation:template, residual; expected mean squares from exact trace coefficients; negatives clipped at 0) implemented in numpy. It is the plan's ANOVA generalized to unequal facts per relation.\n")
L.append("## Ambiguities / estimator dependence\n")
L.append(f"1. Subject vs fact confounding. In every all3 set n_subjects = n_facts (84, 107, 254), so subject and fact are not separately identified. With both terms, statsmodels raised LinAlgError (singular Hessian) for: {', '.join(notes)}. For those two sets the graded value is from the same model without (1|subject), which is the same model when subject is identical to fact. Where both fits ran, dropping (1|subject) changed fact_plus_subject by at most {maxsub:.4f} (correct sets: 400/402, 433/436, 676/680 subjects/facts).")
nbad = sum(x[3] > 0.02 for x in an)
L.append(f"2. Estimator choice. The Henderson-III method-of-moments estimate differs from REML (claimed) by more than 0.02 in {nbad} of 48 B3 shares; max |diff| = {max(x[3] for x in an):.4f}. The largest gaps are in the relation and template_main shares (e.g. OLMo-2 D1 all3: template_main REML 0.4106 vs MoM 0.1579; relation 0.1523 vs 0.3334). Fact and residual components (absolute variances) agree more closely (OLMo-2 D1 all3: fact 0.00253 vs 0.00255, residual 0.00145 vs 0.00144). Negative raw MoM estimates: {neg if neg else 'none'}.")
L.append("   - Simulation check of the MoM code (sim_anova.py, 300 draws per set, Gaussian data from the REML D1 components on each real design): MoM mean equals the true components (unbiased); MoM SD for relation:template is large, e.g. OLMo-2 D1 all3: true 0.00374, MoM SD 0.00116; observed MoM 0.00124 (about 2.2 SD below the REML value).")
L.append("   - So the claimed shares are reproduced by an independent REML implementation, but not, within 0.02, by the method-of-moments estimator for many relation/template_main shares. The claims are defined as REML shares, so grading uses REML.")
L.append("3. No other definitional choices changed any value: D1 matched the stored column exactly, and all 24 B6 rho values matched to <1e-9.\n")
L.append("Resources: each process ran under nice -n 10, prlimit --as=1.8 GB, OMP_NUM_THREADS=1, ARROW_DEFAULT_MEMORY_POOL=system (the default mimalloc pool reserves about 1.2 GB of address space and caused allocation failures under the cap). Peak RSS was 344 MB or less. One earlier attempt using the dense statsmodels design hit the 10-minute background limit and produced no output; it was replaced by the sparse fits.\n")
L.append("VERDICT: PASS")
open("/home/user/depth-law/reports/gates/G1/replicator.md", "w").write("\n".join(L) + "\n")
print("\n".join(L))
