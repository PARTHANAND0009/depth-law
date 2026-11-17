"""S9 adaptive attacks (notes/s9_plan.md). Resumable steps in results/S9/<run_id>/.

python -m depthlaw.attack.run --step predict a1pilot a1 a2 a3 [--run-dir results/S9/<run_id>]
Outputs per attack: <dir>/<attack>/depth.parquet with the same columns as the S7 rome rows
(model_id, edit_fact_id, edited, rtype, fact_id, template_id, ... causal_final), so the S8
detector scores them unchanged; <dir>/<attack>/report.json (efficacy, collateral, compute).
"""
from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from depthlaw.io import ROOT, make_run_id, provenance, seed_everything
from depthlaw.zoo import build as B
from depthlaw.zoo.core import Request, applied, first_token_rank, save_delta, second_moment

SEED = 1234
CFG = {"n_edits": 100, "n_pilot": 10, "a1_layers": [3, 5, 8, 11, 14, 17], "a2_layer": 5, "a2_lam": 1.0,
       "a2_tau": math.log(1e-3), "a2_stop_pen": 0.1, "a3_n": 50, "a3_docs_per_fact": 60, "stats_tokens": 60000}


class Ctx9(B.Ctx):
    def __init__(self, args):
        s7 = sorted((ROOT / "results" / "S7").glob("S7-pythia-1.4b-*"))[0]
        a = argparse.Namespace(model=args.model, run_dir=str(s7), test=False)
        super().__init__(a)                       # S7 dir: requests, prefixes, covariances, controls
        self.s7dir = self.dir
        self.test = args.test
        if args.test:
            self.cache = ROOT / "cache" / "zoo" / (self.mtag + "_s9test")
            self.cache.mkdir(parents=True, exist_ok=True)
        if args.run_dir:
            self.dir = Path(args.run_dir)
            self.run_id = self.dir.name
        else:
            self.run_id = make_run_id("S9test" if args.test else "S9", args.model.split("/")[-1])
            self.dir = ROOT / "results" / "S9" / self.run_id
        self.dir.mkdir(parents=True, exist_ok=True)
        from depthlaw.io import RunLog
        self.log_ = RunLog("S9", self.run_id)
        meta = self.dir / "meta.json"
        if not meta.exists():
            meta.write_text(json.dumps(provenance(self.run_id, {**CFG, "s7": s7.name}, args.model, "main"), indent=2))

    def cov_any(self, layer: int) -> torch.Tensor:
        p = self.cache / f"C_l{layer}.pt"
        if not p.exists():
            docs = (json.loads(line)["text"] for line in open(ROOT / "data/s6/corpus/docs.jsonl"))
            C, seen = second_moment(self.lm, [layer], docs, CFG["stats_tokens"])
            torch.save(C[layer], p)
            self.log(event="stats", layer=layer, tokens=seen)
        return torch.load(p)


# ---------------------------------------------------------------------- predicted depth
def step_predict(c: Ctx9):
    """Attacker's predicted depth per request from the clean depth law (S8 Calibration)."""
    from depthlaw.detect.eval import CLEAN_S3, load_counts
    from depthlaw.detect.features import Calibration
    p = c.dir / "predicted.json"
    if p.exists():
        return
    if c.test:   # code test only: fixed prediction, no counts needed
        d = json.loads(c.req_file().read_text())
        out = {r["fact_id"]: {"d_hat": 0.7, "l_hat": 4, "x": 0.0, "count_missing": True}
               for r in d["requests"][: CFG["n_edits"]] + d["pilot"][: CFG["n_pilot"]]}
        p.write_text(json.dumps({"test": True, "pred": out}, indent=1))
        return
    ce, cf, prov = load_counts()
    controls = set(c.controls())
    clean = pd.read_parquet(ROOT / CLEAN_S3)
    calib = clean[~clean.fact_id.isin(controls)].copy()
    calib["x"] = np.log1p(calib.fact_id.map(ce).astype(float))
    cal = Calibration(calib[calib.x.notna()])
    d = json.loads(c.req_file().read_text())
    out = {}
    for r in d["requests"][: CFG["n_edits"]] + d["pilot"][: CFG["n_pilot"]]:
        cnt = cf.get(r["fact_id"]) if r["type"] == "counterfactual" else ce.get(r["fact_id"])
        x = float(np.log1p(cnt)) if cnt is not None and not pd.isna(cnt) else 0.0
        X = cal._design(pd.DataFrame({"relation": [r["relation"]], "x": [x]}))
        dh = float((X @ cal.fit_causal)[0])
        out[r["fact_id"]] = {"d_hat": dh, "l_hat": int(np.clip(round(dh * 24) - 1, 0, 23)), "x": x,
                             "count_missing": cnt is None or pd.isna(cnt)}
    p.write_text(json.dumps({"counts": prov, "calibration": cal.n, "slopes": cal.slopes(), "pred": out}, indent=1))
    c.log(event="predict", n=len(out))


def _pred(c):
    return json.loads((c.dir / "predicted.json").read_text())["pred"]


