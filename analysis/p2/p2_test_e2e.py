"""P2 end-to-end synthetic test of the frozen analysis (test only; not a result). Builds fake runs in the runner format
and checks the rules that the PREREG review asked for.
python analysis/p2/p2_test_e2e.py <work_dir> [n_boot=20] [n_perm=20] [cores=1]
Models (tokenizers must be cached locally):
  A EleutherAI/pythia-410m              complete, 3 carriers, planted carrier shift 0.05 per carrier level
  B EleutherAI/pythia-1.4b              complete, carrier 2 dropped after a 2-chunk pilot (fallback 1)
  C hf-internal-testing/llama-tokenizer complete, 3 carriers (second family, 'llama')
  D EleutherAI/pythia-2.8b              partial run, 150 facts, no manifest (hard stop)    -> MISSING (incomplete)
  E EleutherAI/pythia-70m               complete, p_correct 0.05                           -> MISSING (insufficient data)
Unit checks: a 20-fact pilot with a (false) full 'done' event is incomplete; --nc above the available count is refused.
Exit 1 if any check fails."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from p2_analysis import completeness  # noqa: E402
from p2_fake_run import main as fake, rewrite_manifest  # noqa: E402

work = Path(sys.argv[1]); kv = dict(x.split("=", 1) for x in sys.argv[2:])
nb, nperm, cores = kv.get("n_boot", "20"), kv.get("n_perm", "20"), kv.get("cores", "1")
work.mkdir(parents=True, exist_ok=True)
M = {"A": "EleutherAI/pythia-410m", "B": "EleutherAI/pythia-1.4b", "C": "hf-internal-testing/llama-tokenizer",
     "D": "EleutherAI/pythia-2.8b", "E": "EleutherAI/pythia-70m"}
fake(work / "A", 32, seed=7, carrier_shift=0.05)
fake(work / "B", 32, seed=8)
fake(work / "C", 32, seed=9)
fake(work / "D", 32, seed=10, n_facts=150)
fake(work / "E", 32, seed=11, p_correct=0.05)
rd = work / "B"  # fallback 1: carrier 2 dropped from chunk 2 on; checksums and manifest rewritten
h = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()  # noqa: E731
for c in sorted((rd / "chunks").glob("c*.parquet")):
    n = int(c.stem[1:])
    if n >= 2:
        d = pd.read_parquet(c); d[d.carrier < 2].to_parquet(c, index=False)
    b = c.with_name(f"b{n:05d}.parquet"); c.with_suffix(".sha256").write_text(f"{h(c)}  {c.name}\n{h(b)}  {b.name}\n")
rewrite_manifest(rd)
fake(work / "P", 32, seed=12, n_facts=20); rewrite_manifest(work / "P")  # pilot with a false full 'done'

checks = []
fid = [json.loads(l)["fact_id"] for l in open(ROOT / "materials/facts_v1.jsonl")]
for k, want in (("A", (True, 3)), ("B", (True, 2)), ("C", (True, 3)), ("D", (False, 0)), ("E", (True, 3)), ("P", (False, 0))):
    ok, why, ncr = completeness(work / k, fid)
    checks.append((f"completeness {k}: {why}", (ok, ncr) == want))
runs = [f"{M[k]}={work / k}" for k in "ABCDE"]
py = str(ROOT / ".venv/bin/python")


def call(out, set_name, extra=()):
    p = subprocess.run([py, str(HERE / "p2_analysis.py"), str(work / out), "--runs", *runs, "--set", set_name,
                        "--n-boot", nb, "--cores", cores, "--n-perm", nperm, *extra], capture_output=True, text=True, cwd=ROOT)
    return p


p = call("out_correct", "correct")
checks.append(("correct call exits 0", p.returncode == 0))
if p.returncode != 0:
    print(p.stderr[-2000:])
else:
    r = json.loads((work / "out_correct/p2_results.json").read_text())
    d = json.loads((work / "out_correct/p2_decision.json").read_text())
    st = {k: r["models"][M[k]]["status"] for k in "ABCDE"}
    checks += [("nc_used == 2 (fallback-1 model included)", r["n_carriers_used"] == 2),
               ("A, B, C ok", all(st[k] == "ok" for k in "ABC")),
               ("D MISSING (incomplete)", st["D"].startswith("MISSING (incomplete)")),
               ("E MISSING (insufficient data)", st["E"] == "MISSING (insufficient data)"),
               ("families counted: pythia + llama31", d["families"]["included_families"] == ["llama31", "pythia"])]
    fa = r["models"][M["A"]]["fits"]["D1"]
    checks += [("A D1 fit ok with carrier fixed effect", fa["status"] == "ok" and fa["carrier_fixed"]),
               ("A carrier_f1 fixed effect > 0 (planted shift)", fa["fixef"].get("carrier_f1", 0) > 0)]
    for k in "ABC":
        mm = r["models"][M[k]]
        checks.append((f"{k} null computed (p={mm.get('null', {}).get('p')})", "p" in mm.get("null", {})))
        checks.append((f"{k} MoM residualised diff present", "diff" in mm["mom"]["D1"]))
        checks.append((f"{k} failed-refit fractions recorded", "failed_frac" in mm["fits"]["D1"]["boot"]))
    print(json.dumps({"claims": d["claims"], "families": d["families"],
                      "per_model": {m: {k: v.get(k) for k in ("status", "H1", "H1_alt", "icc1_D1", "diff_D1", "mom_diff_D1", "null_p_D1")}
                                    for m, v in d["per_model"].items()},
                      "carrier_fixef_A": {k: v for k, v in fa["fixef"].items() if k.startswith("carrier")},
                      "H3": d["H3"]}, indent=1, default=float))
for s in ("new226", "all", "all10", "nomanufacturer", "tcov", "lofo", "h4"):
    p = call(f"out_{s}", s, ["--nc", "2"])
    ok = p.returncode == 0
    if ok:
        r = json.loads((work / f"out_{s}/p2_results.json").read_text())
        ok = r["n_carriers_used"] == 2 and r["models"][M["A"]]["status"] == "ok"
        if s == "tcov":
            ok = ok and "tcov_len" in r["models"][M["A"]]["fits"]["D1"].get("covariates", [])
        if s == "lofo":
            ok = ok and len(r["models"][M["A"]]["fits"]) == 10
        if s == "all10":  # too few cells: fits are allowed to be MISSING but the call must not crash
            print("all10 fit status A:", r["models"][M["A"]]["fits"]["D1"].get("status"))
    else:
        print(s, p.stderr[-1500:])
    checks.append((f"set {s} runs with --nc 2", ok))
p = call("out_nc3", "new226", ["--nc", "3"])
checks.append(("--nc 3 refused (only 2 available everywhere)", p.returncode != 0 and "exceeds" in p.stderr))
for name, ok in checks:
    print(("PASS " if ok else "FAIL ") + name)
print(f"{sum(ok for _, ok in checks)}/{len(checks)} checks passed")
sys.exit(0 if all(ok for _, ok in checks) else 1)
