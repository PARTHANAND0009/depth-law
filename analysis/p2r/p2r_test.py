#!/usr/bin/env python3
"""Tests for the P2R wrapper and the four-family summary (test only; no model data).
1. Family mapping: the two P2R models map to new families; P2 families unchanged.
2. Refusals of the gating call (before any tokenizer or data is loaded): the five P2 models, one P2R model only, a
   P2R model plus a P2 model, n_boot other than 1000.
3. Four-family summary on synthetic per-model fits: the frozen decide() counts families across both calls, refuses a
   model present in both calls, and evaluates 'fact share > 0' over all included families.
Exit 1 if any check fails."""
import copy
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE.parent / "p2")); sys.path.insert(0, str(HERE))
import p2_analysis as PA  # noqa: E402
from p2r_analysis import P2R_MODELS, configure  # noqa: E402
from p2r_combine import combine  # noqa: E402

fails = []
def check(name, cond):
    print(("ok   " if cond else "FAIL ") + name); cond or fails.append(name)

configure()
check("gemma-2-9b -> gemma2", PA.family("google/gemma-2-9b") == "gemma2")
check("Mistral-7B-v0.1 -> mistral", PA.family("mistralai/Mistral-7B-v0.1") == "mistral")
check("P2 families unchanged", [PA.family(m) for m in ("meta-llama/Llama-3.1-8B", "allenai/OLMo-2-1124-7B", "Qwen/Qwen3-8B",
                                                       "EleutherAI/pythia-1.4b")] == ["llama31", "olmo2", "qwen3", "pythia"])

def refused(args):
    p = subprocess.run([sys.executable, str(HERE / "p2r_analysis.py"), "/tmp/p2r_refusal_test", *args],
                       capture_output=True, text=True, cwd=ROOT)
    return p.returncode != 0 and ("must name each prereg model" in (p.stderr + p.stdout) or "fixes --n-boot" in (p.stderr + p.stdout))
p2 = ["Qwen/Qwen3-8B=none", "meta-llama/Llama-3.1-8B=none", "EleutherAI/pythia-1.4b=none", "EleutherAI/pythia-2.8b=none",
      "allenai/OLMo-2-1124-7B=none"]
check("refuses the five P2 models", refused(["--runs", *p2]))
check("refuses one P2R model only", refused(["--runs", "google/gemma-2-9b=none"]))
check("refuses a P2R model plus a P2 model", refused(["--runs", "google/gemma-2-9b=none", "meta-llama/Llama-3.1-8B=none"]))
check("refuses n_boot != 1000", refused(["--runs", "google/gemma-2-9b=none", "mistralai/Mistral-7B-v0.1=none", "--n-boot", "10"]))

def fake_model(fam, icc1, null_p, diff_lo=-0.05):
    f = {"status": "ok", "point": {"icc1": icc1, "diff": 0.1, "wording": 0.5, "tf_minus_resid": -0.1, "nprime_G": 6},
         "boot": {"ci": {"icc1": [icc1 - 0.05, icc1 + 0.05], "diff": [diff_lo, 0.2]}},
         "vc": {"fact": 1.0, "fc": 0.1}}
    return {"family": fam, "status": "ok", "fits": {"D1": f, "D4": copy.deepcopy(f)},
            "mom": {"D1": {"diff": 0.1}, "D4": {"diff": 0.1}}, "null": {"p": null_p, "status": "ok"}}
def call(models, nc):
    r = {"set": "correct", "gating": True, "test": False, "n_carriers_used": nc, "runs": list(models), "models": models}
    return r, PA.decide(r, "correct", {}, {}, nc if nc else 3)
