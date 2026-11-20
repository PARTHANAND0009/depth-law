"""Primary test of prereg amendment 2 (configs/prereg_amendment_2026-11-20.yaml).

  half_prob_depth ~ cooc_within + cooc_rel + log_subj + obj_logprob_final + n_answer_tokens
                    + n_subject_tokens + (1 + cooc_within | relation)

Per model, EXACT counts only (Pythia: piletrain, OLMo-2: olmo-mix-1124). partial R^2 of
cooc_within (marginal R^2 full - reduced), relation-cluster bootstrap CIs, Holm over models,
decision with the g1 thresholds. Sensitivities are labelled not gating.

Two subcommands:
  inputs : build data/amend2_inputs.parquet (fact-level covariates for every index; needs the
           infini-gram cache/API for answer first-token counts, used by one sensitivity only).
  test   : run the test on depth parquets from `run_depth --halfprob`; offline given the inputs.
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
from depthlaw.stats.mixed import partial_r2_general

AMEND = ROOT / "configs" / "prereg_amendment_2026-11-20.yaml"
INPUTS = ROOT / "data" / "amend2_inputs.parquet"
Y = "half_prob_depth"
X = "cooc_within"
OTHERS = ["cooc_rel", "log_subj", "obj_logprob_final", "n_answer_tokens", "n_subject_tokens"]
OLD_CONTROLS = ["log_subj", "log_obj", "n_answer_tokens", "log_answer_first_token_freq", "n_subject_tokens"]
INDEXES = ["piletrain", "olmo-mix-1124"]
FAMS = ["pythia", "olmo2"]
GATE_MODELS = ["pythia-1.4b", "pythia-2.8b", "olmo-2-1124-7b"]


# ----------------------------------------------------------------------------- inputs
def build_inputs(facts_path: Path, out: Path, first_token: bool = True) -> pd.DataFrame:
    from depthlaw.stats.prep import first_token_counts
    facts = pd.read_parquet(facts_path)
    exact = pd.read_parquet(ROOT / "data" / "counts_exact.parquet")
    cnf = pd.read_parquet(ROOT / "data" / "counts_primary.parquet")
    d = facts[["fact_id", "subject", "object", "relation"] +
              [f"n_{k}_tok_{f}" for f in FAMS for k in ("obj", "subj")]].copy()
    d = d.merge(exact[["fact_id"] + [f"exact_{ix}" for ix in INDEXES]], on="fact_id", how="left")
    d = d.merge(cnf[["fact_id"] + [f"{k}_{ix}" for ix in INDEXES for k in ("subj", "obj")]], on="fact_id", how="left")
    for ix in INDEXES:
        d[f"answer_first_token_count_{ix}"] = np.nan
        if first_token:
            try:
                ftc = first_token_counts(d.object.unique().tolist(), ix)
                d[f"answer_first_token_count_{ix}"] = d.object.map(ftc)
            except Exception as e:  # noqa: BLE001 - sensitivity input only; reported as MISSING
                print(f"first-token counts for {ix} unavailable: {e!r}")
    d["count_label"] = "EXACT"
    d.to_parquet(out, index=False)
    meta = {"facts": str(facts_path.relative_to(ROOT)), "n_facts": int(len(d)),
            "sources": ["data/counts_exact.parquet", "data/counts_primary.parquet"],
            "first_token_nonnull": {ix: int(d[f"answer_first_token_count_{ix}"].notna().sum()) for ix in INDEXES}}
    out.with_suffix(".meta.json").write_text(json.dumps(meta, indent=2))
    return d


def index_for(model: str) -> tuple[str, str]:
    m = model.lower()
    if "pythia" in m:
        return "piletrain", "pythia"
    if "olmo-2" in m:
        return "olmo-mix-1124", "olmo2"
    raise ValueError(f"{model}: amendment 2 uses EXACT indexes only (Pythia, OLMo-2)")


def assemble(depth: pd.DataFrame, inputs: pd.DataFrame) -> pd.DataFrame:
    model = depth.model.iloc[0]
    ix, fam = index_for(model)
    f = inputs.rename(columns={f"exact_{ix}": "exact_cooc", f"subj_{ix}": "subj_count", f"obj_{ix}": "obj_count",
                               f"answer_first_token_count_{ix}": "ftc", f"n_obj_tok_{fam}": "n_answer_tokens",
                               f"n_subj_tok_{fam}": "n_subject_tokens"})
    f = f[["fact_id", "subject", "object", "exact_cooc", "subj_count", "obj_count", "ftc", "n_answer_tokens",
           "n_subject_tokens"]]
    d = depth.drop(columns=[c for c in ("subject", "object") if c in depth]).merge(f, on="fact_id", how="left")
    d["log_cooc"] = np.log1p(d.exact_cooc)
    d["log_subj"] = np.log1p(d.subj_count)
    d["log_obj"] = np.log1p(d.obj_count)
    d["log_answer_first_token_freq"] = np.log1p(d.ftc)
    d["obj_logprob_final"] = d.obj_first_logprob
    d["template"] = d.relation + ":" + d.template_id.astype(str)
    d["count_index"], d["count_label"] = ix, "EXACT"
    return d


def add_within(d: pd.DataFrame) -> pd.DataFrame:
    d = d.copy()
    d["cooc_rel"] = d.groupby("relation").log_cooc.transform("mean")
    d[X] = d.log_cooc - d.cooc_rel
    return d


# ----------------------------------------------------------------------------- fits
def boot(d: pd.DataFrame, y: str, x: str, others: list[str], n_boot: int, seed: int) -> dict:
    rng = np.random.default_rng(seed)
    rels = d.relation.unique()
    by = {r: g for r, g in d.groupby("relation")}
    sl, pr, fails = [], [], 0
    for _ in range(n_boot):
        parts = []
        for k, r in enumerate(rng.choice(rels, size=len(rels), replace=True)):
            g = by[r].copy()
            g["relation"] = f"{r}#{k}"
            parts.append(g)
        try:
            res = partial_r2_general(pd.concat(parts, ignore_index=True), y, x, others)
            sl.append(res["slope"]), pr.append(res["partial_r2"])
        except Exception:  # noqa: BLE001 - counted and reported
            fails += 1
    q = lambda a: [float(np.percentile(a, 2.5)), float(np.percentile(a, 97.5))] if a else [None, None]
    return {"n_boot": n_boot, "n_failed": fails, "slope_ci": q(sl), "partial_r2_ci": q(pr)}


def summ(pr: dict) -> dict:
    return {"partial_r2": pr["partial_r2"], "slope": pr["slope"], "slope_se": pr["slope_se"], "slope_p": pr["slope_p"],
            "n": pr["full"]["n"], "n_relations": pr["full"]["n_relations"],
            "converged": pr["full"]["converged"] and pr["reduced"]["converged"],
            "r2_marginal_full": pr["full"]["r2_marginal"], "r2_marginal_reduced": pr["reduced"]["r2_marginal"],
            "params": pr["full"]["params"], "pvalues": pr["full"]["pvalues"], "formula": pr["full"]["formula"],
            "re_formula": pr["full"]["re_formula"], "vc": pr["full"]["vc"]}


def safe(fn, *a, **k) -> dict:
    try:
        return summ(fn(*a, **k))
    except Exception as e:  # noqa: BLE001
        return {"missing": f"fit failed: {e!r}"[:300]}


def analyse(depth: pd.DataFrame, inputs: pd.DataFrame, n_boot: int, seed: int) -> dict:
    d0 = assemble(depth, inputs)
    need = [Y, "log_cooc", "log_subj", "obj_logprob_final", "n_answer_tokens", "n_subject_tokens"]
    d = add_within(d0.dropna(subset=need))
    res = {"model": depth.model.iloc[0], "revision": depth.revision.iloc[0],
           "run_ids": sorted(depth.run_id.unique().tolist()), "count_index": d0.count_index.iloc[0],
           "count_label": "EXACT", "n_rows_depth": int(len(depth)), "n_rows_fit": int(len(d)),
           "n_facts_fit": int(d.fact_id.nunique()), "n_relations": int(d.relation.nunique()),
           "n_errors": int(depth["error"].notna().sum()) if "error" in depth else 0,
           "n_layers": int(depth.n_layers.dropna().iloc[0]) if depth.n_layers.notna().any() else None,
           "correct_at1_frac": float(d.correct_at1.mean()),
           "descriptives": {
               "half_prob_depth_quantiles": {str(q): float(d[Y].quantile(q)) for q in (0.1, 0.25, 0.5, 0.75, 0.9)},
               "median_correct": float(d[d.correct_at1][Y].median()) if d.correct_at1.any() else None,
               "median_wrong": float(d[~d.correct_at1][Y].median()) if (~d.correct_at1).any() else None,
               "spearman_raw_log_cooc": float(spearmanr(d[Y], d.log_cooc).statistic),
               "spearman_within_relation": float(spearmanr(d[Y], d[X]).statistic),
               "spearman_obj_logprob_final": float(spearmanr(d[Y], d.obj_logprob_final).statistic),
               "share_patched_final_above_alone": float(d.patched_final_above_alone.mean())
               if "patched_final_above_alone" in d else None}}
    prim = safe(partial_r2_general, d, Y, X, OTHERS)
    if "missing" not in prim and n_boot:
        prim["bootstrap"] = boot(d, Y, X, OTHERS, n_boot, seed)
    res["primary"] = prim
    s = {}
    if "patched_final_above_alone" in d:
        da = add_within(d0.dropna(subset=need)[lambda q: q.patched_final_above_alone.astype(bool)])
        s["drop_final_not_above_carrier_alone"] = safe(partial_r2_general, da, Y, X, OTHERS) if len(da) > 50 else \
            {"missing": f"only {len(da)} rows"}
    s["plus_margin"] = safe(partial_r2_general, d.dropna(subset=["margin"]), Y, X, OTHERS + ["margin"])
    s["plus_template_subject_intercepts"] = safe(partial_r2_general, d, Y, X, OTHERS, vc=True)
    do = d.dropna(subset=OLD_CONTROLS)
    s["original_prereg_controls_unsplit"] = (safe(partial_r2_general, do, Y, "log_cooc", OLD_CONTROLS)
                                             if len(do) > 50 else {"missing": f"{len(do)} rows with all controls"})
    dc = add_within(d0.dropna(subset=need)[lambda q: q.correct_at1.astype(bool)])
    s["correct_rows_only"] = safe(partial_r2_general, dc, Y, X, OTHERS) if dc.relation.nunique() > 2 else \
        {"missing": "too few correct rows"}
    for m in ("causal_final", "logit_lens_depth"):
        dm = add_within(d0.dropna(subset=need + [m]))
        s[f"secondary_{m}"] = (safe(partial_r2_general, dm, m, X, OTHERS) if len(dm) > 50 and dm.relation.nunique() > 2
                               else {"missing": f"{len(dm)} resolved rows"})
        if m in dm:
            s[f"secondary_{m}"]["n_resolved"] = int(len(dm))
    res["sensitivities_not_gating"] = s
    return res


def decision(results: list[dict], amend: dict) -> dict:
    g = amend["primary_test"]
    th = yaml.safe_load(open(ROOT / "configs" / "prereg.yaml"))["g1"]
    per = {}
    for r in results:
        p = r["primary"]
        pr2, sl = p.get("partial_r2"), p.get("slope")
        name = r["model"].split("/")[-1].lower()
        if pr2 is None:
            per[name] = "MISSING"
        elif pr2 >= th["go_partial_r2"] and sl is not None and sl < 0:
            per[name] = "PASS"
        elif pr2 >= th["weak_partial_r2"] and sl is not None and sl < 0:
            per[name] = "WEAK"
        else:
            per[name] = "FAIL"
    n_pass = sum(v == "PASS" for v in per.values())
    n_weak = sum(v == "WEAK" for v in per.values())
    missing = [m for m in GATE_MODELS if m not in per]
    out = {"per_model": per, "n_pass": n_pass, "gate_models_missing": missing, "rule": g["decision"]}
    need = th["min_models_passing"]
    if n_pass >= need:
        out["outcome"] = "GO"
    elif n_pass + n_weak >= need:
        out["outcome"] = "WEAK"
    elif n_pass + n_weak + len(missing) >= need:
        out["outcome"] = "UNDECIDED (gate models missing)"
    else:
        out["outcome"] = "NO-GO"
    return out


def fmt(x, nd=3):
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "MISSING"
    return f"{x:.{nd}f}" if isinstance(x, float) else str(x)


def report(out: dict, path: Path) -> None:
    L = [f"# Amendment 2 primary test{' (DRY RUN, not a gate result)' if out['dry_run'] else ''}\n",
         f"Source of every number: `{out['json']}` (run_id `{out['run_id']}`). "
         "Pre-registration: `configs/prereg_amendment_2026-11-20.yaml`.\n"]
    dec = out["decision"]
    L.append(f"## Decision\nRule: {dec['rule']}\n")
    L.append("| model | index (label) | N rows / facts / relations | partial R² [95% CI] | slope cooc_within [95% CI] | p | p (Holm) | outcome |")
    L.append("|---|---|---|---|---|---|---|---|")
    for r in out["models"]:
        p = r["primary"]
        b = p.get("bootstrap", {})
        ci = lambda k, i, nd=3: fmt((b.get(k) or [None, None])[i], nd)
        name = r["model"].split("/")[-1].lower()
        if "missing" in p:
            L.append(f"| {r['model']} | {r['count_index']} (EXACT) | {r['n_rows_fit']} | MISSING: {p['missing']} | | | | MISSING |")
            continue
        L.append(f"| {r['model']} | {r['count_index']} (EXACT) | {p['n']} / {r['n_facts_fit']} / {p['n_relations']} | "
                 f"{fmt(p['partial_r2'], 4)} [{ci('partial_r2_ci', 0, 4)}, {ci('partial_r2_ci', 1, 4)}] | "
                 f"{fmt(p['slope'], 4)} [{ci('slope_ci', 0, 4)}, {ci('slope_ci', 1, 4)}] | {fmt(p['slope_p'], 4)} | "
                 f"{fmt(p.get('p_holm'), 4)} | {dec['per_model'][name]} |")
    L.append(f"\nGate models not run: {', '.join(dec['gate_models_missing']) or 'none'}. **Outcome: {dec['outcome']}**\n")
    L.append(f"Bootstrap: relation clusters, {out['n_boot']} resamples (failures listed in the json).\n")
    L.append("## Descriptives (half_prob_depth, fit rows)\n")
    L.append("| model | correct@1 | median depth correct / wrong | Spearman raw log cooc | Spearman within relation | Spearman obj logprob | share final > carrier alone |")
    L.append("|---|---|---|---|---|---|---|")
    for r in out["models"]:
        d = r["descriptives"]
        L.append(f"| {r['model']} | {fmt(r['correct_at1_frac'])} | {fmt(d['median_correct'])} / {fmt(d['median_wrong'])} | "
                 f"{fmt(d['spearman_raw_log_cooc'])} | {fmt(d['spearman_within_relation'])} | {fmt(d['spearman_obj_logprob_final'])} | "
                 f"{fmt(d['share_patched_final_above_alone'])} |")
    L.append("\n## Sensitivities (not gating)\n")
    L.append("| model | variant | N | partial R² | slope | p |\n|---|---|---|---|---|---|")
    for r in out["models"]:
        for k, v in r["sensitivities_not_gating"].items():
            if "missing" in v:
                L.append(f"| {r['model']} | {k} | | MISSING: {v['missing']} | | |")
            else:
                L.append(f"| {r['model']} | {k} | {v['n']} | {fmt(v['partial_r2'], 4)} | {fmt(v['slope'], 4)} | {fmt(v['slope_p'], 4)} |")
    L.append("\n## Runs\n")
    for r in out["models"]:
        L.append(f"- {r['model']} @ {r['revision']}: depth rows {r['n_rows_depth']}, errors {r['n_errors']}, "
                 f"layers {r['n_layers']}, depth runs {', '.join(r['run_ids'])}")
    path.write_text("\n".join(L) + "\n")


def main(argv=None):
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("inputs")
    a.add_argument("--facts", default=str(ROOT / "data" / "facts_g1cpu.parquet"))
    a.add_argument("--out", default=str(INPUTS))
    a.add_argument("--no-first-token", action="store_true")
    t = sub.add_parser("test")
    t.add_argument("--depth", nargs="+", required=True)
    t.add_argument("--inputs", default=str(INPUTS))
    t.add_argument("--n-boot", type=int, default=1000)
    t.add_argument("--seed", type=int, default=1234)
    t.add_argument("--dry-run", action="store_true")
    t.add_argument("--report", default=None, help="report path (default reports/A2_PRIMARY[_DRYRUN].md)")
    args = ap.parse_args(argv)
    if args.cmd == "inputs":
        d = build_inputs(Path(args.facts), Path(args.out), first_token=not args.no_first_token)
        print(args.out, len(d))
        return
    seed_everything(args.seed)
    amend = yaml.safe_load(open(AMEND))["amendment_2"]
    run_id = make_run_id("A2dry" if args.dry_run else "A2")
    log = RunLog("A2", run_id)
    (log.dir / "meta.json").write_text(json.dumps(provenance(run_id, vars(args)), indent=2))
    inputs = pd.read_parquet(args.inputs)
    results = []
    for p in args.depth:
        dep = pd.read_parquet(p)
        log.log(event="model_start", depth=p, model=dep.model.iloc[0], rows=len(dep))
        results.append(analyse(dep, inputs, args.n_boot, args.seed))
    keys = [i for i, r in enumerate(results) if r["primary"].get("slope_p") is not None]
    if keys:
        adj = multipletests([results[i]["primary"]["slope_p"] for i in keys], method="holm")[1]
        for i, v in zip(keys, adj):
            results[i]["primary"]["p_holm"] = float(v)
    out = {"run_id": run_id, "dry_run": args.dry_run, "n_boot": args.n_boot, "label": "PRE-REGISTERED (amendment_2)",
           "models": results, "decision": decision(results, amend)}
    jp = log.dir / "a2.json"
    out["json"] = str(jp.relative_to(ROOT))
    jp.write_text(json.dumps(out, indent=2, default=lambda o: o.item() if hasattr(o, "item") else str(o)))
    rp = Path(args.report) if args.report else ROOT / "reports" / ("A2_PRIMARY_DRYRUN.md" if args.dry_run else "A2_PRIMARY.md")
    report(out, rp)
    log.log(event="done", report=str(rp))
    print(jp)
    print(rp)


if __name__ == "__main__":
    main()
