"""Model loading, layer discovery, prompt helpers, patching hooks (raw HF forward hooks).

nnsight 0.8.2 is installed but its tracing API changed substantially across versions; raw
hooks are used (CLAUDE.md allows this fallback) so behaviour is explicit and testable.
Layer convention: layer l in [0, L-1] is the OUTPUT of decoder block l (residual stream).
Normalized depth = (l + 1) / L.
"""
from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


@dataclass
class LM:
    model: torch.nn.Module
    tok: object
    layers: torch.nn.ModuleList
    name: str
    revision: str

    @property
    def n_layers(self) -> int:
        return len(self.layers)

    @property
    def device(self):
        return next(self.model.parameters()).device


def load_lm(name: str, revision: str = "main", dtype=None, device: str | None = None) -> LM:
    device = device or ("cuda" if torch.cuda.is_available() else "cpu")
    if dtype is None:
        dtype = torch.bfloat16 if device == "cuda" else torch.float32
    tok = AutoTokenizer.from_pretrained(name, revision=revision)
    model = AutoModelForCausalLM.from_pretrained(name, revision=revision, dtype=dtype).to(device).eval()
    return LM(model, tok, find_layers(model), name, revision)


def find_layers(model) -> torch.nn.ModuleList:
    n = model.config.get_text_config().num_hidden_layers
    for _, mod in model.named_modules():
        if isinstance(mod, torch.nn.ModuleList) and len(mod) == n:
            return mod
    raise ValueError("could not find decoder layer list")


def final_norm_and_unembed(model):
    """Return (norm, unembed) modules used for the logit lens."""
    unembed = model.get_output_embeddings()
    norm = None
    for name in ["gpt_neox.final_layer_norm", "model.norm", "model.language_model.norm", "transformer.ln_f"]:
        try:
            norm = model.get_submodule(name)
            break
        except AttributeError:
            continue
    if norm is None:
        raise ValueError("final norm not found")
    return norm, unembed


def _out_tensor(out):
    return out[0] if isinstance(out, tuple) else out


@contextmanager
def capture(layers):
    """Record residual output of every block. Yields list filled after forward."""
    store: list = [None] * len(layers)
    hs = []
    for i, layer in enumerate(layers):
        def hook(mod, inp, out, i=i):
            store[i] = _out_tensor(out).detach()
        hs.append(layer.register_forward_hook(hook))
    try:
        yield store
    finally:
        for h in hs:
            h.remove()


@contextmanager
def patch_per_batch_row(layers, layer_idx: list[int], pos: list[int], vecs: torch.Tensor):
    """Row b of the batch gets out[b, pos[b]] = vecs[b] at the output of block layer_idx[b]."""
    by_layer: dict[int, list[int]] = {}
    for b, l in enumerate(layer_idx):
        by_layer.setdefault(l, []).append(b)
    hs = []
    for l, rows in by_layer.items():
        def hook(mod, inp, out, rows=rows):
            t = _out_tensor(out)
            for b in rows:
                t[b, pos[b]] = vecs[b].to(t.dtype)
            return out
        hs.append(layers[l].register_forward_hook(hook))
    try:
        yield
    finally:
        for h in hs:
            h.remove()


def encode(lm: LM, text: str) -> torch.Tensor:
    return lm.tok(text, return_tensors="pt").input_ids.to(lm.device)


def obj_ids(lm: LM, obj: str) -> list[int]:
    return lm.tok.encode(" " + obj, add_special_tokens=False)


def subject_last_pos(lm: LM, template: str, subject: str) -> tuple[torch.Tensor, int]:
    """Token ids of the filled prompt and the index of the subject's last token."""
    prefix, _ = template.split("{}", 1)
    text = template.format(subject)
    enc = lm.tok(text, return_offsets_mapping=True, return_tensors="pt")
    end_char = len(prefix) + len(subject)
    offs = enc.offset_mapping[0].tolist()
    idx = max(i for i, (a, b) in enumerate(offs) if b > a and a < end_char)
    return enc.input_ids.to(lm.device), idx


def rank_of(logits: torch.Tensor, token: int) -> torch.Tensor:
    """logits [..., V] -> 1-based rank of token."""
    return (logits > logits[..., token:token + 1]).sum(-1) + 1


def first_stable_layer(is_ok: list[bool]) -> int | None:
    """Smallest l such that is_ok[l'] for all l' >= l; None if the last is not ok."""
    first = None
    for l in range(len(is_ok) - 1, -1, -1):
        if is_ok[l]:
            first = l
        else:
            break
    return first


def first_true(is_ok: list[bool]) -> int | None:
    for l, ok in enumerate(is_ok):
        if ok:
            return l
    return None
