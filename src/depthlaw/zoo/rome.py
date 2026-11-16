"""ROME (Meng et al. 2022): rank-one edit of one MLP down projection."""
from __future__ import annotations

import torch

from depthlaw.depth.common import LM
from depthlaw.zoo.core import Request, down_proj_name, keys_at, optimize_delta


def rome_factors(lm: LM, req: Request, layer: int, C: torch.Tensor, prefixes: list[str],
                 ridge: float = 1e-6, **opt_kw):
    """Return (factors, info). delta W = right (d_model x 1) @ u^T (1 x d_ff)."""
    k_star = keys_at(lm, layer, [req], prefixes)[:, 0].double()
    Cd = C.double()
    Cd = Cd + ridge * Cd.diagonal().mean() * torch.eye(Cd.shape[0], dtype=Cd.dtype)
    u = torch.linalg.solve(Cd, k_star)
    u = (u / u.norm()).float()
    v_star, v_init, info = optimize_delta(lm, req, layer, prefixes, "mlp", clamp=opt_kw.pop("clamp", 4.0), **opt_kw)
    k_cur = keys_at(lm, layer, [req], [""])[:, 0]
    right = (v_star - v_init) / (k_cur @ u)
    name = down_proj_name(lm, layer)
    info["delta_norm"] = float((v_star - v_init).norm())
    return {f"{name}::B": right[:, None], f"{name}::A": u[None, :]}, info
