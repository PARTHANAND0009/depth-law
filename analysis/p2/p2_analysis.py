"""P2 confirmatory analysis (prereg/P2_prompt_vs_fact.md). One call per set of model run dirs.

python analysis/p2/p2_analysis.py <out_dir> --runs MODEL=RUN_DIR [MODEL=RUN_DIR ...] [--boot param]
       [--n-boot 1000] [--cores 3] [--set SET] [--primary <confirmatory out_dir>] [--n-perm 1000]
SET: correct (confirmatory) | new226 | all | all10 | nomanufacturer | tcov (sensitivities, with CIs)
     | lofo (leave-one-frame-out, point estimates) | h4 (EXPLORATORY frame fixed effects, point estimates).
Runs: exactly one run per model (duplicates are refused). Per prereg section 1 it is the model's first run that passes
the completeness rule; a later run replaces it only through a committed deviation naming the run_id it replaces.
Models: a model is included only if its run is complete (completeness) and it has enough data (min_data); otherwise it
is MISSING. nc (carriers used) = the smallest carrier count among the included models; it is written to
p2_results.json. Every other set must pass --primary <confirmatory out_dir>: it reuses that nc and must be given the
same --runs (refused otherwise). Only --set correct is gating; other sets carry "gating": false.
The gating call needs one --runs entry for each of the five prereg models (MODEL=none for a model with no run; it is
MISSING (not run)), 1000 bootstrap resamples and 1000 null datasets; every run's start events must name that model with
dtype float32 and revision main. --test (synthetic runs only) lifts these checks and marks every output non-gating.
Steps per included model: per-carrier depths D1-D4 from the stored (layer, p_object, rank) curves -> inclusion set
-> REML fits (p2_analysis.R) for D1 and D4 (primary/robustness) and D2, D3 (secondary) -> Henderson III MoM on
covariate-residualised, carrier-averaged cell means (p2_mom.py) -> shuffled-fact null (set correct, D1; p2_null.R)
-> rules, each evaluated on the fits it uses (prereg section 4). Then the family-level claims and H3.
p2_results.json is written before the decisions, so a failing decision step still leaves the fits on disk.
"""
import argparse
import hashlib
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
PREREG_MODELS = ("Qwen/Qwen3-8B", "meta-llama/Llama-3.1-8B", "EleutherAI/pythia-1.4b", "EleutherAI/pythia-2.8b",
                 "allenai/OLMo-2-1124-7B")  # prereg section 1
N_BOOT, N_NULL = 1000, 1000  # prereg section 4
MATERIALS_SHA256 = {  # prereg section 1
    "facts_v1.jsonl": "0f596cd7385a318b9f2d8bea84d5d8cf483ee62c9333fa3bec0ecd60d9f1bfe3",
    "paraphrases_v1.jsonl": "dd481a359860bcb4a8cfec6ed6e85a35904dfcc42b7042a4278d030c1c707548",
    "carriers_v1.jsonl": "dea5a8910cb356d8b42c8d91f09db9cecb646a924bba23e9ea3b07578258aadd"}


def band(icc):
    """Descriptive band for fact ICC(1) (prereg P2 section 5; not a decision rule)."""
    return next(name for hi, name in BANDS if icc < hi) if icc is not None else None


def family(model):
    fam = next((v for k, v in TOKMAP.items() if k in model.lower()), None)
    if fam is None:
        raise SystemExit(f"unknown model family for {model}; families are {sorted(set(TOKMAP.values()))}")
    return fam


def stable_from(ok):
    if not ok[-1]:
        return None
    l = len(ok) - 1
    while l > 0 and ok[l - 1]:
        l -= 1
    return l


def depths(curve_p, curve_rank):
    """D1-D4 for one carrier curve. D1 and D4 are undefined (None) when the final p is 0 (float16 underflow):
    every layer would pass p >= 0.5 * 0 (prereg section 2)."""
    p = np.asarray(curve_p, float); L = len(p)
    d2 = stable_from(list(p >= 0.1)); d3 = stable_from(list(np.asarray(curve_rank) == 1))
    if p[-1] > 0:
        d1 = (stable_from(list(p >= 0.5 * p[-1])) + 1) / L
        d4 = 1 - float(np.mean(np.minimum(1, p / p[-1])))
    else:
        d1 = d4 = None
    return d1, (None if d2 is None else (d2 + 1) / L), (None if d3 is None else (d3 + 1) / L), d4


