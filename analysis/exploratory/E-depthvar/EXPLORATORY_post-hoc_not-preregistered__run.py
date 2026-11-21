"""EXPLORATORY (post hoc, not preregistered) — E-depthvar orchestrator (B3-B7 statistics, decision inputs).

python <this> <out_dir> [--n-boot 1000] [--n-null 1000] [--n-sim 50] [--n-cov-boot 200] [--cores 3]
<out_dir> already holds tables/ from the build step. Writes fits/*.json (R), anova/null/coverage/B6 json,
tables/EXPLORATORY_post-hoc_not-preregistered__E-depthvar_components.csv and e_depthvar.json.
"""
import argparse
import json
import subprocess
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata, spearmanr

HERE = Path(__file__).resolve().parent
P = "EXPLORATORY_post-hoc_not-preregistered__"
FIT, SIM = HERE / f"{P}fit.R", HERE / f"{P}sim.R"
MODELS = ["pythia-1.4b", "pythia-2.8b", "OLMo-2-1124-7B"]
OUTCOMES = ["D1", "D4", "D2", "D2_cens_as_Lp1", "D3"]
SETS = ["correct", "all3"]
SEED = 20261121


def R(*args):
    p = subprocess.run(["Rscript", *map(str, args)], capture_output=True, text=True)
    if p.returncode:
        raise RuntimeError(p.stderr[-1500:])


def ci(x):
    x = np.asarray([v for v in x if v is not None and np.isfinite(v)], float)
    return [float(np.percentile(x, 2.5)), float(np.percentile(x, 97.5))] if len(x) else [None, None]


# ----------------------------------------------------------------------------- ANOVA (method of moments)
def anova(Y, rel):
    """Y: n x 3 (facts x templates, templates nested in relation), rel: relation code per fact."""
    R_ = rel.max() + 1
    n_r = np.bincount(rel, minlength=R_).astype(float)
    keep = n_r > 0
    yf = Y.mean(1)
    yt = np.stack([np.bincount(rel, Y[:, t], minlength=R_) for t in range(3)], 1)
    yt[keep] /= n_r[keep, None]
    yr = np.zeros(R_); yr[keep] = np.bincount(rel, yf, minlength=R_)[keep] / n_r[keep]
    n, Rk = len(yf), int(keep.sum())
    ss_f = 3 * np.sum((yf - yr[rel]) ** 2); df_f = n - Rk
    ss_t = np.sum(n_r[keep, None] * (yt[keep] - yr[keep, None]) ** 2); df_t = 2 * Rk
    res = Y - yf[:, None] - yt[rel] + yr[rel][:, None]
    ss_e = np.sum(res ** 2); df_e = 2 * (n - Rk)
    ms_e = ss_e / df_e if df_e else np.nan
    ms_f = ss_f / df_f if df_f else np.nan
    ms_t = ss_t / df_t
    nbar = n_r[keep].mean()
    s_e, s_f, s_t = ms_e, (ms_f - ms_e) / 3, (ms_t - ms_e) / nbar
    w = 3 * n_r[keep]; N = w.sum(); yb = np.sum(w * yr[keep]) / N
    ss_r = np.sum(w * (yr[keep] - yb) ** 2); c = w * (1 - w / N)
    s_a = (ss_r - np.sum(c * (s_f / n_r[keep] + s_t / 3 + s_e / (3 * n_r[keep])))) / c.sum()
    raw = {"relation": s_a, "fact": s_f, "template_main": s_t, "residual": s_e}
    tr = {k: max(0.0, v) for k, v in raw.items()}
    tot = sum(tr.values())
    return {"raw": raw, "share": {k: v / tot for k, v in tr.items()}}


def balanced(df, y):
    g = df.pivot_table(index=["fact_id", "relation"], columns="template_id", values=y).dropna()
    rel_codes = pd.Categorical(g.index.get_level_values("relation")).codes
    return g.to_numpy(float), rel_codes.astype(int)


def anova_boot(Y, rel, nb, rng):
    out = []
    idx_by = [np.flatnonzero(rel == r) for r in range(rel.max() + 1)]
    for _ in range(nb):
        pick = np.concatenate([rng.choice(ix, len(ix), replace=True) for ix in idx_by if len(ix)])
        out.append(anova(Y[pick], rel[pick])["share"])
    return out


def null_fact_share(Y, rel, nn, rng):
    vals = []
    idx_by = [np.flatnonzero(rel == r) for r in range(rel.max() + 1)]
    for _ in range(nn):
        Z = Y.copy()
        for ix in idx_by:
            for t in range(3):
                Z[ix, t] = Z[rng.permutation(ix), t]
        vals.append(anova(Z, rel)["share"]["fact"])
    return np.array(vals)