def _edit_and_measure(c: Ctx9, r: Request, layer: int, ctrls: list[str], model_id: str, method: str,
                      ll_reg=None) -> tuple[list[dict], dict]:
    from depthlaw.zoo.rome import rome_factors
    t0 = time.time()
    fac, info = rome_factors(c.lm, r, layer, c.cov_any(layer), c.prefixes(),
                             **({"ll_reg": ll_reg} if ll_reg else {}))
    t_edit = time.time() - t0
    save_delta(c.cache / "s9" / method / f"{r.rid}.safetensors", fac,
               {"method": method, "layer": layer, "fact_id": r.rid, "target": r.target, "run_id": c.run_id})
    rows = []
    with applied(c.lm, fac):
        f = c.facts.loc[r.rid]
        ranks = [first_token_rank(c.lm, t, r.subject, r.target) for t in list(f.templates)[:3]]
        ex = {"model_id": model_id, "method": method, "edit_fact_id": r.rid, "rtype": r.rtype,
              "efficacy_edit": ranks[0] == 1, "efficacy_para": float(np.mean([x == 1 for x in ranks[1:]])),
              "opt_steps": info["steps"], "opt_p": info["p_target"], "ll_pen": info.get("ll_pen"),
              "edit_layer": layer, "edit_s": round(t_edit, 1)}
        rows += B.measure(c, r.rid, r.target, {**ex, "edited": True, "object_eval": r.target})
        for cf in ctrls:
            rows += B.measure(c, cf, c.facts.loc[cf].object, {**ex, "edited": False, "object_eval": c.facts.loc[cf].object})
    return rows, ex


def _ctrl_sets(c, n):
    """Same seeded control sets as S7 rome_single (same rng call sequence)."""
    rng = np.random.default_rng(SEED)
    ctrls = c.controls()
    return [list(rng.choice(ctrls, B.CFG["rome_controls_per_edit"], replace=False)) for _ in range(n)]


def _run_single(c: Ctx9, name: str, layer_of, ll_reg_of=None):
    reqs = c.requests()[: CFG["n_edits"]]
    sets = _ctrl_sets(c, len(reqs))
    adir = c.dir / name / "chunks"
    adir.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    for i0 in range(0, len(reqs), 10):
        dst = adir / f"c{i0:04d}.parquet"
        if dst.exists():
            continue
        rows, effs = [], []
        for i in range(i0, min(i0 + 10, len(reqs))):
            r = reqs[i]
            rr, ex = _edit_and_measure(c, r, layer_of(r), sets[i], name, name,
                                       ll_reg_of(r) if ll_reg_of else None)
            rows += rr
            effs.append(ex["efficacy_edit"])
        out = pd.DataFrame(rows)
        out["run_id"], out["model"], out["revision"] = c.run_id, c.args.model, "main"
        out.to_parquet(dst, index=False)
        c.log(event=f"{name}_chunk", start=i0, efficacy=float(np.mean(effs)), s=round(time.time() - t0))
    df = pd.concat([pd.read_parquet(p) for p in sorted(adir.glob("*.parquet"))], ignore_index=True)
    df.to_parquet(c.dir / name / "depth.parquet", index=False)
    e = df[df.edited].drop_duplicates("edit_fact_id")
    ctrl = df[(~df.edited) & (df.template_id == 0)]
    rep = {"attack": name, "n_edits": len(e), "efficacy": float(e.efficacy_edit.mean()),
           "efficacy_para": float(e.efficacy_para.mean()),
           "control_correct_at1_t0": float(ctrl.correct_at1.mean()), "n_control_rows_t0": len(ctrl),
           "edit_s_mean": float(e.edit_s.mean()), "edit_layer_counts": e.edit_layer.value_counts().to_dict(),
           "opt_steps_mean": float(e.opt_steps.mean())}
    (c.dir / name / "report.json").write_text(json.dumps(rep, indent=1, default=str))
    c.log(event=f"{name}_done", **rep)


# ---------------------------------------------------------------------- A1
def step_a1pilot(c: Ctx9):
    p = c.dir / "a1_pilot.json"
    if p.exists():
        return
    pilot = c.requests("pilot")[: CFG["n_pilot"]]
    part = c.dir / "a1_pilot_rows.parquet"
    rows = pd.read_parquet(part).to_dict("records") if part.exists() else []
    done = {(r["edit_fact_id"], r["edit_layer"]) for r in rows}
    for L in CFG["a1_layers"]:
        for r in pilot:
            if (r.rid, L) in done:
                continue
            rr, ex = _edit_and_measure(c, r, L, [], "a1pilot", "a1pilot")
            rows += rr
            pd.DataFrame(rows).to_parquet(part, index=False)
            c.log(event="a1pilot_edit", layer=L, fact_id=r.rid, eff=ex["efficacy_edit"])
    d = pd.DataFrame(rows)
    d["depth"] = d.causal_final.fillna(1.0)
    tab = d.groupby("edit_layer").agg(depth_mean=("depth", "mean"), n=("depth", "size"),
                                      efficacy=("efficacy_edit", "mean")).reset_index()
    p.write_text(json.dumps({"n_pilot": len(pilot), "table": tab.to_dict("records")}, indent=1))
    c.log(event="a1pilot", table=tab.to_dict("records"))


