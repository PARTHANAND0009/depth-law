"""Logit lens, tuned lens, behavioral readouts, and Patchscope depth."""
from __future__ import annotations

import re

import numpy as np
import torch

from depthlaw.depth.common import (LM, capture, final_norm_and_unembed, first_stable_layer,
                                   obj_ids, patch_per_batch_row, rank_of, subject_last_pos)


@torch.no_grad()
def behavior_and_lens(lm: LM, subject: str, obj: str, template: str, tuned=None) -> dict:
    """Correctness, object logprob, margin, logit-lens curve, (tuned-lens curve + depth)."""
    o = obj_ids(lm, obj)
    ids, _ = subject_last_pos(lm, template, subject)
    full = torch.cat([ids, torch.tensor([o[:-1]], device=lm.device, dtype=ids.dtype)], 1) if len(o) > 1 else ids
    with capture(lm.layers) as store:
        logits = lm.model(full).logits[0].float()
    T = ids.shape[1]
    lp = torch.log_softmax(logits, -1)
    obj_lp = float(sum(lp[T - 1 + i, t] for i, t in enumerate(o)))
    last = logits[T - 1]
    top2 = last.topk(2)
    t0 = o[0]
    other = top2.values[1] if top2.indices[0] == t0 else top2.values[0]
    norm, unembed = final_norm_and_unembed(lm.model)
    hs = torch.stack([s[0, T - 1] for s in store]).float()  # [L, d]
    ll_logits = unembed(norm(hs.to(next(unembed.parameters()).dtype))).float()
    ll_rank = rank_of(ll_logits, t0).tolist()
    res = {
        "correct_at1": bool(top2.indices[0] == t0),
        "obj_first_logprob": float(lp[T - 1, t0]),
        "obj_logprob": obj_lp,
        "margin": float(last[t0] - other),
        "n_obj_tokens": len(o),
        "logit_lens_ranks": ll_rank,
        "logit_lens_prob": torch.softmax(ll_logits, -1)[:, t0].tolist(),
    }
    L = lm.n_layers
    if tuned is not None:
        tl = torch.stack([tuned(hs[l:l + 1].to(next(tuned.parameters()).dtype), l)[0] for l in range(L - 1)]).float()
        ranks = rank_of(tl, t0).tolist() + [int(rank_of(last, t0))]  # final layer = model output
        res["tuned_lens_ranks"] = ranks
        l = first_stable_layer([r == 1 for r in ranks])
        res["tuned_lens_depth"] = None if l is None else (l + 1) / L
    l = first_stable_layer([r == 1 for r in ll_rank])
    res["logit_lens_depth"] = None if l is None else (l + 1) / L
    return res


def load_tuned_lens(lm: LM):
    """Pretrained lens from the AlignmentResearch/tuned-lens HF Space; None if unavailable."""
    from tuned_lens import TunedLens
    try:
        tl = TunedLens.from_model_and_pretrained(lm.model).to(lm.device)
        return tl.eval()
    except Exception as e:  # noqa: BLE001
        print(f"tuned lens unavailable for {lm.name}: {e!r}")
        return None


def _match(gen: str, names: list[str]) -> bool:
    g = re.sub(r"\s+", " ", gen).strip().lower()
    return any(g.startswith(n.lower()) for n in names if n)


@torch.no_grad()
def patchscope_depth(lm: LM, subject: str, obj: str, aliases: list[str], template: str,
                     src_template: str | None = None, max_new_tokens: int = 6, batch: int = 32) -> dict:
    """Attribute-extraction Patchscope: source = fact prompt (src_template or template) at the
    subject last token, block l; target = relation template with placeholder X, same block l.
    Greedy-generate; correct if generation starts with object or an alias. Depth = first
    source layer from which it stays correct to the last layer."""
    src_t = src_template or template
    ids, s_pos = subject_last_pos(lm, src_t, subject)
    with capture(lm.layers) as store:
        lm.model(ids)
    vecs = torch.stack([s[0, s_pos] for s in store])
    t_ids, t_pos = subject_last_pos(lm, template, "X")
    L = lm.n_layers
    ok, gens = [], []
    for s in range(0, L, batch):
        ls = list(range(s, min(L, s + batch)))
        cur = t_ids.repeat(len(ls), 1)
        for step in range(max_new_tokens):
            # the patch is applied at the placeholder position on every step (no KV cache)
            with patch_per_batch_row(lm.layers, ls, [t_pos] * len(ls), vecs[ls]):
                nxt = lm.model(cur).logits[:, -1].argmax(-1, keepdim=True)
            cur = torch.cat([cur, nxt], 1)
        for b in range(len(ls)):
            g = lm.tok.decode(cur[b, t_ids.shape[1]:])
            gens.append(g)
            ok.append(_match(g, [obj, *aliases]))
    l = first_stable_layer(ok)
    return {"patchscope_depth": None if l is None else (l + 1) / L, "patchscope_ok": ok,
            "patchscope_gens": gens}
