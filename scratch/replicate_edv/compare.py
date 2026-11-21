import json
O = "/home/user/depth-law/scratch/replicate_edv/"
c = json.load(open("/home/user/depth-law/reports/gates/G1/EXPLORATORY_post-hoc_not-preregistered__claimed_numbers.json"))
ml = json.load(open(O + "ml.json")); s1 = json.load(open(O + "stage1.json"))
rows = []; an = []
for k, v in c["B3_shares"].items():
    r = ml.get(k, {}); src = "MixedLM REML (fact+subject)"
    if "shares" not in r: r = ml[k + "|nosubject"]; src = "MixedLM REML (fact only; subject==fact)"
    a = s1["B3_anova"][k]
    assert a["n_cells"] == v["n_cells"] and a["n_facts"] == v["n_facts"], k
    for f in ("fact_plus_subject", "template_main", "residual", "relation"):
        y = r["shares"][f]; d = abs(y - v[f])
        rows.append((f"B3 {k} {f}", v[f], y, d, 0.02, "PASS" if d <= 0.02 else "FAIL", src))
        an.append((f"B3 {k} {f}", v[f], a["shares"][f], abs(a["shares"][f] - v[f])))
for k, v in c["B6_rho"].items():
    r = s1["B6"][k]; assert r["n_facts"] == v["n_facts"], k
    for f in ("rho", "rho_within_relation"):
        d = abs(r[f] - v[f])
        rows.append((f"B6 {k} {f}", v[f], r[f], d, 0.03, "PASS" if d <= 0.03 else "FAIL", "scipy spearmanr"))
print("n rows", len(rows), "FAIL", sum(x[5] == "FAIL" for x in rows), "max B3 diff", max(x[3] for x in rows if x[0].startswith("B3")),
      "max B6 diff", max(x[3] for x in rows if x[0].startswith("B6")))
print("| field | claimed | yours | abs diff | tol | result |\n|---|---|---|---|---|---|")
for x in rows: print(f"| {x[0]} | {x[1]:.4f} | {x[2]:.4f} | {x[3]:.4f} | {x[4]} | {x[5]} |")
print("\nANOVA\n| field | claimed (REML) | Henderson-III MoM | abs diff | within 0.02 |\n|---|---|---|---|---|")
for x in an: print(f"| {x[0]} | {x[1]:.4f} | {x[2]:.4f} | {x[3]:.4f} | {'yes' if x[3] <= 0.02 else 'no'} |")
print({k: v["raw_unclipped"]["relation"] for k, v in s1["B3_anova"].items() if "all3" in k})
print({k: (v["n_subjects"], v["n_facts"]) for k, v in s1["B3_anova"].items()})