# ----------------------------------------------------------------------------- B7b coverage arm (ANOVA)
def sim_curves_depth(m, L, s=0.05):
    lay = np.arange(1, L + 1) / L
    P_ = 1 / (1 + np.exp(-(lay[None, :] - m[:, None]) / s))
    pf = P_[:, -1:]
    ok = P_ >= 0.5 * pf
    bad = ~ok
    last_bad = np.where(bad.any(1), L - np.argmax(bad[:, ::-1], 1), 0)
    D1 = (last_bad + 1) / L
    D4 = 1 - np.minimum(P_ / pf, 1).mean(1)
    return D1, D4


def coverage(cells, n_sim, nb, rng):
    d = cells[(cells.correct == 1) & (cells.n_correct_templates == 3)]
    Y0, rel = balanced(d, "D1")
    L = int(cells.L.iloc[0]); mu, V = cells[cells.correct == 1].D1.mean(), cells[cells.correct == 1].D1.var()
    n, R_ = Y0.shape[0], rel.max() + 1
    out = []
    for cf in (0.1, 0.3, 0.5, 0.7):
        for ct in (0.05, 0.2):
            ce = 1 - 0.05 - cf - ct
            hits = {"D1": {"fact": 0, "template_main": 0}, "D4": {"fact": 0, "template_main": 0}}
            est = {"D1": [], "D4": []}
            for _ in range(n_sim):
                a = rng.normal(0, np.sqrt(0.05 * V), R_)[rel][:, None]
                b = rng.normal(0, np.sqrt(ct * V), (R_, 3))[rel]
                f = rng.normal(0, np.sqrt(cf * V), n)[:, None]
                e = rng.normal(0, np.sqrt(ce * V), (n, 3))
                M = mu + a + b + f + e
                D1, D4 = sim_curves_depth(M.ravel(), L)
                for k, D in (("D1", D1), ("D4", D4)):
                    Y = D.reshape(n, 3)
                    pt = anova(Y, rel)["share"]
                    bs = anova_boot(Y, rel, nb, rng)
                    est[k].append(pt)
                    for comp, planted in (("fact", cf), ("template_main", ct)):
                        lo, hi = ci([x[comp] for x in bs])
                        hits[k][comp] += int(lo <= planted <= hi)
            out.append({"planted": {"fact": cf, "template_main": ct, "relation": 0.05, "residual": ce},
                        "n_sim": n_sim, "n_boot": nb,
                        "coverage": {k: {c: v / n_sim for c, v in hv.items()} for k, hv in hits.items()},
                        "anova_mean_share": {k: {c: float(np.mean([x[c] for x in est[k]])) for c in ("fact", "template_main")}
                                             for k in est}})
    return {"design": {"n_facts_balanced": int(n), "n_relations_with_facts": int(len(np.unique(rel))), "L": L},
            "conditions": out}


