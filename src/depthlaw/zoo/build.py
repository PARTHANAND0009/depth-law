"""S7 zoo builder (notes/s7_plan.md). Resumable steps in one work dir results/S7/<run_id>/.

python -m depthlaw.zoo.build --step all [--run-dir results/S7/<run_id>] [--model EleutherAI/pythia-1.4b]
Steps: requests stats rome z pilot batch lora manifest evaltables (all = in this order).
"""
from __future__ import annotations

import argparse
import itertools
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from depthlaw.depth.causal import causal_depth
from depthlaw.depth.common import load_lm
from depthlaw.depth.lenses import behavior_and_lens
from depthlaw.io import ROOT, RunLog, make_run_id, provenance, seed_everything
from depthlaw.zoo.core import (Request, apply_delta, applied, context_prefixes, first_token_rank,
                               load_delta, null_space_projector, optimize_delta, save_delta,
                               second_moment)

SEED = 1234
CFG = {
    "n_controls": 300, "n_requests": 1000, "n_pilot": 100,
    "rome_layer": 5, "memit_layers": [3, 4, 5, 6, 7], "rome_n": 100, "rome_controls_per_edit": 5,
    "stats_tokens": 60000, "mom2_candidates": [15000, 1500, 150, 15],
    "ae_thresh": 2e-2, "ae_L2": 10.0, "keep_efficacy": 0.9,
    "lora": {"r": 8, "alpha": 16, "lr": 3e-4, "bs": 8, "max_epochs": 20},
    "batch_sizes": [100, 1000], "lora_sizes": [50, 200, 1000], "synthdoc_n": 50, "docs_per_fact": 10,
    "carriers_from": "configs/s3.yaml",
}


class Ctx:
    def __init__(self, args):
        self.args = args
        if args.run_dir:
            self.dir = Path(args.run_dir)
            self.run_id = self.dir.name
        else:
            self.run_id = make_run_id("S7", args.model.split("/")[-1])
            self.dir = ROOT / "results" / "S7" / self.run_id
        self.log_ = RunLog("S7", self.run_id)
        self.dir = self.log_.dir
        self.mtag = args.model.split("/")[-1]
        self.cache = ROOT / "cache" / "zoo" / (self.mtag + ("_test" if args.test else ""))
        self.cache.mkdir(parents=True, exist_ok=True)
        self._lm = None
        self.facts = pd.read_parquet(ROOT / "data" / "facts.parquet").set_index("fact_id", drop=False)
        import yaml
        self.carriers = yaml.safe_load(open(ROOT / CFG["carriers_from"]))["carriers"]
        meta = self.dir / "meta.json"
        if not meta.exists():
            meta.write_text(json.dumps(provenance(self.run_id, CFG, args.model, "main"), indent=2))

    def log(self, **kw):
        self.log_.log(**kw)
        print(json.dumps(kw, default=str), flush=True)

    @property
    def lm(self):
        if self._lm is None:
            self._lm = load_lm(self.args.model)
            for p in self._lm.model.parameters():
                p.requires_grad_(False)
        return self._lm

    # ------------------------------------------------------------------ shared data
    def req_file(self) -> Path:
        if self.args.test:
            return self.dir / "requests.json"
        return ROOT / "data" / "splits" / "s7_requests.json"

    def requests(self, which: str = "edit") -> list[Request]:
        d = json.loads(self.req_file().read_text())
        rows = d["requests"] if which == "edit" else d["pilot"]
        return [Request(r["fact_id"], r["subject"], r["template"], r["target"], r["type"]) for r in rows]

    def controls(self) -> list[str]:
        return json.loads(self.req_file().read_text())["controls"]

    def prefixes(self) -> list[str]:
        p = self.dir / "prefixes.json"
        if not p.exists():
            p.write_text(json.dumps(context_prefixes(self.lm, 5, seed=SEED)))
        return json.loads(p.read_text())

    def cov(self, layers) -> dict:
        return {l: torch.load(self.cache / f"C_l{l}.pt") for l in layers}


