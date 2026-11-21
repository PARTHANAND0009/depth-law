"""Synthetic P2 run in the exact runner format (chunks/c*.parquet, b*.parquet, *.sha256, manifest.json) for an
end-to-end test of p2_analysis.py. Latent midpoint m = 0.6 + relation + frame + relation:frame + fact
+ fact:template + fact:carrier + e (planted variances); per carrier p(l) = 0.6 * sigmoid(((l+1)/L - m)/0.05);
rank = 1 from round(m*L) on, else 7. correct_at1 ~ Bernoulli(0.5) per (fact, template).
python analysis/p2/p2_fake_run.py <run_dir> [L=32]"""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
COMP = {"relation": 0.0017, "frame": 0.0005, "rt": 0.0025, "fact": 0.0027, "ft": 0.0012, "fc": 0.0002, "e": 0.0009}


def main(rd, L=32, seed=7):
    rng = np.random.default_rng(seed)
    rd = Path(rd); (rd / "chunks").mkdir(parents=True, exist_ok=True)
    facts = [json.loads(l) for l in open(ROOT / "materials/facts_v1.jsonl")]
    rels = sorted({f["relation"] for f in facts})
    g = lambda k, n: rng.normal(0, COMP[k] ** 0.5, n)  # noqa: E731
    a = dict(zip(rels, g("relation", len(rels)))); b = g("frame", 10)
    c = {(r, t): v for r in rels for t, v in zip(range(10), g("rt", 10))}
    lay = np.arange(1, L + 1) / L
    for ci in range(0, len(facts), 10):
        rows, beh = [], []
        for f in facts[ci:ci + 10]:
            fe = g("fact", 1)[0]; fc = g("fc", 3)
            for t in range(10):
                ft = g("ft", 1)[0]
                beh.append({"fact_id": f["fact_id"], "relation": f["relation"], "template_id": t, "frame": f"F{t}",
                            "correct_at1": bool(rng.random() < 0.5), "obj_first_logprob": -1.0, "n_prompt_tokens": 10,
                            **{f"carrier_alone_logprob_c{k}": float(rng.normal(-12, 1)) for k in range(3)}})
                for k in range(3):
                    m = 0.6 + a[f["relation"]] + b[t] + c[(f["relation"], t)] + fe + ft + fc[k] + g("e", 1)[0]
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
    man = {}
    for s in sorted((rd / "chunks").glob("c*.sha256")):
        for line in s.read_text().splitlines():
            hh, name = line.split(); man[name] = {"sha256": hh, "ok": True}
    (rd / "manifest.json").write_text(json.dumps(man))
    print(rd, len(man))


if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 32)
