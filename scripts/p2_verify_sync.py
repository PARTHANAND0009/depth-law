"""P2 GPU session: is everything off the VM? (reports/p2/GPU_SESSION_RUNBOOK.md). Not frozen code; read-only.
Run OFF the VM, on a checkout of the sync branch (e.g. git fetch origin p2-gpu-session && git worktree add ...).
python scripts/p2_verify_sync.py <sync checkout root>
Checks:
  1. VM_FILES.sha256 (written on the VM after the session, runbook step 13) exists, and every file it lists is present in
     the sync checkout with the same sha256 (this is the off-VM checksum check).
  2. The latest non-dry session log (results/logs/p2_gpu_run_*.log) ends with 'finished after' or a BUDGET REACHED line;
     its FATAL lines are listed; the number of deviation files D-P2-<session>-*.md equals the log's DEVIATION lines.
  3. Every model run dir under results/P2/ is checked with the analysis completeness rule (checksums recomputed).
     Incomplete runs are reported as MISSING (incomplete): they are results too and must be kept, not re-run.
Prints SAFE TO DESTROY THE VM: YES only if 1 passes for every file and 2 finds the session's end line."""
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis" / "p2"))
from p2_analysis import completeness  # noqa: E402


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main(root):
    root = Path(root); ok_all = True
    # 1. VM file list
    vm = root / "VM_FILES.sha256"
    if not vm.exists():
        print("1. VM_FILES.sha256: MISSING (runbook step 13 not done or not pushed)"); ok_all = False
    else:
        bad, n = [], 0
        for line in vm.read_text().splitlines():
            if not line.strip():
                continue
            h, rel = line.split(None, 1); rel = rel.strip().lstrip("*"); n += 1
            f = root / rel
            if not f.exists():
                bad.append(f"absent: {rel}")
            elif sha(f) != h:
                bad.append(f"sha256 differs: {rel}")
        print(f"1. VM_FILES.sha256: {n} files listed; {n - len(bad)} present with the same sha256; {len(bad)} problems")
        for b in bad[:20]:
            print("     ", b)
        ok_all &= not bad and n > 0
    # 2. session log
    logs = [p for p in sorted((root / "results/logs").glob("p2_gpu_run_*.log")) if "DRY=0" in p.read_text()[:300]]
    if not logs:
        print("2. session log: MISSING"); ok_all = False; ts = None
    else:
        log = logs[-1]; t = log.read_text(); ts = log.stem.replace("p2_gpu_run_", "")
        end = re.findall(r".*(finished after .*|BUDGET REACHED.*)", t)
        fatal = [l for l in t.splitlines() if "FATAL" in l]
        devs = sorted(set(re.findall(r"DEVIATION (D-P2-[0-9TZ]+-\w+)", t)))  # unique ids
        files = sorted(p.name for p in (root / "deviations_pending").glob(f"D-P2-{ts}-*.md")) if (root / "deviations_pending").exists() else []
        print(f"2. session log {log.name}: end line: {end[-1] if end else 'NONE'}")
        print(f"   FATAL lines: {len(fatal)}" + "".join(f"\n      {l}" for l in fatal))
        print(f"   DEVIATION lines in log: {len(devs)}; deviation files for this session: {len(files)} {files}")
        budget_file = any(n.endswith("-budget.md") for n in files)
        ok_all &= bool(end) and (len(files) == len(devs) + (1 if budget_file else 0))
    # 3. run dirs
    fids = [json.loads(l)["fact_id"] for l in open(ROOT / "materials/facts_v1.jsonl")]
    print("3. model run dirs (analysis completeness rule, checksums recomputed):")
    for rd in sorted((root / "results/P2").glob("P2-*")) if (root / "results/P2").exists() else []:
        starts = [json.loads(l) for l in open(rd / "log.jsonl") if '"start"' in l] if (rd / "log.jsonl").exists() else []
        model = starts[0].get("model") if starts else "?"
        ok, why, ncr = completeness(rd, fids)
        print(f"   {rd.name}  model={model}  {'complete, carriers=' + str(ncr) if ok else 'MISSING (incomplete): ' + why}")
    print("SAFE TO DESTROY THE VM:", "YES" if ok_all else "NO")
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