# ---------------------------------------------------------------------- step: requests
def step_requests(c: Ctx):
    if c.req_file().exists():
        c.log(event="requests", status="exists")
        return
    g1 = set(json.loads((ROOT / "data/splits/g1_cpu_subsample.json").read_text())["fact_ids"])
    F = c.facts
    g1f = F[F.fact_id.isin(g1)]
    ctrl = g1f.groupby("relation").sample(12, random_state=SEED).sample(CFG["n_controls"], random_state=SEED)
    pool = F[~F.fact_id.isin(g1) & (F.n_templates >= 3)].sample(frac=1.0, random_state=SEED)
    bpath = c.dir / "pool_behaviour.parquet"
    done = pd.read_parquet(bpath) if bpath.exists() else pd.DataFrame(columns=["fact_id", "r0", "r1", "r2"])
    have = set(done.fact_id)
    rows = []
    t0 = time.time()
    for i, f in enumerate(pool.itertuples()):
        if f.fact_id in have:
            continue
        rk = [first_token_rank(c.lm, t, f.subject, f.object) for t in list(f.templates)[:3]]
        rows.append({"fact_id": f.fact_id, "r0": rk[0], "r1": rk[1], "r2": rk[2]})
        if len(rows) % 250 == 0:
            done = pd.concat([done, pd.DataFrame(rows)], ignore_index=True)
            done.to_parquet(bpath, index=False)
            rows = []
            c.log(event="behaviour", n=len(done), s=round(time.time() - t0))
    if rows:
        done = pd.concat([done, pd.DataFrame(rows)], ignore_index=True)
        done.to_parquet(bpath, index=False)
    beh = done.set_index("fact_id")
    rng = np.random.default_rng(SEED)
    objs = F.groupby("relation").apply(lambda g: g[["object", "obj_first_tok_pythia"]].drop_duplicates("object").values.tolist(),
                                       include_groups=False).to_dict()
    need = CFG["n_requests"] + CFG["n_pilot"]
    out, used = [], set()
    want = itertools.cycle(["counterfactual", "true_new"])
    typ = next(want)
    for f in pool.itertuples():
        if len(out) >= need:
            break
        if f.fact_id in used:
            continue
        tmpl = list(f.templates)
        if typ == "true_new":
            b = beh.loc[f.fact_id]
            if min(b.r0, b.r1, b.r2) == 1:
                continue
            target = f.object
        else:
            cands = [o for o, t in objs[f.relation] if o != f.object and t != f.obj_first_tok_pythia]
            if not cands:
                continue
            target = cands[int(rng.integers(len(cands)))]
        out.append({"fact_id": f.fact_id, "subject": f.subject, "relation": f.relation, "template": tmpl[0],
                    "templates": tmpl[:3], "true_object": f.object, "target": target, "type": typ})
        used.add(f.fact_id)
        typ = next(want)
    assert len(out) == need, len(out)
    d = {"created": time.strftime("%Y-%m-%d"), "run_id": c.run_id, "seed": SEED,
         "rule": "notes/s7_plan.md (requests alternate counterfactual / true_new over a seeded shuffle "
                 "of the non-G1 pool; pilot = last 100)",
         "controls": sorted(ctrl.fact_id.tolist()),
         "requests": out[: CFG["n_requests"]], "pilot": out[CFG["n_requests"]:]}
    c.req_file().write_text(json.dumps(d, indent=1))
    c.log(event="requests", n=len(out), types=pd.Series([o["type"] for o in out]).value_counts().to_dict())


# ---------------------------------------------------------------------- step: stats
def step_stats(c: Ctx):
    layers = sorted(set(CFG["memit_layers"]) | {CFG["rome_layer"]})
    if all((c.cache / f"C_l{l}.pt").exists() for l in layers):
        c.log(event="stats", status="exists")
        return
    docs = (json.loads(line)["text"] for line in open(ROOT / "data/s6/corpus/docs.jsonl"))
    t0 = time.time()
    last = [0]

    def lg(seen):
        if seen - last[0] >= 5000:
            last[0] = seen
            c.log(event="stats_progress", tokens=seen, s=round(time.time() - t0))
    C, seen = second_moment(c.lm, layers, docs, CFG["stats_tokens"], log=lg)
    for l in layers:
        torch.save(C[l], c.cache / f"C_l{l}.pt")
    c.log(event="stats", tokens=seen, layers=layers, s=round(time.time() - t0),
          source="data/s6/corpus/docs.jsonl (FineWeb-Edu sample-10BT, first docs)")


