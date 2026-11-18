"""Summarise S7 causal-only depth evals per kept model (edited vs control facts).

Reads results/S7eval/S7eval-<model>-*/depth.parquet and data/zoo/<model>_eval.parquet;
writes <S7 run dir>/eval_summary.json and eval_summary.csv. Numbers only, no fitting.
"""
import argparse
import glob
import json
import os

import numpy as np
import pandas as pd


def summarise(mid: str) -> list[dict]:
    dirs = sorted(glob.glob(f"results/S7eval/S7eval-{mid}-*/depth.parquet"))
    if not dirs:
        return [{"model_id": mid, "missing": "no depth.parquet"}]
    d = pd.read_parquet(dirs[0])
    lab = pd.read_parquet(f"data/zoo/{mid}_eval.parquet")[["fact_id", "edited", "rtype"]]
    d = d.merge(lab, on="fact_id", how="left")
    out = []
    for edited, g in d.groupby("edited"):
        t0 = g[g.template_id == 0]
        res = g.causal_final.notna()
        out.append({
            "model_id": mid, "run_id": str(g.run_id.iloc[0]), "path": dirs[0],
            "group": "edited" if edited else "control",
            "n_facts": int(g.fact_id.nunique()), "n_rows": int(len(g)),
            "correct_at1_t0": float(t0.correct_at1.mean()), "n_t0": int(len(t0)),
            "causal_resolved_frac": float(res.mean()),
            "causal_final_median_resolved": float(g.causal_final[res].median()) if res.any() else None,
            "logit_lens_resolved_frac": float(g.logit_lens_depth.notna().mean()),
            "logit_lens_depth_median": float(g.logit_lens_depth.median()) if g.logit_lens_depth.notna().any() else None,
            "obj_first_logprob_median": float(g.obj_first_logprob.median()),
        })
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--s7-dir", default=sorted(glob.glob("results/S7/S7-pythia-1.4b-*"))[0])
    a = ap.parse_args()
    mids = sorted(os.path.basename(p)[:-len("_eval.parquet")] for p in glob.glob("data/zoo/*_eval.parquet"))
    rows = [r for m in mids for r in summarise(m)]
    json.dump(rows, open(os.path.join(a.s7_dir, "eval_summary.json"), "w"), indent=1)
    pd.DataFrame(rows).to_csv(os.path.join(a.s7_dir, "eval_summary.csv"), index=False)
    print(pd.DataFrame(rows).drop(columns=["path", "run_id"], errors="ignore").to_string())


if __name__ == "__main__":
    main()
