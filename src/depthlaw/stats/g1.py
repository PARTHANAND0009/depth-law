"""G1 analysis: fit every (model x measure), write results/G1/<run_id>/g1.json and the report
reports/GATE_G1.md (or reports/G1_DRYRUN_<model>.md with --dry-run). Every number in the
report is read from g1.json, which is written by this logged run.

Usage: python -m depthlaw.stats.g1 --depth results/S3/<run>/depth.parquet [...] [--n-boot 1000]
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from scipy.stats import spearmanr
from statsmodels.stats.multitest import multipletests

from depthlaw.io import ROOT, RunLog, make_run_id, provenance, seed_everything
from depthlaw.stats import prep
from depthlaw.stats.bootstrap import cluster_bootstrap
from depthlaw.stats.mixed import CONTROLS, partial_r2
from depthlaw.stats.shapes import compare
from depthlaw.stats.survival import hazard_ratio

HEADLINE = "causal_final"
FIT_MEASURES = ["causal_final", "patchscope_depth", "tuned_lens_depth", "logit_lens_depth", "causal_subj_onset"]


def analyse_model(depth: pd.DataFrame, n_boot: int, seed: int, exact_path=None) -> dict:
    model = depth.model.iloc[0]
    d = prep.build(depth, model, exact_path=exact_path)
    n_layers = int(d.n_layers.iloc[0])
    res = {"model": model, "count_index": d.count_index.iloc[0], "count_label": d.count_label.iloc[0],
           "run_ids": sorted(depth.run_id.unique().tolist()), "n_rows": int(len(d)),
           "n_facts": int(d.fact_id.nunique()), "n_errors": int(d.get("error", pd.Series(dtype=str)).notna().sum()),
           "correct_at1_frac": float(d.correct_at1.mean()), "n_layers": n_layers, "measures": {}}
    # override control
    ok = d[[HEADLINE, "override_depth"]].dropna()
    res["override"] = {"n_both": int(len(ok)), "median_override": float(d.override_depth.median()) if d.override_depth.notna().any() else None,
                       "spearman_with_headline": float(spearmanr(ok[HEADLINE], ok.override_depth).statistic) if len(ok) > 2 else None,
                       "share_equal": float((ok[HEADLINE] == ok.override_depth).mean()) if len(ok) else None}
    for m in FIT_MEASURES:
        if m not in d or d[m].notna().sum() < 30:
            res["measures"][m] = {"missing": f"fewer than 30 resolved rows ({int(d[m].notna().sum()) if m in d else 0})"}
            continue
        r = {"n_resolved": int(d[m].notna().sum()), "n_censored": int(d[m].isna().sum())}
        dd = d[d[m].notna() & d.log_cooc.notna()].copy()
        dd = dd.dropna(subset=CONTROLS)
        try:
            pr = partial_r2(dd, m)
            r.update({k: pr[k] for k in ("partial_r2", "slope", "slope_se", "slope_p")})
            r["r2_marginal_full"] = pr["full"]["r2_marginal"]
            r["r2_marginal_reduced"] = pr["reduced"]["r2_marginal"]
            r["converged"] = pr["full"]["converged"] and pr["reduced"]["converged"]
            r["n_fit"] = pr["full"]["n"]
        except Exception as e:  # noqa: BLE001
            r["fit_error"] = repr(e)[:300]
        if n_boot and "partial_r2" in r:
            r["bootstrap"] = cluster_bootstrap(dd, m, n_boot=n_boot, seed=seed)
        try:
            r["survival"] = hazard_ratio(d[d.log_cooc.notna()].dropna(subset=CONTROLS), m, n_layers)
        except Exception as e:  # noqa: BLE001
            r["survival_error"] = repr(e)[:300]
        try:
            r["shape_aic"] = compare(dd, m)
        except Exception as e:  # noqa: BLE001
            r["shape_error"] = repr(e)[:300]
        if m == HEADLINE:
            try:  # sensitivities (not gating): CNF predictor; override covariate
                s1 = partial_r2(dd.assign(log_cooc=dd.log_cnf_cooc), m, controls=CONTROLS + ["approx_flag"])
                r["sens_cnf_predictor"] = {k: s1[k] for k in ("partial_r2", "slope", "slope_p")}
                do = dd.dropna(subset=["override_depth"])
                s2 = partial_r2(do, m, controls=CONTROLS + ["override_depth"])
                r["sens_override_covariate"] = {k: s2[k] for k in ("partial_r2", "slope", "slope_p")}
                r["sens_override_covariate"]["n"] = int(len(do))
            except Exception as e:  # noqa: BLE001
                r["sens_error"] = repr(e)[:300]
        res["measures"][m] = r
    # measure agreement: fact-level (template-averaged) Spearman
    agg = d.groupby("fact_id")[[m for m in FIT_MEASURES if m in d]].mean()
    res["agreement_spearman"] = {f"{a}|{b}": float(spearmanr(agg[[a, b]].dropna()).statistic)
                                 for i, a in enumerate(agg.columns) for b in agg.columns[i + 1:]
                                 if len(agg[[a, b]].dropna()) > 10}
    # validation of the exact predictor against non-approx CNF counts
    fv = d.drop_duplicates("fact_id")
    na = fv[fv.approx_flag == 0][["exact_cooc", "cnf_cooc"]].dropna()
    res["exact_vs_cnf_nonapprox"] = {"n": int(len(na)),
                                    "spearman": float(spearmanr(na.exact_cooc, na.cnf_cooc).statistic) if len(na) > 10 else None}
    # 5 example facts per frequency decile (headline measure, template-averaged)
    ex = d.groupby(["fact_id", "subject", "object", "relation"]).agg(
        exact_cooc=("exact_cooc", "first"), depth=(HEADLINE, "mean"), correct=("correct_at1", "mean")).reset_index()
    ex["decile"] = pd.qcut(ex.exact_cooc.rank(method="first"), 10, labels=False)
    res["examples"] = {int(k): g.sample(min(5, len(g)), random_state=seed)[
        ["fact_id", "subject", "object", "relation", "exact_cooc", "depth", "correct"]].to_dict("records")
        for k, g in ex.groupby("decile")}
    return res


def decision(results: list[dict], prereg: dict) -> dict:
    g = prereg["g1"]
    per = {}
    for r in results:
        m = r["measures"].get(HEADLINE, {})
        pr2, slope = m.get("partial_r2"), m.get("slope")
        if pr2 is None:
            per[r["model"]] = "MISSING"
        elif pr2 >= g["go_partial_r2"] and slope is not None and slope < 0:
            per[r["model"]] = "PASS"
        elif pr2 >= g["weak_partial_r2"] and slope is not None and slope < 0:
            per[r["model"]] = "WEAK"
        else:
            per[r["model"]] = "FAIL"
    n_pass = sum(v == "PASS" for v in per.values())
    gate_models = [m.split("/")[-1].lower() for m in g["models"]]
    present = [r["model"].split("/")[-1].lower() for r in results]
    return {"per_model": per, "n_pass": n_pass, "min_models_passing": g["min_models_passing"],
            "gate_models_missing": [m for m in gate_models if m not in present],
            "outcome": "GO" if n_pass >= g["min_models_passing"] else
                       ("WEAK" if n_pass + sum(v == "WEAK" for v in per.values()) >= g["min_models_passing"] else "NO-GO"),
            "rule": f"PASS = partial R^2 >= {g['go_partial_r2']} with negative slope on {HEADLINE}; "
                    f"WEAK = >= {g['weak_partial_r2']}; GO needs >= {g['min_models_passing']} PASS models."}


def fmt(x, nd=3):
    return "MISSING" if x is None or (isinstance(x, float) and np.isnan(x)) else (f"{x:.{nd}f}" if isinstance(x, float) else str(x))


def report(out: dict, path: Path, dry: bool) -> None:
    L = []
    title = "G1 DRY RUN (not a gate result)" if dry else "GATE G1"
    L.append(f"# {title}\n")
    L.append(f"Source of every number: `{out['json']}` (run_id `{out['run_id']}`).")
    if dry:
        L.append("Dry run on a test model / subsample. It checks the pipeline end to end; it is NOT the G1 decision.\n")
    dec = out["decision"]
    L.append(f"\n## Decision rule (configs/prereg.yaml g1 + amendment_1)\n{dec['rule']}\n")
    L.append("| model | count index (label) | partial R² | outcome |\n|---|---|---|---|")
    for r in out["models"]:
        m = r["measures"].get(HEADLINE, {})
        L.append(f"| {r['model']} | {r['count_index']} ({r['count_label']}) | {fmt(m.get('partial_r2'))} | {dec['per_model'][r['model']]} |")
    L.append(f"\nPASS models: {dec['n_pass']} (need {dec['min_models_passing']}). Gate models not run: "
             f"{', '.join(dec['gate_models_missing']) or 'none'}. **Outcome: {dec['outcome']}**\n")
    L.append("## Per model × measure\n")
    L.append("| model | measure | N resolved / censored | N fit | partial R² [CI] | slope [CI] | p (Holm) | HR [CI] | best shape (AIC) |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    for r in out["models"]:
        for mname, m in r["measures"].items():
            if "missing" in m:
                L.append(f"| {r['model']} | {mname} | MISSING: {m['missing']} | | | | | | |")
                continue
            b = m.get("bootstrap", {})
            s = m.get("survival", {})
            L.append(f"| {r['model']} | {mname} | {m['n_resolved']} / {m['n_censored']} | {m.get('n_fit', 'MISSING')} | "
                     f"{fmt(m.get('partial_r2'))} [{fmt((b.get('partial_r2_ci') or [None])[0])}, {fmt((b.get('partial_r2_ci') or [None, None])[1])}] | "
                     f"{fmt(m.get('slope'), 4)} [{fmt((b.get('slope_ci') or [None])[0], 4)}, {fmt((b.get('slope_ci') or [None, None])[1], 4)}] | "
                     f"{fmt(m.get('p_holm'), 4)} | {fmt(s.get('hr'))} [{fmt((s.get('hr_ci') or [None])[0])}, {fmt((s.get('hr_ci') or [None, None])[1])}] | "
                     f"{m.get('shape_aic', {}).get('best', 'MISSING')} |")
    L.append("\nCIs: cluster bootstrap over relations "
             f"(n_boot = {out['n_boot']}); HR = discrete-time cloglog hazard ratio per unit log1p(exact cooc), "
             "relation-clustered SEs. Holm across models × measures.\n")
    L.append("## Controls and sensitivities (headline measure)\n")
    L.append("| model | override median | Spearman(headline, override) | share equal | CNF-predictor partial R² | +override covariate partial R² | exact vs CNF Spearman (non-approx, N) |")
    L.append("|---|---|---|---|---|---|---|")
    for r in out["models"]:
        m = r["measures"].get(HEADLINE, {})
        o = r["override"]
        v = r["exact_vs_cnf_nonapprox"]
        L.append(f"| {r['model']} | {fmt(o['median_override'])} | {fmt(o['spearman_with_headline'])} | {fmt(o['share_equal'])} | "
                 f"{fmt(m.get('sens_cnf_predictor', {}).get('partial_r2'))} | {fmt(m.get('sens_override_covariate', {}).get('partial_r2'))} | "
                 f"{fmt(v['spearman'])} ({v['n']}) |")
    L.append("\n## Measure agreement (fact-level Spearman)\n")
    for r in out["models"]:
        L.append(f"**{r['model']}**: " + "; ".join(f"{k} {fmt(v, 2)}" for k, v in r["agreement_spearman"].items()))
    L.append("\n## 5 example facts per frequency decile (headline depth, template mean)\n")
    for r in out["models"]:
        L.append(f"**{r['model']}**\n\n| decile | subject | object | relation | exact cooc | depth | correct |\n|---|---|---|---|---|---|---|")
        for k, rows in r["examples"].items():
            for e in rows:
                L.append(f"| {k} | {e['subject']} | {e['object']} | {e['relation']} | {int(e['exact_cooc'])} | {fmt(e['depth'])} | {fmt(e['correct'], 2)} |")
    L.append("\n## Run facts\n")
    for r in out["models"]:
        L.append(f"- {r['model']}: rows {r['n_rows']}, facts {r['n_facts']}, errors {r['n_errors']}, "
                 f"correct@1 {fmt(r['correct_at1_frac'])}, layers {r['n_layers']}, depth runs {', '.join(r['run_ids'])}")
    path.write_text("\n".join(L) + "\n")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--depth", nargs="+", required=True)
    ap.add_argument("--n-boot", type=int, default=1000)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--seed", type=int, default=1234)
    ap.add_argument("--exact", default=None, help="exact-count parquet (default data/counts_exact.parquet)")
    args = ap.parse_args(argv)
    seed_everything(args.seed)
    prereg = yaml.safe_load(open(ROOT / "configs" / "prereg.yaml"))
    run_id = make_run_id("G1dry" if args.dry_run else "G1")
    log = RunLog("G1", run_id)
    results = []
    for p in args.depth:
        dep = pd.read_parquet(p)
        log.log(event="model_start", depth=p, model=dep.model.iloc[0])
        results.append(analyse_model(dep, args.n_boot, args.seed, args.exact))
    # Holm across models x measures
    keys = [(i, m) for i, r in enumerate(results) for m, v in r["measures"].items() if v.get("slope_p") is not None]
    if keys:
        adj = multipletests([results[i]["measures"][m]["slope_p"] for i, m in keys], method="holm")[1]
        for (i, m), a in zip(keys, adj):
            results[i]["measures"][m]["p_holm"] = float(a)
    out = {"run_id": run_id, "n_boot": args.n_boot, "dry_run": args.dry_run, "models": results,
           "decision": decision(results, prereg)}
    jpath = log.dir / "g1.json"
    out["json"] = str(jpath.relative_to(ROOT))
    jpath.write_text(json.dumps(out, indent=2, default=lambda o: o.item() if hasattr(o, "item") else str(o)))
    (log.dir / "meta.json").write_text(json.dumps(provenance(run_id, vars(args)), indent=2))
    name = (f"G1_DRYRUN_{results[0]['model'].split('/')[-1]}.md" if args.dry_run else "GATE_G1.md")
    report(out, ROOT / "reports" / name, args.dry_run)
    log.log(event="done", report=name)
    print(ROOT / "reports" / name)


if __name__ == "__main__":
    main()
