"""Shared machinery for locate-then-edit methods (ROME, MEMIT, AlphaEdit) and delta files.

Conventions (GPT-NeoX / Pythia; Llama-style names supported for the MLP down projection):
- key k at layer l   = input to the MLP down projection (post-activation, d_ff)
- value at layer l   = output of the MLP down projection (d_model)
- z at layer l       = residual stream output of block l (MEMIT target)
All positions are the subject's last token. Edits are stored as weight deltas, never as full
models: low-rank factors ("<param>::B", "<param>::A", delta = B @ A) or full ("<param>::full").
"""
from __future__ import annotations

import json
import math
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import torch

from depthlaw.depth.common import LM, obj_ids


@dataclass
class Request:
    rid: str          # request id (= fact_id)
    subject: str
    template: str     # edit prompt template with "{}"
    target: str       # new object string
    rtype: str = ""   # counterfactual | true_new


# ----------------------------------------------------------------------------- modules
def down_proj(lm: LM, l: int) -> torch.nn.Linear:
    mlp = lm.layers[l].mlp
    for name in ["dense_4h_to_h", "down_proj", "fc_out", "c_proj"]:
        if hasattr(mlp, name):
            return getattr(mlp, name)
    raise ValueError("MLP down projection not found")


def down_proj_name(lm: LM, l: int) -> str:
    mod = down_proj(lm, l)
    for n, m in lm.model.named_modules():
        if m is mod:
            return n + ".weight"
    raise ValueError


# ----------------------------------------------------------------------------- tokenization
def build_prompt(lm: LM, prefix: str, template: str, subject: str, target: str | None):
    """ids for prefix + template.format(subject) [+ target tokens except the last], the subject's
    last-token index and the target token ids (positions T-1+i predict target[i])."""
    pre_t, _ = template.split("{}", 1)
    text = prefix + template.format(subject)
    enc = lm.tok(text, return_offsets_mapping=True)
    end_char = len(prefix) + len(pre_t) + len(subject)
    offs = enc["offset_mapping"]
    s_idx = max(i for i, (a, b) in enumerate(offs) if b > a and a < end_char)
    ids = list(enc["input_ids"])
    T = len(ids)
    tgt = obj_ids(lm, target) if target is not None else []
    full = ids + tgt[:-1]
    return full, s_idx, T, tgt


def pad_batch(seqs: list[list[int]], pad: int):
    n = max(len(s) for s in seqs)
    ids = torch.full((len(seqs), n), pad, dtype=torch.long)
    mask = torch.zeros((len(seqs), n), dtype=torch.long)
    for i, s in enumerate(seqs):
        ids[i, : len(s)] = torch.tensor(s)
        mask[i, : len(s)] = 1
    return ids, mask


# ----------------------------------------------------------------------------- context prefixes
def context_prefixes(lm: LM, n: int = 5, length: int = 10, seed: int = 1234) -> list[str]:
    """ROME-style random prefixes: model samples (top-k 5) from short starters; '' (bare) first."""
    starters = ["The", "Therefore", "Because", "I", "You", "It", "In", "When"]
    g = torch.Generator().manual_seed(seed)
    out = [""]
    for s in starters[:n]:
        ids = torch.tensor([lm.tok.encode(s)])
        with torch.no_grad():
            for _ in range(length):
                logits = lm.model(ids).logits[0, -1]
                top = logits.topk(5)
                p = torch.softmax(top.values, -1)
                nxt = top.indices[torch.multinomial(p, 1, generator=g)]
                ids = torch.cat([ids, nxt.view(1, 1)], 1)
        txt = lm.tok.decode(ids[0]).replace("{", " ").replace("}", " ")
        out.append(txt.strip() + ". ")
    return out


# ----------------------------------------------------------------------------- keys / covariance
@torch.no_grad()
def keys_at(lm: LM, layer: int, reqs: list[Request], prefixes: list[str]) -> torch.Tensor:
    """[d_ff, n] keys at the subject's last token, averaged over the prefixes."""
    mod = down_proj(lm, layer)
    out = []
    for r in reqs:
        acc = []
        for p in prefixes:
            ids, s_idx, _, _ = build_prompt(lm, p, r.template, r.subject, None)
            store = {}
            h = mod.register_forward_pre_hook(lambda m, a: store.__setitem__("k", a[0].detach()))
            try:
                lm.model(torch.tensor([ids], device=lm.device))
            finally:
                h.remove()
            acc.append(store["k"][0, s_idx].float())
        out.append(torch.stack(acc).mean(0))
    return torch.stack(out, 1)