def completeness(run_dir, fact_ids, n_templates=N_TEMPLATES):
    """THE completeness rule (prereg section 1); scripts/p2_done_check.py calls this same function.
    Returns (ok, reason, nc_run)."""
    rd = Path(run_dir)
    if not (rd / "manifest.json").exists():
        return False, "no manifest.json (the run did not reach its end)", 0
    man = json.loads((rd / "manifest.json").read_text())
    if not man or not all(v["ok"] for v in man.values()):
        return False, "checksum failure or empty manifest", 0
    for name, v in man.items():  # recomputed here, so a copy damaged after the run is caught
        f = rd / "chunks" / name
        if not f.exists() or hashlib.sha256(f.read_bytes()).hexdigest() != v["sha256"]:
            return False, f"checksum mismatch or missing file on recomputation: {name}", 0
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
    want = {(f, t) for f in fact_ids for t in range(n_templates)}
    have = set(zip(beh.fact_id, beh.template_id.astype(int)))
    if have != want or len(beh) != len(want):
        return False, f"behaviour rows cover {len(have & want)} of {len(want)} fact x paraphrase cells", 0
    long = pd.concat([pd.read_parquet(p, columns=["fact_id", "template_id", "carrier", "layer", "p_object"]) for p in chunks])
    if int(long.p_object.isna().sum()) > 0:
        return False, f"{int(long.p_object.isna().sum())} NaN p values", 0
    nl = long.groupby(["fact_id", "template_id", "carrier"]).layer.nunique()
    if nl.nunique() != 1:
        return False, "unequal layer counts across curves", 0
    cs = long.groupby(["fact_id", "template_id"]).carrier.agg(lambda s: tuple(sorted(set(s))))
    if len(cs) != len(want):
        return False, f"curves cover {len(cs)} of {len(want)} fact x paraphrase cells", 0
    if not all(c == tuple(range(len(c))) for c in cs):
        return False, "carrier ids are not 0..k-1 in some cell", 0
    nc_fact = cs.map(len).groupby(level=0).min()
    if nc_fact.min() < 2:
        return False, "some fact has fewer than 2 carriers", 0
    return True, "complete", int(nc_fact.min())


def run_identity(run_dir, model):
    """Every 'start' event of the run (the pilot and any resume) must name this model, dtype float32, and every meta
    file revision main (prereg section 1). Returns (ok, reason)."""
    rd = Path(run_dir)
    starts = [e for e in (json.loads(l) for l in open(rd / "log.jsonl")) if e.get("event") == "start"]
    if not starts:
        return False, "no start event"
    for e in starts:
        if e.get("model") != model:
            return False, f"start event names {e.get('model')}, not {model}"
        if e.get("dtype") != "torch.float32":
            return False, f"dtype {e.get('dtype')}, not torch.float32"
    for m in [rd / "meta.json", *sorted(rd.glob("meta_resume_*.json"))]:
        if m.exists() and json.loads(m.read_text()).get("hf_revision") != "main":
            return False, f"{m.name}: revision is not main"
    return True, "ok"


def subject_tokens_in_context(tok, fl):
    """n_subject_tokens (round-3 non-blocking 13): the subject's token count as it appears in the fact's 10 paraphrases
    (no leading space at the start of a prompt, a leading space after a word), averaged over the paraphrases."""
    paras = {}
    for l in open(ROOT / "materials/paraphrases_v1.jsonl"):
        q = json.loads(l); paras.setdefault(q["relation"], []).append(q["template"])
    enc = lambda x: len(tok.encode(x, add_special_tokens=False))  # noqa: E731
    out = []
    for f in fl:
        n = []
        for t in paras[f["relation"]]:
            before = t.split("{}", 1)[0].rstrip()
            n.append(enc(before + " " + f["subject"]) - enc(before) if before else enc(f["subject"]))
        out.append(float(np.mean(n)))
    return out


