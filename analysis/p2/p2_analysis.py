"""P2 confirmatory analysis (prereg/P2_prompt_vs_fact.md). One call per set of model run dirs.

python analysis/p2/p2_analysis.py <out_dir> --runs MODEL=RUN_DIR [MODEL=RUN_DIR ...] [--boot param|twoway]
       [--n-boot 1000] [--cores 3] [--set SET] [--nc NC] [--n-perm 1000]
SET: correct (primary) | new226 | all | all10 | nomanufacturer | tcov (sensitivities, with CIs)
     | lofo (leave-one-frame-out, point estimates) | h4 (EXPLORATORY frame fixed effects, point estimates).
The confirmatory call (--set correct) gets every model run dir of the session. Models that are incomplete or have
too little data are MISSING and excluded; nc (carriers used) is the minimum over the included models and is written
to p2_results.json. Every sensitivity call passes --nc <that value> and the same --runs (prereg section 4).
Steps per model: completeness check -> per-carrier depths D1-D4 from the stored (layer, p_object, rank) curves ->
minimum-data rule -> inclusion set -> REML fits (p2_analysis.R) for D1 and D4 (primary/robustness) and D2, D3
(secondary) -> Henderson III MoM on covariate-residualised, carrier-averaged cell means (p2_mom.py) -> shuffled-fact
null (set correct, D1; p2_null.R) -> hypotheses. Then the family-level claims and H3 across models.
Writes p2_results.json and p2_decision.json.
"""
import argparse
import json
import subprocess
import sys
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from p2_mom import henderson3  # noqa: E402

SEED = 20261121
BANDS = [(0.15, "prompt-dominated"), (0.4, "mixed"), (0.7, "moderately fact-stable"), (float("inf"), "fact-stable")]
TOKMAP = {"llama": "llama31", "qwen": "qwen3", "pythia": "pythia", "olmo": "olmo2"}  # model family (prereg section 5)
N_TEMPLATES = 10
MIN_FACTS_2CORRECT, MIN_RELATIONS = 150, 15          # minimum-data rule (prereg section 3)
COV = ["n_answer_tokens", "n_subject_tokens", "log_cooc_proxy", "answer_prior"]
TCOV = ["tcov_len", "tcov_dist"]
CI_SETS = ("correct", "new226", "all", "all10", "nomanufacturer", "tcov")
POINT_SETS = ("lofo", "h4")


def band(icc):
    """Descriptive band for fact ICC(1) (prereg P2 section 5; not a decision rule)."""
    return next(name for hi, name in BANDS if icc < hi) if icc is not None else None


def stable_from(ok):
    if not ok[-1]:
        return None
    l = len(ok) - 1
    while l > 0 and ok[l - 1]:
        l -= 1
    return l


def depths(curve_p, curve_rank):
    """D1-D4 for one carrier curve. D1 and D4 are undefined (None) when the final p is 0 (float16 underflow):
    every layer would pass p >= 0.5 * 0 (prereg section 2; stats-reviewer round 1 item 18)."""
    p = np.asarray(curve_p, float); L = len(p)
    d2 = stable_from(list(p >= 0.1)); d3 = stable_from(list(np.asarray(curve_rank) == 1))
    if p[-1] > 0:
        d1 = (stable_from(list(p >= 0.5 * p[-1])) + 1) / L
        d4 = 1 - float(np.mean(np.minimum(1, p / p[-1])))
    else:
        d1 = d4 = None
    return d1, (None if d2 is None else (d2 + 1) / L), (None if d3 is None else (d3 + 1) / L), d4