def step_a1(c: Ctx9):
    tab = json.loads((c.dir / "a1_pilot.json").read_text())["table"]
    pred = _pred(c)

    def layer_of(r):
        dh = pred[r.rid]["d_hat"]
        return int(min(tab, key=lambda t: (abs(t["depth_mean"] - dh), t["edit_layer"]))["edit_layer"])
    _run_single(c, "a1_layer_match", layer_of)


# ---------------------------------------------------------------------- A2
def step_a2(c: Ctx9):
    pred = _pred(c)
    L = CFG["a2_layer"]

    def reg_of(r):
        top = min(pred[r.rid]["l_hat"], c.lm.n_layers - 1)
        return {"layers": list(range(L + 1, top)), "lam": CFG["a2_lam"],
                "tau": CFG["a2_tau"], "stop_pen": CFG["a2_stop_pen"]}
    _run_single(c, "a2_depth_reg", lambda r: L, reg_of)


# ---------------------------------------------------------------------- A3
def make_docs_all(subject, templates, obj):
    from depthlaw.zoo.synth_docs import DOC_TEMPLATES, fact_sentence
    docs = []
    for t in templates:
        fs = fact_sentence(t, subject, obj)
        for dt in DOC_TEMPLATES:
            docs.append(dt.format(fact=fs, fact_lc=fs[0].lower() + fs[1:]))
    return docs


def step_a3(c: Ctx9):
    from depthlaw.zoo.lora_inject import doc_examples, train_lora
    name = "a3_freq_spoof"
    adir = c.dir / name
    adir.mkdir(exist_ok=True)
    rep_p = adir / "model.json"
    reqs = c.requests()[: CFG["a3_n"]]
    dpath = c.cache / "s9" / f"{name}.safetensors"
    if not rep_p.exists():
        docs = [d for r in reqs for d in make_docs_all(r.subject, list(c.facts.loc[r.rid].templates)[:3], r.target)]
        (adir / "docs.json").write_text(json.dumps(docs, indent=0))
        lc = B.CFG["lora"]
        t0 = time.time()
        fac, info = train_lora(c.lm, doc_examples(c.lm, docs), reqs, r=lc["r"], alpha=lc["alpha"], lr=lc["lr"],
                               bs=lc["bs"], max_epochs=lc["max_epochs"], stop_eff=B.CFG["keep_efficacy"], seed=SEED,
                               log=lambda **k: c.log(event=f"{name}_epoch", **k))
        s = time.time() - t0
        dpath.parent.mkdir(parents=True, exist_ok=True)
        save_delta(dpath, fac, {"method": name, "n": len(reqs), "run_id": c.run_id})
        with applied(c.lm, fac):
            rep = B.model_report(c, reqs, name, {"method": name, "delta": str(dpath.relative_to(ROOT)),
                                                 "train": info, "train_s": round(s), "n_docs": len(docs)})
        rep_p.write_text(json.dumps(rep, indent=1))
        c.log(event="a3_model", **{k: v for k, v in rep.items() if k not in ("edited_fact_ids", "train")})
    # eval table in the S7 format (edited facts with new object + the 300 controls)
    t = adir / "eval.parquet"
    if not t.exists():
        F = c.facts
        ed = F.loc[[r.rid for r in reqs]].copy()
        ed["true_object"] = ed.object
        ed["object"] = [r.target for r in reqs]
        ed["edited"], ed["rtype"] = True, [r.rtype for r in reqs]
        ct = F.loc[c.controls()].copy()
        ct["true_object"] = ct.object
        ct["edited"], ct["rtype"] = False, "control"
        pd.concat([ed, ct]).reset_index(drop=True).to_parquet(t, index=False)
    c.log(event="a3_ready", delta=str(dpath.relative_to(ROOT)), eval_table=str(t.relative_to(ROOT)))


STEPS = {"predict": step_predict, "a1pilot": step_a1pilot, "a1": step_a1, "a2": step_a2, "a3": step_a3}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="EleutherAI/pythia-1.4b")
    ap.add_argument("--run-dir", default=None)
    ap.add_argument("--step", nargs="+", default=list(STEPS))
    ap.add_argument("--threads", type=int, default=4)
    ap.add_argument("--test", action="store_true", help="tiny config for pythia-70m code tests")
    args = ap.parse_args(argv)
    if args.test:
        CFG.update(n_edits=2, n_pilot=1, a1_layers=[1, 3], a2_layer=1, a3_n=2, a3_docs_per_fact=60, stats_tokens=2000)
        B.CFG["lora"]["max_epochs"] = 2
    torch.set_num_threads(args.threads)
    seed_everything(SEED)
    c = Ctx9(args)
    for s in args.step:
        c.log(event="step_start", step=s)
        STEPS[s](c)
        c.log(event="step_done", step=s)
    print(c.dir)


if __name__ == "__main__":
    main()
