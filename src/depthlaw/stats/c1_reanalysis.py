"""Claim 1 re-analysis on existing S3 data (EXPLORATORY; not in configs/prereg.yaml).

Requested by the human 2026-11-20. No new model runs. Per model (pythia-1.4b, pythia-2.8b):
  1. raw Spearman(depth, log1p EXACT cooc) on resolved rows (row level, fact level, within relation)
  2. OLS slope of depth on log cooc alone, then + each prereg control one at a time, then cumulative;
     relation-cluster bootstrap CI (n_boot) for the slope; which control (if any) removes the effect
  3. discrete-time survival (cloglog) on ALL rows, unresolved rows censored; with and without controls
  4. logistic regression of correct@1 on log cooc (sanity check that counts behave)
  5. 1-4 repeated for tuned-lens depth (MISSING if no rows) and, as the available lens, logit-lens depth
Counts: EXACT (v4_piletrain_llama) for Pythia; label carried in `count_label`.
"""
from __future__ import annotations

import argparse
import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy.stats import spearmanr

from depthlaw.io import ROOT, RunLog, make_run_id, provenance
from depthlaw.stats import prep
from depthlaw.stats.mixed import CONTROLS
from depthlaw.stats.survival import person_period

S3_RUNS = {"EleutherAI/pythia-1.4b": "S3-pythia-1.4b-b9a353d-20261108T064941Z",
           "EleutherAI/pythia-2.8b": "S3-pythia-2.8b-be99060-20261109T021915Z"}
MEASURES = ["causal_final", "tuned_lens_depth", "logit_lens_depth"]


def _ols(d: pd.DataFrame, y: str, xs: list[str], fe: bool):
    f = f"{y} ~ " + " + ".join(xs + (["C(relation)"] if fe else []))
    return smf.ols(f, d).fit()


def ols_slope(d, y, xs, fe, n_boot, rng):
    r = _ols(d, y, ["log_cooc"] + xs, fe)
    r0 = _ols(d, y, xs, fe) if (xs or fe) else None
    pr2 = r.rsquared - (r0.rsquared if r0 is not None else 0.0)
    rels = d.relation.unique()
    groups = {k: g for k, g in d.groupby("relation")}
    bs = []
    for _ in range(n_boot):
        pick = rng.choice(rels, len(rels), replace=True)
        bd = pd.concat([groups[k].assign(relation=f"{k}#{i}") for i, k in enumerate(pick)], ignore_index=True)
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                bs.append(float(_ols(bd, y, ["log_cooc"] + xs, fe).params["log_cooc"]))
        except Exception:  # noqa: BLE001
            continue
    ci = [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))] if len(bs) > 50 else None
    return {"slope": float(r.params["log_cooc"]), "slope_se_ols": float(r.bse["log_cooc"]),
            "p_ols": float(r.pvalues["log_cooc"]), "ci95_cluster_boot": ci, "n_boot_ok": len(bs),
            "partial_r2_ols": float(pr2), "n": int(r.nobs)}


def survival(d: pd.DataFrame, y: str, L: int, controls: list[str]) -> dict:
    pp = person_period(d, y, L)
    pp["layer_bin"] = pd.cut(pp.layer, bins=min(12, L), labels=False)
    cols = [c for c in controls if pp[c].nunique() > 1]
    f = "event ~ log_cooc" + "".join(f" + {c}" for c in cols) + " + C(layer_bin)"
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        r = smf.glm(f, pp, family=sm.families.Binomial(link=sm.families.links.CLogLog())).fit(
            cov_type="cluster", cov_kwds={"groups": pd.factorize(pp.relation)[0]})
    b, se = float(r.params["log_cooc"]), float(r.bse["log_cooc"])
    return {"hr": float(np.exp(b)), "hr_ci": [float(np.exp(b - 1.96 * se)), float(np.exp(b + 1.96 * se))],
            "p": float(r.pvalues["log_cooc"]), "n_rows": int(len(d)), "n_events": int(pp.event.sum()),
            "n_person_periods": int(len(pp))}


def survival_among_resolved(d: pd.DataFrame, y: str, L: int, controls: list[str]) -> dict:
    """Same hazard model restricted to rows that resolve (no censoring): isolates 'earlier'
    from 'resolves at all' (exploratory addition, not requested)."""
    return survival(d[d[y].notna()], y, L, controls)


