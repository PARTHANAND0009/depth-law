"""G2 analysis (notes/s6_plan.md, fixed before training): Spearman(freq, causal depth) over S6
fictional facts learned in all seeds. Writes results/G2/<run_id>/g2.json and reports/GATE_G2.md.

  python -m depthlaw.stats.g2 --eval results/S6eval_seed1/<run>/depth.parquet [...] --train results/S6/<run> [...]
"""
from __future__ import annotations

import argparse
import json

import numpy as np
import pandas as pd
import yaml
from scipy.stats import spearmanr

from depthlaw.io import ROOT, RunLog, make_run_id, provenance

Y = "causal_final"


def per_seed(dep: pd.DataFrame) -> pd.DataFrame:
    g = dep.groupby("fact_id")
    return pd.DataFrame({"n_correct": g.correct_at1.sum(), "n_templates": g.size(),
                         "depth": g[Y].mean(), "n_resolved": g[Y].apply(lambda x: int(x.notna().sum()))})


def fmt(x, nd=3):
    if x is None or (isinstance(x, float) and not np.isfinite(x)):
        return "MISSING"
    return f"{x:.{nd}f}" if isinstance(x, float) else str(x)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--eval", nargs="+", required=True)
    ap.add_argument("--train", nargs="+", required=True)
    a = ap.parse_args(argv)
    prereg = yaml.safe_load(open(ROOT / "configs" / "prereg.yaml"))
    thr = float(prereg["g2"]["spearman_max"])
    run_id = make_run_id("G2")
    log = RunLog("G2", run_id)
    facts = pd.read_parquet(ROOT / "data" / "s6" / "facts.parquet").set_index("fact_id")
    seeds, eval_ids, train_info = [], [], []
    for p in a.eval:
        dep = pd.read_parquet(p)
        eval_ids.append(sorted(dep.run_id.unique().tolist()))
        s = per_seed(dep)
        s["learned"] = s.n_correct >= 2
        seeds.append(s)
    for t in a.train:
        rows = [json.loads(l) for l in open(ROOT / t / "log.jsonl")]
        steps = [r for r in rows if r.get("event") == "step"]
        train_info.append({"run": str(t), "final_step": steps[-1]["step"] if steps else None,
                           "final_loss": steps[-1]["loss"] if steps else None,
                           "mean_loss_last_10_logs": float(np.mean([r["loss"] for r in steps[-10:]])) if steps else None})
    out = {"run_id": run_id, "threshold_spearman_max": thr, "eval_run_ids": eval_ids, "train": train_info,
           "n_seeds": len(seeds), "per_seed": [], "per_bin": {}}
    freq = facts.freq
    for i, s in enumerate(seeds):
        s = s.join(freq)
        r = s[s.learned & s.depth.notna()]
        out["per_seed"].append({
            "seed_index": i, "n_facts": int(len(s)), "n_learned": int(s.learned.sum()),
            "learned_share_per_freq": {int(k): float(v) for k, v in s.groupby("freq").learned.mean().items()},
            "spearman_freq_depth_learned": float(spearmanr(r.freq, r.depth).statistic) if len(r) > 10 else None,
            "n_learned_with_depth": int(len(r))})
    learned_all = np.logical_and.reduce([s.learned & s.depth.notna() for s in seeds])
    ids = seeds[0].index[learned_all]
    dep_mean = pd.concat([s.loc[ids, "depth"] for s in seeds], axis=1).mean(axis=1)
    d = pd.DataFrame({"depth": dep_mean}).join(freq)
    out["n_learned_all_seeds"] = int(len(d))
    if len(d) > 10 and d.freq.nunique() > 1:
        rho = spearmanr(d.freq, d.depth)
        out["spearman"] = float(rho.statistic)
        out["spearman_p"] = float(rho.pvalue)
        out["outcome"] = "PASS" if rho.statistic < thr else "FAIL"
    else:
        out["spearman"] = None
        out["outcome"] = f"MISSING: {len(d)} facts learned in all seeds, {d.freq.nunique()} frequency bins"
    for f, g in d.groupby("freq"):
        out["per_bin"][int(f)] = {"n": int(len(g)), "median_depth": float(g.depth.median()),
                                  "q25": float(g.depth.quantile(0.25)), "q75": float(g.depth.quantile(0.75))}
    jp = log.dir / "g2.json"
    out["json"] = str(jp.relative_to(ROOT))
    jp.write_text(json.dumps(out, indent=2))
    (log.dir / "meta.json").write_text(json.dumps(provenance(run_id, vars(a)), indent=2))
    L = ["# GATE G2\n", f"Source of every number: `{out['json']}` (run_id `{run_id}`). Plan: `notes/s6_plan.md` "
         "(CPU-scaled S6; deviations from the CLAUDE.md spec are listed there).\n",
         f"## Decision rule (configs/prereg.yaml g2)\nPASS = Spearman(frequency, causal depth) < {thr} on facts learned in all seeds.\n",
         f"| N facts learned in all {len(seeds)} seeds | Spearman | p | outcome |\n|---|---|---|---|",
         f"| {out['n_learned_all_seeds']} | {fmt(out.get('spearman'))} | {fmt(out.get('spearman_p'), 4)} | **{out['outcome']}** |\n",
         "## Depth per frequency bin (facts learned in all seeds; depth = mean over seeds of the template-mean causal_final, (l+1)/8)\n",
         "| freq | N | median | IQR |\n|---|---|---|---|"]
    for f, b in sorted(out["per_bin"].items()):
        L.append(f"| {f} | {b['n']} | {fmt(b['median_depth'])} | [{fmt(b['q25'])}, {fmt(b['q75'])}] |")
    L.append("\n## Per seed\n\n| seed | eval run | learned (of 2000) | learned share by freq (1/4/16/64/256) | Spearman on learned | N | final train loss |")
    L.append("|---|---|---|---|---|---|---|")
    for i, s in enumerate(out["per_seed"]):
        sh = "/".join(fmt(s["learned_share_per_freq"].get(f), 2) for f in (1, 4, 16, 64, 256))
        L.append(f"| {i + 1} | {', '.join(eval_ids[i])} | {s['n_learned']} | {sh} | {fmt(s['spearman_freq_depth_learned'])} | "
                 f"{s['n_learned_with_depth']} | {fmt(train_info[i]['final_loss']) if i < len(train_info) else 'MISSING'} |")
    L.append("\nTraining runs: " + ", ".join(t["run"] for t in train_info) + ".")
    (ROOT / "reports" / "GATE_G2.md").write_text("\n".join(L) + "\n")
    log.log(event="done")
    print(ROOT / "reports" / "GATE_G2.md")


if __name__ == "__main__":
    main()