def min_data(run_dir):
    """Minimum-data rule (prereg section 3), from the behaviour rows only (it does not depend on nc)."""
    beh = pd.concat([pd.read_parquet(p, columns=["fact_id", "relation", "correct_at1"])
                     for p in sorted((Path(run_dir) / "chunks").glob("b*.parquet"))])
    nct = beh.groupby("fact_id").correct_at1.sum()
    f2 = set(nct[nct >= 2].index)
    n_rel = beh[beh.fact_id.isin(f2)].relation.nunique()
    entry = {"facts_with_2plus_correct": len(f2), "relations_with_such_facts": int(n_rel)}
    return len(f2) >= MIN_FACTS_2CORRECT and n_rel >= MIN_RELATIONS, entry


def load_model(run_dir, facts, nc):
    run_dir = Path(run_dir)
    long = pd.concat([pd.read_parquet(p) for p in sorted((run_dir / "chunks").glob("c*.parquet"))])
    beh = pd.concat([pd.read_parquet(p) for p in sorted((run_dir / "chunks").glob("b*.parquet"))])
    long = long[long.carrier < nc]  # carriers present for every fact in every included model (fallback 1)
    rows = []
    for (fid, rel, t, c), g in long.sort_values("layer").groupby(["fact_id", "relation", "template_id", "carrier"]):
        p = g.p_object.to_numpy(np.float32)
        d1, d2, d3, d4 = depths(p, g["rank"].to_numpy())
        rows.append((fid, rel, int(t), int(c), d1, d2, d3, d4, bool(p[-1] <= 0), bool(p[-1] < 1e-4)))
    D = pd.DataFrame(rows, columns=["fact_id", "relation", "template_id", "carrier", "D1", "D2", "D3", "D4",
                                    "p_final_zero", "p_final_lt_1e4"])
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
    """Covariate-residualised, carrier-averaged cell means for Henderson III (prereg section 4)."""
    d = D.dropna(subset=[y]).copy()
    X = [np.ones(len(d))] + [d[c].to_numpy(float) for c in cov if c in d and d[c].std() > 0]
    X += [(d.carrier == k).to_numpy(float) for k in sorted(d.carrier.unique())[1:]]
    X = np.column_stack(X); yy = d[y].to_numpy(float)
    b, *_ = np.linalg.lstsq(X, yy, rcond=None)
    d["yr"] = yy - X @ b
    return d.groupby(["fact_id", "relation", "frame"], as_index=False).yr.mean().rename(columns={"fact_id": "fact", "yr": "y"})


def mom(D, y, cov):
    try:
        return henderson3(mom_cells(D, y, cov))
    except Exception as e:  # noqa: BLE001
        return {"missing": repr(e)[:300]}


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


