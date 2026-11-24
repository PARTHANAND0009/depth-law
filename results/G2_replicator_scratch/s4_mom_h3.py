# MoM (own residualisation + own cell means; henderson3 from analysis/p2/p2_mom.py) and H3.
import json, os, sys
import numpy as np, pandas as pd
from scipy.stats import spearmanr
sys.path.insert(0, "/home/user/depth-law/analysis/p2")
from p2_mom import henderson3
S = os.path.dirname(os.path.abspath(__file__)); cov = ["n_answer_tokens", "n_subject_tokens", "log_cooc_proxy", "answer_prior"]
reml = json.load(open(f"{S}/s3_reml.json")); out = {}
tabs = {k: pd.read_csv(f"{S}/tab_{k}.csv") for k in ["llama", "olmo"]}
for k, d in tabs.items():
    for y in ["D1", "D4"]:
        X = np.column_stack([np.ones(len(d))] + [d[c].to_numpy(float) for c in cov] + [(d.carrier == j).to_numpy(float) for j in (1, 2)])
        beta, *_ = np.linalg.lstsq(X, d[y].to_numpy(float), rcond=None)
        r = d[y].to_numpy(float) - X @ beta
        cm = d.assign(y=r).groupby(["fact_id", "template_id"]).agg(y=("y", "mean"), relation=("relation", "first"), n=("y", "size")).reset_index()
        assert (cm.n == 3).all()
        cm = cm.rename(columns={"fact_id": "fact", "template_id": "frame"})
        m = henderson3(cm[["relation", "frame", "fact", "y"]])
        out[f"{k}_{y}"] = {"diff": m.get("diff"), "icc1": m["icc1"], "n_cells": m["n_cells"], "raw": m["raw"]}
        print(k, y, "MoM diff", m.get("diff"), "icc1", m["icc1"], "cells", m["n_cells"])
# H3
fm = {k: d.groupby("fact_id").D1.mean() for k, d in tabs.items()}
kbar = {k: d.groupby("fact_id").template_id.nunique().mean() for k, d in tabs.items()}
common = fm["llama"].index.intersection(fm["olmo"].index)
rho = spearmanr(fm["llama"][common], fm["olmo"][common]).statistic
def G(v, k, nc=3): return v["fact"] / (v["fact"] + v["ft"] / k + v["fc"] / nc + v["Residual"] / (k * nc))
g = {k: G(reml[f"{k}_D1"]["vc"], kbar[k]) for k in tabs}
out["H3"] = {"n_common": len(common), "rho": rho, "kbar": kbar, "G": g, "disatt": rho / np.sqrt(g["llama"] * g["olmo"])}
# variant: fact mean of cell means (identical when all cells have 3 carriers) and facts with >=2 correct only
f2 = {k: d.groupby("fact_id").filter(lambda x: x.template_id.nunique() >= 2).groupby("fact_id").D1.mean() for k, d in tabs.items()}
c2 = f2["llama"].index.intersection(f2["olmo"].index)
out["H3_variant_2plus"] = {"n_common": len(c2), "rho": spearmanr(f2["llama"][c2], f2["olmo"][c2]).statistic}
print(out["H3"], out["H3_variant_2plus"])
json.dump(out, open(f"{S}/s4_mom_h3.json", "w"), indent=1, default=float)
