"""P2 depth runner (prereg/P2_prompt_vs_fact.md design; materials/*_v1.jsonl).

For each fact x paraphrase: run the filled paraphrase, take the final-token residual at the output of every
block, write it into the final token of each carrier (carrier "{}" filled with "X"), and record at the
carrier's final position, for every source layer, the probability (softmax, fp32 logits) and the rank of the
object's first token. Long-format rows: fact_id, relation, template_id, carrier, layer, p_object (float16),
rank (int16), plus per (fact, template) behaviour rows (correct@1, final object logprob, carrier-alone object
logprob). Chunks of --chunk facts are written as results/<stage>/<run_id>/chunks/cNNNNN.parquet with a
.sha256 next to each; a chunk that exists is skipped (resume). Verified chunk checksums go to manifest.json.

python -m depthlaw.p2.run_p2 --model M [--n-facts N] [--n-templates K] [--n-carriers C] [--dtype float32]
       [--chunk 10] [--stage P2] [--run-dir DIR] [--device cpu|cuda]
Sync off the instance after each chunk (printed by the runner): rsync -a <run_dir>/ <dest>/<run_id>/
"""
from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from depthlaw.depth.causal import carrier_ids, source_states
from depthlaw.depth.common import load_lm, obj_ids, patch_per_batch_row, rank_of
from depthlaw.io import ROOT, RunLog, make_run_id, provenance, seed_everything

SEED = 20261121


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


