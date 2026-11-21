"""Secondary outcome logitdiff_onset (prereg/HR_revised.md B1). GPU job; PENDING until run.

Same patch as half_prob_depth (fact prompt's final-token residual at block l written into each
carrier's final token). Per carrier: d_c(l) = logit(object first token) - logit(distractor first
token) at the carrier's final position; onset_c = min l with d_c(l') > 0 for all l' >= l,
normalized (l+1)/L; missing if d_c(L-1) <= 0. Row value = mean over carriers when all 3 are
defined. Distractor: most frequent canonical object among the relation's 50 facts whose first
token differs from this fact's object first token; ties alphabetical.

python -m depthlaw.hr.logitdiff --model M [--n N] [--dtype float32] [--out-stage HRld]
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import yaml

from depthlaw.depth.causal import carrier_ids, source_states
from depthlaw.depth.common import first_stable_layer, load_lm, obj_ids, patch_per_batch_row
from depthlaw.io import ROOT, RunLog, make_run_id, provenance, seed_everything


def distractors(facts: pd.DataFrame, first) -> dict:
    out = {}
    for rel, g in facts.groupby("relation"):
        freq = g.object.value_counts()
        order = sorted(freq.index, key=lambda o: (-freq[o], o))
        for f in g.itertuples():
            out[f.fact_id] = next((o for o in order if first(o) != first(f.object)), None)
    return out


@torch.no_grad()
def logitdiff_curves(lm, subject, template, carriers, target, distractor, batch=64):
    _, _, states, _ = source_states(lm, template, subject)
    vecs = states[:, -1]
    L = vecs.shape[0]
    curves = []
    for c in carriers:
        c_ids, _ = carrier_ids(lm, c)
        pos = c_ids.shape[1] - 1
        diff = []
        for s in range(0, L, batch):
            ls = list(range(s, min(L, s + batch)))
            with patch_per_batch_row(lm.layers, ls, [pos] * len(ls), vecs[ls]):
                lg = lm.model(c_ids.repeat(len(ls), 1)).logits[:, -1].float()
            diff.extend((lg[:, target] - lg[:, distractor]).tolist())
        curves.append(np.array(diff))
    return curves


def onset(curves):
    vals = []
    for d in curves:
        if d[-1] <= 0:
            return None
        vals.append((first_stable_layer(list(d > 0)) + 1) / len(d))
    return float(np.mean(vals))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--facts", default=str(ROOT / "data" / "facts_g1cpu.parquet"))
    ap.add_argument("--n", type=int, default=None)
    ap.add_argument("--templates", type=int, default=3)
    ap.add_argument("--dtype", default="float32")
    ap.add_argument("--stage", default="HRld")
    a = ap.parse_args(argv)
    cfg = yaml.safe_load(open(ROOT / "configs" / "s3.yaml"))
    seed_everything(cfg["seed"])
    facts = pd.read_parquet(a.facts).reset_index(drop=True)
    lm = load_lm(a.model, "main", dtype=getattr(torch, a.dtype))
    first = lambda o: obj_ids(lm, o)[0]  # noqa: E731
    dis = distractors(facts, first)
    sel = facts.sample(a.n, random_state=cfg["seed"]) if a.n else facts
    run_id = make_run_id(a.stage, a.model.split("/")[-1])
    log = RunLog(a.stage, run_id)
    (log.dir / "meta.json").write_text(json.dumps(provenance(run_id, {**cfg, **vars(a)}, a.model, "main"), indent=2, default=str))
    log.log(event="start", model=a.model, n_facts=len(sel), dtype=a.dtype, device=str(lm.device))
    rows = []
    for f in sel.itertuples():
        for ti, tmpl in enumerate(list(f.templates)[: a.templates]):
            row = {"fact_id": f.fact_id, "template_id": ti, "relation": f.relation, "distractor": dis[f.fact_id]}
            if dis[f.fact_id] is None:
                row["logitdiff_onset"] = None
            else:
                cur = logitdiff_curves(lm, f.subject, tmpl, cfg["carriers"], first(f.object), first(dis[f.fact_id]))
                row["logitdiff_onset"] = onset(cur)
                row["logitdiff_curves"] = [c.tolist() for c in cur]
            rows.append(row)
    out = pd.DataFrame(rows)
    out["run_id"], out["model"] = run_id, a.model
    out.to_parquet(log.dir / "logitdiff.parquet", index=False)
    log.log(event="done", n_rows=len(out), n_defined=int(out.logitdiff_onset.notna().sum()))
    print(log.dir / "logitdiff.parquet")


if __name__ == "__main__":
    main()
