#!/usr/bin/env python3
"""Integrity summary for the paper's integrity appendix (G5). Run through scripts/log_run.py.

Writes results/integrity/summary.json: preregistrations (recorded vs current hashes), deviations and incidents,
ledger statistics, guard tests (run here), and the verdict line of every gate review (reports/gates/*/*.md,
verbatim files, never edited). Reads only; runs the guard tests in throwaway repositories.
Usage: integrity_summary.py [out.json]
"""
import datetime, hashlib, json, pathlib, re, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "results" / "integrity" / "summary.json"


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def git(*a):
    return subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True).stdout.strip()


S = {"generated_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
     "git_head": git("rev-parse", "HEAD")}

# preregistrations
hr_rec = re.search(r"commit (\w+) \(([^)]*)\)", (ROOT / "prereg/HASH.txt").read_text())
p2_rec = (ROOT / "prereg/HASH_P2.txt").read_text().split()[0]
S["preregistrations"] = [
    {"id": "H-R", "file": "prereg/HR_revised.md", "freeze_commit": hr_rec.group(1), "freeze_utc": hr_rec.group(2),
     "sha256_now": sha("prereg/HR_revised.md"),
     "unchanged_since_freeze": not git("diff", "--name-only", hr_rec.group(1), "--", "prereg/HR_revised.md")},
    {"id": "P2", "file": "prereg/P2_prompt_vs_fact.md", "freeze_tag": "prereg-P2",
     "freeze_commit": git("rev-parse", "prereg-P2"), "sha256_recorded": p2_rec,
     "sha256_now": sha("prereg/P2_prompt_vs_fact.md"), "unchanged_since_freeze": p2_rec == sha("prereg/P2_prompt_vs_fact.md")},
]

# deviations and incidents
devs = []
for f in sorted((ROOT / "prereg/deviations").glob("*.md")):
    first = f.read_text().splitlines()[0].lstrip("# ").strip()
    devs.append({"file": f.relative_to(ROOT).as_posix(), "title": first, "installed": True})
for f in sorted((ROOT / "reports/pending_frozen_changes").rglob("INC-*.md")):
    rel = f"prereg/deviations/{f.name}"
    if not (ROOT / rel).exists():
        devs.append({"file": f.relative_to(ROOT).as_posix(), "title": f.read_text().splitlines()[0].lstrip("# ").strip(),
                     "installed": False, "note": "staged for the human (APPLY_guard.sh); not yet in prereg/deviations/"})
S["deviations"] = devs
S["deviations_log_lines"] = [l for l in (ROOT / "prereg/DEVIATIONS.md").read_text().splitlines() if l.count("|") >= 3
                             and not l.startswith("Format")]

# ledger
L = [json.loads(l) for l in (ROOT / "results/ledger.jsonl").read_text().splitlines() if l.strip()]
runs = [r for r in L if r.get("kind") == "RUN"]
S["ledger"] = {
    "entries": len(L), "runs": len(runs), "notes": len(L) - len(runs),
    "runs_confirmatory": sum(r.get("status") == "CONFIRMATORY" for r in runs),
    "runs_exploratory": sum(r.get("status") == "EXPLORATORY" for r in runs),
    "runs_nonzero_exit": sum(r.get("exit_code") not in (0, None) for r in runs),
    "runs_frozen_violation": sum(bool(r.get("frozen_violation")) for r in runs),
    "notes_integrity_incident": [r["tag"] for r in L if "INTEGRITY INCIDENT" in str(r.get("tag", ""))],
    "notes_s5_relaunch": sum("S5 relaunch" in str(r.get("tag", "")) for r in L),
    "first_utc": L[0].get("utc") or L[0].get("utc_start"), "last_utc": L[-1].get("utc") or L[-1].get("utc_start"),
}

# guard tests
def run(cmd):
    p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


rc, out = run([sys.executable, "-m", "pytest", "-q", "tests/test_frozen_guard.py"])
m = re.search(r"(\d+) passed", out); f = re.search(r"(\d+) failed", out)
tests = [{"suite": "tests/test_frozen_guard.py (commit, worktree, runtime and log_run layers; incident route)",
          "passed": int(m.group(1)) if m else 0, "failed": int(f.group(1)) if f else 0, "exit": rc}]
for sh, hook in (("hooks/tests/test_frozen_hook.sh", "hooks/proposed/protect_frozen.py"),
                 ("hooks/tests/test_kill_hook.sh", "hooks/proposed/protect_frozen.py"),
                 ("hooks/tests/test_frozen_hook.sh", ".claude/hooks/protect_frozen.py")):
    rc, out = run(["bash", sh, hook])
    ok = re.search(r"pass=(\d+) fail=(\d+)", out) or re.search(r"RESULT: (\d+) correct, (\d+) wrong", out)
    tests.append({"suite": f"{sh} on {hook}", "passed": int(ok.group(1)) if ok else None,
                  "failed": int(ok.group(2)) if ok else None, "exit": rc})
S["guard_tests"] = tests
rc, out = run([sys.executable, "scripts/frozen_guard.py", "immutable", "verify"])
S["immutable_attribute"] = {"frozen_files": len(run([sys.executable, "scripts/frozen_guard.py", "list"])[1].split()),
                            "all_set": rc == 0}
rc, _ = run([sys.executable, "scripts/frozen_guard.py", "check-worktree"])
S["worktree_frozen_clean"] = rc == 0
rc, out = run([sys.executable, "scripts/check_numbers.py"])
S["check_numbers"] = out.strip().splitlines()[-1] if out.strip() else ""

# gate reviews (verbatim files; only the last VERDICT line is read)
rev = []
for f in sorted((ROOT / "reports/gates").glob("*/*.md")):
    if f.name in ("responses.md",) or f.name.startswith("GATE_"):
        continue
    t = f.read_text()
    v = re.findall(r"^\**VERDICT\**:?\**\s*(.+)$", t, re.M)
    v = [re.split(r"[;(]", x)[0].strip().rstrip(".") for x in v]
    rev.append({"gate": f.parent.name, "agent": f.stem, "verdict": v[-1][:60] if v else "per-claim (no single verdict line)",
                "sha256": sha(f.relative_to(ROOT).as_posix())})
S["reviews"] = rev
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(S, indent=1) + "\n")
print(f"wrote {OUT.relative_to(ROOT)}: {len(rev)} reviews, {len(devs)} deviations/incidents, {len(L)} ledger entries")