def check_materials():
    for f, want in MATERIALS_SHA256.items():
        got = hashlib.sha256((ROOT / "materials" / f).read_bytes()).hexdigest()
        if got != want:
            raise SystemExit(f"materials/{f} sha256 {got} differs from the preregistered {want}")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("out"); ap.add_argument("--runs", nargs="+", required=True)
    ap.add_argument("--boot", default="param"); ap.add_argument("--n-boot", type=int, default=1000)
    ap.add_argument("--cores", type=int, default=3); ap.add_argument("--set", default="correct")
    ap.add_argument("--primary", default=None, help="sensitivity sets: the confirmatory call's out_dir")
    ap.add_argument("--n-perm", type=int, default=N_NULL, help="fact-share null: simulated datasets (set correct only)")
    ap.add_argument("--test", action="store_true", help="synthetic runs only: lifts the prereg checks; output non-gating")
    a = ap.parse_args(argv)
    if a.set not in CI_SETS + POINT_SETS:
        raise SystemExit(f"unknown set {a.set}")
    if a.boot != "param":
        raise SystemExit("only --boot param is preregistered")
    check_materials()
    models = [s.split("=", 1)[0] for s in a.runs]
    if not a.test:
        if sorted(models) != sorted(PREREG_MODELS):
            raise SystemExit(f"--runs must name each prereg model once (MODEL=none if it has no run): {PREREG_MODELS}")
        if a.n_boot != N_BOOT or (a.set == "correct" and a.n_perm != N_NULL):
            raise SystemExit(f"the prereg fixes --n-boot {N_BOOT} and --n-perm {N_NULL}")
    dirs = [str(Path(s.split("=", 1)[1]).resolve()) for s in a.runs if s.split("=", 1)[1] != "none"]
    if len(set(dirs)) != len(dirs):
        raise SystemExit("the same run dir is given for two models")
    if len(set(models)) != len(models):
        raise SystemExit("one run per model: duplicate model in --runs (prereg section 1: the first complete run; a "
                         "replacement needs a committed deviation naming the run_id it replaces)")
    for m in models:
        family(m)
    primary = None
    if a.set == "correct":
        if a.primary:
            raise SystemExit("--primary is for sensitivity sets only")
    else:
        if not a.primary:
            raise SystemExit("sensitivity sets need --primary <confirmatory out_dir> (prereg section 3)")
        primary = json.loads((Path(a.primary) / "p2_results.json").read_text())
        if primary.get("set") != "correct" or sorted(primary["runs"]) != sorted(a.runs):
            raise SystemExit("--runs differ from the confirmatory call's runs (or --primary is not a confirmatory call)")
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    fl = [json.loads(l) for l in open(ROOT / "materials/facts_v1.jsonl")]
    fact_ids = [f["fact_id"] for f in fl]
    gating = a.set == "correct" and not a.test
    res = {"set": a.set, "gating": gating, "test": a.test, "boot": a.boot, "n_boot": a.n_boot, "seed": SEED,
           "runs": a.runs, "models": {}}
    # 1. inclusion of models: completeness, then minimum data; nc over the included models (prereg sections 1, 3)
    included = {}
    for spec in a.runs:
        model, rd = spec.split("=", 1)
        if rd == "none":
            res["models"][model] = {"family": family(model), "status": "MISSING (not run)"}
            continue
        if not a.test:
            idok, idwhy = run_identity(rd, model)
            if not idok:
                raise SystemExit(f"run {rd} does not belong to {model}: {idwhy}")
        ok, why, ncr = completeness(rd, fact_ids)
        if not ok:
            res["models"][model] = {"family": family(model), "status": f"MISSING (incomplete): {why}"}
            continue
        enough, entry = min_data(rd)
        if not enough:
            res["models"][model] = {"family": family(model), "status": "MISSING (insufficient data)", "min_data": entry}
            continue
        included[model] = (rd, ncr, entry)
    nc_avail = min((v[1] for v in included.values()), default=0)
    nc_used = primary["n_carriers_used"] if primary else nc_avail
    if primary and nc_used != nc_avail:
        raise SystemExit(f"nc mismatch: confirmatory {nc_used}, available now {nc_avail}")
    res["n_carriers_used"] = nc_used
    fact_means, kbar = {}, {}
    for model, (rd, ncr, entry) in included.items():
        fam = family(model)
        facts = pd.DataFrame([{"fact_id": f["fact_id"], "relation": f["relation"], "subject": f["subject"],
                               "log_cooc_proxy": f["log1p_cooc_dclm"]} for f in fl])
        from transformers import AutoTokenizer
        tok = AutoTokenizer.from_pretrained(model, local_files_only=True)
        facts["n_answer_tokens"] = [len(tok.encode(" " + f["object"], add_special_tokens=False)) for f in fl]
        facts["n_subject_tokens"] = subject_tokens_in_context(tok, fl)
        D = load_model(rd, facts, nc_used)
        n_pzero, n_psmall = int(D.p_final_zero.sum()), int(D.p_final_lt_1e4.sum())
        # 2. inclusion set
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
                "min_data": entry, "n_curves_p_final_zero": n_pzero, "n_curves_p_final_lt_1e-4": n_psmall,
                "n_rows": int(len(D)), "n_facts": int(D.fact_id.nunique()), "fits": {}, "mom": {}}
        extra = ["tcov=1"] if a.set == "tcov" else []
        if a.set in CI_SETS:
            csv = out / f"long_{tag}.csv"; D.to_csv(csv, index=False)
            for y in ("D1", "D4", "D2", "D3"):
                mres["fits"][y] = rfit(csv, out / f"fit_{tag}_{y}.json", y, a, nc_used, a.n_boot, extra)
                mres["mom"][y] = mom(D, y, cov)
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
                mres["mom"][f"drop{k}"] = {y: mom(Dk, y, cov) for y in ("D1", "D4")}
        else:  # h4, EXPLORATORY
            csv = out / f"long_{tag}.csv"; D.to_csv(csv, index=False)
            for y in ("D1", "D4"):
                mres["fits"][y] = rfit(csv, out / f"fit_{tag}_{y}.json", y, a, nc_used, 0, ["h4=1"])
        res["models"][model] = mres
    (out / "p2_results.json").write_text(json.dumps(res, indent=1, default=float))  # before the decisions
    dec = decide(res, a.set, fact_means, kbar, nc_used, gating)
    (out / "p2_decision.json").write_text(json.dumps(dec, indent=1, default=float))
    print(json.dumps(dec.get("claims", {}), indent=1))


