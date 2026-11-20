"""Summaries for the causal_final audit (EXPLORATORY).

Live audits (results/AUDIT/<run>/carriers.parquet, layers.parquet) and, for pythia-1.4b, the
same 200 random facts read from the S3 fp32 rows (no new model run). Writes summary.json in
results/AUDITsum/<run_id>/.
"""
from __future__ import annotations

import argparse
import json

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from depthlaw.depth.audit import audit_facts
from depthlaw.depth.common import first_stable_layer
from depthlaw.io import ROOT, RunLog, make_run_id, provenance

S3_14B = "S3-pythia-1.4b-b9a353d-20261108T064941Z"


def two_by_two(correct: pd.Series, resolved: pd.Series) -> dict:
    c, r = correct.astype(bool), resolved.astype(bool)
    return {"correct_resolved": int((c & r).sum()), "correct_censored": int((c & ~r).sum()),
            "wrong_resolved": int((~c & r).sum()), "wrong_censored": int((~c & ~r).sum()), "n": int(len(c))}


def live_summary(run: str) -> dict:
    d = ROOT / "results" / "AUDIT" / run
    car = pd.read_parquet(d / "carriers.parquet")
    lay = pd.read_parquet(d / "layers.parquet")
    L = int(lay.layer.max()) + 1
    out = {"run_id": run, "n_layers": L, "n_fact_templates": int(car.groupby(["fact_id", "template_id"]).ngroups),
           "n_facts": int(car.fact_id.nunique())}
    out["two_by_two_per_carrier"] = {}
    for s in ["hand", "random", "all"]:
        q = car if s == "all" else car[car.set == s]
        out["two_by_two_per_carrier"][s] = {int(c): two_by_two(g.correct_at1, g.resolved) for c, g in q.groupby("carrier")}
        ft = q.drop_duplicates(["fact_id", "template_id"])
        out.setdefault("two_by_two_all_carriers", {})[s] = two_by_two(ft.correct_at1, ft.causal_final.notna())
    out["last_layer_identity"] = {
        "max_abs_logit_diff": float(car.lastlayer_max_abs_logit_diff.max()),
        "median_abs_logit_diff": float(car.lastlayer_max_abs_logit_diff.median()),
        "share_rank_equal_src": float(car.lastlayer_rank_equals_src.mean()), "n": int(len(car))}
    w = car.dropna(subset=["write_final_dpos"])
    out["write_position_checks"] = {
        "n_checked": int(len(w)),
        "final_write_max_abs_diff_at_pos": float(w.write_final_dpos.max()),
        "final_write_max_abs_diff_other_pos": float(w.write_final_dother.max()),
        "subj_write_max_abs_diff_at_pos": float(w.write_subj_dpos.max()),
        "subj_write_max_abs_diff_other_pos": float(w.write_subj_dother.max()),
        "carrier_write_tokens": sorted(set(zip(car.carrier.astype(int), car.write_tok_str, car.placeholder_tok_str))),
    }
    ft = car.drop_duplicates(["fact_id", "template_id"])
    out["source_positions"] = {"share_subject_last_token_ok": float(ft.subj_pos_ok.mean()),
                               "share_subject_prefix_ok": float(ft.subj_prefix_ok.mean()),
                               "n": int(len(ft)),
                               "failures": ft[~ft.subj_pos_ok][["fact_id", "subject", "subj_last_tok_str"]].head(10).to_dict("records"),
                               "examples": ft[["subject", "subj_last_tok_str", "src_final_tok_str"]].head(8).to_dict("records")}
    ca = car.groupby("carrier").agg(share_obj_rank1=("carrier_alone_obj_rank", lambda s: float((s == 1).mean())),
                                    median_obj_rank=("carrier_alone_obj_rank", "median"),
                                    share_obj_top10=("carrier_alone_obj_rank", lambda s: float((s <= 10).mean())),
                                    n=("carrier_alone_obj_rank", "size"))
    out["carrier_alone"] = {int(k): v for k, v in ca.to_dict("index").items()}
    out["carrier_alone_top1_tokens"] = {int(c): g.carrier_alone_top1_str.value_counts().head(3).to_dict()
                                        for c, g in car.groupby("carrier")}
    # per-layer: patched object rank vs unpatched readouts (means over fact x template x carrier)
    lay["patched_rank1"] = lay.patched_obj_rank == 1
    lay["patched_top1_is_src_top1"] = lay.patched_top1 == lay.unpatched_src_top1
    lay["ll_rank1"] = lay.unpatched_ll_obj_rank == 1
    pl = lay.groupby(["correct_at1", "layer"]).agg(
        share_patched_obj_rank1=("patched_rank1", "mean"), share_patched_top1_eq_src_top1=("patched_top1_is_src_top1", "mean"),
        share_unpatched_ll_obj_rank1=("ll_rank1", "mean"), median_patched_obj_rank=("patched_obj_rank", "median"),
        n=("layer", "size")).reset_index()
    out["per_layer"] = pl.to_dict("records")
    # proposed correctness-free measure on the audit sample
    hg = ft[ft.set == "random"]
    out["half_gain_depth"] = {
        "share_defined_all": float(hg.half_gain_depth.notna().mean()),
        "share_defined_correct": float(hg[hg.correct_at1].half_gain_depth.notna().mean()) if hg.correct_at1.any() else None,
        "share_defined_wrong": float(hg[~hg.correct_at1].half_gain_depth.notna().mean()),
        "n": int(len(hg)), "n_correct": int(hg.correct_at1.sum()),
        "median_correct": float(hg[hg.correct_at1].half_gain_depth.median()) if hg.correct_at1.any() else None,
        "median_wrong": float(hg[~hg.correct_at1].half_gain_depth.median()),
    }
    both = hg.dropna(subset=["half_gain_depth", "causal_final"])
    out["half_gain_depth"]["spearman_with_causal_final"] = (
        {"rho": float(spearmanr(both.half_gain_depth, both.causal_final).statistic), "n": int(len(both))}
        if len(both) > 10 else {"rho": None, "n": int(len(both))})
    pc = car[car.set == "random"]
    out["half_gain_depth"]["per_carrier_share_defined"] = {int(c): float(g.half_gain_depth.notna().mean())
                                                           for c, g in pc.groupby("carrier")}
    # rows resolved but not correct@1: rank_of counts strictly greater logits, argmax breaks ties
    wr = car[(~car.correct_at1) & car.resolved]
    out["resolved_not_correct"] = {"n_rows": int(len(wr)), "src_obj_rank_values": sorted(set(wr.src_obj_rank.astype(int))),
                                   "facts": wr[["fact_id", "object", "src_top1_str"]].drop_duplicates().to_dict("records")}
    # variant B: probability half-max depth = first l with p_patch(l') >= 0.5 * p_patch(L-1) for all l' >= l
    def pdepth(g):
        p = np.exp(g.sort_values("layer").patched_obj_logprob.to_numpy())
        l = first_stable_layer(list(p >= 0.5 * p[-1]))
        return np.nan if l is None else (l + 1) / L
    ph = lay.groupby(["fact_id", "template_id", "carrier"]).apply(pdepth).rename("prob_half").reset_index()
    m = car.merge(ph, on=["fact_id", "template_id", "carrier"])
    r = m[m.set == "random"]
    ftr = r.groupby(["fact_id", "template_id"]).agg(prob_half=("prob_half", "mean"), hg=("half_gain_depth", "first"),
                                                    cf=("causal_final", "first"), is_corr=("correct_at1", "first"),
                                                    lp=("src_obj_logprob", "first")).reset_index()
    b = ftr.dropna(subset=["cf"])
    def sp(a, c):
        q = pd.concat([a, c], axis=1).dropna()
        return {"rho": float(spearmanr(q.iloc[:, 0], q.iloc[:, 1]).statistic), "n": int(len(q))} if len(q) > 10 else None
    out["prob_half_depth"] = {
        "share_defined": float(ftr.prob_half.notna().mean()), "n": int(len(ftr)),
        "median_correct": float(ftr[ftr.is_corr].prob_half.median()) if ftr.is_corr.any() else None,
        "median_wrong": float(ftr[~ftr.is_corr].prob_half.median()),
        "spearman_with_causal_final_resolved": sp(b.prob_half, b.cf),
        "spearman_with_src_obj_logprob": sp(ftr.prob_half, ftr.lp),
        "quantiles": {q: float(ftr.prob_half.quantile(q)) for q in (0.1, 0.25, 0.5, 0.75, 0.9)}}
    out["half_gain_depth"]["spearman_with_src_obj_logprob"] = sp(ftr.hg, ftr.lp)
    out["half_gain_depth"]["quantiles"] = {q: float(ftr.hg.quantile(q)) for q in (0.1, 0.25, 0.5, 0.75, 0.9)}
    return out


