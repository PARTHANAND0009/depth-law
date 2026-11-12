"""S4 analyses on CPU (notes/s4_plan.md): held-out relation families, minimal pairs, TOST of
the slope against the prereg margin, SANSKRITI slice. Writes results/S4/<run_id>/s4.json and
reports/S4.md; every number in the report is read from s4.json.

Usage: python -m depthlaw.stats.s4 --depth <g1 depth.parquet> [...] [--sanskriti <depth.parquet>]
"""
from __future__ import annotations

import argparse
import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
import yaml
from scipy.stats import norm, spearmanr, wilcoxon

from depthlaw.io import ROOT, RunLog, make_run_id, provenance, seed_everything
from depthlaw.stats import prep
from depthlaw.stats.bootstrap import cluster_bootstrap
from depthlaw.stats.mixed import CONTROLS, fit, partial_r2

Y = "causal_final"
LN10 = float(np.log(10))
FAMILIES = {
    "geo_place": ["capital", "continent", "country", "headquarters", "formation_location", "place_of_birth",
                  "place_of_death", "work_location"],
    "language": ["native_language", "official_language", "original_language"],
    "person_role": ["occupation", "field_of_work", "sport", "sport_position", "instrument", "music_genre",
                    "citizenship", "employer"],
    "org_product": ["manufacturer", "developer", "company_ceo", "country_of_origin"],
}


def family(rel: str) -> str:
    for k, v in FAMILIES.items():
        if rel in v:
            return k
    return "other"


def tost(slope: float, se: float, margin_decade: float) -> dict:
    """Two one-sided z-tests that the slope per decade lies within +-margin; 90% CI."""
    b, s = slope * LN10, se * LN10
    p_lo = 1 - norm.cdf((b + margin_decade) / s)
    p_hi = norm.cdf((b - margin_decade) / s)
    p = float(max(p_lo, p_hi))
    return {"slope_per_decade": b, "se_per_decade": s, "ci90_per_decade": [b - 1.645 * s, b + 1.645 * s],
            "margin_per_decade": margin_decade, "p_tost": p, "equivalent": bool(p < 0.05)}


def _fit_fixed(d: pd.DataFrame, with_x: bool):
    cols = [c for c in CONTROLS if d[c].nunique() > 1]
    fx = " + ".join((["log_cooc"] if with_x else []) + cols) or "1"
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        m = smf.mixedlm(f"{Y} ~ {fx}", d, groups=d["relation"], re_formula="1 + log_cooc" if with_x else "1",
                        vc_formula={"template": "0 + C(template)", "subject": "0 + C(fact_id)"})
        return m.fit(reml=False, method=["lbfgs", "powell"])


def held_out_families(d: pd.DataFrame, margin: float) -> dict:
    d = d.assign(family=d.relation.map(family))
    out = {"families": {f: sorted(g.relation.unique().tolist()) for f, g in d.groupby("family")}, "per_family": {},
           "leave_one_out": {}}
    for f, g in d.groupby("family"):
        r = {"n_rows": int(len(g)), "n_facts": int(g.fact_id.nunique()), "n_relations": int(g.relation.nunique())}
        try:
            pr = partial_r2(g, Y)
            r.update({"partial_r2": pr["partial_r2"], "slope": pr["slope"], "slope_se": pr["slope_se"],
                      "slope_p": pr["slope_p"], "converged": pr["full"]["converged"] and pr["reduced"]["converged"]})
            if pr["slope_se"] and np.isfinite(pr["slope_se"]):
                r["tost"] = tost(pr["slope"], pr["slope_se"], margin)
        except Exception as e:  # noqa: BLE001 - reported as MISSING
            r["fit_error"] = repr(e)[:300]
        out["per_family"][f] = r
        # leave this family out: fit on the rest, predict this family from fixed effects
        tr = d[d.family != f]
        try:
            full, red = _fit_fixed(tr, True), _fit_fixed(tr, False)
            yhat_f, yhat_r = np.asarray(full.predict(g)), np.asarray(red.predict(g))
            y = g[Y].to_numpy()
            ss = float(np.sum((y - y.mean()) ** 2))
            r2f, r2r = 1 - float(np.sum((y - yhat_f) ** 2)) / ss, 1 - float(np.sum((y - yhat_r) ** 2)) / ss
            out["leave_one_out"][f] = {"n_test_rows": int(len(g)), "n_train_rows": int(len(tr)),
                                       "oof_r2_with_cooc": r2f, "oof_r2_without_cooc": r2r, "delta_r2": r2f - r2r,
                                       "train_slope": float(full.fe_params["log_cooc"]),
                                       "spearman_pred_with_cooc": float(spearmanr(y, yhat_f).statistic)}
        except Exception as e:  # noqa: BLE001
            out["leave_one_out"][f] = {"fit_error": repr(e)[:300]}
    return out


