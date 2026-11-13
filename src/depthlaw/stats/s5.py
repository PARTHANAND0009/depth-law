"""S5 checkpoint dynamics (notes/s5_plan.md; exploratory). Writes results/S5/<run_id>/s5.json and
reports/S5.md; every number in the report is read from s5.json.

  python -m depthlaw.stats.s5 --model pythia-1.4b --final results/S3/<g1 run>/depth.parquet [--model ... --final ...]
Revision depth files are found as results/S5/S5-<model>_<rev>-*/depth.parquet.
"""
from __future__ import annotations

import argparse
import glob
import json
import re
import warnings

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy.stats import spearmanr

from depthlaw.io import ROOT, RunLog, make_run_id, provenance
from depthlaw.stats import prep
from depthlaw.stats.mixed import CONTROLS, partial_r2

Y = "causal_final"
FINAL_STEP = 143000


def load(model: str, final: str) -> tuple[pd.DataFrame, list[str]]:
    facts = set(pd.read_parquet(ROOT / "data" / "facts_s5.parquet").fact_id)
    parts, runs = [], []
    for p in sorted(glob.glob(str(ROOT / "results" / "S5" / f"S5-{model}_step*-*" / "depth.parquet"))):
        d = pd.read_parquet(p)
        d["step"] = int(re.search(r"_step(\d+)-", p).group(1))
        parts.append(d); runs.append(d.run_id.iloc[0])
    f = pd.read_parquet(final)
    f = f[f.fact_id.isin(facts)].copy()
    f["step"] = FINAL_STEP
    keep = ["fact_id", "template_id", "relation", "correct_at1", Y, "run_id", "model", "revision", "step"]
    parts = [p[[c for c in keep if c in p.columns]] for p in parts] + [f[keep]]
    runs.append(f.run_id.iloc[0])
    d = pd.concat(parts, ignore_index=True)
    d[Y] = pd.to_numeric(d[Y], errors="coerce").astype(float)  # all-censored revisions come back as object dtype
    d["correct_at1"] = d.correct_at1.astype(float)
    return d, runs


def analyse(model_short: str, final: str) -> dict:
    d, runs = load(model_short, final)
    model = f"EleutherAI/{model_short}"
    d["model"] = model
    steps = sorted(d.step.unique())
    res = {"model": model, "run_ids": runs, "steps": [int(s) for s in steps], "per_step": {}}
    b = prep.build(d.drop(columns=["step"]).assign(_step=d.step.values), model)
    b["step"] = b.pop("_step")
    res["count_index"] = f"{b.count_index.iloc[0]} ({b.count_label.iloc[0]})"
    for s in steps:
        g = b[b.step == s]
        r = {"n_rows": int(len(g)), "n_resolved": int(g[Y].notna().sum()), "share_resolved": float(g[Y].notna().mean()),
             "correct_at1": float(g.correct_at1.mean()), "median_depth": float(g[Y].median()) if g[Y].notna().any() else None}
        rr = g.dropna(subset=[Y, "log_cooc"] + CONTROLS)
        if len(rr) >= 30 and rr.relation.nunique() > 2:
            try:
                pr = partial_r2(rr, Y)
                r.update({"slope": pr["slope"], "slope_se": pr["slope_se"], "slope_p": pr["slope_p"], "partial_r2": pr["partial_r2"]})
            except Exception as e:  # noqa: BLE001
                r["fit_error"] = repr(e)[:200]
        else:
            r["fit"] = f"MISSING: fewer than 30 resolved rows ({len(rr)})"
        res["per_step"][int(s)] = r
    # fact x step: resolved by template majority (>= 2 of 3)
    fs = b.groupby(["fact_id", "step"]).agg(n_res=(Y, lambda x: int(x.notna().sum())), depth=(Y, "mean"),
                                            cooc=("exact_cooc", "first")).reset_index()
    fs["res"] = fs.n_res >= 2
    piv = fs.pivot(index="fact_id", columns="step", values="res").reindex(columns=steps).fillna(False)
    acq = {}
    for fid, row in piv.iterrows():
        v = row.to_numpy()
        if not v[-1]:
            continue
        k = len(v) - 1
        while k > 0 and v[k - 1]:
            k -= 1
        acq[fid] = steps[k]
    cooc = fs.drop_duplicates("fact_id").set_index("fact_id").cooc
    a = pd.DataFrame({"acq_step": pd.Series(acq)}).join(cooc)
    res["acquisition"] = {"n_facts_resolved_at_final": int(len(a)), "n_facts": int(len(piv)),
                          "spearman_cooc_vs_acq_step": float(spearmanr(a.cooc, a.acq_step).statistic) if len(a) > 10 and a.acq_step.nunique() > 1 else None,
                          "n_per_acq_step": {int(k): int(v) for k, v in a.acq_step.value_counts().sort_index().items()}}
    # discrete-time hazard of first stable resolution over checkpoints (facts resolved at final)
    pp = []
    for fid, s0 in acq.items():
        for i, s in enumerate(steps):
            pp.append({"fact_id": fid, "k": i, "event": int(s == s0), "log_cooc": float(np.log1p(cooc[fid]))})
            if s == s0:
                break
    pp = pd.DataFrame(pp)
    if len(pp) and pp.event.sum() > 10 and pp.loc[pp.event == 1, "k"].nunique() >= 2:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            m = smf.glm("event ~ C(k) + log_cooc", pp, family=sm.families.Binomial(link=sm.families.links.CLogLog())).fit(
                cov_type="cluster", cov_kwds={"groups": pd.factorize(pp.fact_id)[0]})
        b1, se = float(m.params["log_cooc"]), float(m.bse["log_cooc"])
        res["acquisition"]["hazard_ratio_per_log1p_cooc"] = {"hr": float(np.exp(b1)), "ci": [float(np.exp(b1 - 1.96 * se)), float(np.exp(b1 + 1.96 * se))],
                                                            "p": float(m.pvalues["log_cooc"]), "n_person_periods": int(len(pp))}
    else:
        res["acquisition"]["hazard_ratio_per_log1p_cooc"] = {"missing": "MISSING: events at fewer than 2 checkpoints or <= 10 events"}
    # depth drift relative to the final checkpoint (facts resolved by majority at both)
    fin = fs[(fs.step == FINAL_STEP) & fs.res].set_index("fact_id").depth
    drift = {}
    for s in steps[:-1]:
        g = fs[(fs.step == s) & fs.res].set_index("fact_id").depth
        j = g.index.intersection(fin.index)
        if len(j):
            diff = g.loc[j] - fin.loc[j]
            drift[int(s)] = {"n": int(len(j)), "mean_diff": float(diff.mean()), "median_diff": float(diff.median())}
    res["depth_drift_vs_final"] = drift
    return res


