"""S3 depth runner: all depth measures for one model over a fact table; one row per (fact, template).

Resumable: rows are written in chunks to results/<stage>/<run_dir>/chunks/*.parquet and a
chunk that exists is skipped, so a restarted run continues where it stopped (pass the same
--run-dir). Shardable: --shard i --n-shards k processes every k-th fact (one process per GPU).
Measures (prereg amendment_1): causal_final (headline), override_depth (control),
causal_subj_onset/stable, tuned/logit lens, Patchscope, behaviour (correct, logprob, margin).
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from depthlaw.depth.causal import causal_depth, override_depth
from depthlaw.depth.common import load_lm
from depthlaw.depth.lenses import behavior_and_lens, load_tuned_lens, patchscope_depth
from depthlaw.io import ROOT, RunLog, make_run_id, provenance, seed_everything


def partners(facts: pd.DataFrame, seed: int) -> dict:
    """Fixed partner B for each fact A: different relation and different object (seeded)."""
    rng = np.random.default_rng(seed)
    ids = facts.fact_id.to_numpy()
    rel = facts.relation.to_numpy()
    obj = facts.object.to_numpy()
    out = {}
    for i in range(len(facts)):
        for _ in range(1000):
            j = int(rng.integers(len(facts)))
            if rel[j] != rel[i] and obj[j] != obj[i]:
                break
        out[ids[i]] = j
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--revision", default="main")
    ap.add_argument("--facts", default=str(ROOT / "data" / "facts.parquet"))
    ap.add_argument("--n", type=int, default=None, help="random sample of N facts (seeded)")
    ap.add_argument("--templates", type=int, default=3, help="use the first K templates")
    ap.add_argument("--stage", default="S3")
    ap.add_argument("--run-dir", default=None, help="resume into this results dir")
    ap.add_argument("--shard", type=int, default=0)
    ap.add_argument("--n-shards", type=int, default=1)
    ap.add_argument("--chunk", type=int, default=25, help="facts per checkpoint chunk")
    ap.add_argument("--no-patchscope", action="store_true")
    ap.add_argument("--dtype", default=None, help="e.g. bfloat16 on GPU")
    ap.add_argument("--causal-only", action="store_true",
                    help="S5: behaviour + causal_final only (no subject patching, override, Patchscope)")
    args = ap.parse_args(argv)
    cfg = yaml.safe_load(open(ROOT / "configs" / "s3.yaml"))
    seed_everything(cfg["seed"])
    if args.run_dir:
        rdir = Path(args.run_dir)
        run_id = rdir.name
        log = RunLog(args.stage, run_id)
    else:
        tag = args.model.split("/")[-1] + ("" if args.revision == "main" else f"_{args.revision}")
        run_id = make_run_id(args.stage, tag)
        log = RunLog(args.stage, run_id)
        rdir = log.dir
    cdir = rdir / "chunks"
    cdir.mkdir(parents=True, exist_ok=True)

    all_facts = pd.read_parquet(args.facts).reset_index(drop=True)
    pmap = partners(all_facts, cfg["seed"])
    facts = all_facts.sample(args.n, random_state=cfg["seed"]) if args.n else all_facts
    facts = facts.iloc[args.shard::args.n_shards]
    (rdir / f"meta_shard{args.shard}.json").write_text(json.dumps(
        provenance(run_id, {**cfg, **vars(args)}, args.model, args.revision), indent=2))

    import torch
    dtype = getattr(torch, args.dtype) if args.dtype else None
    lm = load_lm(args.model, args.revision, dtype=dtype)
    tl = load_tuned_lens(lm)
    log.log(event="start", model=args.model, n_facts=len(facts), shard=args.shard,
            n_shards=args.n_shards, tuned_lens=tl is not None, device=str(lm.device))
    t0 = time.time()
    chunks = [facts.iloc[i:i + args.chunk] for i in range(0, len(facts), args.chunk)]
    for ci, ch in enumerate(chunks):
        dst = cdir / f"s{args.shard:02d}_c{ci:05d}.parquet"
        if dst.exists():
            continue
        rows = []
        for f in ch.itertuples():
            b = all_facts.iloc[pmap[f.fact_id]]
            for ti, tmpl in enumerate(list(f.templates)[: args.templates]):
                row = {"fact_id": f.fact_id, "template_id": ti, "relation": f.relation,
                       "partner_fact_id": b.fact_id}
                try:
                    row.update(behavior_and_lens(lm, f.subject, f.object, tmpl, tuned=tl))
                    row.update(causal_depth(lm, f.subject, f.object, tmpl, cfg["carriers"], final_only=args.causal_only))
                    if args.causal_only:
                        rows.append(row)
                        continue
                    tb = list(b.templates)[min(ti, len(b.templates) - 1)]
                    row.update(override_depth(lm, f.subject, f.object, tmpl, b.subject, tb))
                    if not args.no_patchscope:
                        row.update(patchscope_depth(lm, f.subject, f.object, list(f.o_aliases), tmpl,
                                                    max_new_tokens=cfg["patchscope_max_new_tokens"]))
                except Exception as e:  # noqa: BLE001 - recorded, reported as MISSING
                    row["error"] = repr(e)[:300]
                rows.append(row)
        out = pd.DataFrame(rows)
        out["run_id"], out["model"], out["revision"] = run_id, args.model, args.revision
        out.to_parquet(dst.with_suffix(".tmp"), index=False)
        dst.with_suffix(".tmp").rename(dst)
        log.log(event="chunk", shard=args.shard, chunk=ci, of=len(chunks), s=round(time.time() - t0))
    merge(rdir)
    print(rdir / "depth.parquet")


def merge(rdir: Path) -> Path:
    parts = sorted((rdir / "chunks").glob("*.parquet"))
    df = pd.concat([pd.read_parquet(p) for p in parts], ignore_index=True)
    dst = rdir / "depth.parquet"
    df.to_parquet(dst, index=False)
    return dst


if __name__ == "__main__":
    main()
