#!/usr/bin/env python3
"""EXPLORATORY analyses for the G5 revision (not preregistered; requested by the G5 reviews and the human's G5 message).
Reads existing results files only; writes results/G5expl/expl.json. Every quantity here is EXPLORATORY.

Study 2 (correct cells, carrier-averaged D1 in layers):
  - frame-pair differences: RMS |D1_a - D1_b| (layers) within fact for pairs of frames that differ only by the neutral
    prefix "According to reference sources," (length), only by order (SF/RF), only by form (cloze/question), and by a
    lexical variant;
  - discreteness: number of distinct D1 values, share of cells at the modal layer;
  - facts with >= 8 correct paraphrases; facts with a single correct paraphrase;
  - H4 (preregistered as EXPLORATORY): order, form and length main effects from the frame fixed effects, in layers;
  - D4 split of the wording share (rt + frame vs ft) and Phi-based n' (absolute coefficient) from p2_results.json.
Study 1 (H-R rows, results/S3b):
  - co-occurrence slope of the H3 model in layers per log1p unit, with a Wald 95% interval (coef +- 1.96 SE) x L;
  - shares of the random variance (relation, relation x template, subject, residual) from the H1 fit;
  - convergent check: Spearman between D1 (half_prob_depth) and the logit-lens depth on rows where both exist;
  - worked example for the correctness audit (Pythia-1.4B): one fact with one correct and one wrong template.
Compute: GPU minutes per run from the start/done events of each run's log.jsonl.
Usage: g5_expl.py [out.json]"""
import json, math, os, pathlib, statistics, sys

os.environ.setdefault("ARROW_DEFAULT_MEMORY_POOL", "system")
import numpy as np
import pandas as pd
import pyarrow as pa
pa.set_cpu_count(1); pa.set_io_thread_count(1)
import pyarrow.parquet as pq

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "results/G5expl/expl.json"
D = ROOT / "results/P2analysis/correct"
MODELS = {"Llama": ("Llama-3.1-8B", "meta-llama/Llama-3.1-8B", 32), "Olmo": ("OLMo-2-1124-7B", "allenai/OLMo-2-1124-7B", 32)}
R = {"status": "EXPLORATORY", "study2": {}, "study1": {}, "compute": {}}

frames = {}
for l in (ROOT / "materials/paraphrases_v1.jsonl").read_text().splitlines():
    f = json.loads(l); frames[f["template_id"]] = f["frame"]
PAIRS = {"prefix": [(0, 1), (2, 3), (4, 5), (6, 7)], "order": [(0, 2), (1, 3), (4, 6), (5, 7)],
         "form": [(0, 4), (1, 5), (2, 6), (3, 7)], "lexical": [(0, 8), (2, 9)]}
res2 = json.loads((D / "p2_results.json").read_text())
for k, (short, full, Lk) in MODELS.items():
    d = pd.read_csv(D / f"long_{short}_correct.csv")
    c = d.groupby(["fact_id", "template_id"], as_index=False)["D1"].mean()
    c["layer"] = c["D1"] * Lk
    w = c.pivot(index="fact_id", columns="template_id", values="layer")
    out = {}
    for name, prs in PAIRS.items():
        diffs = np.concatenate([(w[a] - w[b]).dropna().to_numpy() for a, b in prs if a in w and b in w])
        out[name] = {"rms_layers": float(np.sqrt(np.mean(diffs ** 2))), "n_pairs": int(len(diffs))}
    vals = np.round(c["layer"].to_numpy(), 6)
    vc = pd.Series(vals).value_counts()
    ncorr = c.groupby("fact_id").size()
    # H4 frame fixed effects (frame0 = SF-cloze-short is the reference), D1, in layers
    h4 = json.loads((ROOT / f"results/P2analysis/h4/fit_{short}_h4_D1.json").read_text())["fixef"]
    fe = {0: 0.0, **{i: h4[f"frame{i}"] for i in range(1, 10)}}
    mean = lambda ids: statistics.mean(fe[i] for i in ids) * Lk
    h4l = {"order_RF_minus_SF": mean([2, 3, 6, 7]) - mean([0, 1, 4, 5]),
           "form_question_minus_cloze": mean([4, 5, 6, 7]) - mean([0, 1, 2, 3]),
           "length_long_minus_short": mean([1, 3, 5, 7]) - mean([0, 2, 4, 6]),
           "range_all_frames": (max(fe.values()) - min(fe.values())) * Lk}
    pm = res2["models"][full]["fits"]
    v4 = pm["D4"]["vc"]; nc = res2["n_carriers_used"]
    den4 = v4["fact"] + v4["rt"] + v4["frame"] + v4["ft"] + (v4["fc"] + v4["Residual"]) / nc
    R["study2"][k] = {
        "pairs": out, "n_cells": int(len(c)), "n_distinct_d1": int(vc.size), "share_modal": float(vc.iloc[0] / len(c)),
        "modal_layer": float(vc.index[0]), "facts_ge8": int((ncorr >= 8).sum()), "facts_single": int((ncorr == 1).sum()),
        "n_facts": int(ncorr.size), "h4_layers": h4l,
        "d4_split": {"systematic": (v4["rt"] + v4["frame"]) / den4, "fact_x_paraphrase": v4["ft"] / den4},
        "nprime_phi_d1": pm["D1"]["point"]["nprime_Phi"], "nprime_g_d4": pm["D4"]["point"]["nprime_G"],
        "nprime_phi_d4": pm["D4"]["point"]["nprime_Phi"], "g1_d1": pm["D1"]["point"]["G_k"][0],
    }

