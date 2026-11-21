# EXPLORATORY (post hoc, not preregistered) independent replication of E-depthvar B3/B6.
# Libraries: statsmodels MixedLM (REML, variance components) + own Henderson-III method-of-moments.
import json, sys, time
import pyarrow as pa; pa.set_cpu_count(1); pa.set_io_thread_count(1)
import numpy as np, pandas as pd
from scipy.stats import spearmanr
import statsmodels.api as sm
import warnings; warnings.filterwarnings("ignore")
R = "/home/user/depth-law/"
RUNS = {"pythia-1.4b": "results/S3b/S3b-pythia-1.4b-a7dfeb5-20261121T063528Z/depth.parquet",
        "pythia-2.8b": "results/S3b/S3b-pythia-2.8b-a7dfeb5-20261121T064110Z/depth.parquet",
        "OLMo-2-1124-7B": "results/S3b/S3b-OLMo-2-1124-7B-923945f-20261121T061237Z/depth.parquet"}
facts = pd.read_parquet(R + "data/facts_g1cpu.parquet", columns=["fact_id", "subject"], use_threads=False)
subj = dict(zip(facts.fact_id, facts.subject))

def depths(curves):
    d1, d4 = [], []
    for c in curves:
        lp = np.asarray(c, dtype=float); L = len(lp)
        ok = lp >= np.log(0.5) + lp[-1]
        bad = np.where(~ok)[0]
        ls = 0 if len(bad) == 0 else bad[-1] + 1
        d1.append((ls + 1) / L)
        d4.append(1 - np.mean(np.minimum(1.0, np.exp(lp - lp[-1]))))
    return np.mean(d1), np.mean(d4)

data = {}
for m, p in RUNS.items():
    d = pd.read_parquet(R + p, columns=["fact_id", "template_id", "relation", "correct_at1",
                                        "final_logprob_curves", "half_prob_depth", "n_layers"], use_threads=False)
    v = np.array([depths(c) for c in d.final_logprob_curves])
    d["D1"], d["D4"] = v[:, 0], v[:, 1]
    d = d.drop(columns="final_logprob_curves")
    diff = np.abs(d.D1 - d.half_prob_depth)
    print(m, "rows", len(d), "L", d.n_layers.unique(), "max|D1-half_prob_depth|", diff.max(),
          "n_mismatch>1e-9", int((diff > 1e-9).sum()), flush=True)
    d["subject"] = d.fact_id.map(subj)
    d["rt"] = d.relation + ":" + d.template_id.astype(str)
    data[m] = d

def proj(X):
    Q, Rr = np.linalg.qr(X)
    keep = np.abs(np.diag(Rr)) > 1e-8 * np.abs(np.diag(Rr)).max()
    # rank-revealing via SVD for safety
    U, s, _ = np.linalg.svd(X, full_matrices=False)
    U = U[:, s > 1e-8 * s.max()]
    return U @ U.T

def dummies(x):
    return pd.get_dummies(x).to_numpy(dtype=float)

def anova_h3(df, y):
    """Henderson method III with sequential SS: relation, rt|rel, fact|rt; residual. fact = fact+subject."""
    n = len(df); one = np.ones((n, 1))
    Zr, Zt, Zf = dummies(df.relation), dummies(df.rt), dummies(df.fact_id)
    P0 = proj(one); P1 = proj(np.hstack([one, Zr])); P2 = proj(np.hstack([one, Zt]))
    P3 = proj(np.hstack([one, Zt, Zf])); I = np.eye(n)
    As = [P1 - P0, P2 - P1, P3 - P2, I - P3]
    Zs = [Zr, Zt, Zf, None]
    M = np.zeros((4, 4)); ss = np.zeros(4)
    for i, A in enumerate(As):
        ss[i] = y @ A @ y
        for k, Z in enumerate(Zs):
            M[i, k] = np.trace(A) if Z is None else np.trace(Z.T @ A @ Z)
    sig = np.linalg.solve(M, ss)
    raw = dict(zip(["relation", "template_main", "fact_plus_subject", "residual"], sig))
    sig = np.clip(sig, 0, None)
    tot = sig.sum()
    return {k: s / tot for k, s in zip(["relation", "template_main", "fact_plus_subject", "residual"], sig)}, raw