def minimal_pairs(d: pd.DataFrame, facts: pd.DataFrame, min_ratio: float, seed: int) -> dict:
    """Fact pairs with the same object first token (pythia tokenizer) and (c_hi+1)/(c_lo+1) >= min_ratio,
    both with a fact-level causal_final depth (mean over resolved templates)."""
    fd = d.groupby("fact_id").agg(depth=(Y, "mean"), cooc=("exact_cooc", "first"), relation=("relation", "first"))
    fd = fd.join(facts.set_index("fact_id")[["obj_first_tok_pythia", "object"]]).dropna(subset=["depth", "cooc"])
    pairs = []
    for tok, g in fd.groupby("obj_first_tok_pythia"):
        g = g.sort_values("cooc")
        ids = g.index.to_list()
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                lo, hi = g.loc[ids[i]], g.loc[ids[j]]
                ratio = (hi.cooc + 1) / (lo.cooc + 1)
                if ratio >= min_ratio:
                    pairs.append({"tok": int(tok), "lo": ids[i], "hi": ids[j], "obj_lo": lo.object, "obj_hi": hi.object,
                                  "rel_lo": lo.relation, "rel_hi": hi.relation, "cooc_lo": float(lo.cooc),
                                  "cooc_hi": float(hi.cooc), "ratio": float(ratio),
                                  "diff_hi_minus_lo": float(hi.depth - lo.depth)})
    p = pd.DataFrame(pairs)
    out = {"min_ratio": min_ratio, "ratio_rule": "(cooc_hi+1)/(cooc_lo+1)", "n_facts_with_depth": int(len(fd))}
    if p.empty:
        return {**out, "missing": "no pairs"}

    def summ(q: pd.DataFrame) -> dict:
        r = {"n_pairs": int(len(q)), "n_distinct_facts": int(len(set(q.lo) | set(q.hi))),
             "n_object_tokens": int(q.tok.nunique()), "mean_diff": float(q.diff_hi_minus_lo.mean()),
             "median_diff": float(q.diff_hi_minus_lo.median()), "share_hi_shallower": float((q.diff_hi_minus_lo < 0).mean())}
        nz = q.diff_hi_minus_lo[q.diff_hi_minus_lo != 0]
        if len(nz) >= 6:
            w = wilcoxon(nz)
            r.update({"wilcoxon_n_nonzero": int(len(nz)), "wilcoxon_p": float(w.pvalue)})
        else:
            r["wilcoxon"] = f"MISSING: fewer than 6 non-zero differences ({len(nz)})"
        return r

    one = p.sort_values("ratio", ascending=False).groupby("tok").head(1)  # one independent pair per object token
    same_rel = p[p.rel_lo == p.rel_hi]
    out.update({"all_pairs": summ(p), "one_per_object_token": summ(one),
                "same_relation": summ(same_rel) if len(same_rel) else {"missing": "no same-relation pairs"},
                "examples": one.sample(min(10, len(one)), random_state=seed).to_dict("records")})
    return out


