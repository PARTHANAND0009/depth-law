"""P2 end-to-end synthetic test of the frozen analysis (test only; not a result). Builds fake runs in the runner format
and checks the rules asked for by the PREREG reviews (rounds 1 and 2).
python analysis/p2/p2_test_e2e.py <work_dir> [n_boot=20] [n_perm=20] [cores=1]
Models (tokenizers must be cached locally):
  A EleutherAI/pythia-410m              complete, 3 carriers, planted carrier shift 0.05 per carrier level
  B EleutherAI/pythia-1.4b              complete, carrier 2 dropped after a 2-chunk pilot (fallback 1)
  C hf-internal-testing/llama-tokenizer complete, 3 carriers (second family, 'llama')
  D EleutherAI/pythia-2.8b              partial run, 150 facts, no manifest (hard stop)    -> MISSING (incomplete)
  E EleutherAI/pythia-70m               complete, p_correct 0.05, carrier 2 dropped        -> MISSING (insufficient data)
Checks: completeness (incl. a 20-fact pilot with a false full 'done' event); inclusion and nc (nc over complete AND
sufficient models: A+C+E gives nc 3 although E has 2 carriers); every sensitivity set through --primary; refusals
(no --primary, different --runs, duplicate model, unknown family); forced fit failures (in-process, rfit patched):
A's D4 fit and C's D1 fit fail -> outputs are written; A keeps its D1-only rules and loses H1/H1-alt; C loses every
D1 rule; H3 pairs with C are MISSING. Round-3 additions: the parametric fact-share null's output; non-test refusals
(models other than the prereg five; resample counts other than 1000); run identity on a real dry-run dir; a corrupted
chunk is caught by checksum recomputation; an undefined n' does not meet the 'N paraphrases' rule. Synthetic calls use
--test (non-gating). Exit 1 if any check fails."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import p2_analysis as PA  # noqa: E402
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
h = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()  # noqa: E731
for k in "BE":  # fallback 1: carrier 2 dropped from chunk 2 on; checksums and manifest rewritten
    rd = work / k
    for c in sorted((rd / "chunks").glob("c*.parquet")):
        n = int(c.stem[1:])
        if n >= 2:
            d = pd.read_parquet(c); d[d.carrier < 2].to_parquet(c, index=False)
        b = c.with_name(f"b{n:05d}.parquet"); c.with_suffix(".sha256").write_text(f"{h(c)}  {c.name}\n{h(b)}  {b.name}\n")
    rewrite_manifest(rd)
fake(work / "P", 32, seed=12, n_facts=20); rewrite_manifest(work / "P")  # pilot with a false full 'done'

checks = []
fid = [json.loads(l)["fact_id"] for l in open(ROOT / "materials/facts_v1.jsonl")]
for k, want in (("A", (True, 3)), ("B", (True, 2)), ("C", (True, 3)), ("D", (False, 0)), ("E", (True, 2)), ("P", (False, 0))):
    ok, why, ncr = PA.completeness(work / k, fid)
    checks.append((f"completeness {k}: {why}", (ok, ncr) == want))
runs = [f"{M[k]}={work / k}" for k in "ABCDE"]
py = str(ROOT / ".venv/bin/python")


def call(out, set_name, extra=(), run_list=None):
    return subprocess.run([py, str(HERE / "p2_analysis.py"), str(work / out), "--runs", *(run_list or runs), "--set", set_name,
                           "--n-boot", nb, "--cores", cores, "--n-perm", nperm, "--test", *extra], capture_output=True, text=True, cwd=ROOT)


p = call("out_correct", "correct")
checks.append(("correct call exits 0", p.returncode == 0))
if p.returncode != 0:
    print(p.stderr[-2000:])
else:
    r = json.loads((work / "out_correct/p2_results.json").read_text())
    d = json.loads((work / "out_correct/p2_decision.json").read_text())
    st = {k: r["models"][M[k]]["status"] for k in "ABCDE"}
    checks += [("nc_used == 2 (fallback-1 model B included)", r["n_carriers_used"] == 2),
               ("A, B, C ok", all(st[k] == "ok" for k in "ABC")),
               ("D MISSING (incomplete)", st["D"].startswith("MISSING (incomplete)")),
               ("E MISSING (insufficient data)", st["E"] == "MISSING (insufficient data)"),
               ("families counted: pythia + llama31", d["families"]["included_families"] == ["llama31", "pythia"]),
               ("test output is non-gating", r["gating"] is False and d["gating"] is False)]
    fa = r["models"][M["A"]]["fits"]["D1"]
    checks += [("A D1 fit ok with carrier fixed effect", fa["status"] == "ok" and fa["carrier_fixed"]),
               ("A carrier_f1 fixed effect > 0 (planted shift)", fa["fixef"].get("carrier_f1", 0) > 0)]
    for k in "ABC":
        mm = r["models"][M[k]]
        nl = mm.get("null", {})
        checks.append((f"{k} parametric null computed (p={nl.get('p')}, failed {nl.get('n_failed')})",
                       "p" in nl and str(nl.get("method", "")).startswith("parametric")))
        checks.append((f"{k} MoM residualised diff present", "diff" in mm["mom"]["D1"]))
        checks.append((f"{k} rules all evaluated", d["per_model"][M[k]]["rules_missing"] == []))
    print(json.dumps({"claims": d["claims"], "families": d["families"],
                      "per_model": {m: {k: v.get(k) for k in ("status", "H1", "H1_alt", "icc1_D1", "diff_D1", "mom_diff_D1", "null_p_D1")}
                                    for m, v in d["per_model"].items()},
                      "carrier_fixef_A": {k: v for k, v in fa["fixef"].items() if k.startswith("carrier")}}, indent=1, default=float))
for s in ("new226", "all", "all10", "nomanufacturer", "tcov", "lofo", "h4"):
    p = call(f"out_{s}", s, ["--primary", str(work / "out_correct")])
    ok = p.returncode == 0
    if ok:
        r = json.loads((work / f"out_{s}/p2_results.json").read_text())
        ok = r["n_carriers_used"] == 2 and r["models"][M["A"]]["status"] == "ok" and r["gating"] is False
        if s == "tcov":
            ok = ok and "tcov_len" in r["models"][M["A"]]["fits"]["D1"].get("covariates", [])
        if s == "lofo":
            ok = ok and len(r["models"][M["A"]]["fits"]) == 10
        if s == "all10":
            print("all10 fit status A:", r["models"][M["A"]]["fits"]["D1"].get("status"))
    else:
        print(s, p.stderr[-1500:])
    checks.append((f"set {s} runs with --primary (nc 2, gating false)", ok))
# nc over complete AND sufficient models: E (2 carriers, insufficient data) must not force nc = 2
p = call("out_ACE", "correct", ["--n-perm", "0"], [f"{M[k]}={work / k}" for k in "ACE"])
okr = p.returncode == 0 and json.loads((work / "out_ACE/p2_results.json").read_text())["n_carriers_used"] == 3
checks.append(("nc = 3 when the only 2-carrier model (E) has insufficient data", okr))
# refusals
p = call("out_x1", "new226")
checks.append(("sensitivity without --primary refused", p.returncode != 0 and "--primary" in p.stderr))
p = call("out_x2", "new226", ["--primary", str(work / "out_correct")], runs[:3])
checks.append(("--runs different from the confirmatory call refused", p.returncode != 0 and "differ" in p.stderr))
p = call("out_x3", "correct", (), runs + [f"{M['A']}={work / 'C'}"])
checks.append(("duplicate model in --runs refused", p.returncode != 0 and "duplicate" in p.stderr))
p = call("out_x4", "correct", (), runs + [f"foo/bar={work / 'C'}"])
checks.append(("unknown model family refused", p.returncode != 0 and "unknown model family" in p.stderr))
# non-test refusals (prereg checks)
p = subprocess.run([py, str(HERE / "p2_analysis.py"), str(work / "out_x5"), "--runs", *runs, "--set", "correct"],
                   capture_output=True, text=True, cwd=ROOT)
checks.append(("non-test call with non-prereg models refused", p.returncode != 0 and "prereg model" in p.stderr))
pre = [f"{m}=none" for m in PA.PREREG_MODELS]
p = subprocess.run([py, str(HERE / "p2_analysis.py"), str(work / "out_x6"), "--runs", *pre, "--set", "correct", "--n-boot", "20"],
                   capture_output=True, text=True, cwd=ROOT)
checks.append(("non-test call with --n-boot 20 refused", p.returncode != 0 and "--n-boot 1000" in p.stderr))
# run identity on a real runner dir (dry run, pythia-70m)
dry = sorted((ROOT / "results/P2dry").glob("P2dry-pythia-70m-ae9fb2a-20261123T101958Z"))
if dry:
    okA, _ = PA.run_identity(dry[0], "EleutherAI/pythia-70m"); okB, whyB = PA.run_identity(dry[0], "EleutherAI/pythia-1.4b")
    checks.append((f"run identity: right model accepted, wrong model refused ({whyB})", okA and not okB))
else:
    checks.append(("run identity: dry-run dir missing", False))
# corrupted copy is caught by checksum recomputation
import shutil  # noqa: E402
shutil.copytree(work / "A", work / "Abad")
c0 = work / "Abad/chunks/c00003.parquet"; b = bytearray(c0.read_bytes()); b[100] ^= 0xFF; c0.write_bytes(bytes(b))
okc, whyc = PA.completeness(work / "Abad", fid)[:2]
checks.append((f"corrupted chunk caught ({whyc})", not okc and "checksum mismatch" in whyc))
# undefined n' does not meet the 'N paraphrases' rule (decide on a copy of the confirmatory results)
if (work / "out_correct/p2_results.json").exists():
    rr = json.loads((work / "out_correct/p2_results.json").read_text())
    rr["models"][M["A"]]["fits"]["D1"]["point"]["nprime_G"] = None
    dd = PA.decide(rr, "correct", {}, {}, rr["n_carriers_used"], False)
    pa_ = dd["per_model"][M["A"]]
    checks.append(("undefined n' -> nprime_ge_8 False (not MISSING), G ceiling reported",
                   pa_["nprime_ge_8"] is False and pa_["nprime_undefined"] is True and pa_["G_ceiling_D1"] is not None
                   and "nprime_ge_8" not in pa_["rules_missing"]))
# forced fit failures (in-process; the frozen code is not changed): A's D4 fit and C's D1 fit fail
orig = PA.rfit


def failing(csv, js, y, a, nc, n_boot, extra=()):
    if (Path(csv).name.startswith("long_pythia-410m_correct") and y == "D4") or \
       (Path(csv).name.startswith("long_llama-tokenizer_correct") and y == "D1"):
        return {"status": "MISSING: fit error", "missing": "forced test failure"}
    return orig(csv, js, y, a, nc, n_boot, extra)


PA.rfit = failing
crashed = None
try:
    PA.main([str(work / "out_fail"), "--runs", *runs, "--set", "correct", "--n-boot", nb, "--cores", cores, "--n-perm", nperm, "--test"])
except Exception as e:  # noqa: BLE001
    crashed = repr(e)
PA.rfit = orig
checks.append((f"forced fit failures: no crash ({crashed})", crashed is None))
okw = (work / "out_fail/p2_results.json").exists() and (work / "out_fail/p2_decision.json").exists()
checks.append(("forced fit failures: both output files written", okw))
if okw:
    d = json.loads((work / "out_fail/p2_decision.json").read_text())
    pa, pc = d["per_model"][M["A"]], d["per_model"][M["C"]]
    checks += [("A (D4 failed): H1, H1-alt MISSING", pa["H1"] is None and pa["H1_alt"] is None),
               ("A (D4 failed): D1-only rules still evaluated (no fixed layer, null, n', tf)",
                pa["icc1_upper_lt_0.15"] is not None and pa["null_lt_0.01"] is not None and pa["nprime_ge_8"] is not None
                and pa["tf_gt_resid_D1"] is not None),
               ("C (D1 failed): every D1 rule MISSING; null still reported",
                all(pc[k] is None for k in ("H1", "H1_alt", "icc1_upper_lt_0.15", "nprime_ge_8", "tf_gt_resid_D1"))),
               ("H3 pairs with C MISSING", all("missing" in v for k, v in d["H3"].items() if M["C"] in k)),
               ("H3 pair A-B still computed", any("rho" in v for k, v in d["H3"].items() if M["C"] not in k)),
               ("H1 families exclude C's family (llama31; C's H1 is MISSING)", "llama31" not in d["families"]["H1"])]
    print("forced-failure per-model rules:", json.dumps({m: {k: v.get(k) for k in ("H1", "H1_alt", "icc1_upper_lt_0.15", "null_lt_0.01",
                                                                                     "rules_missing")} for m, v in d["per_model"].items()},
                                                         indent=1, default=float))
    print("forced-failure claims:", json.dumps(d["claims"], indent=1))
for name, ok in checks:
    print(("PASS " if ok else "FAIL ") + name)
print(f"{sum(ok for _, ok in checks)}/{len(checks)} checks passed")
sys.exit(0 if all(ok for _, ok in checks) else 1)