# ---------------------------------------------------------------------- measurement rows
def measure(c: Ctx, fact_id: str, obj: str, extra: dict) -> list[dict]:
    f = c.facts.loc[fact_id]
    rows = []
    for ti, t in enumerate(list(f.templates)[:3]):
        row = {"fact_id": fact_id, "template_id": ti, "relation": f.relation, **extra}
        try:
            row.update(behavior_and_lens(c.lm, f.subject, obj, t))
            row.update(causal_depth(c.lm, f.subject, obj, t, c.carriers, final_only=True))
        except Exception as e:  # noqa: BLE001
            row["error"] = repr(e)[:300]
        rows.append(row)
    return rows


# ---------------------------------------------------------------------- step: rome
def step_rome(c: Ctx):
    from depthlaw.zoo.rome import rome_factors
    L = CFG["rome_layer"]
    C = c.cov([L])[L]
    pre = c.prefixes()
    reqs = c.requests()[: CFG["rome_n"]]
    ctrls = c.controls()
    rng = np.random.default_rng(SEED)
    ctrl_sets = [list(rng.choice(ctrls, CFG["rome_controls_per_edit"], replace=False)) for _ in reqs]
    rdir = c.dir / "rome"
    (rdir / "chunks").mkdir(parents=True, exist_ok=True)
    ddir = c.cache / "rome"
    t0 = time.time()
    for i0 in range(0, len(reqs), 10):
        dst = rdir / "chunks" / f"c{i0:04d}.parquet"
        if dst.exists():
            continue
        rows, effs = [], []
        for i in range(i0, min(i0 + 10, len(reqs))):
            r = reqs[i]
            fac, info = rome_factors(c.lm, r, L, C, pre)
            save_delta(ddir / f"{r.rid}.safetensors", fac, {"method": "rome", "layer": L, "fact_id": r.rid,
                                                             "target": r.target, "run_id": c.run_id})
            with applied(c.lm, fac):
                f = c.facts.loc[r.rid]
                ranks = [first_token_rank(c.lm, t, r.subject, r.target) for t in list(f.templates)[:3]]
                eff = ranks[0] == 1
                ex = {"model_id": f"rome_{r.rid}", "method": "rome", "edit_fact_id": r.rid, "rtype": r.rtype,
                      "efficacy_edit": eff, "efficacy_para": float(np.mean([x == 1 for x in ranks[1:]])),
                      "opt_steps": info["steps"], "opt_p": info["p_target"]}
                rows += measure(c, r.rid, r.target, {**ex, "edited": True, "object_eval": r.target})
                for cf in ctrl_sets[i]:
                    rows += measure(c, cf, c.facts.loc[cf].object, {**ex, "edited": False,
                                                                     "object_eval": c.facts.loc[cf].object})
            effs.append(eff)
        out = pd.DataFrame(rows)
        out["run_id"], out["model"], out["revision"] = c.run_id, c.args.model, "main"
        out.to_parquet(dst, index=False)
        c.log(event="rome_chunk", start=i0, efficacy=float(np.mean(effs)), s=round(time.time() - t0))
    parts = sorted((rdir / "chunks").glob("*.parquet"))
    df = pd.concat([pd.read_parquet(p) for p in parts], ignore_index=True)
    df.to_parquet(rdir / "depth.parquet", index=False)
    e = df[df.edited].drop_duplicates("edit_fact_id")
    c.log(event="rome_done", n_edits=len(e), efficacy=float(e.efficacy_edit.mean()),
          efficacy_para=float(e.efficacy_para.mean()))


# ---------------------------------------------------------------------- step: z
def step_z(c: Ctx):
    L = CFG["memit_layers"][-1]
    pre = c.prefixes()
    zdir = c.cache / f"z_l{L}"
    zdir.mkdir(parents=True, exist_ok=True)
    reqs = c.requests() + c.requests("pilot")
    t0 = time.time()
    n = 0
    for r in reqs:
        p = zdir / f"{r.rid}.pt"
        if p.exists():
            continue
        z, init, info = optimize_delta(c.lm, r, L, pre, "resid", clamp=0.75)
        torch.save({"z": z, "init": init, "info": info, "target": r.target}, p)
        n += 1
        if n % 25 == 0:
            c.log(event="z_progress", done=len(list(zdir.glob("*.pt"))), of=len(reqs), s=round(time.time() - t0))
    c.log(event="z_done", n=len(reqs))