# Study 1
hr = json.loads((ROOT / "results/HR_gate.json").read_text())
for key, m in hr["models"].items():
    run = pathlib.Path(m["depth_run"]).parent
    t = pq.read_table(ROOT / m["depth_run"].split("depth-law/")[-1] if "depth-law/" in m["depth_run"] else ROOT / m["depth_run"],
                      columns=["fact_id", "template_id", "correct_at1", "half_prob_depth", "logit_lens_depth", "n_layers"]).to_pandas()
    L = int(t["n_layers"].iloc[0])
    mm = m["main"]; vc = mm["vc"]; tot = sum(vc.values())
    both = t.dropna(subset=["half_prob_depth", "logit_lens_depth"])
    R["study1"][key] = {
        "L": L, "n_correct": int(mm["n_correct"]), "n_rows": int(mm["n_rows"]),
        "cooc_slope_layers": mm["cooc_coef"] * L, "cooc_slope_lo": (mm["cooc_coef"] - 1.96 * mm["cooc_se"]) * L,
        "cooc_slope_hi": (mm["cooc_coef"] + 1.96 * mm["cooc_se"]) * L,
        "vc_share": {g: vc[g] / tot for g in vc},
        "lens_spearman": float(both["half_prob_depth"].rank().corr(both["logit_lens_depth"].rank())), "lens_n": int(len(both)),
    }
# worked example (Pythia-1.4B): first fact (by id) with template 0 correct and template 1 wrong
m = hr["models"]["EleutherAI/pythia-1.4b"]
t = pq.read_table(ROOT / "results/S3b/S3b-pythia-1.4b-a7dfeb5-20261121T063528Z/depth.parquet",
                  columns=["fact_id", "template_id", "relation", "correct_at1", "half_prob_depth", "causal_final",
                           "final_logprob_curves", "final_rank_curves", "n_layers"]).to_pandas()
t["template_id"] = t["template_id"].astype(int)
ok = t.pivot_table(index="fact_id", columns="template_id", values="correct_at1", aggfunc="first")
fid = sorted(ok.index[(ok[0] == True) & (ok[1] == False)])[0]  # noqa: E712
ex = []
for tid in (0, 1):
    r = t[(t.fact_id == fid) & (t.template_id == tid)].iloc[0]
    lp = np.array([np.array(c, dtype=float) for c in r["final_logprob_curves"]])   # carriers x layers
    rk = np.array([np.array(c, dtype=float) for c in r["final_rank_curves"]])
    ex.append({"template_id": tid, "correct": bool(r["correct_at1"]), "d1": float(r["half_prob_depth"]),
               "rank1_onset": None if r["causal_final"] is None or (isinstance(r["causal_final"], float) and math.isnan(r["causal_final"])) else float(r["causal_final"]),
               "p_mean": np.exp(lp).mean(axis=0).tolist(), "rank_median": np.median(rk, axis=0).tolist()})
facts = pd.read_parquet(ROOT / "data/facts_g1cpu.parquet", columns=["fact_id", "subject", "relation", "object", "templates"]) \
    if (ROOT / "data/facts_g1cpu.parquet").exists() else None
row = facts[facts.fact_id == fid].iloc[0] if facts is not None else None
R["study1"]["audit_example"] = {"model": "EleutherAI/pythia-1.4b", "fact_id": fid, "L": int(t["n_layers"].iloc[0]),
                                "subject": None if row is None else row["subject"], "object": None if row is None else row["object"],
                                "relation": None if row is None else row["relation"],
                                "templates": None if row is None else [str(x) for x in list(row["templates"])[:2]],
                                "curves": ex}
# compute (GPU minutes per run from log.jsonl start/done)
def minutes(logf):
    ev = [json.loads(l) for l in logf.read_text().splitlines() if l.strip()]
    ts = [pd.Timestamp(e["utc"]) for e in ev if "utc" in e]
    dev = next((e.get("device") for e in ev if e.get("event") == "start"), None)
    return (max(ts) - min(ts)).total_seconds() / 60, dev
for lab, pat in (("study2", "results/P2/P2-*/log.jsonl"), ("study1", "results/S3b/S3b-*/log.jsonl")):
    runs = {p.parent.name: minutes(p) for p in sorted(ROOT.glob(pat))}
    R["compute"][lab] = {"runs": {k: {"minutes": v[0], "device": v[1]} for k, v in runs.items()},
                         "total_minutes": sum(v[0] for v in runs.values())}
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(R, indent=1, default=float) + "\n")
print("wrote", OUT.relative_to(ROOT))
