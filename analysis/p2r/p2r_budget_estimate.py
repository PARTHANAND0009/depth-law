#!/usr/bin/env python3
"""EXPLORATORY planning estimate (not an analysis of any P2R data): GPU minutes and INR for the P2R session.

Inputs (read only):
  results/logs/p2_gpu_run_20261124T162942Z.log   P2 session driver log (same GPU type, RTX PRO 6000)
  results/P2/P2-*-ff119ca-*/log.jsonl            per-chunk seconds of the five P2 model runs
  config.json of the P2 and P2R models from the Hugging Face Hub (P2R at the pinned commits)
Output: the JSON given as argv[1] (all inputs, intermediate values and the per-balance outcome).

Per-unit time (one fact x paraphrase, 3 carriers) is scaled from the three 7-8B P2 models by two rules, and the
range over models x rules is reported: (B) proportional to total parameters (weights read per forward), and
(A) proportional to layers x total parameters (each unit patches every layer). The pythia models are not used
for the scale (relatively more fixed overhead). The pilot projection is the frozen driver's formula
(scripts/p2_gpu_run.sh: q x (2800 + 3000) / 60 + 3 + 1 minutes; Mistral projected at Gemma's rate)."""
import json
import math
import re
import sys
from datetime import datetime
from pathlib import Path

from huggingface_hub import HfApi, hf_hub_download

ROOT = Path(__file__).resolve().parents[2]
LOG = ROOT / "results/logs/p2_gpu_run_20261124T162942Z.log"
PIN = json.loads((ROOT / "materials/p2r_weights_pinned.json").read_text())
P2 = {"Qwen/Qwen3-8B": "P2-Qwen3-8B-", "meta-llama/Llama-3.1-8B": "P2-Llama-3.1-8B-", "allenai/OLMo-2-1124-7B": "P2-OLMo-2-1124-7B-",
      "EleutherAI/pythia-1.4b": "P2-pythia-1.4b-", "EleutherAI/pythia-2.8b": "P2-pythia-2.8b-"}
P2R = ["google/gemma-2-9b", "mistralai/Mistral-7B-v0.1"]
SCALE = ["Qwen/Qwen3-8B", "meta-llama/Llama-3.1-8B", "allenai/OLMo-2-1124-7B"]
UNITS = 3000
DRIVER_RATE = 207.36


def params(c):
    h, L, V = c["hidden_size"], c["num_hidden_layers"], c["vocab_size"]
    nh = c["num_attention_heads"]; kv = c.get("num_key_value_heads") or nh
    hd = c.get("head_dim") or h // nh
    if c.get("model_type") == "gpt_neox":
        layer = 4 * h * h + 2 * h * c["intermediate_size"]
    else:
        layer = 2 * h * nh * hd + 2 * h * kv * hd + 3 * h * c["intermediate_size"]
    return {"layers": L, "hidden": h, "vocab": V, "nonembed": layer * L, "unembed": V * h, "total": layer * L + V * h}


def utc(s):
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ")


