# Independent completeness + minimum-data check for the five P2 runs.
import json, hashlib, glob, os, sys
import numpy as np, pandas as pd
ROOT = "/home/user/depth-law"
OUT = os.path.dirname(os.path.abspath(__file__))
facts = [json.loads(l) for l in open(f"{ROOT}/materials/facts_v1.jsonl")]
fact_rel = {f["fact_id"]: f["relation"] for f in facts}
assert len(fact_rel) == 300 and len(set(fact_rel.values())) == 20
res = {}
for rd in sorted(glob.glob(f"{ROOT}/results/P2/P2-*")):
    name = os.path.basename(rd); r = {}
    man = json.load(open(f"{rd}/manifest.json"))
    bad = [k for k, v in man.items() if hashlib.sha256(open(f"{rd}/chunks/{k}", "rb").read()).hexdigest() != v["sha256"]]
    parq = sorted(os.path.basename(p) for p in glob.glob(f"{rd}/chunks/*.parquet"))
    r["manifest_bad"] = bad; r["unlisted_parquet"] = sorted(set(parq) - set(man)); r["manifest_ok_flags"] = all(v["ok"] for v in man.values())
    ev = [json.loads(l) for l in open(f"{rd}/log.jsonl")]
    last = ev[-1]; r["last_done"] = last["event"] == "done" and last.get("all_ok") and last.get("n_facts") == 300
    r["starts"] = [(e["model"], e["dtype"]) for e in ev if e["event"] == "start"]
    r["meta_rev"] = json.load(open(f"{rd}/meta.json"))["hf_revision"]
    b = pd.concat([pd.read_parquet(p) for p in sorted(glob.glob(f"{rd}/chunks/b*.parquet"))])
    c = pd.concat([pd.read_parquet(p) for p in sorted(glob.glob(f"{rd}/chunks/c*.parquet"))])
    cells_b = set(zip(b.fact_id, b.template_id)); cells_c = set(zip(c.fact_id, c.template_id))
    allcells = {(f, t) for f in fact_rel for t in range(10)}
    r["b_rows"] = len(b); r["b_dup"] = int(b.duplicated(["fact_id", "template_id"]).sum())
    r["cells_b_complete"] = cells_b == allcells; r["cells_c_complete"] = cells_c == allcells
    r["p_nan"] = int(c.p_object.isna().sum())
    car = c.groupby(["fact_id", "template_id"]).carrier.agg(lambda s: tuple(sorted(set(s))))
    r["carrier_sets"] = sorted(set(map(str, car.unique())))
    nl = c.groupby(["fact_id", "template_id", "carrier"]).layer.agg(["nunique", "min", "max", "size"])
    r["layers_per_curve"] = sorted(set(map(tuple, nl.to_numpy().tolist())))
    r["relation_match"] = bool((b.relation == b.fact_id.map(fact_rel)).all())
    ok = (not bad and not r["unlisted_parquet"] and r["last_done"] and r["cells_b_complete"] and r["cells_c_complete"]
          and r["p_nan"] == 0 and r["b_dup"] == 0 and len(r["layers_per_curve"]) == 1)
    r["complete"] = bool(ok)
    corr = b[b.correct_at1.astype(bool)]
    nper = corr.groupby("fact_id").size()
    f2 = nper[nper >= 2].index
    r["n_correct_cells"] = len(corr); r["facts_any_correct"] = int((nper >= 1).sum())
    r["facts_2plus"] = len(f2); r["rels_2plus"] = len({fact_rel[f] for f in f2})
    r["included"] = bool(ok and r["facts_2plus"] >= 150 and r["rels_2plus"] >= 15)
    res[name] = r
    print(name, {k: v for k, v in r.items()})
json.dump(res, open(f"{OUT}/s1_inclusion.json", "w"), indent=1, default=str)
