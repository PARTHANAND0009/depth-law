"""S6 learnability check on a trained model: next-token accuracy restricted to the relation's
10 candidate objects, on 3 training templates and the 3 held-out eval templates, per frequency bin.
Chance = 0.1. Writes results/S6learn/<run_id>/learn.json.

  python -m depthlaw.pretrain.learnability --model results/S6/<run>/final [--per-bin 60]
"""
from __future__ import annotations

import argparse
import json

import pandas as pd
import torch
from transformers import AutoTokenizer, GPTNeoXForCausalLM

from depthlaw.io import ROOT, RunLog, make_run_id, provenance


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--per-bin", type=int, default=60)
    ap.add_argument("--threads", type=int, default=1)
    a = ap.parse_args(argv)
    torch.set_num_threads(a.threads)
    run_id = make_run_id("S6learn")
    log = RunLog("S6learn", run_id)
    tk = AutoTokenizer.from_pretrained(a.model)
    m = GPTNeoXForCausalLM.from_pretrained(a.model).eval()
    allf = pd.read_parquet(ROOT / "data" / "s6" / "facts.parquet")
    cands = {rel: sorted(g.obj_first_tok.unique()) for rel, g in allf.groupby("relation")}
    f = allf.groupby("freq").sample(a.per_bin, random_state=0)
    rows = []
    with torch.no_grad():
        for x in f.itertuples():
            c = cands[x.relation]
            for kind, tl in (("train", list(x.train_templates)[:3]), ("eval", list(x.templates))):
                for t in tl:
                    lo = m(torch.tensor([tk(t.format(x.subject), add_special_tokens=False).input_ids])).logits[0, -1]
                    cl = lo[c]
                    rows.append({"freq": int(x.freq), "kind": kind, "top1": int(lo.argmax()) == x.obj_first_tok,
                                 "cand_acc": c[int(cl.argmax())] == x.obj_first_tok,
                                 "cand_rank": int((cl > lo[x.obj_first_tok]).sum()) + 1,
                                 "pred_in_cands": int(lo.argmax()) in c})
    d = pd.DataFrame(rows)
    g = d.groupby(["kind", "freq"])
    tab = {f"{k}|{fr}": {"n_prompts": int(len(v)), **{c: float(v[c].mean()) for c in ["top1", "cand_acc", "cand_rank", "pred_in_cands"]}}
           for (k, fr), v in g}
    out = {"run_id": run_id, "model_dir": a.model, "n_facts_per_bin": a.per_bin, "chance_cand_acc": 0.1, "table": tab}
    (log.dir / "learn.json").write_text(json.dumps(out, indent=2))
    (log.dir / "meta.json").write_text(json.dumps(provenance(run_id, vars(a)), indent=2))
    log.log(event="done")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
