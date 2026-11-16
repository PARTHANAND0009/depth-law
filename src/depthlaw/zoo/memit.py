"""MEMIT (Meng et al. 2023) batch edit spread over several MLP layers; optional AlphaEdit
(Fang et al. 2025) null-space-projected update. Targets z are computed once per request
(depthlaw.zoo.core.optimize_delta with where='resid' at the last edited layer) and reused."""
from __future__ import annotations

import torch

from depthlaw.depth.common import LM
from depthlaw.zoo.core import Request, down_proj, down_proj_name, keys_at, residual_at


@torch.no_grad()
def memit_factors(lm: LM, reqs: list[Request], zs: torch.Tensor, layers: list[int],
                  C: dict[int, torch.Tensor], prefixes: list[str], mom2_weight: float = 15000.0,
                  projectors: dict[int, torch.Tensor] | None = None, L2: float = 10.0, log=None):
    """zs [d_model, n]: target residual at layers[-1]. Applies the updates to lm in place while
    computing them (as in MEMIT); the caller reverts with apply_delta(sign=-1).
    projectors given -> AlphaEdit update. Returns {name::full: delta}."""
    out = {}
    for i, l in enumerate(layers):
        K = keys_at(lm, l, reqs, prefixes).double()                    # [d_ff, n]
        cur = residual_at(lm, layers[-1], reqs).double()               # [d_model, n]
        R = (zs.double() - cur) / (len(layers) - i)                    # [d_model, n]
        if projectors is None:
            A = mom2_weight * C[l].double() + K @ K.T
            upd = R @ torch.linalg.solve(A, K).T                       # [d_model, d_ff]
        else:
            P = projectors[l].double()
            A = P @ (K @ K.T) + L2 * torch.eye(K.shape[0], dtype=K.dtype)
            upd = torch.linalg.solve(A, P @ K @ R.T).T
        W = down_proj(lm, l).weight
        W.add_(upd.to(W.dtype))
        out[f"{down_proj_name(lm, l)}::full"] = upd.float()
        if log:
            log(layer=l, resid_norm=float(R.norm(dim=0).mean()), upd_norm=float(upd.norm()))
    return out
