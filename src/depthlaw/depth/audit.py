"""Audit of causal_final (exploratory; requested by the human 2026-11-20).

For each (fact, template, carrier) and each layer l, logs the object's rank and logprob when the
fact prompt's residual at block l is patched into the carrier (exactly the S3 causal_final code
path: depth.causal.patched_ranks semantics), next to the model's UNPATCHED readouts: the source
prompt's final top-1 token and its logit-lens top-1 / object rank at block l.

Mechanics checks per (fact, template):
  - source read position: index of the subject's last token (used by causal_subj) and the final
    prompt token (used by causal_final, amendment_1), decoded;
  - carrier write position: final carrier token (causal_final) and the "X" placeholder
    (causal_subj), decoded; the hook writes exactly the source vector there and leaves every other
    position at block l unchanged (max abs diff vs an unpatched carrier pass);
  - last-layer identity: patching at block L-1 gives the source's own final logits.
Carrier-alone: rank / logprob of the object under each carrier with the placeholder, unpatched.
Also computes the proposed correctness-free measure (half-gain depth) on the audit sample only.

Run: python -m depthlaw.depth.audit --model EleutherAI/pythia-410m [--dtype bfloat16] [--n-random 200]
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import yaml

from depthlaw.depth.causal import PLACEHOLDER, carrier_ids, source_states
from depthlaw.depth.common import (LM, capture, final_norm_and_unembed, find_layers, first_stable_layer,
                                   load_lm, obj_ids, patch_per_batch_row, rank_of, subject_last_pos)
from depthlaw.io import ROOT, RunLog, make_run_id, provenance, seed_everything


def audit_facts(n_random: int, seed: int) -> pd.DataFrame:
    """20 hand facts (configs/hand_facts.yaml) + n_random facts from the G1 subsample (seeded)."""
    hand = yaml.safe_load(open(ROOT / "configs" / "hand_facts.yaml"))["facts"]
    rows = [{"fact_id": f"hand{i:02d}", "set": "hand", "subject": s, "object": o, "relation": "hand",
             "templates": [t]} for i, (t, s, o) in enumerate(hand)]
    g1 = pd.read_parquet(ROOT / "data" / "facts_g1cpu.parquet")
    pick = g1.sample(n_random, random_state=seed).sort_values("fact_id")
    for f in pick.itertuples():
        rows.append({"fact_id": f.fact_id, "set": "random", "subject": f.subject, "object": f.object,
                     "relation": f.relation, "templates": list(f.templates)[:3]})
    return pd.DataFrame(rows)


@torch.no_grad()
def carrier_pass(lm, c_ids, write_pos=None, write_layers=None, vecs=None):
    """Batched carrier forward; returns (logits at final pos [B, V], captured residuals or None)."""
    B = 1 if write_layers is None else len(write_layers)
    ids = c_ids.repeat(B, 1)
    if write_layers is None:
        return lm.model(ids).logits[:, -1].float()
    with patch_per_batch_row(lm.layers, write_layers, [write_pos] * B, vecs):
        return lm.model(ids).logits[:, -1].float()


@torch.no_grad()
def write_check(lm, c_ids, pos, layer, vec) -> tuple[float, float]:
    """(max |h[pos] - vec|, max |h[other] - unpatched h[other]|) at block `layer` output."""
    with capture(lm.layers) as base:
        lm.model(c_ids)
    h0 = base[layer][0].float()
    with capture(lm.layers) as st, patch_per_batch_row(lm.layers, [layer], [pos], vec[None]):
        lm.model(c_ids)
    h1 = st[layer][0].float()
    other = [i for i in range(h1.shape[0]) if i != pos]
    d_pos = float((h1[pos] - vec.float()).abs().max())
    d_other = float((h1[other] - h0[other]).abs().max()) if other else 0.0
    return d_pos, d_other


class _CpuLM(LM):
    @property
    def device(self):
        return torch.device("cpu")


def load_offloaded(name: str, dtype, max_cpu_mem: str) -> LM:
    """Main-revision model with weights offloaded to disk (accelerate); same forward hooks apply."""
    from transformers import AutoModelForCausalLM, AutoTokenizer
    off = ROOT / "cache" / "offload" / name.replace("/", "--")
    off.mkdir(parents=True, exist_ok=True)
    model = AutoModelForCausalLM.from_pretrained(name, dtype=dtype, device_map="auto",
                                                 max_memory={"cpu": max_cpu_mem}, offload_folder=str(off)).eval()
    tok = AutoTokenizer.from_pretrained(name)
    return _CpuLM(model, tok, find_layers(model), name, "main")


def half_gain_depth(lp_patch: np.ndarray, lp_carrier: float, min_gain: float) -> float | None:
    """First l with gain(l') >= 0.5 * gain(L-1) for all l' >= l, gain = lp_patch - lp_carrier.
    None if gain(L-1) < min_gain (the fact prompt does not raise the object above the carrier)."""
    g = lp_patch - lp_carrier
    G = g[-1]
    if not np.isfinite(G) or G < min_gain:
        return None
    l = first_stable_layer(list(g >= 0.5 * G))
    return None if l is None else (l + 1) / len(g)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--dtype", default=None)
    ap.add_argument("--n-random", type=int, default=200)
    ap.add_argument("--min-gain", type=float, default=float(np.log(2)))
    ap.add_argument("--offload", action="store_true", help="disk-offload weights (RAM-limited runs)")
    ap.add_argument("--max-cpu-mem", default="1GiB")
    ap.add_argument("--hand-only", action="store_true")
    args = ap.parse_args(argv)
    try:  # if RAM runs out, the kernel should kill this audit, not the S5 chain
        Path("/proc/self/oom_score_adj").write_text("1000")
    except OSError:
        pass
    cfg = yaml.safe_load(open(ROOT / "configs" / "s3.yaml"))
    seed_everything(cfg["seed"])
    run_id = make_run_id("AUDIT", args.model.split("/")[-1])
    log = RunLog("AUDIT", run_id)
    rdir = log.dir
    (rdir / "meta.json").write_text(json.dumps(provenance(run_id, {**cfg, **vars(args)}, args.model, "main"), indent=2))
    facts = audit_facts(args.n_random, cfg["seed"])
    dtype = getattr(torch, args.dtype) if args.dtype else None
    if args.offload:
        lm = load_offloaded(args.model, dtype or torch.bfloat16, args.max_cpu_mem)
    else:
        lm = load_lm(args.model, "main", dtype=dtype, device="cpu")
    if args.hand_only:
        facts = facts[facts.set == "hand"].reset_index(drop=True)
    L = lm.n_layers
    norm, unembed = final_norm_and_unembed(lm.model)
    tok = lm.tok
    carriers = cfg["carriers"]
    cinfo = []
    for c in carriers:
        c_ids, c_pos = carrier_ids(lm, c)
        cinfo.append((c, c_ids, c_pos))
    log.log(event="start", model=args.model, dtype=str(dtype), n_facts=len(facts), L=L)

    layer_rows, ft_rows = [], []
    for fi, f in enumerate(facts.itertuples()):
        target = obj_ids(lm, f.object)[0]
        for ti, tmpl in enumerate(f.templates):
            ids, s_pos, states, src_logits = source_states(lm, tmpl, f.subject)
            src_logits = src_logits.float()
            src_lp = torch.log_softmax(src_logits, -1)
            src_top1 = int(src_logits.argmax())
            src_rank = int(rank_of(src_logits, target))
            ll = unembed(norm(states[:, -1].to(next(unembed.parameters()).dtype))).float()  # [L, V]
            ll_top1 = ll.argmax(-1).tolist()
            ll_rank = rank_of(ll, target).tolist()
            prefix = tmpl.split("{}", 1)[0]
            dec_upto_spos = tok.decode(ids[0, : s_pos + 1])
            ft = {"fact_id": f.fact_id, "set": f.set, "relation": f.relation, "template_id": ti,
                  "subject": f.subject, "object": f.object, "obj_tok": target,
                  "obj_tok_str": tok.decode([target]), "src_top1": src_top1,
                  "src_top1_str": tok.decode([src_top1]), "src_obj_rank": src_rank,
                  "correct_at1": src_top1 == target, "src_obj_logprob": float(src_lp[target]),
                  "subj_last_tok_str": tok.decode([int(ids[0, s_pos])]),
                  "subj_pos_ok": dec_upto_spos.rstrip().endswith(f.subject.strip()),
                  "subj_prefix_ok": (prefix + f.subject).startswith(dec_upto_spos),
                  "src_final_pos": int(ids.shape[1] - 1),
                  "src_final_tok_str": tok.decode([int(ids[0, -1])])}
            per_c = []
            for ci, (c, c_ids, c_pos) in enumerate(cinfo):
                alone = carrier_pass(lm, c_ids)[0]
                alone_lp = torch.log_softmax(alone, -1)
                fpos = c_ids.shape[1] - 1
                logits = carrier_pass(lm, c_ids, fpos, list(range(L)), states[:, -1])
                lps = torch.log_softmax(logits, -1)
                ranks = rank_of(logits, target).tolist()
                lp_obj = lps[:, target].numpy()
                top1 = logits.argmax(-1).tolist()
                st = first_stable_layer([r == 1 for r in ranks])
                hg = half_gain_depth(lp_obj, float(alone_lp[target]), args.min_gain)
                per_c.append({"carrier": ci, "resolved": st is not None,
                              "depth": None if st is None else (st + 1) / L, "half_gain_depth": hg,
                              "carrier_alone_obj_rank": int(rank_of(alone, target)),
                              "carrier_alone_obj_logprob": float(alone_lp[target]),
                              "carrier_alone_top1_str": tok.decode([int(alone.argmax())]),
                              "lastlayer_max_abs_logit_diff": float((logits[-1] - src_logits).abs().max()),
                              "lastlayer_rank_equals_src": ranks[-1] == src_rank,
                              "write_pos": fpos, "write_tok_str": tok.decode([int(c_ids[0, fpos])]),
                              "placeholder_pos": c_pos, "placeholder_tok_str": tok.decode([int(c_ids[0, c_pos])])})
                for l in range(L):
                    layer_rows.append({"fact_id": f.fact_id, "template_id": ti, "carrier": ci, "layer": l,
                                       "patched_obj_rank": ranks[l], "patched_obj_logprob": float(lp_obj[l]),
                                       "patched_top1": top1[l], "unpatched_src_top1": src_top1,
                                       "unpatched_ll_top1": ll_top1[l], "unpatched_ll_obj_rank": ll_rank[l],
                                       "correct_at1": src_top1 == target})
                if fi < 20 or fi % 20 == 0:  # write-position check on a subset (cheap but not free)
                    mid = L // 2
                    d_pos, d_oth = write_check(lm, c_ids, fpos, mid, states[mid, -1])
                    d_pos_s, d_oth_s = write_check(lm, c_ids, c_pos, mid, states[mid, s_pos])
                    per_c[-1].update(write_final_dpos=d_pos, write_final_dother=d_oth,
                                     write_subj_dpos=d_pos_s, write_subj_dother=d_oth_s)
            ds = [p["depth"] for p in per_c]
            ft["causal_final"] = float(np.mean(ds)) if all(d is not None for d in ds) else None
            hgs = [p["half_gain_depth"] for p in per_c]
            ft["half_gain_depth"] = float(np.mean(hgs)) if all(h is not None for h in hgs) else None
            for p in per_c:
                ft_rows.append({**ft, **p})
        if fi % 20 == 0:
            log.log(event="progress", done=fi + 1, of=len(facts))
    pd.DataFrame(layer_rows).to_parquet(rdir / "layers.parquet", index=False)
    pd.DataFrame(ft_rows).to_parquet(rdir / "carriers.parquet", index=False)
    log.log(event="done", rows_layers=len(layer_rows), rows_carriers=len(ft_rows))
    print(rdir)


if __name__ == "__main__":
    main()