@torch.no_grad()
def residual_at(lm: LM, layer: int, reqs: list[Request]) -> torch.Tensor:
    """[d_model, n] block-`layer` output at the subject's last token of the bare edit prompt."""
    out = []
    for r in reqs:
        ids, s_idx, _, _ = build_prompt(lm, "", r.template, r.subject, None)
        store = {}
        h = lm.layers[layer].register_forward_hook(
            lambda m, a, o: store.__setitem__("z", (o[0] if isinstance(o, tuple) else o).detach()))
        try:
            lm.model(torch.tensor([ids], device=lm.device))
        finally:
            h.remove()
        out.append(store["z"][0, s_idx].float())
    return torch.stack(out, 1)


@torch.no_grad()
def second_moment(lm: LM, layers: list[int], docs: list[str], n_tokens: int, ctx: int = 512,
                  log=None) -> dict[int, torch.Tensor]:
    """C_l = E[k k^T] over corpus tokens at each layer's MLP down-projection input (fp64 sums)."""
    d_ff = down_proj(lm, layers[0]).in_features
    sums = {l: torch.zeros(d_ff, d_ff, dtype=torch.float64) for l in layers}
    store: dict = {}
    hs = [down_proj(lm, l).register_forward_pre_hook(
        lambda m, a, l=l: store.__setitem__(l, a[0].detach())) for l in layers]
    seen = 0
    try:
        for doc in docs:
            ids = lm.tok.encode(doc)[:ctx]
            if len(ids) < 16:
                continue
            lm.model(torch.tensor([ids], device=lm.device))
            for l in layers:
                k = store[l][0].float()
                sums[l] += (k.T @ k).double()
            seen += len(ids)
            if log:
                log(seen)
            if seen >= n_tokens:
                break
    finally:
        for h in hs:
            h.remove()
    return {l: (sums[l] / seen).float() for l in layers}, seen


# ----------------------------------------------------------------------------- target optimization
def optimize_delta(lm: LM, req: Request, layer: int, prefixes: list[str], where: str,
                   steps: int = 25, lr: float = 0.5, kl_w: float = 0.0625, wd: float = 0.5,
                   clamp: float = 4.0, stop_p: float = 0.9, ll_reg: dict | None = None):
    """Find delta added at the subject's last token so the model predicts req.target.
    where='mlp': delta on the down-projection output of `layer` (ROME v*).
    where='resid': delta on the residual output of block `layer` (MEMIT z).
    Returns (target_vector, init_vector, info) with target = init + delta, measured on the bare prompt.
    ll_reg (S9 attack A2, notes/s9_plan.md): {"layers": [...], "lam": float, "tau": float} adds
    lam * mean_l softplus(LL_l(target first token) - tau) on the bare prompt (prefix 0), where LL_l is
    the logit-lens log-prob of block l's output at the last prompt token. Default None = S7 ROME."""
    dev = lm.device
    seqs, sidx, tpos, tgts = [], [], [], []
    for p in prefixes:
        full, s_idx, T, tgt = build_prompt(lm, p, req.template, req.subject, req.target)
        seqs.append(full)
        sidx.append(s_idx)
        tpos.append(T)
        tgts.append(tgt)
    # KL prompt: "{subject} is a"
    kl_full, kl_s, kl_T, _ = build_prompt(lm, "", "{} is a", req.subject, None)
    seqs.append(kl_full)
    sidx.append(kl_s)
    pad = lm.tok.pad_token_id if lm.tok.pad_token_id is not None else 0
    ids, mask = pad_batch(seqs, pad)
    ids, mask = ids.to(dev), mask.to(dev)
    n_ctx = len(prefixes)
    mod = down_proj(lm, layer) if where == "mlp" else lm.layers[layer]
    d = mod.out_features if where == "mlp" else lm.model.config.hidden_size
    delta = torch.zeros(d, device=dev, requires_grad=True)
    store: dict = {}

    def hook(m, a, o):
        t = o[0] if isinstance(o, tuple) else o
        if "init" not in store:
            store["init"] = t[0, sidx[0]].detach().clone()
        t = t.clone()
        for b in range(len(seqs)):
            t[b, sidx[b]] = t[b, sidx[b]] + delta
        return (t,) + tuple(o[1:]) if isinstance(o, tuple) else t

    with torch.no_grad():
        base_logits = lm.model(ids, attention_mask=mask).logits
        kl_ref = torch.log_softmax(base_logits[n_ctx, kl_T - 1].float(), -1)
    for p in lm.model.parameters():
        p.requires_grad_(False)
    opt = torch.optim.Adam([delta], lr=lr)
    h = mod.register_forward_hook(hook)
    info = {"steps": 0, "p_target": None}
    try:
        for step in range(steps):
            opt.zero_grad()
            out = lm.model(ids, attention_mask=mask, output_hidden_states=ll_reg is not None)
            logits = out.logits.float()
            lps, probs = [], []
            for b in range(n_ctx):
                lp = torch.log_softmax(logits[b], -1)
                tok_lp = torch.stack([lp[tpos[b] - 1 + i, t] for i, t in enumerate(tgts[b])])
                lps.append(tok_lp.mean())
                probs.append(tok_lp.sum().exp())
            nll = -torch.stack(lps).mean()
            kl_now = torch.log_softmax(logits[n_ctx, kl_T - 1], -1)
            kl = torch.nn.functional.kl_div(kl_now, kl_ref, log_target=True, reduction="sum")
            reg = wd * delta.norm() ** 2 / store["init"].norm() ** 2
            loss = nll + kl_w * kl + reg
            if ll_reg is not None and ll_reg["layers"]:
                from depthlaw.depth.common import final_norm_and_unembed
                norm, unemb = final_norm_and_unembed(lm.model)
                hl = torch.stack([out.hidden_states[l + 1][0, tpos[0] - 1] for l in ll_reg["layers"]])
                llp = torch.log_softmax(unemb(norm(hl)).float(), -1)[:, tgts[0][0]]
                pen = torch.nn.functional.softplus(llp - ll_reg["tau"]).mean()
                loss = loss + ll_reg["lam"] * pen
                info["ll_pen"] = float(pen)
            p_mean = float(torch.stack(probs).mean())
            info.update(steps=step + 1, p_target=p_mean, nll=float(nll))
            if p_mean > stop_p and (ll_reg is None or not ll_reg["layers"]
                                    or info["ll_pen"] < ll_reg.get("stop_pen", 0.1)):
                break
            loss.backward()
            opt.step()
            with torch.no_grad():
                mx = clamp * store["init"].norm()
                if delta.norm() > mx:
                    delta.mul_(mx / delta.norm())
    finally:
        h.remove()
    init = store["init"].float()
    return (init + delta.detach()).float(), init, info


