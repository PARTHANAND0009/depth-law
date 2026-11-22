"""P2 confirmatory analysis (prereg/P2_prompt_vs_fact.md). One call per set of model run dirs.

python analysis/p2/p2_analysis.py <out_dir> --runs MODEL=RUN_DIR [MODEL=RUN_DIR ...] [--boot param|twoway]
       [--n-boot 1000] [--cores 3] [--set correct|all10|all|new226]
Steps per model: per-carrier depths D1-D4 from the stored (layer, p_object, rank) curves -> inclusion -> REML fits
(p2_analysis.R) for D1 and D4 (primary/robustness) and D2, D3 (secondary) -> Henderson III MoM on carrier-averaged
cell means (p2_mom.py) -> hypotheses. Then H3 across models. Writes p2_results.json and p2_decision.json.
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


def band(icc):
    """Descriptive band for fact ICC(1) (prereg P2 section 5; not a decision rule)."""
    return next(name for hi, name in BANDS if icc < hi) if icc is not None else None
TOKMAP = {"llama": "llama31", "qwen": "qwen3", "pythia": "pythia", "olmo": "olmo2"}


def stable_from(ok):
    if not ok[-1]:
        return None
    l = len(ok) - 1
    while l > 0 and ok[l - 1]:
        l -= 1
    return l


def depths(curve_p, curve_rank):
    p = np.asarray(curve_p, float); L = len(p)
    d1 = (stable_from(list(p >= 0.5 * p[-1])) + 1) / L
    d2 = stable_from(list(p >= 0.1)); d3 = stable_from(list(np.asarray(curve_rank) == 1))
    d4 = 1 - float(np.mean(np.minimum(1, p / p[-1]))) if p[-1] > 0 else None
    return d1, (None if d2 is None else (d2 + 1) / L), (None if d3 is None else (d3 + 1) / L), d4


def carriers_everywhere(run_dirs):
    """Prereg section 3, fallback 1: if any model ran with 2 carriers, every model is analysed on carriers 0-1."""
    n = []
    for rd in run_dirs:
        c = pd.concat([pd.read_parquet(p, columns=["fact_id", "carrier"]) for p in sorted((Path(rd) / "chunks").glob("c*.parquet"))])
        n.append(int(c.groupby("fact_id").carrier.nunique().min()))
    return min(n)


def load_model(run_dir, facts, nc):
    run_dir = Path(run_dir)
    man = json.loads((run_dir / "manifest.json").read_text())
    assert all(v["ok"] for v in man.values()), f"checksum failure in {run_dir}"
    long = pd.concat([pd.read_parquet(p) for p in sorted((run_dir / "chunks").glob("c*.parquet"))])
    beh = pd.concat([pd.read_parquet(p) for p in sorted((run_dir / "chunks").glob("b*.parquet"))])
    rows = []
    for (fid, rel, t, c), g in long.sort_values("layer").groupby(["fact_id", "relation", "template_id", "carrier"]):
        d1, d2, d3, d4 = depths(g.p_object.to_numpy(np.float32), g["rank"].to_numpy())
        rows.append((fid, rel, int(t), int(c), d1, d2, d3, d4))
    D = pd.DataFrame(rows, columns=["fact_id", "relation", "template_id", "carrier", "D1", "D2", "D3", "D4"])
    D = D.merge(beh, on=["fact_id", "relation", "template_id"])
    ap = [c for c in beh.columns if c.startswith("carrier_alone_logprob_c") and int(c.rsplit("c", 1)[1]) < nc]
    prior = beh.groupby("fact_id")[ap].mean().mean(axis=1).rename("answer_prior")
    D = D.merge(prior, on="fact_id").merge(facts, on=["fact_id", "relation"])
    D = D[D.carrier < nc]  # carriers present for every fact in every model (carriers_everywhere)
    D["frame"] = D.template_id
    D["n_correct_templates"] = D.fact_id.map(beh.groupby("fact_id").correct_at1.sum())
    return D


def zs(d, cols):
    for c in cols:
        s = d[c].std()
        d[c] = (d[c] - d[c].mean()) / s if s and s > 0 else 0.0
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out"); ap.add_argument("--runs", nargs="+", required=True)
    ap.add_argument("--boot", default="param"); ap.add_argument("--n-boot", type=int, default=1000)
    ap.add_argument("--cores", type=int, default=3); ap.add_argument("--set", default="correct")
    a = ap.parse_args()
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    fl = [json.loads(l) for l in open(ROOT / "materials/facts_v1.jsonl")]
    res = {"set": a.set, "boot": a.boot, "n_boot": a.n_boot, "seed": SEED, "models": {}}
    fact_means = {}
    nc_used = carriers_everywhere([s.split("=", 1)[1] for s in a.runs]); res["n_carriers_used"] = nc_used
    for spec in a.runs:
        model, rd = spec.split("=", 1)
        fam = next((v for k, v in TOKMAP.items() if k in model.lower()), None)
        facts = pd.DataFrame([{"fact_id": f["fact_id"], "relation": f["relation"], "subject": f["subject"],
                               "log_cooc_proxy": f["log1p_cooc_dclm"]} for f in fl])
        from transformers import AutoTokenizer
        tok = AutoTokenizer.from_pretrained(model, local_files_only=True)
        facts["n_answer_tokens"] = [len(tok.encode(" " + f["object"], add_special_tokens=False)) for f in fl]
        facts["n_subject_tokens"] = [len(tok.encode(" " + f["subject"], add_special_tokens=False)) for f in fl]
        D = load_model(rd, facts, nc_used)
        if a.set == "correct":
            D = D[D.correct_at1]
        elif a.set == "all10":
            D = D[D.n_correct_templates == 10]
        elif a.set == "new226":  # prereg sensitivity: correct cells of the 226 facts not analysed in G1
            keep = set(json.loads((ROOT / "materials/facts_v1_not_in_G1.json").read_text()))
            D = D[D.correct_at1 & D.fact_id.isin(keep)]
        elif a.set != "all":
            raise SystemExit(f"unknown set {a.set}")
        D = zs(D.copy(), ["n_answer_tokens", "n_subject_tokens", "log_cooc_proxy", "answer_prior"])
        csv = out / f"long_{model.split('/')[-1]}_{a.set}.csv"
        D.to_csv(csv, index=False)
        mres = {"family": fam, "n_rows": int(len(D)), "n_facts": int(D.fact_id.nunique()), "n_carriers_used": nc_used, "fits": {}, "mom": {}}
        for y in ("D1", "D4", "D2", "D3"):
            js = out / f"fit_{model.split('/')[-1]}_{a.set}_{y}.json"
            p = subprocess.run(["Rscript", str(HERE / "p2_analysis.R"), str(csv), str(js), f"y={y}", f"boot={a.boot}",
                                f"n_boot={a.n_boot}", f"seed={SEED}", f"cores={a.cores}", f"nc={nc_used}"], capture_output=True, text=True, cwd=ROOT)
            mres["fits"][y] = json.loads(js.read_text()) if p.returncode == 0 else {"missing": p.stderr[-600:]}
            cm = D.dropna(subset=[y]).groupby(["fact_id", "relation", "frame"], as_index=False)[y].mean().rename(columns={"fact_id": "fact", y: "y"})
            try:
                mres["mom"][y] = henderson3(cm)
            except Exception as e:  # noqa: BLE001
                mres["mom"][y] = {"missing": repr(e)[:300]}
        fact_means[model] = D.groupby(["fact_id", "relation"]).D1.mean()
        res["models"][model] = mres
    # hypotheses per model
    dec = {"per_model": {}}
    for m, r in res["models"].items():
        f1, f4 = r["fits"].get("D1", {}), r["fits"].get("D4", {})
        ok = "point" in f1 and "point" in f4
        if not ok:
            dec["per_model"][m] = {"missing": "D1 or D4 fit missing"}; continue
        mom1, mom4 = r["mom"].get("D1", {}), r["mom"].get("D4", {})
        h1 = all(f["boot"]["ci"]["diff"][0] > 0 for f in (f1, f4)) and all(mm.get("diff", -1) > 0 for mm in (mom1, mom4))
        h1alt = all(f["point"]["icc1"] >= 0.5 and f["boot"]["ci"]["icc1"][0] >= 0.4 for f in (f1, f4)) and \
            all(mm.get("icc1", 0) >= 0.5 for mm in (mom1, mom4))
        dec["per_model"][m] = {"H1": h1, "H1_alt": h1alt,
                               "icc1_D1": f1["point"]["icc1"], "icc1_D1_ci": f1["boot"]["ci"]["icc1"],
                               "icc1_band_D1": band(f1["point"]["icc1"]), "icc1_band_D4": band(f4["point"]["icc1"]),
                               "icc1_upper_lt_0.15": f1["boot"]["ci"]["icc1"][1] < 0.15,
                               "nprime_G_D1": f1["point"]["nprime_G"],
                               "tf_gt_resid_D1": f1["point"]["tf_minus_resid"] > 0,
                               "diff_D1": f1["point"]["diff"], "diff_D1_ci": f1["boot"]["ci"]["diff"],
                               "mom_diff_D1": mom1.get("diff"), "mom_diff_D4": mom4.get("diff")}
    # H3 cross-model rho (estimation only)
    h3 = {}
    for x, y in combinations(fact_means, 2):
        common = sorted(set(fact_means[x].index) & set(fact_means[y].index))
        if len(common) < 10:
            h3[f"{x} vs {y}"] = {"missing": f"{len(common)} common facts"}; continue
        u, v = fact_means[x].loc[common].to_numpy(), fact_means[y].loc[common].to_numpy()
        gx = res["models"][x]["fits"]["D1"]["point"]["G_k"][9]; gy = res["models"][y]["fits"]["D1"]["point"]["G_k"][9]
        rho = float(spearmanr(u, v).statistic)
        h3[f"{x} vs {y}"] = {"n_facts": len(common), "rho": rho, "G10": [gx, gy], "disattenuated": rho / np.sqrt(gx * gy)}
    dec["H3"] = h3
    n = lambda k: sum(1 for v in dec["per_model"].values() if v.get(k))  # noqa: E731
    dec["claims"] = {
        "H1_holds_(>=2_models)": n("H1") >= 2, "H1alt_holds_(>=2_models)": n("H1_alt") >= 2,
        "no_fixed_layer_(ICC1_upper<0.15_in>=2)": n("icc1_upper_lt_0.15") >= 2,
        "single_prompt_poor_(H1_and_nprime>=8_in>=2)": sum(1 for v in dec["per_model"].values() if v.get("H1") and (v.get("nprime_G_D1") or 31) >= 8) >= 2,
        "wording_shifts_together_(tf>resid_and_H1_in>=2)": sum(1 for v in dec["per_model"].values() if v.get("H1") and v.get("tf_gt_resid_D1")) >= 2,
        "fact_depth_unexplained_(H1alt_in>=2)": n("H1_alt") >= 2}
    (out / "p2_results.json").write_text(json.dumps(res, indent=1, default=float))
    (out / "p2_decision.json").write_text(json.dumps(dec, indent=1, default=float))
    print(json.dumps(dec["claims"], indent=1))


if __name__ == "__main__":
    main()