def fmt(x, nd=3):
    if x is None or (isinstance(x, float) and not np.isfinite(x)):
        return "MISSING"
    return f"{x:.{nd}f}" if isinstance(x, float) else str(x)


def report(out: dict) -> None:
    L = ["# S5: checkpoint dynamics (CPU, exploratory)\n",
         f"Source of every number: `{out['json']}` (run_id `{out['run_id']}`). Plan: `notes/s5_plan.md`. "
         "Facts: 508 facts resolved at the final checkpoint of either Pythia model (data/splits/s5_facts.json); "
         "measure causal_final; counts exact Pile phrase co-occurrence (EXACT). OLMo-2-1124-7B: MISSING (does not fit in 15 GB RAM).\n"]
    for m in out["models"]:
        L.append(f"## {m['model']} ({m['count_index']})\n")
        L.append("| step | N rows | resolved | share resolved | correct@1 | median depth | slope (p) | partial R² |")
        L.append("|---|---|---|---|---|---|---|---|")
        for s, r in m["per_step"].items():
            sl = f"{fmt(r.get('slope'), 4)} ({fmt(r.get('slope_p'), 3)})" if "slope" in r else r.get("fit", r.get("fit_error", "MISSING"))
            L.append(f"| {s} | {r['n_rows']} | {r['n_resolved']} | {fmt(r['share_resolved'])} | {fmt(r['correct_at1'])} | "
                     f"{fmt(r['median_depth'])} | {sl} | {fmt(r.get('partial_r2'), 4)} |")
        a = m["acquisition"]
        h = a.get("hazard_ratio_per_log1p_cooc", {})
        L.append(f"\nAcquisition (first checkpoint from which the fact stays resolved on >= 2 of 3 templates): "
                 f"{a['n_facts_resolved_at_final']} of {a['n_facts']} facts resolved at the final checkpoint; "
                 f"Spearman(cooc, acquisition step) {fmt(a['spearman_cooc_vs_acq_step'])}; "
                 f"hazard ratio per log1p(cooc) {fmt(h.get('hr'))} [{fmt((h.get('ci') or [None])[0])}, {fmt((h.get('ci') or [None, None])[1])}] "
                 f"(p {fmt(h.get('p'), 4)}, {h.get('n_person_periods', 'MISSING')} person-periods). Facts per acquisition step: "
                 + ", ".join(f"{k}: {v}" for k, v in a["n_per_acq_step"].items()) + ".\n")
        L.append("| step | N facts resolved here and at final | mean depth minus final depth | median |\n|---|---|---|---|")
        for s, r in m["depth_drift_vs_final"].items():
            L.append(f"| {s} | {r['n']} | {fmt(r['mean_diff'], 4)} | {fmt(r['median_diff'], 4)} |")
        L.append(f"\nRuns: {', '.join(m['run_ids'])}.\n")
    (ROOT / "reports" / "S5.md").write_text("\n".join(L) + "\n")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", action="append", required=True)
    ap.add_argument("--final", action="append", required=True)
    a = ap.parse_args(argv)
    run_id = make_run_id("S5stats")
    log = RunLog("S5", run_id)
    out = {"run_id": run_id, "models": [analyse(m, f) for m, f in zip(a.model, a.final)]}
    jp = log.dir / "s5.json"
    out["json"] = str(jp.relative_to(ROOT))
    jp.write_text(json.dumps(out, indent=2, default=lambda o: o.item() if hasattr(o, "item") else str(o)))
    (log.dir / "meta.json").write_text(json.dumps(provenance(run_id, vars(a)), indent=2))
    report(out)
    log.log(event="done")
    print(jp)


if __name__ == "__main__":
    main()
