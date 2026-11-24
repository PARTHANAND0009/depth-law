# Build the carrier-level analysis table (correct set) from raw chunks + materials, own code.
import json, glob, os
import numpy as np, pandas as pd
from transformers import AutoTokenizer
ROOT = "/home/user/depth-law"; OUT = os.path.dirname(os.path.abspath(__file__))
RUNS = {"llama": ("P2-Llama-3.1-8B-ff119ca-20261124T164743Z", "models--meta-llama--Llama-3.1-8B"),
        "olmo": ("P2-OLMo-2-1124-7B-ff119ca-20261124T171447Z", "models--allenai--OLMo-2-1124-7B")}
facts = pd.DataFrame([json.loads(l) for l in open(f"{ROOT}/materials/facts_v1.jsonl")]).set_index("fact_id")
para = pd.DataFrame([json.loads(l) for l in open(f"{ROOT}/materials/paraphrases_v1.jsonl")])

def depth(g):
    p = g.sort_values("layer").p_object.to_numpy().astype(np.float64)  # float16 -> float64 exact
    L = len(p); pf = p[-1]
    if pf == 0: return pd.Series({"D1": np.nan, "D4": np.nan, "pf0": True, "pflt": True})
    ok = p >= 0.5 * pf
    # l* = min l such that ok[l'] for all l' >= l
    bad = np.where(~ok)[0]
    lstar = 0 if len(bad) == 0 else bad.max() + 1
    d1 = (lstar + 1) / L
    d4 = 1 - np.mean(np.minimum(1.0, p / pf))
    return pd.Series({"D1": d1, "D4": d4, "pf0": False, "pflt": pf < 1e-4})

summary = {}
for key, (run, hub) in RUNS.items():
    rd = f"{ROOT}/results/P2/{run}"
    snap = glob.glob(f"{ROOT}/cache/hf/hub/{hub}/snapshots/*/tokenizer.json")[0]
    tok = AutoTokenizer.from_pretrained(os.path.dirname(snap))
    ntok = lambda s: len(tok(s, add_special_tokens=False)["input_ids"])
    b = pd.concat([pd.read_parquet(p) for p in sorted(glob.glob(f"{rd}/chunks/b*.parquet"))])
    c = pd.concat([pd.read_parquet(p) for p in sorted(glob.glob(f"{rd}/chunks/c*.parquet"))])
    curves = c.groupby(["fact_id", "template_id", "carrier"]).apply(depth, include_groups=False).reset_index()
    s = {"curves": len(curves), "pf0_all": int(curves.pf0.sum()), "pflt_all": int(curves.pflt.sum())}
    corr = b[b.correct_at1.astype(bool)][["fact_id", "template_id", "carrier_alone_logprob_c0", "carrier_alone_logprob_c1", "carrier_alone_logprob_c2"]]
    d = curves.merge(corr, on=["fact_id", "template_id"], how="inner")
    d = d[~d.pf0]
    # fact-level covariates
    fl = pd.DataFrame(index=sorted(d.fact_id.unique()))
    fl["relation"] = facts.loc[fl.index, "relation"]
    fl["log_cooc_proxy"] = facts.loc[fl.index, "log1p_cooc_dclm"].astype(float)
    fl["n_answer_tokens"] = [ntok(" " + facts.loc[f, "object"]) for f in fl.index]
    def nsub(f):
        subj = facts.loc[f, "subject"]; rel = facts.loc[f, "relation"]
        ts = para[para.relation == rel].template
        return np.mean([ntok(subj) if t.startswith("{}") else ntok(" " + subj) for t in ts])
    fl["n_subject_tokens"] = [nsub(f) for f in fl.index]
    ap = b.drop_duplicates("fact_id").set_index("fact_id")[["carrier_alone_logprob_c0", "carrier_alone_logprob_c1", "carrier_alone_logprob_c2"]]
    fl["answer_prior"] = ap.loc[fl.index].mean(axis=1)
    # sanity: carrier-alone logprobs constant within fact
    s["ap_const_within_fact"] = bool((b.groupby("fact_id")[["carrier_alone_logprob_c0", "carrier_alone_logprob_c1", "carrier_alone_logprob_c2"]].nunique() == 1).all().all())
    for v in ["log_cooc_proxy", "n_answer_tokens", "n_subject_tokens", "answer_prior"]:
        fl[v + "_raw"] = fl[v]; fl[v] = (fl[v] - fl[v].mean()) / fl[v].std(ddof=1)
    d = d.merge(fl.drop(columns="relation"), left_on="fact_id", right_index=True)
    d["relation"] = facts.loc[d.fact_id, "relation"].to_numpy()
    d["fact"] = d.fact_id; d["frame"] = d.template_id
    s.update(n_rows=len(d), n_facts=d.fact_id.nunique(), n_rel=d.relation.nunique(), n_cells=len(d.groupby(["fact_id", "template_id"])))
    summary[key] = s; print(key, s)
    d.to_csv(f"{OUT}/tab_{key}.csv", index=False)
json.dump(summary, open(f"{OUT}/s2_summary.json", "w"), indent=1)
