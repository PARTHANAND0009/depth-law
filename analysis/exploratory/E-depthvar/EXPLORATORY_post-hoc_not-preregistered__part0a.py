"""EXPLORATORY (post hoc, not preregistered) — Part 0a: jackknife summary + company_ceo diagnostics.

python <this> <run_dir> <out_dir>
Runs the leave-one-relation-out R script, summarizes min/max/median and the most influential relations,
applies the pre-logged stop criterion (OLMo D1 diff <= 0 in > 13 of 26 fits), and writes company_ceo
diagnostics per model x template, including a self-readout depth: the half-probability rule applied to the
stored logit-lens probability of the object first token at the fact prompt's own final position (no carrier).
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P = "EXPLORATORY_post-hoc_not-preregistered__"
LAB = "EXPLORATORY (post hoc, not preregistered)"
MODELS = ["pythia-1.4b", "pythia-2.8b", "OLMo-2-1124-7B"]
S3B = {"pythia-1.4b": "results/S3b/S3b-pythia-1.4b-a7dfeb5-20261121T063528Z/depth.parquet",
       "pythia-2.8b": "results/S3b/S3b-pythia-2.8b-a7dfeb5-20261121T064110Z/depth.parquet",
       "OLMo-2-1124-7B": "results/S3b/S3b-OLMo-2-1124-7B-923945f-20261121T061237Z/depth.parquet"}


def half_prob(p):
    p = np.asarray(p, float)
    ok = p >= 0.5 * p[-1]
    l = len(p) - 1
    while l > 0 and ok[l - 1]:
        l -= 1
    return (l + 1) / len(p)


def main(run, out):
    run, out = Path(run), Path(out); out.mkdir(parents=True, exist_ok=True)
    jj = out / f"{P}jackknife.json"
    p = subprocess.run(["Rscript", str(HERE / f"{P}jackknife.R"), str(run / "tables"), str(jj)], capture_output=True, text=True)
    if p.returncode:
        raise SystemExit(p.stderr[-2000:])
    jk = json.loads(jj.read_text())
    summ = {}
    for k, v in jk.items():
        loo = v["loo"]
        s = {"full": {x: v["full"][x] for x in ("diff", "icc1", "share_fact_subject", "share_template_main", "share_residual", "share_relation", "singular")},
             "n_loo": len(loo), "n_singular_loo": int(sum(r["singular"] for r in loo)),
             "n_with_warnings": int(sum(bool(r["warnings"]) for r in loo))}
        for stat in ("diff", "icc1"):
            vals = np.array([r[stat] for r in loo])
            ch = vals - v["full"][stat]
            order = np.argsort(-np.abs(ch))
            s[stat] = {"min": float(vals.min()), "max": float(vals.max()), "median": float(np.median(vals)),
                       "most_influential": [{"dropped": loo[i]["dropped"], "value": float(vals[i]), "change": float(ch[i])} for i in order[:3]]}
        s["n_diff_le_0"] = int(sum(r["diff"] <= 0 for r in loo))
        s["influence_by_relation"] = {r["dropped"]: float(r["diff"] - v["full"]["diff"]) for r in loo}
        summ[k] = s
    olmo = summ["OLMo-2-1124-7B|D1"]
    stop = olmo["n_diff_le_0"] > olmo["n_loo"] / 2
    # company_ceo diagnostics + self-readout depth
    diag = {}
    for m in MODELS:
        cells = pd.read_csv(run / "tables" / f"{P}cells_{m}.csv")
        s3 = pd.read_parquet(ROOT / S3B[m], columns=["fact_id", "template_id", "relation", "logit_lens_prob", "logit_lens_depth"])
        c = cells[cells.relation == "company_ceo"].merge(s3, on=["fact_id", "template_id", "relation"])
        c["self_readout_halfprob"] = [half_prob(x) for x in c.logit_lens_prob]
        rows = []
        for t, g in c.groupby("template_id"):
            gc = g[g.correct == 1]
            rows.append({"template_id": int(t), "n_cells": int(len(g)), "n_correct": int(len(gc)),
                         "mean_D1_correct": float(gc.D1.mean()) if len(gc) else None,
                         "mean_D4_correct": float(gc.D4.mean()) if len(gc) else None,
                         "mean_D1_carrier": [float(gc[f"D1_c{i}"].mean()) if len(gc) else None for i in range(3)],
                         "share_D1_ge_0.95_correct": float((gc.D1 >= 0.95).mean()) if len(gc) else None,
                         "mean_self_readout_halfprob_correct": float(gc.self_readout_halfprob.mean()) if len(gc) else None,
                         "mean_logit_lens_depth_correct": float(gc.logit_lens_depth.mean()) if len(gc) else None,
                         "mean_D1_all": float(g.D1.mean()), "mean_self_readout_halfprob_all": float(g.self_readout_halfprob.mean())})
        allc = cells[cells.correct == 1]
        diag[m] = {"templates": rows,
                   "model_correct_cells_with_D1_ge_0.95": int((allc.D1 >= 0.95).sum()),
                   "of_which_company_ceo": int(((allc.D1 >= 0.95) & (allc.relation == "company_ceo")).sum())}
    texts = pd.read_parquet(ROOT / "data/facts_g1cpu.parquet")
    tt = texts[texts.relation == "company_ceo"].iloc[0].templates
    res = {"label": LAB, "criterion": "OLMo D1 diff <= 0 in > 13 of 26 leave-one-relation-out fits -> STOP",
           "stop": bool(stop), "summary": summ, "company_ceo": diag, "company_ceo_templates": list(tt)[:3]}
    (out / f"{P}part0a.json").write_text(json.dumps(res, indent=1))
    print(json.dumps({"stop": stop, **{k: {"diff": v["diff"], "icc1": v["icc1"], "n_diff_le_0": v["n_diff_le_0"],
                                            "n_singular_loo": v["n_singular_loo"]} for k, v in summ.items()},
                      "company_ceo": diag, "templates": list(tt)[:3]}, indent=1, default=str))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
