# EXPLORATORY (post hoc, not preregistered) independent replication of E-depthvar B3/B6.
# Stage 1 (fast): D1/D4, D1 check, Henderson-III ANOVA shares, B6 rho. Stage 2: statsmodels MixedLM REML.
# usage: rep2.py stage1 | rep2.py ml <key-substring> [sparse] [method]
import json, sys, time, os
import pyarrow as pa; pa.set_cpu_count(1); pa.set_io_thread_count(1)
import numpy as np, pandas as pd
import warnings; warnings.filterwarnings("ignore")
R = "/home/user/depth-law/"; OUT = R + "scratch/replicate_edv/"
RUNS = {"pythia-1.4b": "results/S3b/S3b-pythia-1.4b-a7dfeb5-20261121T063528Z/depth.parquet",
        "pythia-2.8b": "results/S3b/S3b-pythia-2.8b-a7dfeb5-20261121T064110Z/depth.parquet",
        "OLMo-2-1124-7B": "results/S3b/S3b-OLMo-2-1124-7B-923945f-20261121T061237Z/depth.parquet"}

def depths(curves):
    d1, d4 = [], []
    for c in curves:
        lp = np.asarray(c, dtype=float); L = len(lp)
        bad = np.where(~(lp >= np.log(0.5) + lp[-1]))[0]
        ls = 0 if len(bad) == 0 else bad[-1] + 1
        d1.append((ls + 1) / L)
        d4.append(1 - np.mean(np.minimum(1.0, np.exp(lp - lp[-1]))))
    return np.mean(d1), np.mean(d4)

def load():
    cache = OUT + "cells.parquet"
    if os.path.exists(cache):
        return pd.read_parquet(cache, use_threads=False)
    facts = pd.read_parquet(R + "data/facts_g1cpu.parquet", columns=["fact_id", "subject"], use_threads=False)
    subj = dict(zip(facts.fact_id, facts.subject)); parts = []
    for m, p in RUNS.items():
        d = pd.read_parquet(R + p, columns=["fact_id", "template_id", "relation", "correct_at1",
                            "final_logprob_curves", "half_prob_depth", "n_layers"], use_threads=False)
        v = np.array([depths(c) for c in d.final_logprob_curves])
        d["D1"], d["D4"] = v[:, 0], v[:, 1]
        d = d.drop(columns="final_logprob_curves")
        diff = np.abs(d.D1 - d.half_prob_depth)
        print(m, "rows", len(d), "L", d.n_layers.unique(), "max|D1-half_prob_depth|", diff.max(),
              "n>1e-9", int((diff > 1e-9).sum()), flush=True)
        d["subject"] = d.fact_id.map(subj); d["rt"] = d.relation + ":" + d.template_id.astype(str)
        d["model"] = m; parts.append(d)
    a = pd.concat(parts, ignore_index=True); a.to_parquet(cache); return a

def sets(a):
    for m in RUNS:
        d = a[a.model == m]; corr = d[d.correct_at1]
        nc = corr.groupby("fact_id").size()
        yield m, "correct", corr
        yield m, "all3", corr[corr.fact_id.isin(nc[nc == 3].index)]

def proj(X):
    U, s, _ = np.linalg.svd(X, full_matrices=False)
    U = U[:, s > 1e-8 * s.max()]; return U @ U.T

def dm(x): return pd.get_dummies(x).to_numpy(dtype=float)

NAMES = ["relation", "template_main", "fact_plus_subject", "residual"]
def anova_h3(df, y):
    n = len(df); one = np.ones((n, 1)); Zr, Zt, Zf = dm(df.relation), dm(df.rt), dm(df.fact_id)
    P0 = proj(one); P1 = proj(np.hstack([one, Zr])); P2 = proj(np.hstack([one, Zt]))
    P3 = proj(np.hstack([one, Zt, Zf]))
    As = [P1 - P0, P2 - P1, P3 - P2, np.eye(n) - P3]; Zs = [Zr, Zt, Zf, None]
    M = np.zeros((4, 4)); ss = np.zeros(4)
    for i, A in enumerate(As):
        ss[i] = y @ A @ y
        for k, Z in enumerate(Zs):
            M[i, k] = np.trace(A) if Z is None else np.trace(Z.T @ A @ Z)
    raw = np.linalg.solve(M, ss); sig = np.clip(raw, 0, None)
    return dict(zip(NAMES, sig / sig.sum())), dict(zip(NAMES, raw))