def completeness(run_dir, fact_ids):
    """Prereg section 1: a model is analysed only if its run reached its end. Returns (ok, reason, nc_run)."""
    rd = Path(run_dir)
    if not (rd / "manifest.json").exists():
        return False, "no manifest.json (the run did not reach its end)", 0
    man = json.loads((rd / "manifest.json").read_text())
    if not man or not all(v["ok"] for v in man.values()):
        return False, "checksum failure or empty manifest", 0
    ev = [json.loads(l) for l in open(rd / "log.jsonl")] if (rd / "log.jsonl").exists() else []
    last = ev[-1] if ev else {}
    if last.get("event") != "done" or not last.get("all_ok"):
        return False, f"last log event is not a successful 'done' ({last.get('event')})", 0
    if last.get("n_facts") is not None and last["n_facts"] != len(fact_ids):
        return False, f"run covered {last['n_facts']} of {len(fact_ids)} facts", 0
    chunks = sorted((rd / "chunks").glob("c*.parquet"))
    if len(chunks) != len([n for n in man if n.startswith("c")]):
        return False, "chunk files and manifest disagree", 0
    beh = pd.concat([pd.read_parquet(p, columns=["fact_id", "template_id"]) for p in sorted((rd / "chunks").glob("b*.parquet"))])
    want = {(f, t) for f in fact_ids for t in range(N_TEMPLATES)}
    have = set(zip(beh.fact_id, beh.template_id.astype(int)))
    if have != want or len(beh) != len(want):
        return False, f"behaviour rows cover {len(have & want)} of {len(want)} fact x paraphrase cells", 0
    long = pd.concat([pd.read_parquet(p, columns=["fact_id", "template_id", "carrier", "layer"]) for p in chunks])
    nl = long.groupby(["fact_id", "template_id", "carrier"]).layer.nunique()
    if nl.nunique() != 1:
        return False, "unequal layer counts across curves", 0
    cs = long.groupby(["fact_id", "template_id"]).carrier.agg(lambda s: tuple(sorted(set(s))))
    if len(cs) != len(want):
        return False, f"curves cover {len(cs)} of {len(want)} fact x paraphrase cells", 0
    nc_cell = cs.map(len)
    if not all(c == tuple(range(len(c))) for c in cs):
        return False, "carrier ids are not 0..k-1 in some cell", 0
    nc_fact = nc_cell.groupby(level=0).min()
    if nc_fact.min() < 2:
        return False, "some fact has fewer than 2 carriers", 0
    return True, "complete", int(nc_fact.min())


def load_model(run_dir, facts, nc):
    run_dir = Path(run_dir)
    long = pd.concat([pd.read_parquet(p) for p in sorted((run_dir / "chunks").glob("c*.parquet"))])
    beh = pd.concat([pd.read_parquet(p) for p in sorted((run_dir / "chunks").glob("b*.parquet"))])
    long = long[long.carrier < nc]  # carriers present for every fact in every included model (fallback 1)
    rows = []
    for (fid, rel, t, c), g in long.sort_values("layer").groupby(["fact_id", "relation", "template_id", "carrier"]):
        p = g.p_object.to_numpy(np.float32)
        d1, d2, d3, d4 = depths(p, g["rank"].to_numpy())
        rows.append((fid, rel, int(t), int(c), d1, d2, d3, d4, bool(p[-1] <= 0)))
    D = pd.DataFrame(rows, columns=["fact_id", "relation", "template_id", "carrier", "D1", "D2", "D3", "D4", "p_final_zero"])
    D = D.merge(beh, on=["fact_id", "relation", "template_id"])
    ap = [c for c in beh.columns if c.startswith("carrier_alone_logprob_c") and int(c.rsplit("c", 1)[1]) < nc]
    prior = beh.groupby("fact_id")[ap].mean().mean(axis=1).rename("answer_prior")
    D = D.merge(prior, on="fact_id").merge(facts, on=["fact_id", "relation"])
    D["frame"] = D.template_id
    D["n_correct_templates"] = D.fact_id.map(beh.groupby("fact_id").correct_at1.sum())
    return D


def zs(d, cols):
    for c in cols:
        s = d[c].std()
        d[c] = (d[c] - d[c].mean()) / s if s and s > 0 else 0.0
    return d


def mom_cells(D, y, cov):
    """Covariate-residualised, carrier-averaged cell means for Henderson III (prereg section 4; item 1)."""
    d = D.dropna(subset=[y]).copy()
    X = [np.ones(len(d))] + [d[c].to_numpy(float) for c in cov if c in d and d[c].std() > 0]
    X += [(d.carrier == k).to_numpy(float) for k in sorted(d.carrier.unique())[1:]]
    X = np.column_stack(X); yy = d[y].to_numpy(float)
    b, *_ = np.linalg.lstsq(X, yy, rcond=None)
    d["yr"] = yy - X @ b
    return d.groupby(["fact_id", "relation", "frame"], as_index=False).yr.mean().rename(columns={"fact_id": "fact", "yr": "y"})


def rfit(csv, js, y, a, nc, n_boot, extra=()):
    p = subprocess.run(["Rscript", str(HERE / "p2_analysis.R"), str(csv), str(js), f"y={y}", f"boot={a.boot}",
                        f"n_boot={n_boot}", f"seed={SEED}", f"cores={a.cores}", f"nc={nc}", *extra],
                       capture_output=True, text=True, cwd=ROOT)
    return json.loads(js.read_text()) if p.returncode == 0 else {"status": "MISSING: fit error", "missing": p.stderr[-600:]}