# ----------------------------------------------------------------------------- B6
def cross_model(cells, fits, nb, rng):
    res = {}
    for y in ("D1", "D4"):
        for mode in ("strict_all3", "any_correct"):
            fm = {}
            for m in MODELS:
                c = cells[m]
                c = c[c.correct == 1]
                if mode == "strict_all3":
                    c = c[c.n_correct_templates == 3]
                fm[m] = c.groupby(["fact_id", "relation"])[y].mean()
            common = sorted(set.intersection(*[set(s.index) for s in fm.values()]))
            for a, b in combinations(MODELS, 2):
                x = fm[a].loc[common].to_numpy(); z = fm[b].loc[common].to_numpy()
                rels = np.array([r for _, r in common])
                xw = x - pd.Series(x).groupby(rels).transform("mean").to_numpy()
                zw = z - pd.Series(z).groupby(rels).transform("mean").to_numpy()
                rho, rho_w = float(spearmanr(x, z).statistic), float(spearmanr(xw, zw).statistic)
                ga, gb = fits[(a, y, "all3")]["g3"], fits[(b, y, "all3")]["g3"]
                bs, bsw = [], []
                for _ in range(nb):
                    i = rng.integers(0, len(x), len(x))
                    bs.append(spearmanr(x[i], z[i]).statistic); bsw.append(spearmanr(xw[i], zw[i]).statistic)
                den = np.sqrt(ga * gb) if ga and gb and ga > 0 and gb > 0 else np.nan
                res[f"{y}|{mode}|{a} vs {b}"] = {
                    "outcome": y, "facts": mode, "pair": f"{a} vs {b}", "n_facts": len(common),
                    "n_relations": int(len(set(rels))), "rho": rho, "rho_ci": ci(bs),
                    "rho_within_relation": rho_w, "rho_within_relation_ci": ci(bsw),
                    "g3": {a: ga, b: gb}, "disattenuated_rho": float(rho / den) if np.isfinite(den) else None,
                    "disattenuated_rho_ci": [v / den for v in ci(bs)] if np.isfinite(den) else [None, None],
                    "disattenuated_rho_within": float(rho_w / den) if np.isfinite(den) else None}
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--n-boot", type=int, default=1000)
    ap.add_argument("--n-null", type=int, default=1000)
    ap.add_argument("--n-sim", type=int, default=50)
    ap.add_argument("--n-cov-boot", type=int, default=200)
    ap.add_argument("--cores", type=int, default=3)
    a = ap.parse_args()
    out = Path(a.out); fdir = out / "fits"; fdir.mkdir(exist_ok=True)
    tab = lambda m: out / "tables" / f"{P}cells_{m}.csv"  # noqa: E731
    cells = {m: pd.read_csv(tab(m)) for m in MODELS}
    fits, boots = {}, {}
    # B3 point (+B5 covariates) and bootstrap
    for m in MODELS:
        for y in OUTCOMES:
            for s in SETS:
                f = fdir / f"{P}point_{m}_{y}_{s}.json"
                if not f.exists():
                    R(FIT, "point", tab(m), f, f"y={y}", f"set={s}", "cov=1")
                fits[(m, y, s)] = json.loads(f.read_text())
    print("points done", flush=True)
    order = [(m, y, s) for y in OUTCOMES for s in SETS for m in MODELS]  # D1, D4 first
    for (m, y, s) in order:
        f = fdir / f"{P}boot_{m}_{y}_{s}.json"
        if not f.exists():
            R(FIT, "boot", tab(m), f, f"y={y}", f"set={s}", f"n_boot={a.n_boot}", f"seed={SEED}", f"cores={a.cores}")
        boots[(m, y, s)] = json.loads(f.read_text())
        print("boot done", m, y, s, flush=True)
    # B7c carrier facet
    carrier = {}
    for m in MODELS:
        for y in ("D1", "D4"):
            f = fdir / f"{P}carrier_{m}_{y}.json"
            if not f.exists():
                R(FIT, "carrier", out / "tables" / f"{P}carrier_long_{m}.csv", f, f"y={y}", "set=correct")
            carrier[f"{m}|{y}"] = json.loads(f.read_text())
    print("carrier done", flush=True)
    rng = np.random.default_rng(SEED)
    # ANOVA cross-check + shuffled-fact null (balanced sets)
    anov, nulls = {}, {}
    for m in MODELS:
        for y in ("D1", "D4"):
            for s, dd in (("all_cells", cells[m]), ("all3", cells[m][(cells[m].correct == 1) & (cells[m].n_correct_templates == 3)])):
                Y, rel = balanced(dd, y)
                obs = anova(Y, rel)
                nv = null_fact_share(Y, rel, a.n_null, rng)
                anov[f"{m}|{y}|{s}"] = {**obs, "n_facts": int(len(Y)), "n_relations": int(len(np.unique(rel)))}
                nulls[f"{m}|{y}|{s}"] = {"observed_fact_share": obs["share"]["fact"], "n_perm": a.n_null,
                                         "null_mean": float(nv.mean()), "null_p95": float(np.percentile(nv, 95)),
                                         "null_p99": float(np.percentile(nv, 99)),
                                         "p_value": float((1 + np.sum(nv >= obs["share"]["fact"])) / (a.n_null + 1))}
    print("anova/null done", flush=True)
    # B7b planted recovery: bias (lme4, exact correct-cell design) and coverage (ANOVA, balanced design)
    planted = {}
    for m in MODELS:
        f = fdir / f"{P}sim_{m}.json"
        if not f.exists():
            R(SIM, tab(m), f, f"n_sim={a.n_sim}", f"seed={SEED}", f"cores={a.cores}")
        sim = json.loads(f.read_text())
        bias = []
        for c in sim["conditions"]:
            pl, dr = c["planted"], c["draws"]
            row = {"planted_fact": pl["fact"], "planted_template_main": pl["template_main"]}
            for k in ("D1", "D4"):
                fs = np.array([v for v in dr[f"{k}.fact_subject"] if v is not None], float)
                tm = np.array([v for v in dr[f"{k}.template_main"] if v is not None], float)
                row[f"{k}_mean_fact_subject"], row[f"{k}_mean_template_main"] = float(fs.mean()), float(tm.mean())
                row[f"{k}_bias_fact"], row[f"{k}_bias_template_main"] = float(fs.mean() - pl["fact"]), float(tm.mean() - pl["template_main"])
                row[f"{k}_n_ok"] = int(len(fs))
            bias.append(row)
        cov = coverage(cells[m], a.n_sim, a.n_cov_boot, rng)
        maxbias = max(abs(r[f"{k}_bias_{c}"]) for r in bias for k in ("D1", "D4") for c in ("fact", "template_main"))
        planted[m] = {"bias_lme4": bias, "coverage_anova": cov, "max_abs_bias": maxbias, "pass_within_0.05": bool(maxbias <= 0.05)}
        print("planted done", m, flush=True)
    b6 = cross_model(cells, {k: v for k, v in fits.items()}, a.n_boot, rng)
    print("B6 done", flush=True)
    # components table + decision inputs
    rows = []
    for (m, y, s), ft in fits.items():
        bt = boots[(m, y, s)]["draws"]
        sh = lambda k: ft[k]  # noqa: E731
        rows.append({"EXPLORATORY (post hoc, not preregistered) model": m, "outcome": y, "set": s,
                     "n_cells": ft["n_cells"], "n_facts": ft["n_facts"], "n_relations": ft["n_relations"],
                     "share_fact_subject": sh("share_fact_subject"), "share_fact_subject_ci": ci(bt["fact_subject"]),
                     "share_template_main": sh("share_template_main"), "share_template_main_ci": ci(bt["template_main"]),
                     "share_residual": sh("share_residual"), "share_residual_ci": ci(bt["residual"]),
                     "share_relation": sh("share_relation"), "share_relation_ci": ci(bt["relation"]),
                     "diff_prompt_minus_fact": sh("diff_prompt_minus_fact"), "diff_ci": ci(bt["diff_prompt_minus_fact"]),
                     "icc1": ft["icc1"], "icc1_ci": ci(bt["icc1"]), "icc1_rel": ft["icc1_rel"],
                     "nprime_phi": ft["nprime_phi"], "nprime_phi_ci": ci(bt["nprime_phi"]), "nprime_g": ft["nprime_g"],
                     "g3": ft["g3"], "phi3": ft["phi3"], "singular": ft["singular"],
                     "n_boot": boots[(m, y, s)]["n_boot"], "n_boot_failed": boots[(m, y, s)]["n_failed"]})
    comp = pd.DataFrame(rows)
    flat = comp.copy()
    for c in [c for c in comp if c.endswith("_ci")]:
        flat[c.replace("_ci", "_lo")] = [v[0] for v in comp[c]]
        flat[c.replace("_ci", "_hi")] = [v[1] for v in comp[c]]
        del flat[c]
    flat.to_csv(out / "tables" / f"{P}E-depthvar_components.csv", index=False)
    # decision (human's G1 rule, set (i) correct cells)
    def prompt_wins(y):
        r = comp[(comp.outcome == y) & (comp.set == "correct")]
        return {m: bool(r[r.iloc[:, 0] == m].diff_ci.iloc[0][0] > 0) for m in MODELS}
    def fact_half(y):
        r = comp[(comp.outcome == y) & (comp.set == "correct")]
        return {m: bool(r[r.iloc[:, 0] == m].share_fact_subject.iloc[0] >= 0.5) for m in MODELS}
    d1, d4 = prompt_wins("D1"), prompt_wins("D4")
    d4dir = {m: bool(comp[(comp.outcome == "D4") & (comp.set == "correct") & (comp.iloc[:, 0] == m)].diff_prompt_minus_fact.iloc[0] > 0) for m in MODELS}
    null_pass = {k: v["p_value"] < 0.01 for k, v in nulls.items()}
    plant_pass = {m: planted[m]["pass_within_0.05"] for m in MODELS}
    dec = {"prompt_wins_D1_ci_excludes_0": d1, "prompt_direction_D4": d4dir, "prompt_wins_D4_ci_excludes_0": d4,
           "fact_share_ge_0.5_D1": fact_half("D1"), "fact_share_ge_0.5_D4": fact_half("D4"),
           "null_fact_share_above_null_p<0.01": null_pass, "planted_recovery_pass": plant_pass}
    res = {"label": "EXPLORATORY (post hoc, not preregistered)", "seed": SEED, "n_boot": a.n_boot, "n_null": a.n_null,
           "n_sim": a.n_sim, "n_cov_boot": a.n_cov_boot,
           "build_summary": json.loads((out / "build_summary.json").read_text()),
           "components": comp.to_dict("records"),
           "dstudy": {f"{m}|{y}|{s}": {"phi_k": fits[(m, y, s)]["phi_k"], "g_k": fits[(m, y, s)]["g_k"]}
                      for (m, y, s) in fits},
           "covariates_B5": {f"{m}|{y}|{s}": fits[(m, y, s)].get("covariates") for (m, y, s) in fits},
           "anova_B3_crosscheck": anov, "null_B7a": nulls, "planted_B7b": planted, "carrier_B7c": carrier,
           "cross_model_B6": b6, "decision_inputs": dec}
    (out / "e_depthvar.json").write_text(json.dumps(res, indent=1, default=float))
    print(json.dumps(dec, indent=1))


if __name__ == "__main__":
    main()