def stage1():
    from scipy.stats import spearmanr
    a = load(); out = {"B3_anova": {}, "B6": {}}
    for m, sname, s in sets(a):
        for D in ("D1", "D4"):
            sh, raw = anova_h3(s, s[D].to_numpy())
            key = f"{m}|{D}|{sname}"
            out["B3_anova"][key] = {"n_cells": len(s), "n_facts": s.fact_id.nunique(),
                                    "n_subjects": s.subject.nunique(), "shares": sh, "raw_unclipped": raw}
            print(key, len(s), s.fact_id.nunique(), s.subject.nunique(), {k: round(v, 4) for k, v in sh.items()}, flush=True)
    ms = list(RUNS); pairs = [(ms[0], ms[1]), (ms[0], ms[2]), (ms[1], ms[2])]
    ncorr = {m: a[a.model == m].groupby("fact_id").correct_at1.sum() for m in ms}
    strict = sorted(set.intersection(*[set(ncorr[m][ncorr[m] == 3].index) for m in ms]))
    anyc = sorted(set.intersection(*[set(ncorr[m][ncorr[m] >= 1].index) for m in ms]))
    rel = a[a.model == ms[0]].groupby("fact_id").relation.first()
    for D in ("D1", "D4"):
        for sname, S in (("strict_all3", strict), ("any_correct", anyc)):
            fm = {}
            for m in ms:
                d = a[(a.model == m) & a.correct_at1 & a.fact_id.isin(S)]
                f = d.groupby("fact_id")[D].mean().loc[S]
                fm[m] = (f, f - f.groupby(rel.loc[S]).transform("mean"))
            for x, y in pairs:
                r1 = spearmanr(fm[x][0], fm[y][0]).statistic; r2 = spearmanr(fm[x][1], fm[y][1]).statistic
                key = f"{D}|{sname}|{x} vs {y}"
                out["B6"][key] = {"n_facts": len(S), "rho": float(r1), "rho_within_relation": float(r2)}
                print(key, len(S), round(r1, 4), round(r2, 4), flush=True)
    json.dump(out, open(OUT + "stage1.json", "w"), indent=1)

def ml(keysub, sparse_, method):
    import statsmodels.api as sm
    a = load(); res = {}
    path = OUT + "ml.json"
    if os.path.exists(path): res = json.load(open(path))
    for m, sname, s in sets(a):
        for D in ("D1", "D4"):
            key = f"{m}|{D}|{sname}"
            if keysub not in key: continue
            for withsub in (True, False):
                t = time.time(); dd = s.assign(y=s[D].to_numpy(), g=1)
                vc = {"relation": "0+C(relation)", "rt": "0+C(rt)", "fact": "0+C(fact_id)"}
                if withsub: vc["subject"] = "0+C(subject)"
                mod = sm.MixedLM.from_formula("y ~ 1", groups="g", vc_formula=vc, re_formula="0",
                                              data=dd, use_sparse=sparse_)
                try:
                    r = mod.fit(reml=True, method=method, maxiter=1000)
                except np.linalg.LinAlgError as e:
                    print(key, "withsub" if withsub else "nosub", "LinAlgError:", e, "(subjects", s.subject.nunique(), "facts", s.fact_id.nunique(), ")", flush=True)
                    res[key + ("" if withsub else "|nosubject")] = {"error": str(e)}
                    continue
                comp = dict(zip(mod.exog_vc.names, map(float, r.vcomp))); comp["residual"] = float(r.scale)
                tot = sum(comp.values())
                sh = {"relation": comp["relation"] / tot, "template_main": comp["rt"] / tot,
                      "fact_plus_subject": (comp["fact"] + comp.get("subject", 0.0)) / tot,
                      "residual": comp["residual"] / tot}
                k2 = key + ("" if withsub else "|nosubject")
                res[k2] = {"n_cells": len(s), "shares": sh, "raw": comp, "reml_llf": float(r.llf),
                           "converged": bool(r.converged), "method": str(method), "secs": time.time() - t}
                print(k2, {k: round(v, 4) for k, v in sh.items()}, "llf", round(r.llf, 3), "conv", r.converged,
                      f"{time.time()-t:.1f}s", flush=True)
                json.dump(res, open(path, "w"), indent=1)

if __name__ == "__main__":
    if sys.argv[1] == "stage1": stage1()
    else: ml(sys.argv[2], len(sys.argv) > 3 and sys.argv[3] == "sparse", sys.argv[4] if len(sys.argv) > 4 else "lbfgs")
