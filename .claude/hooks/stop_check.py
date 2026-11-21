#!/usr/bin/env python3
import json, pathlib, re, subprocess, sys
d = json.load(sys.stdin)
if d.get("stop_hook_active"):
    sys.exit(0)  # never loop: block at most once per stop attempt
root = pathlib.Path(d.get("cwd") or ".")
run = lambda cmd: subprocess.run(cmd, cwd=root, capture_output=True, text=True, timeout=110)
problems = []
status = run(["git", "status", "--porcelain"]).stdout
if re.search(r"paper/\S+\.(tex|bib)", status):
    r = run([sys.executable, "scripts/check_numbers.py"])
    if r.returncode:
        problems.append("check_numbers.py failed:\n" + r.stdout[-2500:] + r.stderr[-800:])
if re.search(r"^( M|M |\?\?) (analysis|results|scripts)/", status, re.M) and "PROGRESS.md" not in status:
    problems.append("analysis/results changed but PROGRESS.md was not updated; update it and commit")
prog = root / "PROGRESS.md"
m = re.search(r"STATUS:\s*AWAITING GO (\S+)", prog.read_text() if prog.exists() else "")
if m:
    r = run([sys.executable, "scripts/gate_check.py", m.group(1)])
    if r.returncode:
        problems.append(f"gate {m.group(1)} not ready:\n" + r.stdout[-2500:])
if problems:
    print("\n\n".join(problems), file=sys.stderr); sys.exit(2)
sys.exit(0)