def mixedlm(df, y, with_subject=True):
    dd = df.assign(y=y, g=1)
    vc = {"relation": "0+C(relation)", "rt": "0+C(rt)", "fact": "0+C(fact_id)"}
    if with_subject: vc["subject"] = "0+C(subject)"
    mod = sm.MixedLM.from_formula("y ~ 1", groups="g", vc_formula=vc, re_formula="0", data=dd)
    best = None
    for meth in (["lbfgs"], ["powell", "lbfgs"], ["bfgs"], ["nm", "lbfgs"]):
        try:
            r = mod.fit(reml=True, method=meth, maxiter=2000)
        except Exception as e:
            print("  fit fail", meth, e, flush=True); continue
        if best is None or r.llf > best.llf + 1e-9: best = r
    r = best
    comp = dict(zip(mod.exog_vc.names, r.vcomp)); comp["residual"] = r.scale
    tot = sum(comp.values())
    sh = {"relation": comp["relation"] / tot, "template_main": comp["rt"] / tot,
          "fact_plus_subject": (comp["fact"] + comp.get("subject", 0.0)) / tot,
          "residual": comp["residual"] / tot}
    return sh, comp, r.llf, r.converged

out = {"B3": {}, "B6": {}}
for m, d in data.items():
    corr = d[d.correct_at1].copy()
    nc = corr.groupby("fact_id").size()
    all3 = corr[corr.fact_id.isin(nc[nc == 3].index)].copy()
    for D in ("D1", "D4"):
        for sname, s in (("correct", corr), ("all3", all3)):
            key = f"{m}|{D}|{sname}"
            t = time.time()
            y = s[D].to_numpy()
            sh_ml, comp, llf, conv = mixedlm(s, y, True)
            sh_ml2, comp2, llf2, conv2 = mixedlm(s, y, False)
            sh_an, raw_an = anova_h3(s, y)
            out["B3"][key] = {"n_cells": len(s), "n_facts": s.fact_id.nunique(),
                              "n_subjects": s.subject.nunique(),
                              "mixedlm_reml": sh_ml, "mixedlm_reml_raw": comp, "mixedlm_llf": llf, "converged": bool(conv),
                              "mixedlm_reml_nosubject": sh_ml2, "mixedlm_nosubject_llf": llf2,
                              "anova_h3": sh_an, "anova_h3_raw_unclipped": raw_an}
            print(key, len(s), s.fact_id.nunique(), {k: round(v, 4) for k, v in sh_ml.items()},
                  "| noSubj", {k: round(v, 4) for k, v in sh_ml2.items()},
                  "| ANOVA", {k: round(v, 4) for k, v in sh_an.items()}, f"{time.time()-t:.1f}s", flush=True)

# B6
ms = list(RUNS)
pairs = [(ms[0], ms[1]), (ms[0], ms[2]), (ms[1], ms[2])]
ncorr = {m: d.groupby("fact_id").correct_at1.sum() for m, d in data.items()}
strict = set.intersection(*[set(ncorr[m][ncorr[m] == 3].index) for m in ms])
anyc = set.intersection(*[set(ncorr[m][ncorr[m] >= 1].index) for m in ms])
rel = data[ms[0]].groupby("fact_id").relation.first()
for D in ("D1", "D4"):
    for sname, S in (("strict_all3", strict), ("any_correct", anyc)):
        fm = {}
        for m in ms:
            d = data[m]; d = d[d.correct_at1 & d.fact_id.isin(S)]
            f = d.groupby("fact_id")[D].mean().sort_index()
            fw = f - f.groupby(rel.reindex(f.index)).transform("mean")
            fm[m] = (f, fw)
        for a, b in pairs:
            idx = sorted(S)
            r1 = spearmanr(fm[a][0].loc[idx], fm[b][0].loc[idx]).statistic
            r2 = spearmanr(fm[a][1].loc[idx], fm[b][1].loc[idx]).statistic
            key = f"{D}|{sname}|{a} vs {b}"
            out["B6"][key] = {"n_facts": len(idx), "rho": float(r1), "rho_within_relation": float(r2)}
            print(key, len(idx), round(r1, 4), round(r2, 4), flush=True)
json.dump(out, open(R + "scratch/replicate_edv/rep_out.json", "w"), indent=1, default=float)