def s3_summary(n_random: int, seed: int) -> dict:
    """pythia-1.4b audit from the S3 fp32 rows for the same 200 random facts."""
    facts = audit_facts(n_random, seed)
    ids = set(facts[facts.set == "random"].fact_id)
    d = pd.read_parquet(ROOT / "results" / "S3" / S3_14B / "depth.parquet")
    d = d[d.fact_id.isin(ids)]
    L = int(d.n_layers.iloc[0])
    out = {"s3_run_id": S3_14B, "n_facts": int(d.fact_id.nunique()), "n_rows": int(len(d)), "n_layers": L}
    per = {}
    rows = []
    for r in d.itertuples():
        for c, curve in enumerate(r.final_rank_curves):
            curve = list(curve)
            st = first_stable_layer([x == 1 for x in curve])
            rows.append({"carrier": c, "correct_at1": bool(r.correct_at1), "resolved": st is not None,
                         "last_rank1": curve[-1] == 1, "stored_per_carrier_ok": (st is None) == bool(np.isnan(r.causal_final_per_carrier[c])),
                         **{f"rank_l{l}": curve[l] for l in range(L)},
                         **{f"ll_l{l}": r.logit_lens_ranks[l] for l in range(L)}})
    q = pd.DataFrame(rows)
    for c, g in q.groupby("carrier"):
        per[int(c)] = two_by_two(g.correct_at1, g.resolved)
    out["two_by_two_per_carrier"] = per
    out["two_by_two_all_carriers"] = two_by_two(d.correct_at1, d.causal_final.notna())
    out["last_layer_rank1_equals_correct_share"] = float((q.last_rank1 == q.correct_at1).mean())
    out["recomputed_depth_matches_stored_share"] = float(q.stored_per_carrier_ok.mean())
    pl = []
    for corr, g in q.groupby("correct_at1"):
        for l in range(L):
            pl.append({"correct_at1": bool(corr), "layer": l, "share_patched_obj_rank1": float((g[f"rank_l{l}"] == 1).mean()),
                       "median_patched_obj_rank": float(g[f"rank_l{l}"].median()),
                       "share_unpatched_ll_obj_rank1": float((g[f"ll_l{l}"] == 1).mean()), "n": int(len(g))})
    out["per_layer"] = pl
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", nargs="*", default=[], help="AUDIT run dirs (names)")
    ap.add_argument("--n-random", type=int, default=200)
    ap.add_argument("--seed", type=int, default=1234)
    args = ap.parse_args(argv)
    run_id = make_run_id("AUDITsum")
    log = RunLog("AUDITsum", run_id)
    (log.dir / "meta.json").write_text(json.dumps(provenance(run_id, vars(args)), indent=2))
    out = {"run_id": run_id, "label": "EXPLORATORY", "live": {r: live_summary(r) for r in args.live},
           "pythia-1.4b_from_S3": s3_summary(args.n_random, args.seed)}
    (log.dir / "summary.json").write_text(json.dumps(out, indent=2, default=str))
    print(log.dir / "summary.json")


if __name__ == "__main__":
    main()