MISSING = {"status": "MISSING (insufficient data)", "family": None}
p2c = call({"meta-llama/Llama-3.1-8B": fake_model("llama31", 0.31, 0.001, 0.2), "allenai/OLMo-2-1124-7B": fake_model("olmo2", 0.42, 0.001)}, 3)
both = call({P2R_MODELS[0]: fake_model("gemma2", 0.3, 0.001, 0.2), P2R_MODELS[1]: fake_model("mistral", 0.3, 0.5)}, 3)
d = combine(*p2c, *both)
check("summary counts four families", sorted(d["families"]["included_families"]) == ["gemma2", "llama31", "mistral", "olmo2"])
check("summary: fact share > 0 in >= 2 families -> licensed", d["claims"]["fact_share_gt0_(null_p<0.01_in>=2_families)"] is True)
check("summary: H1 in llama31 + gemma2 -> H1 holds (>= 2 families)", d["claims"]["H1_holds_(>=2_families)"] is True)
check("summary: per-rule family lists (k of 4 tallies)", d["families_per_rule"]["fact_share_gt0 (null p<0.01)"] == ["gemma2", "llama31", "olmo2"] and d["families_per_rule"]["H1"] == ["gemma2", "llama31"])
bad = copy.deepcopy(both[1]); bad["per_model"][P2R_MODELS[0]]["G_ceiling_D1"] = 0.123
try:
    combine(*p2c, both[0], bad); check("refuses a decision file that differs from its own results", False)
except SystemExit:
    check("refuses a decision file that differs from its own results", True)
miss2 = call({P2R_MODELS[0]: {**MISSING, "family": "gemma2"}, P2R_MODELS[1]: {**MISSING, "family": "mistral"}}, 0)
try:
    d2 = combine(*p2c, *miss2); ok = sorted(d2["families"]["included_families"]) == ["llama31", "olmo2"]
except Exception as e:  # noqa: BLE001
    ok = False; print("   ", repr(e))
check("both P2R models MISSING (nc 0): no crash, two families", ok)
miss1 = call({P2R_MODELS[0]: fake_model("gemma2", 0.3, 0.001), P2R_MODELS[1]: {**MISSING, "family": "mistral"}}, 3)
check("one P2R model MISSING: three families", sorted(combine(*p2c, *miss1)["families"]["included_families"]) == ["gemma2", "llama31", "olmo2"])
nc2 = call({P2R_MODELS[0]: fake_model("gemma2", 0.3, 0.001), P2R_MODELS[1]: fake_model("mistral", 0.3, 0.001)}, 2)
d3 = combine(*p2c, *nc2)
check("nc 3 (P2) vs 2 (P2R): each model keeps its own call's G ceiling",
      abs(d3["per_model"]["meta-llama/Llama-3.1-8B"]["G_ceiling_D1"] - p2c[1]["per_model"]["meta-llama/Llama-3.1-8B"]["G_ceiling_D1"]) < 1e-12
      and abs(d3["per_model"][P2R_MODELS[0]]["G_ceiling_D1"] - nc2[1]["per_model"][P2R_MODELS[0]]["G_ceiling_D1"]) < 1e-12)
try:
    combine(*p2c, {**both[0], "models": {**both[0]["models"], "meta-llama/Llama-3.1-8B": fake_model("llama31", 0.3, 0.001)}}, both[1])
    check("refuses a model present in both calls", False)
except SystemExit:
    check("refuses a model present in both calls", True)
try:
    combine(*p2c, {**both[0], "test": True}, both[1]); check("refuses a --test input", False)
except SystemExit:
    check("refuses a --test input", True)
from p2r_combine import load, P2_PINNED  # noqa: E402
rp2, rp2dec = load(ROOT / "results/P2analysis/correct", P2_PINNED)
try:
    d4 = combine(rp2, rp2dec, *miss2)
    check("real pinned P2 files + MISSING P2R: flags consistent, licensed fact share as in P2",
          d4["claims"]["fact_share_gt0_(null_p<0.01_in>=2_families)"] is True and sorted(d4["families"]["included_families"]) == ["llama31", "olmo2"])
except SystemExit as e:
    print("   ", e); check("real pinned P2 files + MISSING P2R: flags consistent, licensed fact share as in P2", False)
print(f"{'FAILED' if fails else 'all passed'} ({len(fails)} failures)")
sys.exit(1 if fails else 0)