def load_z(c: Ctx, reqs):
    L = CFG["memit_layers"][-1]
    zs = []
    for r in reqs:
        d = torch.load(c.cache / f"z_l{L}" / f"{r.rid}.pt")
        assert d["target"] == r.target
        zs.append(d["z"])
    return torch.stack(zs, 1)


def model_report(c: Ctx, reqs, model_id: str, extra: dict) -> dict:
    """Efficacy on the edit prompt, paraphrase efficacy, control correct@1 (template 0)."""
    eff, para = [], []
    for r in reqs:
        f = c.facts.loc[r.rid]
        ranks = [first_token_rank(c.lm, t, r.subject, r.target) for t in list(f.templates)[:3]]
        eff.append(ranks[0] == 1)
        para.append(np.mean([x == 1 for x in ranks[1:]]))
    ctrl = [first_token_rank(c.lm, c.facts.loc[cf].templates[0], c.facts.loc[cf].subject,
                             c.facts.loc[cf].object) == 1 for cf in c.controls()]
    rep = {"model_id": model_id, "n_edits": len(reqs), "efficacy": float(np.mean(eff)),
           "efficacy_para": float(np.mean(para)), "control_correct_at1_t0": float(np.mean(ctrl)),
           "n_controls": len(ctrl), "kept": bool(np.mean(eff) >= CFG["keep_efficacy"]),
           "edited_fact_ids": [r.rid for r in reqs], **extra}
    return rep


def clean_control(c: Ctx) -> float:
    p = c.dir / "clean_control.json"
    if not p.exists():
        ctrl = [first_token_rank(c.lm, c.facts.loc[cf].templates[0], c.facts.loc[cf].subject,
                                 c.facts.loc[cf].object) == 1 for cf in c.controls()]
        p.write_text(json.dumps({"control_correct_at1_t0": float(np.mean(ctrl)), "n": len(ctrl)}))
    return json.loads(p.read_text())["control_correct_at1_t0"]


# ---------------------------------------------------------------------- step: pilot
def step_pilot(c: Ctx):
    from depthlaw.zoo.memit import memit_factors
    p = c.dir / "pilot.json"
    if p.exists():
        c.log(event="pilot", status="exists")
        return
    layers = CFG["memit_layers"]
    C = c.cov(layers)
    pre = c.prefixes()
    reqs = c.requests("pilot")
    zs = load_z(c, reqs)
    res = {"candidates": {}}
    for w in CFG["mom2_candidates"]:
        fac = memit_factors(c.lm, reqs, zs, layers, C, pre, mom2_weight=w)
        eff = float(np.mean([first_token_rank(c.lm, r.template, r.subject, r.target) == 1 for r in reqs]))
        apply_delta(c.lm, fac, -1.0)
        res["candidates"][str(w)] = eff
        c.log(event="pilot_memit", mom2_weight=w, efficacy=eff)
    ok = [w for w in CFG["mom2_candidates"] if res["candidates"][str(w)] >= CFG["keep_efficacy"]]
    res["chosen_mom2_weight"] = max(ok) if ok else None
    P = projectors(c, C)
    fac = memit_factors(c.lm, reqs, zs, layers, C, pre, projectors=P, L2=CFG["ae_L2"])
    res["alphaedit_efficacy"] = float(np.mean([first_token_rank(c.lm, r.template, r.subject, r.target) == 1
                                               for r in reqs]))
    apply_delta(c.lm, fac, -1.0)
    res["n_pilot"] = len(reqs)
    p.write_text(json.dumps(res, indent=1))
    c.log(event="pilot", **res)


def projectors(c: Ctx, C):
    out, dims = {}, {}
    for l, Cl in C.items():
        pth = c.cache / f"P_l{l}_t{CFG['ae_thresh']}.pt"
        if pth.exists():
            d = torch.load(pth)
        else:
            P, k = null_space_projector(Cl, CFG["ae_thresh"])
            d = {"P": P, "k": k}
            torch.save(d, pth)
        out[l] = d["P"]
        dims[l] = d["k"]
    c.log(event="nullspace_dims", dims=dims)
    return out