def sanskriti_slice(dep: pd.DataFrame, margin: float) -> dict:
    sk = pd.read_parquet(ROOT / "data" / "sanskriti_s4.parquet")
    cnt = pd.read_parquet(ROOT / "data" / "sanskriti_cloze_exact.parquet")
    d = dep.merge(sk[["fact_id", "subject", "object"]], on="fact_id").merge(
        cnt[["fact_id", "exact_piletrain", "run_id"]].rename(columns={"run_id": "count_run_id"}), on="fact_id", how="left")
    d["log_cooc"] = np.log1p(d.exact_piletrain)
    fl = d.groupby("fact_id").agg(cooc=("exact_piletrain", "first"), depth=(Y, "mean"), correct=("correct_at1", "mean"))
    out = {"model": dep.model.iloc[0], "depth_run_ids": sorted(dep.run_id.unique().tolist()),
           "count_run_ids": sorted(d.count_run_id.dropna().unique().tolist()), "count_index": "piletrain (EXACT)",
           "n_items": int(d.fact_id.nunique()), "n_rows": int(len(d)), "n_errors": int(dep.get("error", pd.Series(dtype=str)).notna().sum()),
           "correct_at1_frac": float(d.correct_at1.mean()), "n_resolved_rows": int(d[Y].notna().sum()),
           "n_censored_rows": int(d[Y].isna().sum()), "zero_cooc_frac_items": float((fl.cooc == 0).mean()),
           "median_cooc_items": float(fl.cooc.median())}
    r = d.dropna(subset=[Y, "log_cooc"])
    if len(r) < 30:
        out["fit"] = f"MISSING: fewer than 30 resolved rows ({len(r)})"
        return out
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        m = smf.mixedlm(f"{Y} ~ log_cooc", r, groups=r["fact_id"]).fit(reml=False)
    out["fit"] = {"n_rows": int(len(r)), "n_items": int(r.fact_id.nunique()), "slope": float(m.params["log_cooc"]),
                  "slope_se": float(m.bse["log_cooc"]), "slope_p": float(m.pvalues["log_cooc"]),
                  "model": "causal_final ~ log1p(exact Pile cooc), random intercept per item (no controls)",
                  "tost": tost(float(m.params["log_cooc"]), float(m.bse["log_cooc"]), margin)}
    fr = fl.dropna()
    out["fit"]["spearman_item_level"] = {"n": int(len(fr)), "rho": float(spearmanr(fr.cooc, fr.depth).statistic) if len(fr) > 10 else None}
    return out


def lre_nested(r: pd.DataFrame, lre: pd.DataFrame) -> dict:
    """Relation-level LRE faithfulness as a covariate: does log_cooc add beyond it?"""
    fr = lre.groupby("relation").agg(lre_faith=("faithful", "mean"), n_test=("faithful", "size")).reset_index()
    d = r.merge(fr, on="relation", how="inner")
    rel = d.groupby("relation").agg(depth=(Y, "mean"), lre_faith=("lre_faith", "first"))
    out = {"lre_run_ids": sorted(lre.run_id.unique().tolist()), "layer": int(lre.layer.iloc[0]),
           "beta": float(lre.beta.iloc[0]), "n_train_per_relation": int(lre.n_train.iloc[0]),
           "n_relations": int(len(fr)), "n_test_facts": int(len(lre)),
           "faithfulness_overall": float(lre.faithful.mean()),
           "share_model_top_is_relation_mode": float((lre.model_top == lre.groupby("relation").model_top.transform(
               lambda x: x.mode().iloc[0])).mean()),
           "n_model_correct": int(lre.model_correct.sum()),
           "faithfulness_on_model_correct": float(lre[lre.model_correct].faithful.mean()) if lre.model_correct.any() else None,
           "faithfulness_per_relation": {k: [float(v), int(n)] for k, v, n in fr[["relation", "lre_faith", "n_test"]].itertuples(index=False)},
           "spearman_relation_mean_depth_vs_faith": {"n": int(len(rel)), "rho": float(spearmanr(rel.depth, rel.lre_faith).statistic)},
           "n_rows": int(len(d))}
    red = fit(d, Y, None)
    lf = fit(d, Y, "lre_faith", slope=False)
    out["partial_r2_lre_over_controls"] = lf["r2_marginal"] - red["r2_marginal"]
    out["lre_slope"] = lf["params"].get("lre_faith")
    out["lre_slope_p"] = lf["pvalues"].get("lre_faith")
    pr = partial_r2(d, Y, controls=CONTROLS + ["lre_faith"])
    out["partial_r2_cooc_over_controls_and_lre"] = pr["partial_r2"]
    out["cooc_slope_given_lre"] = pr["slope"]
    out["cooc_slope_p_given_lre"] = pr["slope_p"]
    return out