# ----------------------------------------------------------------------------- deltas
def save_delta(path: Path, factors: dict[str, torch.Tensor], meta: dict) -> None:
    from safetensors.torch import save_file
    path.parent.mkdir(parents=True, exist_ok=True)
    save_file({k: v.contiguous().to(torch.float16) if not k.endswith("::full") else v.contiguous().float()
               for k, v in factors.items()}, str(path), metadata={"meta": json.dumps(meta)})


def load_delta(path: Path) -> dict[str, torch.Tensor]:
    from safetensors.torch import load_file
    return load_file(str(path))


@torch.no_grad()
def apply_delta(lm: LM, factors: dict[str, torch.Tensor], sign: float = 1.0) -> None:
    params = dict(lm.model.named_parameters())
    names = {k.split("::")[0] for k in factors}
    for n in names:
        p = params[n]
        if f"{n}::full" in factors:
            d = factors[f"{n}::full"]
        else:
            d = factors[f"{n}::B"].float() @ factors[f"{n}::A"].float()
        p.add_(sign * d.to(p.dtype).to(p.device))


@contextmanager
def applied(lm: LM, factors: dict[str, torch.Tensor]):
    apply_delta(lm, factors, 1.0)
    try:
        yield
    finally:
        apply_delta(lm, factors, -1.0)


# ----------------------------------------------------------------------------- efficacy
@torch.no_grad()
def first_token_rank(lm: LM, template: str, subject: str, target: str) -> int:
    ids, _, T, tgt = build_prompt(lm, "", template, subject, target)
    logits = lm.model(torch.tensor([ids[:T]], device=lm.device)).logits[0, -1]
    return int((logits > logits[tgt[0]]).sum()) + 1


def null_space_projector(C: torch.Tensor, thresh: float) -> tuple[torch.Tensor, int]:
    """AlphaEdit: projector onto eigenvectors of C with eigenvalue < thresh."""
    evals, evecs = torch.linalg.eigh(C.double())
    U = evecs[:, evals < thresh]
    return (U @ U.T).float(), int(U.shape[1])


def finite(x) -> bool:
    return x is not None and not (isinstance(x, float) and math.isnan(x))


def to_np(x):
    return np.asarray(x)
