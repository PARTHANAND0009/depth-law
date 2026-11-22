"""Synthetic P2 run in the exact runner format (chunks/c*.parquet, b*.parquet, *.sha256, manifest.json, log.jsonl)
for an end-to-end test of p2_analysis.py. Latent midpoint m = 0.6 + relation + frame + relation:frame + fact
+ fact:template + fact:carrier + carrier_shift*carrier + e (planted variances); per carrier
p(l) = 0.6 * sigmoid(((l+1)/L - m)/0.05); rank = 1 from round(m*L) on, else 7.
correct_at1 ~ Bernoulli(p_correct) per (fact, template).
Options for the MISSING tests: n_facts < 300 writes a partial run (no manifest, no 'done' event), as after a hard stop.
python analysis/p2/p2_fake_run.py <run_dir> [L=32] [seed=7] [p_correct=0.5] [n_facts=300] [carrier_shift=0]"""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
COMP = {"relation": 0.0017, "frame": 0.0005, "rt": 0.0025, "fact": 0.0027, "ft": 0.0012, "fc": 0.0002, "e": 0.0009}


def main(rd, L=32, seed=7, p_correct=0.5, n_facts=None, carrier_shift=0.0):
    rng = np.random.default_rng(seed)
    rd = Path(rd); (rd / "chunks").mkdir(parents=True, exist_ok=True)
    facts = [json.loads(l) for l in open(ROOT / "materials/facts_v1.jsonl")]
    n_all = len(facts); n_write = n_facts or n_all
    rels = sorted({f["relation"] for f in facts})
    g = lambda k, n: rng.normal(0, COMP[k] ** 0.5, n)  # noqa: E731
    a = dict(zip(rels, g("relation", len(rels)))); b = g("frame", 10)
    c = {(r, t): v for r in rels for t, v in zip(range(10), g("rt", 10))}
    lay = np.arange(1, L + 1) / L
    log = open(rd / "log.jsonl", "w")
    log.write(json.dumps({"event": "start", "model": "fake", "n_facts": n_all, "n_carriers": 3, "n_layers": L}) + "\n")
    for ci in range(0, n_write, 10):
        rows, beh = [], []
        for f in facts[ci:ci + 10]:
            fe = g("fact", 1)[0]; fc = g("fc", 3)
            for t in range(10):
                ft = g("ft", 1)[0]
                beh.append({"fact_id": f["fact_id"], "relation": f["relation"], "template_id": t, "frame": f"F{t}",
                            "correct_at1": bool(rng.random() < p_correct), "obj_first_logprob": -1.0, "n_prompt_tokens": 10,
                            **{f"carrier_alone_logprob_c{k}": float(rng.normal(-12, 1)) for k in range(3)}})
                for k in range(3):
                    m = 0.6 + a[f["relation"]] + b[t] + c[(f["relation"], t)] + fe + ft + fc[k] + carrier_shift * k + g("e", 1)[0]
                    p = 0.6 / (1 + np.exp(-(lay - m) / 0.05))
                    rk = np.where(np.arange(L) >= int(round(m * L)), 1, 7)
                    for l in range(L):
                        rows.append((f["fact_id"], f["relation"], t, k, l, p[l], rk[l]))
        df = pd.DataFrame(rows, columns=["fact_id", "relation", "template_id", "carrier", "layer", "p_object", "rank"])
        df = df.astype({"template_id": np.int16, "carrier": np.int8, "layer": np.int16, "p_object": np.float16, "rank": np.int16})
        n = ci // 10
        dst, bdst = rd / "chunks" / f"c{n:05d}.parquet", rd / "chunks" / f"b{n:05d}.parquet"
        df.to_parquet(dst, index=False); pd.DataFrame(beh).to_parquet(bdst, index=False)
        h = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()  # noqa: E731
        dst.with_suffix(".sha256").write_text(f"{h(dst)}  {dst.name}\n{h(bdst)}  {bdst.name}\n")
        log.write(json.dumps({"event": "chunk", "chunk": n, "of": (n_all + 9) // 10, "rows": len(df)}) + "\n")
    if n_write >= n_all:
        rewrite_manifest(rd, log)
    log.close()
    print(rd, n_write)


def rewrite_manifest(rd, log=None):
    """manifest.json from the chunk .sha256 files, then a final 'done' event (as run_p2.py does at the end)."""
    rd = Path(rd); man = {}
    for s in sorted((rd / "chunks").glob("c*.sha256")):
        for line in s.read_text().splitlines():
            hh, name = line.split(); man[name] = {"sha256": hh, "ok": True}
    (rd / "manifest.json").write_text(json.dumps(man))
    n_chunks = len(list((rd / "chunks").glob("c*.parquet")))
    ev = json.dumps({"event": "done", "n_chunks": n_chunks, "n_facts": 300, "n_carriers": 3, "all_ok": True}) + "\n"
    if log is not None:
        log.write(ev)
    else:
        with open(rd / "log.jsonl", "a") as f:
            f.write(ev)


if __name__ == "__main__":
    kv = dict(x.split("=", 1) for x in sys.argv[2:])
    main(sys.argv[1], int(kv.get("L", 32)), int(kv.get("seed", 7)), float(kv.get("p_correct", 0.5)),
         int(kv["n_facts"]) if "n_facts" in kv else None, float(kv.get("carrier_shift", 0.0)))
