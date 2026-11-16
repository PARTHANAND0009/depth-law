"""LoRA fine-tuning to inject facts: (a) SFT on edit prompt -> new object, (b) causal-LM
fine-tuning on synthetic documents (depthlaw.zoo.synth_docs). Result is returned as low-rank
delta factors so the base model can be restored and evaluation code is shared with ROME/MEMIT."""
from __future__ import annotations

import random

import torch

from depthlaw.depth.common import LM
from depthlaw.zoo.core import Request, build_prompt, first_token_rank, pad_batch


def sft_examples(lm: LM, reqs: list[Request]):
    ex = []
    for r in reqs:
        full, _, T, tgt = build_prompt(lm, "", r.template, r.subject, r.target)
        ids = full + [tgt[-1]]
        labels = [-100] * T + tgt
        ex.append((ids, labels))
    return ex


def doc_examples(lm: LM, docs: list[str], max_len: int = 256):
    ex = []
    for d in docs:
        ids = lm.tok.encode(d)[:max_len]
        ex.append((ids, list(ids)))
    return ex


def efficacy(lm: LM, reqs: list[Request]) -> float:
    return sum(first_token_rank(lm, r.template, r.subject, r.target) == 1 for r in reqs) / len(reqs)


def train_lora(lm: LM, examples, reqs: list[Request], r: int = 8, alpha: int = 16,
               targets=("query_key_value", "dense_4h_to_h"), lr: float = 3e-4, bs: int = 8,
               max_epochs: int = 20, stop_eff: float = 0.9, seed: int = 1234, log=None):
    """Trains LoRA until efficacy on reqs >= stop_eff or max_epochs. Restores lm.model to the
    base model and returns (factors, info)."""
    from peft import LoraConfig, get_peft_model
    torch.manual_seed(seed)
    rng = random.Random(seed)
    cfg = LoraConfig(r=r, lora_alpha=alpha, target_modules=list(targets), lora_dropout=0.0, bias="none")
    pm = get_peft_model(lm.model, cfg)
    opt = torch.optim.AdamW([p for p in pm.parameters() if p.requires_grad], lr=lr, weight_decay=0.0)
    pad = lm.tok.pad_token_id if lm.tok.pad_token_id is not None else 0
    info = {"epochs": 0, "efficacy": None, "history": []}
    base = lm.model
    lm.model = pm  # efficacy() runs through the adapted model
    try:
        for ep in range(max_epochs):
            pm.train()
            order = list(range(len(examples)))
            rng.shuffle(order)
            tot = 0.0
            for s in range(0, len(order), bs):
                batch = [examples[i] for i in order[s:s + bs]]
                ids, mask = pad_batch([b[0] for b in batch], pad)
                lab, _ = pad_batch([b[1] for b in batch], -100)
                lab[mask == 0] = -100
                out = pm(input_ids=ids.to(base.device), attention_mask=mask.to(base.device),
                         labels=lab.to(base.device))
                opt.zero_grad()
                out.loss.backward()
                opt.step()
                tot += float(out.loss) * len(batch)
            pm.eval()
            eff = efficacy(lm, reqs)
            info["history"].append({"epoch": ep + 1, "loss": tot / len(examples), "efficacy": eff})
            info.update(epochs=ep + 1, efficacy=eff)
            if log:
                log(epoch=ep + 1, loss=tot / len(examples), efficacy=eff)
            if eff >= stop_eff:
                break
        factors = {}
        for name, mod in pm.named_modules():
            if hasattr(mod, "lora_A") and "default" in getattr(mod, "lora_A", {}):
                A = mod.lora_A["default"].weight.detach()
                B = mod.lora_B["default"].weight.detach() * mod.scaling["default"]
                pname = name.replace("base_model.model.", "") + ".weight"
                factors[f"{pname}::B"] = B.float().clone()
                factors[f"{pname}::A"] = A.float().clone()
    finally:
        lm.model = pm.unload()
        lm.model.eval()
        for p in lm.model.parameters():
            p.requires_grad_(False)
    return factors, info
