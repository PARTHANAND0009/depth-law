"""S8 hidden-state pass for the LCF baseline (notes/s8_plan.md).

For each audited model (clean base, each kept batch/LoRA model, each rome_single edit) run the
template-0 prompt of every evaluated fact and of 200 clean calibration facts, take the last-token
residual after every block, form inter-layer differences h_{l+1} - h_l, and score each evaluated
prompt by a per-layer diagonal Mahalanobis distance whose mean/variance come from the 200
calibration prompts run through the SAME audited model. Variances are shrunk toward their mean
(Ledoit-Wolf shrinkage intensity for a diagonal target). Only scores are stored.

Output: results/S8/<run_id>/lcf.parquet with columns model_id, fact_id, edit_fact_id, lcf,
lcf_layers (per-layer distances).
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from depthlaw.depth.common import load_lm
from depthlaw.io import ROOT, RunLog, make_run_id, provenance, seed_everything
from depthlaw.zoo.core import apply_delta, load_delta

SEED = 1234
N_CALIB = 200
BASE = "EleutherAI/pythia-1.4b"


def calib_facts(seed: int = SEED) -> list[str]:
    p = ROOT / "data" / "splits" / "s8_calib.json"
    if p.exists():
        return json.loads(p.read_text())["fact_ids"]
    g1 = json.loads((ROOT / "data" / "splits" / "g1_cpu_subsample.json").read_text())["fact_ids"]
    req = json.loads((ROOT / "data" / "splits" / "s7_requests.json").read_text())
    used = set(req["controls"]) | {r["fact_id"] for r in req["requests"] + req["pilot"]}
    pool = sorted(set(g1) - used)
    rng = np.random.default_rng(seed)
    ids = sorted(rng.choice(pool, N_CALIB, replace=False).tolist())
    p.write_text(json.dumps({"created": time.strftime("%Y-%m-%d"), "seed": seed,
                             "rule": "200 seeded G1 facts, not S7 controls/requests/pilot (notes/s8_plan.md)",
                             "n": len(ids), "fact_ids": ids}, indent=1))
    return ids


@torch.no_grad()
def last_token_states(lm, prompts: list[str], bs: int = 16) -> np.ndarray:
    """[n, L+1, d] float32 residual stream at the last prompt token (embeddings + every block)."""
    tok = lm.tok
    out = []
    for s in range(0, len(prompts), bs):
        enc = [tok.encode(p) for p in prompts[s:s + bs]]
        T = max(len(e) for e in enc)
        pad = tok.pad_token_id if tok.pad_token_id is not None else 0
        ids = torch.tensor([e + [pad] * (T - len(e)) for e in enc])
        mask = torch.tensor([[1] * len(e) + [0] * (T - len(e)) for e in enc])
        hs = lm.model(input_ids=ids.to(lm.device), attention_mask=mask.to(lm.device),
                      output_hidden_states=True).hidden_states
        last = torch.tensor([len(e) - 1 for e in enc])
        H = torch.stack([h[torch.arange(len(enc)), last] for h in hs], 1)  # [b, L+1, d]
        out.append(H.float().cpu().numpy())
    return np.concatenate(out)


def diffs(H: np.ndarray) -> np.ndarray:
    return H[:, 1:] - H[:, :-1]                                             # [n, L, d]


def lw_diag_var(X: np.ndarray) -> np.ndarray:
    """Per-feature variances shrunk toward their mean (Ledoit-Wolf intensity, diagonal target).
    X [n, d] -> [d]."""
    n = X.shape[0]
    Xc = X - X.mean(0)
    v = (Xc ** 2).mean(0)
    mu = v.mean()
    # LW intensity for diagonal shrinkage of the variance vector toward mu
    b2 = ((Xc ** 2 - v) ** 2).sum(0).sum() / n ** 2
    d2 = ((v - mu) ** 2).sum()
    a = min(1.0, b2 / d2) if d2 > 0 else 1.0
    return a * mu + (1 - a) * v


def lcf_scores(calib_D: np.ndarray, eval_D: np.ndarray) -> np.ndarray:
    """calib_D, eval_D [n, L, d] -> per-layer distances [n_eval, L]."""
    L = calib_D.shape[1]
    out = np.zeros((eval_D.shape[0], L))
    for l in range(L):
        m = calib_D[:, l].mean(0)
        v = lw_diag_var(calib_D[:, l])
        out[:, l] = np.sqrt((((eval_D[:, l] - m) ** 2) / v).mean(1))
    return out


def prompt_of(facts: pd.DataFrame, fid: str) -> str:
    return list(facts.loc[fid, "templates"])[0].format(facts.loc[fid, "subject"])


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--s7-run", default=None)
    ap.add_argument("--run-dir", default=None)
    ap.add_argument("--threads", type=int, default=4)
    ap.add_argument("--models", nargs="*", default=None, help="subset of model ids (debug)")
    ap.add_argument("--rome-limit", type=int, default=None)
    args = ap.parse_args(argv)
    torch.set_num_threads(args.threads)
    seed_everything(SEED)
    s7 = args.s7_run or sorted((ROOT / "results" / "S7").glob("S7-pythia-1.4b-*"))[0]
    man = json.loads((ROOT / "zoo" / "manifest.json").read_text())
    facts = pd.read_parquet(ROOT / "data" / "facts.parquet").set_index("fact_id")
    calib = calib_facts()
    calib_prompts = [prompt_of(facts, f) for f in calib]

    if args.run_dir:
        run_id = Path(args.run_dir).name
        log = RunLog("S8", run_id)
    else:
        run_id = make_run_id("S8lcf", BASE)
        log = RunLog("S8", run_id)
        (log.dir / "meta.json").write_text(json.dumps(provenance(run_id, {"n_calib": N_CALIB, "seed": SEED}, BASE, "main"), indent=2))
    parts = log.dir / "lcf_parts"
    parts.mkdir(exist_ok=True)
    lm = load_lm(BASE)

    jobs = []
    for m in man["models"]:
        if m.get("kept"):
            ev = pd.read_parquet(ROOT / "data" / "zoo" / f"{m['model_id']}_eval.parquet")
            jobs.append((m["model_id"], m["delta"], ev.fact_id.tolist(), None))
    rome = pd.read_parquet(Path(s7) / "rome" / "depth.parquet")
    for e in man["rome_single"]["kept_edits"][: args.rome_limit]:
        fids = sorted(set(rome.loc[rome.edit_fact_id == e["fact_id"], "fact_id"]))
        jobs.append(("rome_single", e["delta"], fids, e["fact_id"]))
    if args.models:
        jobs = [j for j in jobs if j[0] in args.models]
    log.log(event="jobs", n=len(jobs))

    for mid, delta, fids, efid in jobs:
        key = f"{mid}__{efid}" if efid else mid
        dst = parts / f"{key}.parquet"
        if dst.exists():
            continue
        t0 = time.time()
        fac = load_delta(ROOT / delta) if delta else None
        if fac:
            apply_delta(lm, fac, 1.0)
        try:
            Dc = diffs(last_token_states(lm, calib_prompts))
            De = diffs(last_token_states(lm, [prompt_of(facts, f) for f in fids]))
        finally:
            if fac:
                apply_delta(lm, fac, -1.0)
        per = lcf_scores(Dc, De)
        out = pd.DataFrame({"model_id": mid, "fact_id": fids, "edit_fact_id": efid,
                            "lcf": per.mean(1), "lcf_layers": list(per.astype(np.float32))})
        out["run_id"] = run_id
        out.to_parquet(dst, index=False)
        log.log(event="lcf_model", key=key, n=len(fids), s=round(time.time() - t0, 1))
    allp = pd.concat([pd.read_parquet(p) for p in sorted(parts.glob("*.parquet"))], ignore_index=True)
    allp.to_parquet(log.dir / "lcf.parquet", index=False)
    log.log(event="done", n_rows=len(allp))
    print(log.dir)


if __name__ == "__main__":
    main()
