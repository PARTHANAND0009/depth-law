"""Run all depth measures for a model over a fact table; one row per (fact, template).
S3 entry point; on CPU only used for the G0 dry run on small models."""
from __future__ import annotations

import argparse
import json
import time

import pandas as pd
import yaml

from depthlaw.depth.causal import causal_depth
from depthlaw.depth.common import load_lm
from depthlaw.depth.lenses import behavior_and_lens, load_tuned_lens, patchscope_depth
from depthlaw.io import ROOT, RunLog, make_run_id, provenance, seed_everything


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--revision", default="main")
    ap.add_argument("--facts", default=str(ROOT / "data" / "facts.parquet"))
    ap.add_argument("--n", type=int, default=None, help="random sample of N facts")
    ap.add_argument("--templates", type=int, default=3, help="use the first K templates")
    ap.add_argument("--stage", default="S3")
    args = ap.parse_args(argv)
    cfg = yaml.safe_load(open(ROOT / "configs" / "s3.yaml"))
    seed_everything(cfg["seed"])
    run_id = make_run_id(args.stage, args.model)
    log = RunLog(args.stage, run_id)
    facts = pd.read_parquet(args.facts)
    if args.n:
        facts = facts.sample(args.n, random_state=cfg["seed"])
    lm = load_lm(args.model, args.revision)
    tl = load_tuned_lens(lm)
    rows = []
    t0 = time.time()
    for k, f in enumerate(facts.itertuples()):
        for ti, tmpl in enumerate(list(f.templates)[: args.templates]):
            row = {"fact_id": f.fact_id, "template_id": ti, "relation": f.relation}
            try:
                row.update(behavior_and_lens(lm, f.subject, f.object, tmpl, tuned=tl))
                c = causal_depth(lm, f.subject, f.object, tmpl, cfg["carriers"])
                row.update(c)
                p = patchscope_depth(lm, f.subject, f.object, list(f.o_aliases), tmpl,
                                     max_new_tokens=cfg["patchscope_max_new_tokens"])
                row.update(p)
            except Exception as e:  # noqa: BLE001
                row["error"] = repr(e)
            rows.append(row)
        if k % 10 == 0:
            log.log(event="progress", done=k + 1, of=len(facts), s=round(time.time() - t0))
    out = pd.DataFrame(rows)
    out["run_id"] = run_id
    out["model"] = args.model
    dst = log.dir / "depth.parquet"
    out.to_parquet(dst, index=False)
    (log.dir / "meta.json").write_text(json.dumps(provenance(run_id, {**cfg, **vars(args)}, args.model, args.revision), indent=2))
    print(dst)


if __name__ == "__main__":
    main()
