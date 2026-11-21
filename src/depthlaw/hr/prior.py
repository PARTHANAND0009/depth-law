"""Model log prior of object first tokens (prereg/HR_revised.md B2), via a streamed forward.

The forward pass is the model's own modules run one at a time: embedding rows for the prompt
tokens -> each decoder block (weights loaded, applied to every prompt, released) -> final norm
-> unembedding in row chunks. Weights come from local safetensors (mmap) or from the Hub by
HTTP range requests, so peak memory is about one block (fp32) and nothing is written to disk.
The arithmetic is that of a standard fp32 forward; tests/test_hr_prior.py checks it against
AutoModelForCausalLM on pythia-70m and on a random tiny OLMo-2.
"""
from __future__ import annotations

import json
import struct
import time

import numpy as np
import torch
from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer

from depthlaw.depth.common import _out_tensor, find_layers

PREFIXES = ["The", "It is", "This is", "The answer is", "I think it is", "Here is", "One example is",
            "Some people say", "The word is", "In the"]
DT = {"F32": torch.float32, "F16": torch.float16, "BF16": torch.bfloat16}
SUPPORTED = {"gpt_neox", "olmo2"}


class LocalSource:
    def __init__(self, files: list[str]):
        from safetensors import safe_open
        self.h = {}
        for f in files:
            h = safe_open(f, "pt")
            for k in h.keys():
                self.h[k] = h

    def __contains__(self, k):
        return k in self.h

    def shape(self, k):
        return list(self.h[k].get_slice(k).get_shape())

    def get(self, k):
        return self.h[k].get_tensor(k)

    def rows(self, k, a, b):
        return self.h[k].get_slice(k)[a:b]


class RemoteSource:
    """safetensors on the Hub, read tensor by tensor with HTTP range requests."""

    def __init__(self, repo: str, revision: str, files: list[str]):
        import requests
        from huggingface_hub import hf_hub_url
        from concurrent.futures import ThreadPoolExecutor
        self.s = requests.Session()
        self.s.mount("https://", requests.adapters.HTTPAdapter(pool_connections=16, pool_maxsize=16))
        self.pool = ThreadPoolExecutor(8)
        self.part = 32 << 20
        self.meta = {}
        self.bytes = 0
        for f in files:
            url = hf_hub_url(repo, f, revision=revision)
            n = struct.unpack("<Q", self._get(url, 0, 8))[0]
            hdr = json.loads(self._get(url, 8, n))
            hdr.pop("__metadata__", None)
            for k, m in hdr.items():
                self.meta[k] = (url, 8 + n, m)

    def _get(self, url, start, length):
        err = None
        for attempt in range(7):
            try:
                r = self.s.get(url, headers={"Range": f"bytes={start}-{start + length - 1}"}, timeout=300)
                r.raise_for_status()
                if len(r.content) != length:
                    raise OSError(f"short read {len(r.content)} != {length}")
                self.bytes += length
                return r.content
            except Exception as e:  # noqa: BLE001 - retried with backoff
                err = e
                time.sleep(2 ** attempt)
        raise RuntimeError(f"range read failed: {url} {start}+{length}: {err!r}")

    def __contains__(self, k):
        return k in self.meta

    def shape(self, k):
        return list(self.meta[k][2]["shape"])

    def _read(self, k, r0=None, r1=None):
        url, base, m = self.meta[k]
        a, b = m["data_offsets"]
        shp = list(m["shape"])
        if r0 is not None:
            rb = (b - a) // shp[0]
            a, b, shp = a + r0 * rb, a + r1 * rb, [r1 - r0] + shp[1:]
        buf = bytearray(b - a)
        parts = [(o, min(b - a, o + self.part)) for o in range(0, b - a, self.part)]

        def fetch(oe):
            o, e = oe
            buf[o:e] = self._get(url, base + a + o, e - o)
        list(self.pool.map(fetch, parts))
        return torch.frombuffer(buf, dtype=DT[m["dtype"]]).reshape(shp)

    def get(self, k):
        return self._read(k)

    def rows(self, k, a, b):
        return self._read(k, a, b)