@torch.no_grad()
def curves(lm, carrier: str, vecs: torch.Tensor, target: int, batch: int = 64):
    c_ids, _ = carrier_ids(lm, carrier)
    L, pos = vecs.shape[0], c_ids.shape[1] - 1
    ps, rks = [], []
    for s in range(0, L, batch):
        ls = list(range(s, min(L, s + batch)))
        with patch_per_batch_row(lm.layers, ls, [pos] * len(ls), vecs[ls]):
            lg = lm.model(c_ids.repeat(len(ls), 1)).logits[:, -1].float()
        ps.extend(torch.softmax(lg, -1)[:, target].tolist())
        rks.extend(rank_of(lg, target).tolist())
    alone = torch.log_softmax(lm.model(c_ids).logits[0, -1].float(), -1)[target].item()
    return np.asarray(ps), np.asarray(rks), alone


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--revision", default="main")
    ap.add_argument("--n-facts", type=int, default=None)
    ap.add_argument("--n-templates", type=int, default=None)
    ap.add_argument("--n-carriers", type=int, default=None)
    ap.add_argument("--dtype", default="float32")
    ap.add_argument("--chunk", type=int, default=10)
    ap.add_argument("--stage", default="P2")
    ap.add_argument("--run-dir", default=None)
    ap.add_argument("--device", default=None)
    a = ap.parse_args(argv)
    seed_everything(SEED)
    facts = [json.loads(l) for l in open(ROOT / "materials/facts_v1.jsonl")]
    paras = [json.loads(l) for l in open(ROOT / "materials/paraphrases_v1.jsonl")]
    carriers = [json.loads(l) for l in open(ROOT / "materials/carriers_v1.jsonl")]
    if a.n_facts:
        facts = facts[: a.n_facts]
    if a.n_carriers:
        carriers = carriers[: a.n_carriers]
    byrel = {}
    for p in paras:
        byrel.setdefault(p["relation"], []).append(p)
    if a.n_templates:
        byrel = {r: v[: a.n_templates] for r, v in byrel.items()}
    if a.run_dir:
        rdir = Path(a.run_dir); run_id = rdir.name; log = RunLog(a.stage, run_id)
    else:
        run_id = make_run_id(a.stage, a.model); log = RunLog(a.stage, run_id); rdir = log.dir
    cdir = rdir / "chunks"; cdir.mkdir(parents=True, exist_ok=True)
    # A resume (e.g. after the pilot) invalidates any earlier manifest: manifest.json exists only after a run that
    # reached its end, so a run cut short (hard stop) never carries the pilot's manifest (prereg P2 section 1).
    if (rdir / "manifest.json").exists():
        (rdir / "manifest.json").rename(rdir / f"manifest_superseded_{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}.json")
    mat = {f: sha256(ROOT / "materials" / f) for f in ("facts_v1.jsonl", "paraphrases_v1.jsonl", "carriers_v1.jsonl")}
    meta_path = rdir / "meta.json"  # a resume (e.g. after the pilot) keeps the first meta and adds meta_resume_<utc>.json
    if meta_path.exists():
        meta_path = rdir / f"meta_resume_{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}.json"
    meta_path.write_text(json.dumps({**provenance(run_id, vars(a), a.model, a.revision), "materials_sha256": mat}, indent=2))
    lm = load_lm(a.model, a.revision, dtype=getattr(torch, a.dtype), device=a.device)
    log.log(event="start", model=a.model, dtype=str(next(lm.model.parameters()).dtype), device=str(lm.device),
            n_facts=len(facts), n_carriers=len(carriers), n_layers=lm.n_layers)
    t0 = time.time()
    chunks = [facts[i:i + a.chunk] for i in range(0, len(facts), a.chunk)]
    for ci, ch in enumerate(chunks):
        dst = cdir / f"c{ci:05d}.parquet"
        if dst.exists() and (dst.with_suffix(".sha256")).exists():
            continue
        rows, beh = [], []
        for f in ch:
            target = obj_ids(lm, f["object"])[0]
            for p in byrel[f["relation"]]:
                ids, _, states, logits = source_states(lm, p["template"], f["subject"])
                lp = torch.log_softmax(logits.float(), -1)
                beh.append({"fact_id": f["fact_id"], "relation": f["relation"], "template_id": p["template_id"],
                            "frame": p["frame"], "correct_at1": bool(int(logits.argmax()) == target),
                            "obj_first_logprob": float(lp[target]), "n_prompt_tokens": int(ids.shape[1])})
                for c in carriers:
                    ps, rks, alone = curves(lm, c["text"], states[:, -1], target)
                    beh[-1][f"carrier_alone_logprob_c{c['carrier_id']}"] = alone
                    for layer in range(len(ps)):
                        rows.append((f["fact_id"], f["relation"], p["template_id"], c["carrier_id"], layer, ps[layer], rks[layer]))
        df = pd.DataFrame(rows, columns=["fact_id", "relation", "template_id", "carrier", "layer", "p_object", "rank"])
        df["p_object"] = df.p_object.astype(np.float16)
        df["rank"] = df["rank"].clip(upper=np.iinfo(np.int16).max).astype(np.int16)
        df["template_id"] = df.template_id.astype(np.int16); df["carrier"] = df.carrier.astype(np.int8); df["layer"] = df.layer.astype(np.int16)
        tmp = dst.with_suffix(".tmp")
        df.to_parquet(tmp, index=False); tmp.rename(dst)
        bdst = cdir / f"b{ci:05d}.parquet"
        pd.DataFrame(beh).to_parquet(bdst, index=False)
        dst.with_suffix(".sha256").write_text(f"{sha256(dst)}  {dst.name}\n{sha256(bdst)}  {bdst.name}\n")
        log.log(event="chunk", chunk=ci, of=len(chunks), rows=len(df), s=round(time.time() - t0))
        print(f"chunk {ci + 1}/{len(chunks)} rows {len(df)} t={time.time() - t0:.0f}s  sync: rsync -a {rdir}/ <dest>/{run_id}/", flush=True)
    manifest = {}
    for s in sorted(cdir.glob("c*.sha256")):
        for line in s.read_text().splitlines():
            h, name = line.split()
            manifest[name] = {"sha256": h, "ok": sha256(cdir / name) == h}
    (rdir / "manifest.json").write_text(json.dumps(manifest, indent=1))
    log.log(event="done", n_chunks=len(chunks), n_facts=len(facts), n_carriers=len(carriers),
            all_ok=all(v["ok"] for v in manifest.values()) and len(manifest) == len(chunks), s=round(time.time() - t0))
    print(rdir)


if __name__ == "__main__":
    main()
