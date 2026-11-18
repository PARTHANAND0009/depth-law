"""S9 summary: where the adaptive attacks put the edited facts, versus their non-adaptive twins.

Reads results/S9score/<run>/fact_scores.parquet (edited facts, label 1) and
results/S9/<run>/predicted.json; writes results/S9/<run>/attack_summary.json and .csv.
Numbers only: medians and fractions per model, no fitting.
"""
import argparse
import glob
import json
import os

import numpy as np
import pandas as pd

MODELS = ["rome_single", "a1_layer_match", "a2_depth_reg", "synthdoc50", "a3_freq_spoof"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--score-dir", default=sorted(glob.glob("results/S9score/S9score-pythia-1.4b-*"))[-1])
    ap.add_argument("--s9-dir", default=sorted(glob.glob("results/S9/S9-pythia-1.4b-*"))[-1])
    a = ap.parse_args()
    f = pd.read_parquet(os.path.join(a.score_dir, "fact_scores.parquet"))
    pred = json.load(open(os.path.join(a.s9_dir, "predicted.json")))["pred"]
    rows = []
    for mid in MODELS:
        for pop in ["primary", "all"]:
            g = f[(f.model_id == mid) & (f.label == 1)]
            if pop == "primary":
                g = g[g.primary]
            lh = np.array([pred[e]["l_hat"] for e in g.edit_fact_id if e in pred], dtype=float)
            rows.append({
                "model_id": mid, "population": pop, "n_pos": int(len(g)),
                "causal_final_f_median": float(g.causal_final_f.median()),
                "ll_depth_f_median": float(g.ll_depth_f.median()),
                "r_causal_median": float(g.r_causal.median()),
                "r_causal_neg_frac": float((g.r_causal < 0).mean()),
                "r_ll_median": float(g.r_ll.median()),
                "r_conf_median": float(g.r_conf.median()),
                "s_maha_median": float(g.s_maha.median()),
                "n_with_l_hat": int(len(lh)),
                "l_hat_le6_frac": float((lh <= 6).mean()) if len(lh) else None,
                "l_hat_median": float(np.median(lh)) if len(lh) else None,
                "score_run_id": str(g.run_id.iloc[0]) if len(g) else None,
            })
    out = os.path.join(a.s9_dir, "attack_summary")
    json.dump({"score_dir": a.score_dir, "s9_dir": a.s9_dir, "rows": rows}, open(out + ".json", "w"), indent=1)
    pd.DataFrame(rows).to_csv(out + ".csv", index=False)
    print(pd.DataFrame(rows).drop(columns=["score_run_id"]).to_string())


if __name__ == "__main__":
    main()
