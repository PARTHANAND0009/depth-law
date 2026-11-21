"""P2 A1: sample 300 facts (20 relations x 15, 5 per co-occurrence tercile) per materials/SAMPLING_RULES_v1.md.
Usage: python scripts/p2_sample_facts.py   (writes materials/facts_v1.jsonl, .sha256, facts_v1_report.md)"""
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from transformers import AutoTokenizer

ROOT = Path(__file__).resolve().parents[1]
SEED = 20261121
TOK = {"llama31": "meta-llama/Llama-3.1-8B", "qwen3": "Qwen/Qwen3-8B", "pythia": "EleutherAI/pythia-1.4b",
       "olmo2": "allenai/OLMo-2-1124-7B"}
WEAK = {"the", "a", "an", "of", "and", "de", "la", "le", "el", "university", "saint", "st", "san", "new", "north",
        "south", "east", "west", "royal", "national", "king", "prince", "lake", "mount", "fort", "port", "united", "republic"}
INFLUENTIAL = {"company_ceo", "developer", "manufacturer"}  # Part 0a, |LOO influence| > 0.1


def main():
    f = pd.read_parquet(ROOT / "data/facts.parquet")
    c = pd.read_parquet(ROOT / "data/counts_exact.parquet")[["fact_id", "exact_dclm-baseline"]]
    f = f.merge(c, on="fact_id", how="left")
    toks = {k: AutoTokenizer.from_pretrained(v, local_files_only=True) for k, v in TOK.items()}
    for k, t in toks.items():
        ids = [t.encode(" " + o, add_special_tokens=False)[0] for o in f.object]
        stored = f[f"obj_first_tok_{k}"].to_numpy()
        assert np.array_equal(np.asarray(ids), stored), f"first-token ids differ from stored for {k}"
        f[f"first_{k}"] = ids
        f[f"first_txt_{k}"] = [t.decode([i]).strip() for i in ids]
    ok_distinct = np.ones(len(f), bool)
    ok_content = np.ones(len(f), bool)
    for k in TOK:
        shared = f.groupby(["relation", f"first_{k}"]).object.transform("nunique") > 1
        ok_distinct &= ~shared.to_numpy()
        txt = f[f"first_txt_{k}"]
        ok_content &= ((txt.str.len() >= 2) & txt.str.contains(r"[A-Za-z]") & ~txt.str.lower().isin(WEAK)).to_numpy()
    f["ok_distinct"], f["ok_content"] = ok_distinct, ok_content
    f["eligible"] = ok_distinct & ok_content & f["exact_dclm-baseline"].notna()
    f["log1p_cooc_dclm"] = np.log1p(f["exact_dclm-baseline"])
    rel_rows = []
    for rel, g in f.groupby("relation"):
        e = g[g.eligible].copy()
        fail_frac = float((~(g.ok_distinct & g.ok_content)).mean())
        n_t = [0, 0, 0]
        if len(e) >= 3:
            e["tercile"] = pd.qcut(e.log1p_cooc_dclm.rank(method="first"), 3, labels=False)
            n_t = [int((e.tercile == t).sum()) for t in range(3)]
        reason = []
        if len(e) < 15:
            reason.append(f"{len(e)} eligible < 15")
        if min(n_t) < 5:
            reason.append(f"tercile sizes {n_t} < 5")
        if fail_frac >= 0.2:
            reason.append(f"{fail_frac:.2f} of pool fail distinct/contentful first token")
        rel_rows.append({"relation": rel, "n_pool": len(g), "n_eligible": len(e), "fail_frac": fail_frac,
                         "tercile_sizes": n_t, "eligible_relation": not reason, "reason": "; ".join(reason),
                         "influential": rel in INFLUENTIAL})
    R = pd.DataFrame(rel_rows)
    cand = R[R.eligible_relation].sort_values(["n_eligible", "relation"], ascending=[False, True])
    chosen = sorted(cand.relation.head(20))
    R["selected"] = R.relation.isin(chosen)
    rng = np.random.default_rng(SEED)
    out = []
    for rel in chosen:
        e = f[(f.relation == rel) & f.eligible].copy()
        e["tercile"] = pd.qcut(e.log1p_cooc_dclm.rank(method="first"), 3, labels=False)
        for t in range(3):
            pool = e[e.tercile == t].sort_values("fact_id")
            pick = rng.choice(len(pool), 5, replace=False)
            for _, r in pool.iloc[sorted(pick)].iterrows():
                out.append({"fact_id": r.fact_id, "relation": rel, "subject": r.subject, "object": r.object, "tercile": int(t),
                            "log1p_cooc_dclm": float(r.log1p_cooc_dclm), "cooc_label": "PROXY (DCLM-baseline EXACT phrase count)",
                            "first_token": {k: {"id": int(r[f"first_{k}"]), "text": r[f"first_txt_{k}"]} for k in TOK},
                            "influential_relation": rel in INFLUENTIAL})
    assert len(out) == 300 if len(chosen) == 20 else True
    dst = ROOT / "materials/facts_v1.jsonl"
    dst.write_text("".join(json.dumps(o, ensure_ascii=False) + "\n" for o in out))
    sha = hashlib.sha256(dst.read_bytes()).hexdigest()
    (ROOT / "materials/facts_v1.jsonl.sha256").write_text(f"{sha}  materials/facts_v1.jsonl\n")
    L = ["# P2 facts v1: selection report", "",
         f"- **Rules:** `materials/SAMPLING_RULES_v1.md`; seed {SEED}.",
         f"- **Facts:** {len(out)}, from {len(chosen)} relations; sha256 {sha}.", "",
         "| relation | pool | eligible | fail frac | tercile sizes | eligible relation | selected | influential (0a) | reason excluded |",
         "|---|---|---|---|---|---|---|---|---|"]
    for _, r in R.sort_values("relation").iterrows():
        L.append(f"| {r.relation} | {r.n_pool} | {r.n_eligible} | {r.fail_frac:.2f} | {r.tercile_sizes} | {r.eligible_relation} | {r.selected} | {r.influential} | {r.reason} |")
    (ROOT / "materials/facts_v1_report.md").write_text("\n".join(L) + "\n")
    print(f"{len(out)} facts, {len(chosen)} relations, sha256 {sha}")
    print(R.sort_values("relation")[["relation", "n_eligible", "fail_frac", "tercile_sizes", "eligible_relation", "selected", "reason"]].to_string())


if __name__ == "__main__":
    main()
