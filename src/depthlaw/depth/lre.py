"""Linear relational embedding (LRE) faithfulness per relation (Hernandez et al. 2024), for the
S4 nested model (notes/s4_plan.md, item D).

s = residual output of block l at the subject's last token; o = residual output of the last
block at the prompt's final token. J = mean over n_train facts of d o / d s (everything else
fixed), b = mean(o - J s). LRE(s) = beta * J s + b. Faithfulness on held-out facts of the
relation = share where argmax(unembed(final_norm(LRE(s)))) equals the model's own argmax next
token for the same prompt. Fixed before running: l = L // 3 - 1, beta = 1, n_train = 8 (seeded,
regardless of correctness), template 0.

Usage: python -m depthlaw.depth.lre --model EleutherAI/pythia-1.4b --facts data/facts_g1cpu.parquet
"""
from __future__ import annotations

import argparse
import json
import time

import numpy as np
import pandas as pd
import torch

from depthlaw.depth.common import LM, _out_tensor, capture, final_norm_and_unembed, load_lm, subject_last_pos
from depthlaw.io import ROOT, RunLog, make_run_id, provenance, seed_everything


def states(lm: LM, template: str, subject: str, layer: int):
    ids, sp = subject_last_pos(lm, template, subject)
    with torch.no_grad(), capture(lm.layers) as st:
        out = lm.model(ids)
    return ids, sp, st[layer][0, sp].clone(), st[-1][0, -1].clone(), int(out.logits[0, -1].argmax())


def jacobian(lm: LM, ids, sp: int, layer: int, s: torch.Tensor, chunk: int = 256) -> torch.Tensor:
    """d o / d s, o = last-block output at the final position; s injected at block `layer`, position sp."""
    sv = s.detach().clone().requires_grad_(True)

    def hook(mod, inp, out):
        t = _out_tensor(out)
        t = torch.cat([t[:, :sp], sv.view(1, 1, -1).to(t.dtype), t[:, sp + 1:]], dim=1)
        return (t,) + tuple(out[1:]) if isinstance(out, tuple) else t

    h = lm.layers[layer].register_forward_hook(hook)
    try:
        store = {}
        h2 = lm.layers[-1].register_forward_hook(lambda m, i, o: store.__setitem__("o", _out_tensor(o)))
        try:
            lm.model(ids)
        finally:
            h2.remove()
    finally:
        h.remove()
    o = store["o"][0, -1]
    d = o.shape[0]
    rows = []
    eye = torch.eye(d, dtype=o.dtype)
    for a in range(0, d, chunk):
        g = torch.autograd.grad(o, sv, grad_outputs=eye[a:a + chunk], is_grads_batched=True, retain_graph=True)[0]
        rows.append(g.detach())
    return torch.cat(rows)  # [d_out, d_in]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--facts", default=str(ROOT / "data" / "facts_g1cpu.parquet"))
    ap.add_argument("--n-train", type=int, default=8)
    ap.add_argument("--beta", type=float, default=1.0)
    ap.add_argument("--relations", nargs="*", default=None)
    ap.add_argument("--run-dir", default=None)
    args = ap.parse_args(argv)
    seed = 1234
    seed_everything(seed)
    from pathlib import Path
    if args.run_dir:
        rdir = Path(args.run_dir); run_id = rdir.name; log = RunLog("S4", run_id)
    else:
        run_id = make_run_id("S4lre", args.model); log = RunLog("S4", run_id); rdir = log.dir
    (rdir / "parts").mkdir(parents=True, exist_ok=True)
    lm = load_lm(args.model)
    for p in lm.model.parameters():
        p.requires_grad_(False)
    norm, unembed = final_norm_and_unembed(lm.model)
    layer = lm.n_layers // 3 - 1
    facts = pd.read_parquet(args.facts)
    rels = args.relations or sorted(facts.relation.unique())
    (rdir / "meta.json").write_text(json.dumps(provenance(run_id, {**vars(args), "layer": layer, "seed": seed},
                                                          args.model, "main"), indent=2))
    log.log(event="start", model=args.model, layer=layer, n_layers=lm.n_layers, relations=len(rels))
    t0 = time.time()
    for rel in rels:
        dst = rdir / "parts" / f"{rel}.parquet"
        if dst.exists():
            continue
        g = facts[facts.relation == rel].sample(frac=1.0, random_state=seed)
        if len(g) <= args.n_train:
            log.log(event="relation_skipped", relation=rel, n=len(g))
            continue
        tr, te = g.iloc[: args.n_train], g.iloc[args.n_train:]
        Js, ss, os_ = [], [], []
        for f in tr.itertuples():
            tmpl = list(f.templates)[0]
            ids, sp, s, o, _ = states(lm, tmpl, f.subject, layer)
            Js.append(jacobian(lm, ids, sp, layer, s))
            ss.append(s); os_.append(o)
        J = torch.stack(Js).mean(0)
        b = (torch.stack(os_) - torch.stack(ss) @ J.T).mean(0)
        rows = []
        for f in te.itertuples():
            tmpl = list(f.templates)[0]
            _, _, s, _, model_top = states(lm, tmpl, f.subject, layer)
            with torch.no_grad():
                pred = int(unembed(norm(args.beta * (J @ s) + b)).argmax())
            obj_first = lm.tok.encode(" " + f.object, add_special_tokens=False)[0]
            rows.append({"fact_id": f.fact_id, "relation": rel, "lre_top": pred, "model_top": model_top,
                         "obj_first": obj_first, "model_correct": model_top == obj_first,
                         "faithful": pred == model_top})
        out = pd.DataFrame(rows)
        out["run_id"], out["model"], out["layer"], out["beta"], out["n_train"] = run_id, args.model, layer, args.beta, len(tr)
        out.to_parquet(dst, index=False)
        log.log(event="relation", relation=rel, n_test=len(out), faithfulness=float(out.faithful.mean()),
                s=round(time.time() - t0))
    df = pd.concat([pd.read_parquet(p) for p in sorted((rdir / "parts").glob("*.parquet"))], ignore_index=True)
    df.to_parquet(rdir / "lre.parquet", index=False)
    print(rdir / "lre.parquet")


if __name__ == "__main__":
    main()
