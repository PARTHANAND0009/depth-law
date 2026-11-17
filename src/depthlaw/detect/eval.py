"""S8 detector evaluation (notes/s8_plan.md). Reads only results/ and data/; writes
results/S8/<run_id>/{fact_scores.parquet, auroc.csv, summary.json, log.jsonl, meta.json}."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.covariance import LedoitWolf
from sklearn.ensemble import AdaBoostClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from depthlaw.detect.features import FEATS, Calibration, fact_level
from depthlaw.io import ROOT, RunLog, make_run_id, provenance, seed_everything

SEED = 1234
N_BOOT = 1000
BASE = "EleutherAI/pythia-1.4b"
CLEAN_S3 = "results/S3/S3-pythia-1.4b-b9a353d-20261108T064941Z/depth.parquet"
METHOD = {"rome_single": "rome", "memit100": "memit", "memit1000": "memit", "alphaedit100": "alphaedit",
          "alphaedit1000": "alphaedit", "lora50": "lora", "lora200": "lora", "lora1000": "lora",
          "synthdoc50": "synthdoc", "a1_layer_match": "a1", "a2_depth_reg": "a2", "a3_freq_spoof": "a3"}
FAMILY = {"rome": "locate", "memit": "locate", "alphaedit": "locate", "lora": "finetune", "synthdoc": "finetune",
          "a1": "adaptive", "a2": "adaptive", "a3": "adaptive"}
G3_MODELS = ["rome_single", "memit100", "memit1000"]
SUP_FEATS = FEATS + ["causal_final_f", "ll_depth_f", "obj_first_logprob", "margin"]


def auroc_ci(y: np.ndarray, s: np.ndarray, rng: np.random.Generator, n_boot: int = N_BOOT):
    ok = ~np.isnan(s)
    y, s = y[ok], s[ok]
    npos, nneg = int(y.sum()), int((1 - y).sum())
    if npos == 0 or nneg == 0:
        return {"n_pos": npos, "n_neg": nneg, "auroc": np.nan, "lo": np.nan, "hi": np.nan}
    a = roc_auc_score(y, s)
    pos, neg = s[y == 1], s[y == 0]
    bs = []
    for _ in range(n_boot):
        p = rng.choice(pos, len(pos))
        q = rng.choice(neg, len(neg))
        bs.append(roc_auc_score(np.r_[np.ones(len(p)), np.zeros(len(q))], np.r_[p, q]))
    return {"n_pos": npos, "n_neg": nneg, "auroc": float(a), "lo": float(np.percentile(bs, 2.5)),
            "hi": float(np.percentile(bs, 97.5))}


def load_counts() -> tuple[pd.Series, pd.Series, dict]:
    ce = pd.read_parquet(ROOT / "data" / "counts_exact.parquet").set_index("fact_id")
    cf = pd.read_parquet(ROOT / "data" / "s7_cf_counts_exact.parquet").set_index("fact_id")
    prov = {"counts_exact": str(ce.run_id.iloc[0]), "s7_cf_counts_exact": str(cf.run_id.iloc[0]),
            "index": "v4_piletrain_llama", "label": "EXACT"}
    return ce.exact_piletrain, cf.exact_piletrain, prov


def model_rows(s7_dir: Path, man: dict, log, extra: list[str] = ()) -> tuple[pd.DataFrame, dict]:
    """extra: 'single:<name>:<depth.parquet>' (rome-like rows with labels) or
    'batch:<name>:<depth.parquet>:<eval_table.parquet>' (run_depth output + S7-format eval table)."""
    parts, src = [], {}
    for e in extra:
        kind, name, *paths = e.split(":")
        d = pd.read_parquet(ROOT / paths[0])
        if kind == "batch":
            lab = pd.read_parquet(ROOT / paths[1])[["fact_id", "edited", "rtype"]]
            d = d.merge(lab, on="fact_id", how="left")
            d["edit_fact_id"] = ""
        d["model_id"] = name
        src[name] = str(d.run_id.iloc[0])
        parts.append(d)
    for m in man["models"]:
        mid = m["model_id"]
        if not m.get("kept"):
            continue
        ev = sorted((ROOT / "results" / "S7eval").glob(f"S7eval-{mid}-*/depth.parquet"))
        if not ev:
            log.log(event="missing_eval", model_id=mid)
            src[mid] = "MISSING: no S7eval depth.parquet"
            continue
        d = pd.read_parquet(ev[0])
        lab = pd.read_parquet(ROOT / "data" / "zoo" / f"{mid}_eval.parquet")[["fact_id", "edited", "rtype"]]
        d = d.merge(lab, on="fact_id", how="left")
        d["model_id"], d["edit_fact_id"] = mid, ""
        src[mid] = str(d.run_id.iloc[0])
        parts.append(d)
    r = pd.read_parquet(s7_dir / "rome" / "depth.parquet")
    r["model_id"] = "rome_single"
    src["rome_single"] = str(r.run_id.iloc[0])
    parts.append(r)
    cols = ["model_id", "edit_fact_id", "fact_id", "template_id", "relation", "edited", "rtype", "correct_at1",
            "obj_first_logprob", "obj_logprob", "margin", "n_obj_tokens", "logit_lens_ranks", "logit_lens_prob",
            "logit_lens_depth", "causal_final"]
    out = pd.concat([p[cols] for p in parts], ignore_index=True)
    out["rtype"] = out.rtype.fillna("control")
    return out, src


def attach_x(d: pd.DataFrame, ce: pd.Series, cf: pd.Series) -> pd.DataFrame:
    is_cf = d.edited.astype(bool) & (d.rtype == "counterfactual")
    c = np.where(is_cf, d.fact_id.map(cf), d.fact_id.map(ce))
    return d.assign(count=c, x=np.log1p(c.astype(float)))


def run_supervised(fl: pd.DataFrame, feats, make_clf, rng, tag: str) -> list[dict]:
    rows = []
    X = fl[feats].values
    y = fl.label.values
    nonadapt = fl.family.values != "adaptive"   # adaptive attacks are never used for training
    # held-out method
    for meth in sorted(fl.method.unique()):
        tr, te = (fl.method.values != meth) & nonadapt, fl.method.values == meth
        if y[tr].min() == y[tr].max() or y[te].min() == y[te].max():
            continue
        clf = make_clf().fit(X[tr], y[tr])
        s = clf.predict_proba(X[te])[:, 1]
        rows.append({"score": tag, "protocol": "heldout_method", "group": meth, **auroc_ci(y[te], s, rng)})
    for fam in sorted(fl.family.unique()):
        tr, te = (fl.family.values != fam) & nonadapt, fl.family.values == fam
        clf = make_clf().fit(X[tr], y[tr])
        s = clf.predict_proba(X[te])[:, 1]
        rows.append({"score": tag, "protocol": "heldout_family", "group": fam, **auroc_ci(y[te], s, rng)})
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--lcf", default=None, help="results/S8/<lcf run>/lcf.parquet")
    ap.add_argument("--extra", nargs="*", default=[], help="S9 attack rows, see model_rows")
    ap.add_argument("--stage", default="S8")
    args = ap.parse_args(argv)
    seed_everything(SEED)
    rng = np.random.default_rng(SEED)
    run_id = make_run_id(args.stage, BASE)
    log = RunLog(args.stage, run_id)
    s7_dir = sorted((ROOT / "results" / "S7").glob("S7-pythia-1.4b-*"))[0]
    man = json.loads((ROOT / "zoo" / "manifest.json").read_text())
    req = json.loads((ROOT / "data" / "splits" / "s7_requests.json").read_text())
    controls = set(req["controls"])
    ce, cf, cprov = load_counts()

    # ---- clean calibration (clean model only)
    clean = pd.read_parquet(ROOT / CLEAN_S3)
    calib = clean[~clean.fact_id.isin(controls)].copy()
    calib = calib.assign(count=calib.fact_id.map(ce))
    calib = calib.assign(x=np.log1p(calib["count"].astype(float)))
    calib = calib[calib.x.notna()]
    cal = Calibration(calib)
    cal_rows = cal.row_features(calib).assign(model_id="clean", edit_fact_id="")
    cal_fl = fact_level(cal_rows, ["model_id", "edit_fact_id", "fact_id"])
    lw = LedoitWolf().fit(cal_fl[FEATS].values)
    mu, prec = lw.location_, lw.precision_
    log.log(event="calibration", **cal.n, slopes=cal.slopes(), lw_shrinkage=float(lw.shrinkage_))

    # ---- audited models
    rows, src = model_rows(s7_dir, man, log, args.extra)
    rows = attach_x(rows, ce, cf)
    n_nox = int(rows.x.isna().sum())
    rows = rows[rows.x.notna()]
    feats = cal.row_features(rows)
    keys = ["model_id", "edit_fact_id", "fact_id"]
    fl = fact_level(feats, keys)
    lab = feats.groupby(keys)[["edited", "rtype"]].first().reset_index()
    fl = fl.merge(lab, on=keys)
    fl["label"] = fl.edited.astype(int)
    fl["method"] = fl.model_id.map(METHOD)
    fl["family"] = fl.method.map(FAMILY)
    Z = fl[FEATS].values - mu
    fl["s_maha"] = np.sqrt(np.einsum("ij,jk,ik->i", Z, prec, Z))
    fl["s_abs_r_causal"] = fl.r_causal.abs()
    fl["s_r_causal"] = fl.r_causal
    fl["s_abs_r_ll"] = fl.r_ll.abs()
    fl["s_r_conf"] = fl.r_conf
    fl["s_d_profile"] = fl.d_profile
    fl["s_conf"] = fl.obj_first_logprob
    fl["s_perp"] = fl.obj_logprob / fl.n_obj_tokens
    fl["s_conf_rarity"] = np.exp(fl.obj_first_logprob) / (1.0 + fl.x)
    if args.lcf:
        lcf = pd.read_parquet(args.lcf)[["model_id", "edit_fact_id", "fact_id", "lcf", "run_id"]]
        lcf["edit_fact_id"] = lcf.edit_fact_id.fillna("")
        src["lcf"] = str(lcf.run_id.iloc[0])
        fl = fl.merge(lcf.drop(columns="run_id").rename(columns={"lcf": "s_lcf"}), on=keys, how="left")
    else:
        fl["s_lcf"] = np.nan
        src["lcf"] = "MISSING: LCF hidden-state pass not run"
    fl["primary"] = fl.correct_t0.fillna(False).astype(bool)
    fl["run_id"] = run_id
    fl.drop(columns=["ll_prob_curve"]).to_parquet(log.dir / "fact_scores.parquet", index=False)

    # ---- unsupervised + baseline AUROCs
    scores = ["s_maha", "s_abs_r_causal", "s_r_causal", "s_abs_r_ll", "s_r_conf", "s_d_profile",
              "s_conf", "s_perp", "s_conf_rarity", "s_lcf"]
    groups = [("model", m, fl.model_id == m) for m in sorted(fl.model_id.unique())]
    groups += [("method", m, fl.method == m) for m in sorted(fl.method.unique())]
    groups += [("family", f, fl.family == f) for f in sorted(fl.family.unique())]
    groups += [("g3_pool", "+".join(G3_MODELS), fl.model_id.isin(G3_MODELS))]
    res = []
    for pop in ["primary", "secondary"]:
        pm = fl.primary if pop == "primary" else pd.Series(True, index=fl.index)
        for gk, gv, gm in groups:
            sub = fl[gm & pm]
            for sc in scores:
                res.append({"population": pop, "level": gk, "group": gv, "score": sc, "protocol": "unsupervised",
                            **auroc_ci(sub.label.values, sub[sc].values.astype(float), rng)})

    # ---- supervised (primary population)
    P = fl[fl.primary].reset_index(drop=True)
    lr = lambda: make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000))  # noqa: E731
    ada = lambda: AdaBoostClassifier(n_estimators=200, random_state=SEED)  # noqa: E731
    sup = []
    # in-distribution upper bound: 5-fold CV within each model
    for mid in sorted(P.model_id.unique()):
        sub = P[P.model_id == mid]
        y = sub.label.values
        if min(y.sum(), (1 - y).sum()) < 5:
            sup.append({"score": "sup_lr", "protocol": "cv5_within_model", "group": mid,
                        **auroc_ci(y, np.full(len(y), np.nan), rng)})
            continue
        s = np.zeros(len(y))
        for tr, te in StratifiedKFold(5, shuffle=True, random_state=SEED).split(sub, y):
            s[te] = lr().fit(sub[SUP_FEATS].values[tr], y[tr]).predict_proba(sub[SUP_FEATS].values[te])[:, 1]
        sup.append({"score": "sup_lr", "protocol": "cv5_within_model", "group": mid, **auroc_ci(y, s, rng)})
    sup += run_supervised(P, SUP_FEATS, lr, rng, "sup_lr")
    P_ada = P.copy()
    curves = fl.loc[fl.primary, "ll_prob_curve"].reset_index(drop=True)
    Xa = np.column_stack([np.stack(curves.values), P.obj_first_logprob.values])
    for c in range(Xa.shape[1]):
        P_ada[f"a{c}"] = Xa[:, c]
    sup += run_supervised(P_ada, [f"a{c}" for c in range(Xa.shape[1])], ada, rng, "youssef_adaboost")
    for r in sup:
        r["population"] = "primary"
        r["level"] = r["protocol"]
    res += sup
    out = pd.DataFrame(res)
    out["run_id"] = run_id
    out.to_csv(log.dir / "auroc.csv", index=False)

    g3 = out[(out.population == "primary") & (out.level == "g3_pool") & (out.score == "s_maha")].iloc[0]
    summ = {"run_id": run_id, "inputs": src, "counts": cprov, "n_rows_without_count": n_nox,
            "calibration": {**cal.n, "slopes": cal.slopes(), "lw_shrinkage": float(lw.shrinkage_),
                            "source": CLEAN_S3},
            "n_facts": {m: {"pos": int(((fl.model_id == m) & (fl.label == 1)).sum()),
                            "neg": int(((fl.model_id == m) & (fl.label == 0)).sum()),
                            "pos_primary": int(((fl.model_id == m) & (fl.label == 1) & fl.primary).sum()),
                            "neg_primary": int(((fl.model_id == m) & (fl.label == 0) & fl.primary).sum())}
                        for m in sorted(fl.model_id.unique())},
            "g3": {"metric": "s_maha fact-level AUROC, primary population, pooled " + "+".join(G3_MODELS),
                   "auroc": g3.auroc, "ci": [g3.lo, g3.hi], "n_pos": int(g3.n_pos), "n_neg": int(g3.n_neg),
                   "threshold": 0.8, "pass": bool(g3.auroc >= 0.8)},
            "model_level_auroc": "MISSING: one clean model of this architecture",
            "two_hop_gap": "MISSING: no two-hop prompts built (CPU budget)"}
    (log.dir / "summary.json").write_text(json.dumps(summ, indent=2, default=float))
    (log.dir / "meta.json").write_text(json.dumps(provenance(run_id, {"seed": SEED, "n_boot": N_BOOT}, BASE, "main"),
                                                  indent=2))
    log.log(event="done", g3=summ["g3"])
    print(json.dumps(summ["g3"], indent=1, default=float))
    print(log.dir)


if __name__ == "__main__":
    main()