def hub_source(name: str, revision: str = "main"):
    """Local cached safetensors if present, else Hub range reads. Returns (source, provenance)."""
    from huggingface_hub import HfApi, try_to_load_from_cache
    from depthlaw.depth.common import weight_files
    files = weight_files(name, revision)
    shards = sorted(f for f in files if f.startswith("model-") and f.endswith(".safetensors"))
    use = shards or ["model.safetensors"]
    if revision != "main":
        raise ValueError("HR prior is computed at main only")
    local = [try_to_load_from_cache(name, f, revision=revision) for f in use]
    if all(isinstance(p, str) for p in local):
        src, mode = LocalSource(local), "local_cache"
    else:
        src, mode = RemoteSource(name, revision, use), "hub_range"
    sha = HfApi().model_info(name, revision=revision).sha
    return src, {"weight_files": {f: files.get(f) for f in use}, "source": mode, "hub_commit": sha}


@torch.no_grad()
def streamed_final_logprobs(config, src, prompt_ids: list[list[int]], head_chunk: int = 8192) -> torch.Tensor:
    """log_softmax over the vocabulary at the final position of each prompt: [n_prompts, V] fp32."""
    if config.model_type not in SUPPORTED:
        raise ValueError(f"streamed forward not validated for {config.model_type}")
    with torch.device("meta"):
        model = AutoModelForCausalLM.from_config(config, dtype=torch.float32, attn_implementation="sdpa")
    model.eval()
    names = {m: n for n, m in model.named_modules()}

    def load(mod):
        p = names[mod] + "." if names[mod] else ""
        sd = {k: src.get(p + k).float() for k in mod.state_dict()}
        mod.load_state_dict(sd, assign=True, strict=True)

    base = model.base_model
    emb, head = model.get_input_embeddings(), model.get_output_embeddings()
    ek = names[emb] + ".weight"
    hk = names[head] + ".weight"
    if hk not in src:
        alias = {"lm_head.weight": "embed_out.weight"}.get(hk)  # GPT-NeoX checkpoint name
        if alias and alias in src:
            hk = alias
        elif getattr(config, "tie_word_embeddings", False):
            hk = ek
        else:
            raise KeyError(f"unembedding {hk} not in checkpoint")
    assert getattr(head, "bias", None) is None, "unembedding bias not handled"
    rot = type(base.rotary_emb)(config=model.config)
    hs, pes, pos = [], [], []
    for ids in prompt_ids:
        h = torch.stack([src.rows(ek, i, i + 1)[0].float() for i in ids])[None]
        p = torch.arange(len(ids))[None]
        hs.append(h), pos.append(p), pes.append(rot(h, p))
    for layer in find_layers(model):
        load(layer)
        for j in range(len(hs)):
            hs[j] = _out_tensor(layer(hs[j], attention_mask=None, position_ids=pos[j], position_embeddings=pes[j]))
        layer.to("meta")
    norm = getattr(base, "final_layer_norm", None) or base.norm
    load(norm)
    last = torch.cat([norm(h[:, -1]) for h in hs])  # [n, d]
    V = src.shape(hk)[0]
    logits = torch.empty(len(hs), V)
    for a in range(0, V, head_chunk):
        b = min(V, a + head_chunk)
        logits[:, a:b] = last @ src.rows(hk, a, b).float().T
    return torch.log_softmax(logits, -1)


def compute_prior(name: str, objects: list[str], revision: str = "main") -> tuple[dict, torch.Tensor, dict]:
    """{object: mean over PREFIXES of log p(first token of ' '+object)}, the [10, V] logprobs, provenance."""
    tok = AutoTokenizer.from_pretrained(name, revision=revision)
    config = AutoConfig.from_pretrained(name, revision=revision)
    src, prov = hub_source(name, revision)
    t0 = time.time()
    ids = [tok(p).input_ids for p in PREFIXES]  # as common.encode
    lp = streamed_final_logprobs(config, src, ids)
    first = {o: tok.encode(" " + o, add_special_tokens=False)[0] for o in objects}
    prior = {o: float(lp[:, t].mean()) for o, t in first.items()}
    prov.update(seconds=round(time.time() - t0, 1), prefix_token_ids=ids, bytes_read=getattr(src, "bytes", None),
                n_layers=config.num_hidden_layers, vocab=int(lp.shape[1]))
    return prior, lp, prov


def standard_final_logprobs(model, prompt_ids):
    out = []
    with torch.no_grad():
        for ids in prompt_ids:
            out.append(torch.log_softmax(model(torch.tensor([ids])).logits[0, -1].float(), -1))
    return torch.stack(out)


def first_token_ids(tok, objects):
    return np.array([tok.encode(" " + o, add_special_tokens=False)[0] for o in objects])