def main(out):
    api = HfApi(); cfg, sizes = {}, {}
    for m in list(P2) + P2R:
        rev = PIN[m]["main_commit"] if m in PIN else None
        cfg[m] = json.loads(Path(hf_hub_download(m, "config.json", revision=rev)).read_text())
        info = api.model_info(m, revision=rev, files_metadata=True)
        sizes[m] = {"revision": info.sha, "safetensors_GB": round(sum(s.size or 0 for s in info.siblings if s.rfilename.endswith(".safetensors")) / 1e9, 2)}
    feat = {m: params(cfg[m]) for m in cfg}
    # P2 timings: chunk seconds from each run's log.jsonl (the pilot and the resumed run are separate segments)
    p2 = {}
    for m, pre in P2.items():
        rd = sorted((ROOT / "results/P2").glob(pre + "ff119ca-*"))
        assert len(rd) == 1, (m, rd)
        ev = [json.loads(l) for l in open(rd[0] / "log.jsonl")]
        segs, cur = [], None
        for e in ev:
            if e.get("event") == "start":
                cur = []; segs.append(cur)
            elif e.get("event") == "chunk":
                cur.append(e["s"])
        secs = sum(s[-1] for s in segs if s)
        p2[m] = {"run_dir": str(rd[0].relative_to(ROOT)), "chunk_seconds_total": secs, "s_per_unit": secs / UNITS}
    t = LOG.read_text()
    wall = {}
    starts = re.findall(r"\[(\S+)\] model (\S+) carriers 3", t)
    ends = re.findall(r"\[(\S+)\] synced \S+/P2-(\S+?)-ff119ca", t)
    for (ts, m), (te, _) in zip(starts, ends):
        wall[m] = round((utc(te) - utc(ts)).total_seconds() / 60, 2)
    first = re.search(r"\[(\S+)\] start DRY=0", t).group(1); fin = re.search(r"\[(\S+)\] .*finished after (\d+) min", t)
    pilot = re.search(r"\[(\S+)\] pilot: ", t).group(1); proj = re.search(r"\[(\S+)\] pilot projection", t).group(1)
    for m in p2:
        p2[m]["wall_min_model_line_to_synced"] = wall.get(m)
        p2[m]["kB_s_per_unit_per_Gparam"] = p2[m]["s_per_unit"] / (feat[m]["total"] / 1e9)
        p2[m]["kA_s_per_unit_per_layer_Gparam"] = p2[m]["s_per_unit"] / (feat[m]["layers"] * feat[m]["total"] / 1e9)
    kB = [p2[m]["kB_s_per_unit_per_Gparam"] for m in SCALE]; kA = [p2[m]["kA_s_per_unit_per_layer_Gparam"] for m in SCALE]
    est = {}
    for m in P2R:
        g = feat[m]["total"] / 1e9
        q = [k * g for k in kB] + [k * feat[m]["layers"] * g for k in kA]
        est[m] = {"s_per_unit_range": [min(q), max(q)], "run_min_3c_range": [min(q) * UNITS / 60, max(q) * UNITS / 60]}
    qg = est["google/gemma-2-9b"]["s_per_unit_range"]
    proj3 = [x * (UNITS - 200 + UNITS) / 60 + 3 + 1 for x in qg]
    proj2 = [x * (UNITS - 200 + UNITS) / 60 * 5 / 7 + 3 + 1 for x in qg]
    # actual run (not the projection): pilot 200 units + rest of Gemma + Mistral, 1 min load each
    run3 = [est["google/gemma-2-9b"]["run_min_3c_range"][i] + est["mistralai/Mistral-7B-v0.1"]["run_min_3c_range"][i] + 2 for i in (0, 1)]
    run2 = [x * 5 / 7 for x in run3]
    # set-up before the driver (bootstrap; planning ranges, see the report) and after it
    p2r_GB = sum(sizes[m]["safetensors_GB"] for m in P2R); p2_GB = sum(sizes[m]["safetensors_GB"] for m in P2)
    p2_step7_to_driver_min = round((utc(first) - utc("2026-11-24T15:55:28Z")).total_seconds() / 60, 1)
    setup = {"prestart_boot_login_typing": [3, 5], "packages_clone_tag_hash": [1, 3], "download_wait_beyond_venv": [5, 22],
             "set_ref_check_cache_attention": [1, 3], "arch_tests_2_models": [2, 6], "check_cache_at_start": [1, 3], "driver_pytest_smoke": [0.5, 1]}
    S = [sum(v[0] for v in setup.values()), sum(v[1] for v in setup.values())]
    pilot_elapsed = [2.0, 3.5]  # driver start -> pilot decision: pytest, smoke, Gemma load, 200 pilot units
    teardown = [2, 4]
    res = {}
    for bal in (147, 647):
        for hourly in (DRIVER_RATE,):
            total = math.floor(min(bal, 700) / hourly * 60)
            row = {"hourly_INR_assumed": hourly, "minutes_affordable": total}
            for case, si, pe, qi in (("fast", 0, 0, 0), ("slow", 1, 1, 1)):
                T = total - S[si] - 10          # bootstrap: driver budget = minutes left - 10 (S includes the prestart minutes)
                rem = T - pilot_elapsed[pe]
                if proj3[qi] <= rem: dec = "3 carriers (full design, no fallback)"
                elif proj2[qi] <= rem: dec = "fallback 1 (2 carriers)"
                else: dec = "fallback 1 (2 carriers) + fallback 2 (drop Llama: a no-op for P2R); per-model skip never fires (no static estimates)"
                need = run3[qi] if dec.startswith("3") else run2[qi]
                row[case] = {"setup_min": S[si], "driver_budget_min": T, "remaining_at_pilot_decision": rem,
                             "pilot_projection_3c": proj3[qi], "pilot_projection_2c": proj2[qi], "decision": dec,
                             "driver_minutes_needed_actual": need + pilot_elapsed[pe] - 2,
                             "completes_both_models": bool(T >= need + pilot_elapsed[pe] - 2),
                             "session_minutes_if_complete": S[si] + need + pilot_elapsed[pe] - 2 + teardown[si],
                             "INR_if_complete_at_hourly": (S[si] + need + pilot_elapsed[pe] - 2 + teardown[si]) * hourly / 60}
            res[str(bal)] = row
    o = {"_status": "EXPLORATORY planning estimate; not a result; not P2R data", "inputs": {"p2_log": str(LOG.relative_to(ROOT))},
         "configs": {m: {k: cfg[m].get(k) for k in ("model_type", "num_hidden_layers", "hidden_size", "intermediate_size", "vocab_size", "num_attention_heads", "num_key_value_heads", "head_dim", "torch_dtype")} for m in cfg},
         "params": feat, "sizes": sizes, "p2_measured": p2,
         "p2_session": {"driver_start": first, "pilot_start": pilot, "pilot_projection_logged": proj, "finished": fin.group(1), "finished_after_min": int(fin.group(2)),
                        "vm_side_step7_commit": "2026-11-24T15:55:28Z", "step7_to_driver_min": p2_step7_to_driver_min, "p2_download_GB": round(p2_GB, 2),
                        "INR_spent_human_figure_approx": 354, "total_vm_minutes": "MISSING (not reported)"},
         "scale_models": SCALE, "kB_range": [min(kB), max(kB)], "kA_range": [min(kA), max(kA)], "p2r_estimates": est,
         "pilot_projection_min": {"3c": proj3, "2c": proj2}, "driver_run_min_actual": {"3c": run3, "2c": run2},
         "p2r_download_GB": round(p2r_GB, 2), "setup_components_min": setup, "setup_total_min": S,
         "pilot_elapsed_min": pilot_elapsed, "teardown_min": teardown, "balances": res}
    Path(out).write_text(json.dumps(o, indent=1) + "\n")
    print(json.dumps({"p2r_estimates": est, "pilot_projection_min": o["pilot_projection_min"], "driver_run_min_actual": o["driver_run_min_actual"],
                      "setup_total_min": S, "balances": res, "p2_wall": wall, "step7_to_driver_min": p2_step7_to_driver_min,
                      "GB": {"p2r": o["p2r_download_GB"], "p2": o["p2_session"]["p2_download_GB"]}}, indent=1))


if __name__ == "__main__":
    main(sys.argv[1])
