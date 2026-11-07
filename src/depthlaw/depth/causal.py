"""Causal depth measures.

causal_subj (CLAUDE.md S3 definition): patch the subject-last-token residual at block l
from the fact prompt into the placeholder token of a neutral carrier prompt; read the
carrier's next-token logits at its final position. NOTE: a patch at the subject position
in the top blocks cannot reach the final position (no layers left to move it), so the
"rank 1 for all l' >= l" rule is degenerate at this position. We therefore store the full
per-layer rank curve and report both:
  - onset  = first l with rank 1           (causal_subj_onset)
  - stable = first l with rank 1 for all l' >= l (causal_subj_stable; the literal spec)
causal_final: same patching but at the final token of the fact prompt into the carrier's
final token; here "stable from l on" is well defined (the depth at which the final
position has causally resolved the object).
All depths are normalized (l + 1) / L; None means censored (never resolved).
"""
from __future__ import annotations

import numpy as np
import torch

from depthlaw.depth.common import (LM, capture, encode, first_stable_layer, first_true,
                                   obj_ids, patch_per_batch_row, rank_of, subject_last_pos)

PLACEHOLDER = "X"


def carrier_ids(lm: LM, carrier: str) -> tuple[torch.Tensor, int]:
    """carrier uses '{}' for the placeholder slot."""
    return subject_last_pos(lm, carrier, PLACEHOLDER)


@torch.no_grad()
def source_states(lm: LM, template: str, subject: str):
    ids, s_pos = subject_last_pos(lm, template, subject)
    with capture(lm.layers) as store:
        out = lm.model(ids)
    states = torch.stack([s[0] for s in store])  # [L, T, d]
    return ids, s_pos, states, out.logits[0, -1]


@torch.no_grad()
def patched_ranks(lm: LM, carrier: str, vecs: torch.Tensor, at_final: bool, target: int,
                  batch: int = 64) -> np.ndarray:
    """vecs [L, d]: vector to write at each layer. Returns rank per layer [L]."""
    c_ids, c_pos = carrier_ids(lm, carrier)
    L = vecs.shape[0]
    pos = c_ids.shape[1] - 1 if at_final else c_pos
    ranks = []
    for s in range(0, L, batch):
        ls = list(range(s, min(L, s + batch)))
        ids = c_ids.repeat(len(ls), 1)
        with patch_per_batch_row(lm.layers, ls, [pos] * len(ls), vecs[ls]):
            logits = lm.model(ids).logits[:, -1]
        ranks.extend(rank_of(logits.float(), target).tolist())
    return np.array(ranks)


def causal_depth(lm: LM, subject: str, obj: str, template: str, carriers: list[str]) -> dict:
    target = obj_ids(lm, obj)[0]
    ids, s_pos, states, src_logits = source_states(lm, template, subject)
    L = lm.n_layers
    out = {"subj_ranks": [], "final_ranks": []}
    for c in carriers:
        out["subj_ranks"].append(patched_ranks(lm, c, states[:, s_pos], False, target))
        out["final_ranks"].append(patched_ranks(lm, c, states[:, -1], True, target))

    def summarize(curves, rule):
        ds = []
        for r in curves:
            l = rule(list(r == 1))
            ds.append(None if l is None else (l + 1) / L)
        vals = [d for d in ds if d is not None]
        return (float(np.mean(vals)) if len(vals) == len(ds) else None), ds

    res = {}
    res["causal_subj_onset"], res["causal_subj_onset_per_carrier"] = summarize(out["subj_ranks"], first_true)
    res["causal_subj_stable"], res["causal_subj_stable_per_carrier"] = summarize(out["subj_ranks"], first_stable_layer)
    res["causal_final"], res["causal_final_per_carrier"] = summarize(out["final_ranks"], first_stable_layer)
    res["subj_rank_curves"] = [r.tolist() for r in out["subj_ranks"]]
    res["final_rank_curves"] = [r.tolist() for r in out["final_ranks"]]
    res["n_layers"] = L
    return res


@torch.no_grad()
def override_depth(lm: LM, subject_a: str, obj_a: str, template_a: str,
                   subject_b: str, template_b: str) -> dict:
    """Carrier-override control (prereg amendment_1): patch fact A's final-token state at each
    block into the final token of fact B's prompt; depth = first l with A's object first token
    at rank 1 for all l' >= l, normalized (l+1)/L; None = censored."""
    target = obj_ids(lm, obj_a)[0]
    _, _, states, _ = source_states(lm, template_a, subject_a)
    c_ids, _ = subject_last_pos(lm, template_b, subject_b)  # B's own fact prompt is the carrier
    L = lm.n_layers
    vecs = states[:, -1]
    pos = c_ids.shape[1] - 1
    ranks = []
    for s in range(0, L, 64):
        ls = list(range(s, min(L, s + 64)))
        with patch_per_batch_row(lm.layers, ls, [pos] * len(ls), vecs[ls]):
            logits = lm.model(c_ids.repeat(len(ls), 1)).logits[:, -1]
        ranks.extend(rank_of(logits.float(), target).tolist())
    l = first_stable_layer([r == 1 for r in ranks])
    return {"override_depth": None if l is None else (l + 1) / L, "override_ranks": ranks}