# ---------------------------------------------------------------------- step: batch (MEMIT / AlphaEdit)
def step_batch(c: Ctx):
    from depthlaw.zoo.memit import memit_factors
    pilot = json.loads((c.dir / "pilot.json").read_text())
    layers = CFG["memit_layers"]
    C = c.cov(layers)
    pre = c.prefixes()
    allreqs = c.requests()
    mdir = c.dir / "models"
    mdir.mkdir(exist_ok=True)
    clean_control(c)
    bs = CFG["batch_sizes"]
    jobs = [(f"alphaedit{n}", n, "alphaedit") for n in bs]
    if pilot["chosen_mom2_weight"] is not None:
        jobs = [(f"memit{n}", n, "memit") for n in bs] + jobs
    else:
        for mid in [f"memit{n}" for n in bs]:
            (mdir / f"{mid}.json").write_text(json.dumps(
                {"model_id": mid, "kept": False, "missing": "MISSING: no mom2 weight reached pilot efficacy 0.9"}))
    for mid, n, meth in jobs:
        if (mdir / f"{mid}.json").exists():
            continue
        reqs = allreqs[:n]
        zs = load_z(c, reqs)
        t0 = time.time()
        if meth == "memit":
            fac = memit_factors(c.lm, reqs, zs, layers, C, pre, mom2_weight=pilot["chosen_mom2_weight"],
                                log=lambda **k: c.log(event=f"{mid}_layer", **k))
            extra = {"mom2_weight": pilot["chosen_mom2_weight"]}
        else:
            fac = memit_factors(c.lm, reqs, zs, layers, C, pre, projectors=projectors(c, C), L2=CFG["ae_L2"],
                                log=lambda **k: c.log(event=f"{mid}_layer", **k))
            extra = {"ae_thresh": CFG["ae_thresh"], "ae_L2": CFG["ae_L2"]}
        dpath = c.cache / f"{mid}.safetensors"
        save_delta(dpath, fac, {"method": meth, "layers": layers, "n": n, "run_id": c.run_id})
        rep = model_report(c, reqs, mid, {"method": meth, "layers": layers, "delta": str(dpath.relative_to(ROOT)),
                                          "s": round(time.time() - t0), **extra})
        apply_delta(c.lm, fac, -1.0)
        (mdir / f"{mid}.json").write_text(json.dumps(rep, indent=1))
        c.log(event="model", **{k: v for k, v in rep.items() if k != "edited_fact_ids"})


# ---------------------------------------------------------------------- step: lora / synthdoc
def step_lora(c: Ctx):
    from depthlaw.zoo.lora_inject import doc_examples, sft_examples, train_lora
    from depthlaw.zoo.synth_docs import make_docs
    allreqs = c.requests()
    mdir = c.dir / "models"
    mdir.mkdir(exist_ok=True)
    clean_control(c)
    lc = CFG["lora"]
    jobs = [(f"lora{n}", n, "lora") for n in CFG["lora_sizes"]] + [(f"synthdoc{CFG['synthdoc_n']}", CFG["synthdoc_n"], "synthdoc")]
    for mid, n, meth in jobs:
        if (mdir / f"{mid}.json").exists():
            continue
        reqs = allreqs[:n]
        t0 = time.time()
        if meth == "lora":
            ex = sft_examples(c.lm, reqs)
        else:
            docs = [d for r in reqs for d in make_docs(r.subject, list(c.facts.loc[r.rid].templates)[:3], r.target,
                                                       CFG["docs_per_fact"], SEED)]
            (c.dir / f"{mid}_docs.json").write_text(json.dumps(docs, indent=0))
            ex = doc_examples(c.lm, docs)
        fac, info = train_lora(c.lm, ex, reqs, r=lc["r"], alpha=lc["alpha"], lr=lc["lr"], bs=lc["bs"],
                               max_epochs=lc["max_epochs"], stop_eff=CFG["keep_efficacy"], seed=SEED,
                               log=lambda **k: c.log(event=f"{mid}_epoch", **k))
        dpath = c.cache / f"{mid}.safetensors"
        save_delta(dpath, fac, {"method": meth, "n": n, "run_id": c.run_id})
        with applied(c.lm, fac):
            rep = model_report(c, reqs, mid, {"method": meth, "delta": str(dpath.relative_to(ROOT)),
                                              "train": info, "s": round(time.time() - t0), **lc})
        (mdir / f"{mid}.json").write_text(json.dumps(rep, indent=1))
        c.log(event="model", **{k: v for k, v in rep.items() if k not in ("edited_fact_ids", "train")})


