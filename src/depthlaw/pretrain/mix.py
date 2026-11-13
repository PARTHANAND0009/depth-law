"""S6 training stream for one seed: the FineWeb-Edu token prefix with fact sentences inserted.

Fact f with frequency k gets k occurrences at corpus fractions (j + u_f) / k, j = 0..k-1, with u_f
uniform per fact and seed (uniform spacing), each snapped to the next document boundary. Each
occurrence uses a training template drawn uniformly from the 20 (seeded) and reads
"<template with subject> <object>." followed by EOS.

  python -m depthlaw.pretrain.mix --seed 1 --tokens 40000000
writes data/s6/seed<k>/train.bin (uint16) and insertions.parquet.
"""
from __future__ import annotations

import argparse
import json

import numpy as np
import pandas as pd
from transformers import AutoTokenizer

from depthlaw.io import ROOT

D = ROOT / "data" / "s6"


def build(seed: int, tokens: int) -> dict:
    tk = AutoTokenizer.from_pretrained(D / "tokenizer")
    eos = tk.eos_token_id
    corpus = np.fromfile(D / "corpus" / "corpus.bin", dtype=np.uint16)
    facts = pd.read_parquet(D / "facts.parquet")
    rng = np.random.default_rng(1000 + seed)
    n_fact_tok_est = int(facts.freq.sum() * 12)
    base = corpus[: max(0, tokens - n_fact_tok_est)]
    bounds = np.flatnonzero(base == eos) + 1  # positions right after each document
    occ = []
    for f in facts.itertuples():
        u = rng.random()
        tmpls = list(f.train_templates)
        for j in range(int(f.freq)):
            frac = (j + u) / f.freq
            ti = int(rng.integers(len(tmpls)))
            occ.append((frac, f.fact_id, j, ti, tmpls[ti].format(f.subject) + " " + f.object + "."))
    occ.sort(key=lambda x: x[0])
    sents = tk([o[4] for o in occ], add_special_tokens=False).input_ids
    pieces, rows, cur, out_len = [], [], 0, 0
    for (frac, fid, j, ti, _), ids in zip(occ, sents):
        p = int(frac * len(base))
        k = np.searchsorted(bounds, p)
        p = int(bounds[k]) if k < len(bounds) else len(base)
        if p > cur:
            pieces.append(base[cur:p]); out_len += p - cur; cur = p
        arr = np.asarray(ids + [eos], dtype=np.uint16)
        rows.append({"fact_id": fid, "occurrence": j, "template_idx": ti, "frac": frac, "stream_pos": out_len})
        pieces.append(arr); out_len += len(arr)
    pieces.append(base[cur:]); out_len += len(base) - cur
    stream = np.concatenate(pieces)
    out = D / f"seed{seed}"
    out.mkdir(parents=True, exist_ok=True)
    stream.tofile(out / "train.bin")
    ins = pd.DataFrame(rows)
    ins.to_parquet(out / "insertions.parquet", index=False)
    meta = {"seed": seed, "target_tokens": tokens, "stream_tokens": int(len(stream)), "corpus_tokens_used": int(len(base)),
            "fact_tokens": int(len(stream) - len(base)), "n_occurrences": int(len(ins))}
    (out / "meta.json").write_text(json.dumps(meta, indent=1))
    return meta


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--tokens", type=int, required=True)
    a = ap.parse_args()
    print(json.dumps(build(a.seed, a.tokens)))


if __name__ == "__main__":
    main()