def logistic_correct(d: pd.DataFrame, controls: list[str]) -> dict:
    out = {}
    for name, xs, fe in [("log_cooc only", [], False), ("+ relation FE", [], True),
                         ("+ prereg controls + relation FE", controls, True)]:
        f = "correct ~ log_cooc" + "".join(f" + {c}" for c in xs) + (" + C(relation)" if fe else "")
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            r = smf.glm(f, d.assign(correct=d.correct_at1.astype(int)), family=sm.families.Binomial()).fit(
                cov_type="cluster", cov_kwds={"groups": pd.factorize(d.relation)[0]})
        b, se = float(r.params["log_cooc"]), float(r.bse["log_cooc"])
        out[name] = {"odds_ratio": float(np.exp(b)), "or_ci": [float(np.exp(b - 1.96 * se)), float(np.exp(b + 1.96 * se))],
                     "p": float(r.pvalues["log_cooc"]), "n": int(r.nobs)}
    return out


def analyse_measure(d: pd.DataFrame, y: str, L: int, n_boot: int, seed: int) -> dict:
    if y not in d or d[y].notna().sum() < 30:
        return {"missing": f"fewer than 30 resolved rows ({int(d[y].notna().sum()) if y in d else 0})"}
    rng = np.random.default_rng(seed)
    res = {"n_rows": int(len(d)), "n_resolved": int(d[y].notna().sum()), "n_censored": int(d[y].isna().sum())}
    r = d[d[y].notna()].dropna(subset=CONTROLS + ["log_cooc"]).copy()
    s = spearmanr(r[y], r.log_cooc)
    fl = r.groupby("fact_id").agg(y=(y, "mean"), x=("log_cooc", "first"), relation=("relation", "first"))
    sf = spearmanr(fl.y, fl.x)
    dm = r.assign(yd=r[y] - r.groupby("relation")[y].transform("mean"),
                  xd=r.log_cooc - r.groupby("relation").log_cooc.transform("mean"))
    sw = spearmanr(dm.yd, dm.xd)
    res["spearman"] = {"row": {"rho": float(s.statistic), "p": float(s.pvalue), "n": int(len(r))},
                       "fact_mean": {"rho": float(sf.statistic), "p": float(sf.pvalue), "n": int(len(fl))},
                       "within_relation_demeaned": {"rho": float(sw.statistic), "p": float(sw.pvalue), "n": int(len(dm))}}
    steps = [("log_cooc only", [], False), ("+ relation FE", [], True)]
    steps += [(f"+ {c} (alone)", [c], False) for c in CONTROLS]
    cum = []
    for c in CONTROLS:
        cum = cum + [c]
        steps.append(("cumulative: " + " + ".join(cum), list(cum), False))
    steps.append(("all controls + relation FE", list(CONTROLS), True))
    res["ols_steps"] = {name: ols_slope(r, y, xs, fe, n_boot, rng) for name, xs, fe in steps}
    full = d.dropna(subset=CONTROLS + ["log_cooc"])
    res["survival_all_rows"] = {"no controls": survival(full, y, L, []),
                                "prereg controls": survival(full, y, L, CONTROLS)}
    res["survival_resolved_only"] = {"no controls": survival_among_resolved(full, y, L, []),
                                     "prereg controls": survival_among_resolved(full, y, L, CONTROLS)}
    return res


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-boot", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=1234)
    args = ap.parse_args(argv)
    run_id = make_run_id("C1re")
    log = RunLog("C1re", run_id)
    (log.dir / "meta.json").write_text(json.dumps(provenance(run_id, vars(args)), indent=2))
    out = {"run_id": run_id, "label": "EXPLORATORY (not pre-registered)", "models": {}}
    for model, s3 in S3_RUNS.items():
        dep = pd.read_parquet(ROOT / "results" / "S3" / s3 / "depth.parquet")
        d = prep.build(dep, model)
        L = int(d.n_layers.iloc[0])
        m = {"s3_run_id": s3, "count_index": d.count_index.iloc[0], "count_label": d.count_label.iloc[0],
             "n_rows": int(len(d)), "n_facts": int(d.fact_id.nunique()), "n_layers": L,
             "correct_at1": float(d.correct_at1.mean()),
             "resolved_equals_correct": {
                 "causal_final_resolved_and_correct": int((d.causal_final.notna() & d.correct_at1).sum()),
                 "causal_final_resolved_not_correct": int((d.causal_final.notna() & ~d.correct_at1).sum()),
                 "causal_final_censored_and_correct": int((d.causal_final.isna() & d.correct_at1).sum()),
                 "causal_final_censored_not_correct": int((d.causal_final.isna() & ~d.correct_at1).sum())},
             "logistic_correct_on_log_cooc": logistic_correct(d.dropna(subset=CONTROLS + ["log_cooc"]), CONTROLS),
             "measures": {}}
        for y in MEASURES:
            m["measures"][y] = analyse_measure(d, y, L, args.n_boot, args.seed)
            log.log(event="measure", model=model, measure=y)
        out["models"][model] = m
    (log.dir / "c1.json").write_text(json.dumps(out, indent=2, default=float))
    print(log.dir / "c1.json")


if __name__ == "__main__":
    main()