def fmt(x, nd=3):
    if x is None or (isinstance(x, float) and not np.isfinite(x)):
        return "MISSING"
    return f"{x:.{nd}f}" if isinstance(x, float) else str(x)


def report(out: dict, path: Path) -> None:
    J = out["json"]
    L = [f"# S4: transfer and controls (CPU, exploratory)\n",
         f"Source of every number: `{J}` (run_id `{out['run_id']}`). Plan: `notes/s4_plan.md`. "
         "The G1 pre-registered outcome was NO-GO and the human replied GO G1. Everything below except the "
         "TOST is exploratory. Counts: exact Pile phrase co-occurrence (EXACT) for every Pythia fit.\n",
         "## Transfer models\n",
         "| model | status |\n|---|---|",
         "| meta-llama/Llama-3.1-8B | MISSING: needs a T1 GPU (8B in bf16 does not fit in 15 GB RAM) |",
         "| Qwen/Qwen3-8B | MISSING: needs a T1 GPU (8B in bf16 does not fit in 15 GB RAM) |",
         "| google/gemma-3-4b-pt | MISSING: not run on CPU (estimated >100 h); needs a GPU |",
         f"\n## TOST: slope vs 0 within ±{out['tost_margin_per_decade']} depth per decade of cooc (prereg margin)\n",
         "| model | N rows | slope/decade | 90% CI (model SE) | TOST (model SE) | 90% CI (relation bootstrap) | TOST (bootstrap) |",
         "|---|---|---|---|---|---|---|"]
    for m in out["models"]:
        p, t, b = m["pooled"], m["pooled"]["tost"], m["pooled"].get("tost_bootstrap", {})
        bc = b.get("ci90_per_decade") or [None, None]
        L.append(f"| {m['model']} | {p['n_rows']} | {fmt(t['slope_per_decade'], 4)} | [{fmt(t['ci90_per_decade'][0], 4)}, {fmt(t['ci90_per_decade'][1], 4)}] | "
                 f"{'equivalent' if t['equivalent'] else 'not shown'} (p {fmt(t['p_tost'], 4)}) | [{fmt(bc[0], 4)}, {fmt(bc[1], 4)}] (n_boot {b.get('n_boot', 'MISSING')}, failed {b.get('n_failed', 'MISSING')}) | "
                 f"{('equivalent' if b['equivalent'] else 'not shown') if b else 'MISSING'} |")
    L.append("\n## Held-out relation families (headline measure causal_final, resolved rows)\n")
    for m in out["models"]:
        h = m["held_out_families"]
        L.append(f"**{m['model']}**\n\n| family | relations | N rows | slope [SE] | slope/decade 90% CI | TOST p | leave-family-out R² with / without cooc | ΔR² |")
        L.append("|---|---|---|---|---|---|---|---|")
        for f, r in h["per_family"].items():
            lo = h["leave_one_out"].get(f, {})
            t = r.get("tost", {})
            ci = t.get("ci90_per_decade") or [None, None]
            L.append(f"| {f} | {r['n_relations']} | {r['n_rows']} | {fmt(r.get('slope'), 4)} [{fmt(r.get('slope_se'), 4)}] | "
                     f"[{fmt(ci[0], 4)}, {fmt(ci[1], 4)}] | {fmt(t.get('p_tost'), 3)} | "
                     f"{fmt(lo.get('oof_r2_with_cooc'))} / {fmt(lo.get('oof_r2_without_cooc'))} | {fmt(lo.get('delta_r2'), 4)} |")
        L.append("")
    L.append("## Minimal pairs (same object first token, (cooc_hi+1)/(cooc_lo+1) >= 10, fact-level causal_final)\n")
    L.append("Difference = depth(high-cooc fact) minus depth(low-cooc fact); negative = high-cooc fact resolves earlier.\n")
    L.append("| model | pair set | N pairs | N facts | N object tokens | mean diff | median diff | share high shallower | Wilcoxon p (N non-zero) |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    for m in out["models"]:
        mp = m["minimal_pairs"]
        if "missing" in mp:
            L.append(f"| {m['model']} | all | MISSING: {mp['missing']} | | | | | | |")
            continue
        for k in ("all_pairs", "one_per_object_token", "same_relation"):
            r = mp[k]
            if "missing" in r:
                L.append(f"| {m['model']} | {k} | MISSING: {r['missing']} | | | | | | |")
                continue
            w = f"{fmt(r['wilcoxon_p'], 4)} ({r['wilcoxon_n_nonzero']})" if "wilcoxon_p" in r else r.get("wilcoxon")
            L.append(f"| {m['model']} | {k} | {r['n_pairs']} | {r['n_distinct_facts']} | {r['n_object_tokens']} | {fmt(r['mean_diff'], 4)} | "
                     f"{fmt(r['median_diff'], 4)} | {fmt(r['share_hi_shallower'])} | {w} |")
    L.append("\nPairs in `all_pairs` share facts and are not independent; `one_per_object_token` keeps the max-ratio pair per token.\n")
    sk = out.get("sanskriti")
    L.append("## SANSKRITI slice (pythia-1.4b, 300 items, Pile counts EXACT)\n")
    if not sk:
        L.append("MISSING: SANSKRITI depth run not available.\n")
    else:
        L.append("| N items | N rows | errors | correct@1 | resolved / censored rows | items with zero cooc | median cooc |\n|---|---|---|---|---|---|---|")
        L.append(f"| {sk['n_items']} | {sk['n_rows']} | {sk['n_errors']} | {fmt(sk['correct_at1_frac'])} | {sk['n_resolved_rows']} / {sk['n_censored_rows']} | "
                 f"{fmt(sk['zero_cooc_frac_items'])} | {fmt(sk['median_cooc_items'], 1)} |")
        f = sk["fit"]
        if isinstance(f, str):
            L.append(f"\nFit: {f}\n")
        else:
            t = f["tost"]
            L.append(f"\nFit ({f['model']}): N rows {f['n_rows']}, items {f['n_items']}; slope {fmt(f['slope'], 4)} (SE {fmt(f['slope_se'], 4)}, p {fmt(f['slope_p'], 4)}); "
                     f"slope/decade 90% CI [{fmt(t['ci90_per_decade'][0], 4)}, {fmt(t['ci90_per_decade'][1], 4)}], TOST p {fmt(t['p_tost'], 4)}. "
                     f"Item-level Spearman(cooc, depth) {fmt(f['spearman_item_level']['rho'])} (N {f['spearman_item_level']['n']}).\n")
        L.append(f"Depth run ids: {', '.join(sk['depth_run_ids'])}; count run ids: {', '.join(sk['count_run_ids'])}.\n")
    L.append("## LRE-faithfulness nested model (pythia-1.4b)\n")
    lr = out.get("lre")
    if not lr:
        L.append("MISSING: LRE run not available.\n")
    elif "error" in lr:
        L.append(f"MISSING: {lr['error']}\n")
    else:
        L.append(f"LRE at block {lr['layer']}, beta {lr['beta']}, {lr['n_train_per_relation']} train facts per relation; "
                 f"{lr['n_test_facts']} test facts over {lr['n_relations']} relations; overall faithfulness {fmt(lr['faithfulness_overall'])}. Run: {', '.join(lr['lre_run_ids'])}.\n")
        L.append(f"Share of test facts whose model top token equals its relation's most common top token: "
                 f"{fmt(lr['share_model_top_is_relation_mode'])} (high values make faithfulness easy). Faithfulness on "
                 f"facts the model gets right: {fmt(lr['faithfulness_on_model_correct'])} (N {lr['n_model_correct']}).\n")
        L.append("| quantity | value |\n|---|---|")
        L.append(f"| N rows in nested fit | {lr['n_rows']} |")
        L.append(f"| Spearman(relation mean depth, faithfulness), N relations | {fmt(lr['spearman_relation_mean_depth_vs_faith']['rho'])} ({lr['spearman_relation_mean_depth_vs_faith']['n']}) |")
        L.append(f"| partial R² of faithfulness over controls | {fmt(lr['partial_r2_lre_over_controls'], 4)} |")
        L.append(f"| faithfulness slope (p) | {fmt(lr['lre_slope'], 4)} ({fmt(lr['lre_slope_p'], 4)}) |")
        L.append(f"| partial R² of log cooc over controls + faithfulness | {fmt(lr['partial_r2_cooc_over_controls_and_lre'], 4)} |")
        L.append(f"| log cooc slope given faithfulness (p) | {fmt(lr['cooc_slope_given_lre'], 4)} ({fmt(lr['cooc_slope_p_given_lre'], 4)}) |")
    path.write_text("\n".join(L) + "\n")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--depth", nargs="+", required=True)
    ap.add_argument("--sanskriti", default=None)
    ap.add_argument("--min-ratio", type=float, default=10.0)
    ap.add_argument("--seed", type=int, default=1234)
    ap.add_argument("--n-boot", type=int, default=1000)
    ap.add_argument("--lre", default=None, help="LRE faithfulness parquet (depthlaw.depth.lre)")
    args = ap.parse_args(argv)
    seed_everything(args.seed)
    prereg = yaml.safe_load(open(ROOT / "configs" / "prereg.yaml"))
    margin = float(prereg["transfer_tost_margin_per_decade"])
    run_id = make_run_id("S4stats")
    log = RunLog("S4", run_id)
    facts = pd.read_parquet(ROOT / "data" / "facts.parquet")
    out = {"run_id": run_id, "tost_margin_per_decade": margin, "models": []}
    for p in args.depth:
        dep = pd.read_parquet(p)
        model = dep.model.iloc[0]
        log.log(event="model_start", depth=p, model=model)
        d = prep.build(dep, model)
        ix, label = prep.index_for(model)
        res = {"model": model, "depth_run_ids": sorted(dep.run_id.unique().tolist()), "count_index": f"{ix} ({label})"}
        r = d.dropna(subset=[Y, "log_cooc"] + CONTROLS)
        pr = partial_r2(r, Y)
        res["pooled"] = {"n_rows": int(len(r)), "slope": pr["slope"], "slope_se": pr["slope_se"],
                         "tost": tost(pr["slope"], pr["slope_se"], margin)}
        if args.n_boot:
            b = cluster_bootstrap(r, Y, n_boot=args.n_boot, seed=args.seed)
            lo, hi = (v * LN10 for v in b["slope_ci90"])
            res["pooled"]["tost_bootstrap"] = {"n_boot": b["n_boot"], "n_failed": b["n_failed"],
                                               "ci90_per_decade": [lo, hi], "margin_per_decade": margin,
                                               "equivalent": bool(lo > -margin and hi < margin)}
        res["held_out_families"] = held_out_families(r, margin)
        res["minimal_pairs"] = minimal_pairs(d, facts, args.min_ratio, args.seed)
        if args.lre and "1.4b" in model:
            try:
                out["lre"] = lre_nested(r, pd.read_parquet(args.lre))
            except Exception as e:  # noqa: BLE001
                out["lre"] = {"error": repr(e)[:300]}
        out["models"].append(res)
    if args.sanskriti:
        log.log(event="sanskriti_start", depth=args.sanskriti)
        out["sanskriti"] = sanskriti_slice(pd.read_parquet(args.sanskriti), margin)
    jpath = log.dir / "s4.json"
    out["json"] = str(jpath.relative_to(ROOT))
    jpath.write_text(json.dumps(out, indent=2, default=lambda o: o.item() if hasattr(o, "item") else str(o)))
    (log.dir / "meta.json").write_text(json.dumps(provenance(run_id, vars(args)), indent=2))
    report(out, ROOT / "reports" / "S4.md")
    log.log(event="done")
    print(jpath)


if __name__ == "__main__":
    main()