def g_at(vc, k, nc):
    f, ft, fc, e = (vc.get(x, 0.0) for x in ("fact", "ft", "fc", "Residual"))
    return f / (f + ft / k + fc / nc + e / (k * nc)) if f > 0 else 0.0


def tcov_table(tok):
    """Template-level covariates (sensitivity model): template length and subject-to-final distance, in tokens."""
    rows = []
    for l in open(ROOT / "materials/paraphrases_v1.jsonl"):
        p = json.loads(l); before, after = p["template"].split("{}", 1)
        rows.append({"relation": p["relation"], "template_id": p["template_id"],
                     "tcov_len": len(tok.encode(" " + (before + after).strip(), add_special_tokens=False)),
                     "tcov_dist": len(tok.encode(" " + after.strip(), add_special_tokens=False)) if after.strip() else 0})
    return pd.DataFrame(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out"); ap.add_argument("--runs", nargs="+", required=True)
    ap.add_argument("--boot", default="param"); ap.add_argument("--n-boot", type=int, default=1000)
    ap.add_argument("--cores", type=int, default=3); ap.add_argument("--set", default="correct")
    ap.add_argument("--nc", type=int, default=None, help="sensitivity calls: the nc of the confirmatory call")
    ap.add_argument("--n-perm", type=int, default=1000, help="shuffled-fact null permutations (set correct only)")
    a = ap.parse_args()
    if a.set not in CI_SETS + POINT_SETS:
        raise SystemExit(f"unknown set {a.set}")
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    fl = [json.loads(l) for l in open(ROOT / "materials/facts_v1.jsonl")]
    fact_ids = [f["fact_id"] for f in fl]
    res = {"set": a.set, "boot": a.boot, "n_boot": a.n_boot, "seed": SEED, "runs": a.runs, "models": {}}
    # 1. completeness (MISSING: incomplete) and carriers used
    comp = {}
    for spec in a.runs:
        model, rd = spec.split("=", 1)
        ok, why, ncr = completeness(rd, fact_ids)
        comp[model] = (ok, why, ncr, rd)
        if not ok:
            res["models"][model] = {"status": f"MISSING (incomplete): {why}"}
    included = {m: v for m, v in comp.items() if v[0]}
    nc_all = min((v[2] for v in included.values()), default=0)
    if a.nc is not None:
        if a.nc > nc_all:
            raise SystemExit(f"--nc {a.nc} exceeds the carriers available in every included model ({nc_all})")
        nc_used = a.nc
    else:
        nc_used = nc_all
    res["n_carriers_used"] = nc_used; res["n_carriers_available"] = nc_all
    fact_means, kbar = {}, {}
    for model, (_, _, ncr, rd) in included.items():
        fam = next((v for k, v in TOKMAP.items() if k in model.lower()), None)
        facts = pd.DataFrame([{"fact_id": f["fact_id"], "relation": f["relation"], "subject": f["subject"],
                               "log_cooc_proxy": f["log1p_cooc_dclm"]} for f in fl])
        from transformers import AutoTokenizer
        tok = AutoTokenizer.from_pretrained(model, local_files_only=True)
        facts["n_answer_tokens"] = [len(tok.encode(" " + f["object"], add_special_tokens=False)) for f in fl]
        facts["n_subject_tokens"] = [len(tok.encode(" " + f["subject"], add_special_tokens=False)) for f in fl]
        D = load_model(rd, facts, nc_used)
        # 2. minimum-data rule on the primary set (MISSING: insufficient data), applied whatever the set
        nct = D.drop_duplicates("fact_id").set_index("fact_id").n_correct_templates
        f2 = nct[nct >= 2].index
        n_rel2 = D[D.fact_id.isin(f2)].relation.nunique()
        entry = {"facts_with_2plus_correct": int(len(f2)), "relations_with_such_facts": int(n_rel2)}
        if len(f2) < MIN_FACTS_2CORRECT or n_rel2 < MIN_RELATIONS:
            res["models"][model] = {"family": fam, "status": "MISSING (insufficient data)", "min_data": entry}
            continue
        n_pzero = int(D.p_final_zero.sum())
        # 3. inclusion set
        if a.set in ("correct", "tcov", "lofo", "h4"):
            D = D[D.correct_at1]
        elif a.set == "all10":
            D = D[D.n_correct_templates == N_TEMPLATES]
        elif a.set == "new226":  # correct cells of the 226 facts not analysed in G1
            keep = set(json.loads((ROOT / "materials/facts_v1_not_in_G1.json").read_text()))
            D = D[D.correct_at1 & D.fact_id.isin(keep)]
        elif a.set == "nomanufacturer":
            D = D[D.correct_at1 & (D.relation != "manufacturer")]
        cov = COV + (TCOV if a.set == "tcov" else [])
        if a.set == "tcov":
            D = D.merge(tcov_table(tok), on=["relation", "template_id"])
        D = zs(D.copy(), cov)
        tag = f"{model.split('/')[-1]}_{a.set}"
        mres = {"family": fam, "status": "ok", "run_dir": rd, "n_carriers_run": ncr, "n_carriers_used": nc_used,
                "min_data": entry, "n_curves_p_final_zero": n_pzero, "n_rows": int(len(D)),
                "n_facts": int(D.fact_id.nunique()), "fits": {}, "mom": {}}
        extra = ["tcov=1"] if a.set == "tcov" else []
        if a.set in CI_SETS:
            csv = out / f"long_{tag}.csv"; D.to_csv(csv, index=False)
            for y in ("D1", "D4", "D2", "D3"):
                mres["fits"][y] = rfit(csv, out / f"fit_{tag}_{y}.json", y, a, nc_used, a.n_boot, extra)
                try:
                    mres["mom"][y] = henderson3(mom_cells(D, y, cov))
                except Exception as e:  # noqa: BLE001
                    mres["mom"][y] = {"missing": repr(e)[:300]}
            if a.set == "correct" and a.n_perm > 0:
                js = out / f"null_{tag}_D1.json"
                p = subprocess.run(["Rscript", str(HERE / "p2_null.R"), str(csv), str(js), "y=D1", f"n_perm={a.n_perm}",
                                    f"seed={SEED}", f"cores={a.cores}", f"nc={nc_used}"], capture_output=True, text=True, cwd=ROOT)
                mres["null"] = json.loads(js.read_text()) if p.returncode == 0 else {"missing": p.stderr[-600:]}
            fact_means[model] = D.groupby(["fact_id", "relation"]).D1.mean()
            kbar[model] = float(D.dropna(subset=["D1"]).groupby("fact_id").template_id.nunique().mean())
        elif a.set == "lofo":
            for k in range(N_TEMPLATES):
                Dk = D[D.template_id != k]; csv = out / f"long_{tag}_drop{k}.csv"; Dk.to_csv(csv, index=False)
                mres["fits"][f"drop{k}"] = {y: rfit(csv, out / f"fit_{tag}_drop{k}_{y}.json", y, a, nc_used, 0) for y in ("D1", "D4")}
                mres["mom"][f"drop{k}"] = {y: henderson3(mom_cells(Dk, y, cov)) for y in ("D1", "D4")}
        else:  # h4, EXPLORATORY
            csv = out / f"long_{tag}.csv"; D.to_csv(csv, index=False)
            for y in ("D1", "D4"):
                mres["fits"][y] = rfit(csv, out / f"fit_{tag}_{y}.json", y, a, nc_used, 0, ["h4=1"])
        res["models"][model] = mres
    dec = decide(res, a.set, fact_means, kbar, nc_used)
    (out / "p2_results.json").write_text(json.dumps(res, indent=1, default=float))
    (out / "p2_decision.json").write_text(json.dumps(dec, indent=1, default=float))
    print(json.dumps(dec.get("claims", {}), indent=1))


def decide(res, set_name, fact_means, kbar, nc):
    dec = {"set": set_name, "n_carriers_used": nc, "per_model": {}}
    if set_name not in CI_SETS:
        dec["note"] = "point estimates only; no decision rules apply to this set"
        return dec
    for m, r in res["models"].items():
        if r.get("status") != "ok":
            dec["per_model"][m] = {"status": r.get("status")}; continue
        f1, f4 = r["fits"].get("D1", {}), r["fits"].get("D4", {})
        if f1.get("status") != "ok" or f4.get("status") != "ok":
            dec["per_model"][m] = {"family": r["family"], "status": "MISSING (D1 or D4 fit)",
                                   "fit_status": [f1.get("status"), f4.get("status")]}
            continue
        mom1, mom4 = r["mom"].get("D1", {}), r["mom"].get("D4", {})
        mom_ok = "diff" in mom1 and "diff" in mom4
        h1 = all(f["boot"]["ci"]["diff"][0] > 0 for f in (f1, f4)) and mom_ok and all(mm["diff"] > 0 for mm in (mom1, mom4))
        h1alt = all(f["point"]["icc1"] >= 0.5 and f["boot"]["ci"]["icc1"][0] >= 0.4 for f in (f1, f4)) and \
            mom_ok and all(mm["diff"] < 0 for mm in (mom1, mom4))
        npr = f1["point"]["nprime_G"] if f1["point"]["nprime_G"] is not None else 31  # undefined (G(30) < 0.8) -> 31
        nul = r.get("null", {})
        dec["per_model"][m] = {"family": r["family"], "status": "ok", "H1": h1, "H1_alt": h1alt,
                               "icc1_D1": f1["point"]["icc1"], "icc1_D1_ci": f1["boot"]["ci"]["icc1"],
                               "icc1_D4": f4["point"]["icc1"], "icc1_D4_ci": f4["boot"]["ci"]["icc1"],
                               "icc1_band_D1": band(f1["point"]["icc1"]), "icc1_band_D4": band(f4["point"]["icc1"]),
                               "icc1_upper_lt_0.15": f1["boot"]["ci"]["icc1"][1] < 0.15,
                               "nprime_G_D1": npr, "tf_gt_resid_D1": f1["point"]["tf_minus_resid"] > 0,
                               "diff_D1": f1["point"]["diff"], "diff_D1_ci": f1["boot"]["ci"]["diff"],
                               "diff_D4": f4["point"]["diff"], "diff_D4_ci": f4["boot"]["ci"]["diff"],
                               "mom_diff_D1": mom1.get("diff"), "mom_diff_D4": mom4.get("diff"),
                               "null_p_D1": nul.get("p"), "null_lt_0.01": (nul.get("p") is not None and nul["p"] < 0.01)}
    ok = {m: v for m, v in dec["per_model"].items() if v.get("status") == "ok"}
    fams = lambda pred: sorted({v["family"] for v in ok.values() if pred(v)})  # noqa: E731
    h1f, h1af = fams(lambda v: v["H1"]), fams(lambda v: v["H1_alt"])
    conflict = len(h1f) >= 2 and len(h1af) >= 2
    dec["families"] = {"H1": h1f, "H1_alt": h1af, "included_models": sorted(ok), "included_families": fams(lambda v: True)}
    dec["claims"] = {
        "H1_holds_(>=2_families)": len(h1f) >= 2, "H1alt_holds_(>=2_families)": len(h1af) >= 2,
        "model_dependent_(H1_and_H1alt_both_>=2_families)": conflict,
        "no_fixed_layer_(ICC1_D1_upper<0.15_in>=2_families)": len(fams(lambda v: v["icc1_upper_lt_0.15"])) >= 2,
        "single_prompt_poor_(H1_and_nprime>=8_in>=2_families)":
            len(fams(lambda v: v["H1"] and v["nprime_G_D1"] >= 8)) >= 2 and not conflict,
        "wording_shifts_together_(H1_and_tf>resid_in>=2_families)":
            len(fams(lambda v: v["H1"] and v["tf_gt_resid_D1"])) >= 2 and not conflict,
        "fact_depth_unexplained_(H1alt_in>=2_families)": len(h1af) >= 2 and not conflict,
        "fact_share_gt0_(null_p<0.01_in>=2_families)":
            (len(fams(lambda v: v["null_lt_0.01"])) >= 2) if set_name == "correct" else None}
    h3 = {}
    for x, y in combinations(fact_means, 2):
        common = sorted(set(fact_means[x].dropna().index) & set(fact_means[y].dropna().index))
        if len(common) < 10:
            h3[f"{x} vs {y}"] = {"missing": f"{len(common)} common facts"}; continue
        u, v = fact_means[x].loc[common].to_numpy(), fact_means[y].loc[common].to_numpy()
        gx = g_at(res["models"][x]["fits"]["D1"]["vc"], kbar[x], nc); gy = g_at(res["models"][y]["fits"]["D1"]["vc"], kbar[y], nc)
        rho = float(spearmanr(u, v).statistic)
        h3[f"{x} vs {y}"] = {"n_facts": len(common), "rho": rho, "kbar": [kbar[x], kbar[y]], "G_kbar": [gx, gy],
                             "disattenuated_approx": rho / np.sqrt(gx * gy) if gx > 0 and gy > 0 else None}
    dec["H3"] = h3
    return dec


if __name__ == "__main__":
    main()