# ---------------------------------------------------------------------- step: manifest + eval tables
def step_manifest(c: Ctx):
    models = [json.loads(p.read_text()) for p in sorted((c.dir / "models").glob("*.json"))]
    rome = pd.read_parquet(c.dir / "rome" / "depth.parquet")
    e = rome[rome.edited].drop_duplicates("edit_fact_id")
    reqs = {r.rid: r for r in c.requests()}
    man = {"run_id": c.run_id, "base_model": c.args.model, "revision": "main",
           "clean_control_correct_at1_t0": clean_control(c),
           "plan": "notes/s7_plan.md", "requests": "data/splits/s7_requests.json",
           "rome_single": {"n_edits": int(len(e)), "efficacy": float(e.efficacy_edit.mean()),
                           "kept_edits": [{"fact_id": f, "target": reqs[f].target, "type": reqs[f].rtype,
                                           "delta": f"cache/zoo/{c.mtag}/rome/{f}.safetensors"}
                                          for f in e[e.efficacy_edit].edit_fact_id]},
           "models": [{**m, "edits": [{"fact_id": f, "target": reqs[f].target, "type": reqs[f].rtype}
                                      for f in m.get("edited_fact_ids", [])]}
                      for m in models]}
    for m in man["models"]:
        m.pop("edited_fact_ids", None)
    (c.dir / "manifest.json").write_text(json.dumps(man, indent=1))
    if c.args.test:
        return
    (ROOT / "zoo").mkdir(exist_ok=True)
    (ROOT / "zoo" / "manifest.json").write_text(json.dumps(man, indent=1))
    c.log(event="manifest", kept=[m["model_id"] for m in man["models"] if m.get("kept")])


def step_evaltables(c: Ctx):
    man = json.loads((c.dir / "manifest.json").read_text())
    F = c.facts.reset_index(drop=True)
    ctrl = F[F.fact_id.isin(c.controls())].copy()
    ctrl["edited"], ctrl["rtype"], ctrl["true_object"] = False, "control", ctrl.object
    out = ROOT / "data" / "zoo"
    out.mkdir(parents=True, exist_ok=True)
    for m in man["models"]:
        if not m.get("kept"):
            continue
        ed = pd.DataFrame(m["edits"])
        e = F.set_index("fact_id").loc[ed.fact_id].reset_index()
        e["true_object"] = e.object
        e["object"] = ed.target.values
        e["o_aliases"] = [[] for _ in range(len(e))]
        e["edited"], e["rtype"] = True, ed.type.values
        t = pd.concat([e, ctrl], ignore_index=True)
        t.to_parquet((c.dir if c.args.test else out) / f"{m['model_id']}_eval.parquet", index=False)
        c.log(event="evaltable", model_id=m["model_id"], n=len(t))


STEPS = {"requests": step_requests, "stats": step_stats, "rome": step_rome, "z": step_z, "pilot": step_pilot,
         "batch": step_batch, "lora": step_lora, "manifest": step_manifest, "evaltables": step_evaltables}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="EleutherAI/pythia-1.4b")
    ap.add_argument("--run-dir", default=None)
    ap.add_argument("--step", nargs="+", default=["all"])
    ap.add_argument("--threads", type=int, default=4)
    ap.add_argument("--test", action="store_true", help="tiny config for pythia-70m code tests")
    args = ap.parse_args(argv)
    if args.test:
        CFG.update(n_requests=20, n_pilot=10, rome_layer=2, memit_layers=[1, 2, 3], rome_n=3,
                   stats_tokens=3000, batch_sizes=[10, 20], lora_sizes=[10], synthdoc_n=5)
        CFG["lora"]["max_epochs"] = 3
    torch.set_num_threads(args.threads)
    seed_everything(SEED)
    c = Ctx(args)
    steps = list(STEPS) if args.step == ["all"] else args.step
    for s in steps:
        c.log(event="step_start", step=s)
        STEPS[s](c)
        c.log(event="step_done", step=s)
    print(c.dir)


if __name__ == "__main__":
    main()