def fit_ok(f):
    return isinstance(f, dict) and f.get("status") == "ok" and "point" in f and "ci" in f.get("boot", {})


def decide(res, set_name, fact_means, kbar, nc, gating=None):
    """Each rule is evaluated on the fits it uses (prereg section 4): a rule whose inputs are MISSING is None (MISSING)
    for that model and does not count toward any family. Rule inputs:
      H1, H1-alt: REML D1 and D4 fits and MoM D1 and D4;  no fixed layer: REML D1;  n' and tf-resid: REML D1 (plus H1);
      fact share > 0: the shuffled-fact null on D1."""
    dec = {"set": set_name, "gating": (set_name == "correct") if gating is None else gating, "n_carriers_used": nc,
           "per_model": {}}
    if set_name not in CI_SETS:
        dec["note"] = "point estimates only; no decision rules apply to this set"
        return dec
    for m, r in res["models"].items():
        if r.get("status") != "ok":
            dec["per_model"][m] = {"family": r.get("family"), "status": r.get("status")}; continue
        f1, f4 = r["fits"].get("D1", {}), r["fits"].get("D4", {})
        mom1, mom4 = r["mom"].get("D1", {}), r["mom"].get("D4", {})
        ok1, ok4 = fit_ok(f1), fit_ok(f4)
        okm = "diff" in mom1 and "diff" in mom4
        both = ok1 and ok4 and okm
        h1 = (all(f["boot"]["ci"]["diff"][0] > 0 for f in (f1, f4)) and all(mm["diff"] > 0 for mm in (mom1, mom4))) if both else None
        h1alt = (all(f["point"]["icc1"] >= 0.5 and f["boot"]["ci"]["icc1"][0] >= 0.4 for f in (f1, f4))
                 and all(mm["diff"] < 0 for mm in (mom1, mom4))) if both else None
        # n' (round-3 non-blocking 3): undefined when G(k) < 0.8 for all k <= 30. G(k) tends to fact/(fact + fc/nc), a
        # ceiling set by carrier noise that paraphrases cannot average out, so an undefined n' does NOT meet the
        # "it takes N paraphrases" rule; the ceiling is reported.
        npr = f1["point"]["nprime_G"] if ok1 else None
        vc1 = f1.get("vc", {}) if ok1 else {}
        g_ceiling = (vc1.get("fact", 0.0) / (vc1.get("fact", 0.0) + vc1.get("fc", 0.0) / nc)
                     if ok1 and vc1.get("fact", 0.0) > 0 else (0.0 if ok1 else None))
        nul = r.get("null", {})
        null_ok = isinstance(nul.get("p"), (int, float)) and nul.get("status", "ok") == "ok"
        pm = {"family": r["family"], "status": "ok",
              "inputs": {"D1_fit": f1.get("status"), "D4_fit": f4.get("status"), "MoM_D1": "ok" if "diff" in mom1 else "MISSING",
                         "MoM_D4": "ok" if "diff" in mom4 else "MISSING", "null": nul.get("status", "ok") if null_ok else "MISSING"},
              "H1": h1, "H1_alt": h1alt,
              "icc1_upper_lt_0.15": (f1["boot"]["ci"]["icc1"][1] < 0.15) if ok1 else None,
              "nprime_G_D1": npr, "nprime_undefined": (npr is None) if ok1 else None, "G_ceiling_D1": g_ceiling,
              "nprime_ge_8": ((npr is not None and npr >= 8) if ok1 else None),
              "tf_gt_resid_D1": (f1["point"]["tf_minus_resid"] > 0) if ok1 else None,
              "null_p_D1": nul.get("p") if null_ok else None, "null_lt_0.01": (nul["p"] < 0.01) if null_ok else None}
        if ok1:
            pm.update({"icc1_D1": f1["point"]["icc1"], "icc1_D1_ci": f1["boot"]["ci"]["icc1"], "icc1_band_D1": band(f1["point"]["icc1"]),
                       "diff_D1": f1["point"]["diff"], "diff_D1_ci": f1["boot"]["ci"]["diff"]})
        if ok4:
            pm.update({"icc1_D4": f4["point"]["icc1"], "icc1_D4_ci": f4["boot"]["ci"]["icc1"], "icc1_band_D4": band(f4["point"]["icc1"]),
                       "diff_D4": f4["point"]["diff"], "diff_D4_ci": f4["boot"]["ci"]["diff"]})
        pm["mom_diff_D1"], pm["mom_diff_D4"] = mom1.get("diff"), mom4.get("diff")
        pm["rules_missing"] = sorted(k for k in ("H1", "H1_alt", "icc1_upper_lt_0.15", "nprime_ge_8", "tf_gt_resid_D1", "null_lt_0.01")
                                     if pm[k] is None)
        dec["per_model"][m] = pm
    ok = {m: v for m, v in dec["per_model"].items() if v.get("status") == "ok"}
    fams = lambda pred: sorted({v["family"] for v in ok.values() if pred(v) is True})  # noqa: E731
    h1f, h1af = fams(lambda v: v["H1"]), fams(lambda v: v["H1_alt"])
    conflict = len(h1f) >= 2 and len(h1af) >= 2
    dec["families"] = {"H1": h1f, "H1_alt": h1af, "included_models": sorted(ok), "included_families": fams(lambda v: True)}
    dec["claims"] = {
        "H1_holds_(>=2_families)": len(h1f) >= 2, "H1alt_holds_(>=2_families)": len(h1af) >= 2,
        "model_dependent_(H1_and_H1alt_both_>=2_families)": conflict,
        "no_fixed_layer_(ICC1_D1_upper<0.15_in>=2_families)": len(fams(lambda v: v["icc1_upper_lt_0.15"])) >= 2,
        "single_prompt_poor_(H1_and_nprime>=8_in>=2_families)":
            len(fams(lambda v: v["H1"] is True and v["nprime_ge_8"] is True)) >= 2 and not conflict,
        "wording_shifts_together_(H1_and_tf>resid_in>=2_families)":
            len(fams(lambda v: v["H1"] is True and v["tf_gt_resid_D1"] is True)) >= 2 and not conflict,
        "fact_depth_unexplained_(H1alt_in>=2_families)": len(h1af) >= 2 and not conflict,
        "fact_share_gt0_(null_p<0.01_in>=2_families)":
            (len(fams(lambda v: v["null_lt_0.01"])) >= 2) if set_name == "correct" else None}
    h3 = {}
    for x, y in combinations(fact_means, 2):
        fx, fy = res["models"][x]["fits"].get("D1", {}), res["models"][y]["fits"].get("D1", {})
        if not (fit_ok(fx) and fit_ok(fy)):
            h3[f"{x} vs {y}"] = {"missing": "D1 fit MISSING in one of the two models"}; continue
        common = sorted(set(fact_means[x].dropna().index) & set(fact_means[y].dropna().index))
        if len(common) < 10:
            h3[f"{x} vs {y}"] = {"missing": f"{len(common)} common facts"}; continue
        u, v = fact_means[x].loc[common].to_numpy(), fact_means[y].loc[common].to_numpy()
        gx, gy = g_at(fx["vc"], kbar[x], nc), g_at(fy["vc"], kbar[y], nc)
        rho = float(spearmanr(u, v).statistic)
        h3[f"{x} vs {y}"] = {"n_facts": len(common), "rho": rho, "kbar": [kbar[x], kbar[y]], "G_kbar": [gx, gy],
                             "disattenuated_approx": rho / np.sqrt(gx * gy) if gx > 0 and gy > 0 else None}
    dec["H3"] = h3
    return dec


if __name__ == "__main__":
    main()
