"""S6 pretraining on CPU: a small GPT-NeoX model trained on data/s6/seed<k>/train.bin in stream order
(one pass, no shuffling, so the fact spacing set in mix.py holds). Resumable from the last checkpoint.

  python -m depthlaw.pretrain.train --seed 1 [--run-dir results/S6/<run>] [--max-steps N --pilot]
Checkpoints: <run_dir>/ckpt/step<N>/ (HF model + tokenizer) and <run_dir>/state.pt (optimizer, step).
"""
from __future__ import annotations

import argparse
import json
import math
import shutil
import time
from pathlib import Path

import numpy as np
import torch
import yaml
from transformers import AutoTokenizer, GPTNeoXConfig, GPTNeoXForCausalLM

from depthlaw.io import ROOT, RunLog, make_run_id, provenance, seed_everything

D = ROOT / "data" / "s6"


def build_model(mcfg: dict, vocab: int) -> GPTNeoXForCausalLM:
    cfg = GPTNeoXConfig(vocab_size=vocab, hidden_size=mcfg["d_model"], num_hidden_layers=mcfg["n_layers"],
                        num_attention_heads=mcfg["n_heads"], intermediate_size=mcfg["d_ff"],
                        max_position_embeddings=mcfg["ctx"], rotary_pct=0.25, use_parallel_residual=True,
                        tie_word_embeddings=False, bos_token_id=0, eos_token_id=0)
    return GPTNeoXForCausalLM(cfg)


def lr_at(step: int, total: int, base: float, warmup: int) -> float:
    if step < warmup:
        return base * (step + 1) / warmup
    p = (step - warmup) / max(1, total - warmup)
    return base * (0.1 + 0.9 * 0.5 * (1 + math.cos(math.pi * min(1.0, p))))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--run-dir", default=None)
    ap.add_argument("--max-steps", type=int, default=None)
    ap.add_argument("--pilot", action="store_true", help="throughput pilot: stage S6pilot, no checkpoints")
    ap.add_argument("--threads", type=int, default=4)
    ap.add_argument("--override", default=None, help="JSON overriding model/train config keys (pilot)")
    a = ap.parse_args(argv)
    cfg = yaml.safe_load(open(ROOT / "configs" / "s6.yaml"))
    if a.override:
        o = json.loads(a.override)
        cfg["model"].update(o.get("model", {})); cfg["train"].update(o.get("train", {}))
    torch.set_num_threads(a.threads)
    seed_everything(a.seed)
    stage = "S6pilot" if a.pilot else "S6"
    if a.run_dir:
        rdir = Path(a.run_dir); run_id = rdir.name
    else:
        run_id = make_run_id(stage, f"s6lm_seed{a.seed}"); rdir = None
    log = RunLog(stage, run_id)
    rdir = log.dir
    tk = AutoTokenizer.from_pretrained(D / "tokenizer")
    data = np.memmap(D / f"seed{a.seed}" / "train.bin", dtype=np.uint16, mode="r")
    ctx, bs = cfg["model"]["ctx"], cfg["train"]["batch_seqs"]
    n_seq = (len(data) - 1) // ctx
    total = n_seq // bs
    model = build_model(cfg["model"], len(tk))
    opt = torch.optim.AdamW(model.parameters(), lr=cfg["train"]["lr"], betas=(0.9, 0.95),
                            weight_decay=cfg["train"]["weight_decay"])
    step = 0
    st = rdir / "state.pt"
    if st.exists():
        s = torch.load(st, weights_only=False)
        model.load_state_dict(s["model"]); opt.load_state_dict(s["opt"]); step = s["step"]
        torch.set_rng_state(s["rng"])
    else:
        (rdir / "meta.json").write_text(json.dumps(provenance(run_id, {**cfg, "seed": a.seed, "n_params": sum(
            p.numel() for p in model.parameters()), "total_steps": total, "stream_tokens": int(len(data))}), indent=2))
    log.log(event="start", step=step, total_steps=total, n_params=sum(p.numel() for p in model.parameters()),
            tokens_per_step=bs * ctx, threads=a.threads)
    model.train()
    t0, tok0 = time.time(), 0
    end = min(total, a.max_steps) if a.max_steps else total
    while step < end:
        lo = step * bs * ctx
        chunk = torch.from_numpy(np.asarray(data[lo: lo + bs * ctx + 1], dtype=np.int64))
        x = chunk[:-1].view(bs, ctx); y = chunk[1:].view(bs, ctx)
        for g in opt.param_groups:
            g["lr"] = lr_at(step, total, cfg["train"]["lr"], cfg["train"]["warmup_steps"])
        logits = model(x).logits
        loss = torch.nn.functional.cross_entropy(logits.view(-1, logits.size(-1)), y.reshape(-1))
        opt.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()
        step += 1; tok0 += bs * ctx
        if step % 50 == 0 or step == end:
            el = time.time() - t0
            log.log(event="step", step=step, loss=float(loss), lr=opt.param_groups[0]["lr"], tok_per_s=tok0 / el)
        if not a.pilot and (step % cfg["train"]["ckpt_every_steps"] == 0 or step == total):
            tmp = rdir / "state.tmp"
            torch.save({"model": model.state_dict(), "opt": opt.state_dict(), "step": step,
                        "rng": torch.get_rng_state()}, tmp)
            tmp.rename(st)
            if step == total:
                out = rdir / "final"
                if out.exists():
                    shutil.rmtree(out)
                model.save_pretrained(out); tk.save_pretrained(out)
    log.log(event="done", step=step)
    print(rdir)


if __name__ == "__main__":
    main()
