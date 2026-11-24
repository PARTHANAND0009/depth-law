#!/usr/bin/env python3
# PROPOSED replacement for .claude/hooks/stop_check.py (staged 2026-11-21, part A5; the human installs it).
# Change vs the installed version: the "results changed but PROGRESS.md not updated" rule ignores the
# background S5 job's per-chunk outputs, matched narrowly (scripts/run_s5_cpu.sh -> run_depth --stage S5
# writes results/S5/<run_id>/chunks/sNN_cNNNNN.parquet and appends one line per chunk to
# results/S5/<run_id>/log.jsonl):
#     results/S5/S5-*/chunks/s[0-9][0-9]_c[0-9][0-9][0-9][0-9][0-9].parquet
#     results/S5/S5-*/log.jsonl
# Nothing else under results/ is exempt (a new S5 run dir's meta/weights json, its merged depth.parquet,
# results/s5_cpu.out and every non-S5 path still require a PROGRESS.md update). Untracked files are listed
# one by one (--untracked-files=all) so a new chunk is matched as a file, not as its parent directory.
import json, pathlib, re, subprocess, sys
# Anchored regexes (fnmatch's * would also cross "/"): exactly one run-dir level under results/S5/.
S5_EXEMPT = (re.compile(r"results/S5/S5-[^/]+/chunks/s\d{2}_c\d{5}\.parquet"),
             re.compile(r"results/S5/S5-[^/]+/log\.jsonl"))


def exempt(path: str) -> bool:
    return any(g.fullmatch(path) for g in S5_EXEMPT)


def main():
    d = json.load(sys.stdin)
    if d.get("stop_hook_active"):
        sys.exit(0)  # never loop: block at most once per stop attempt
    root = pathlib.Path(d.get("cwd") or ".")
    run = lambda cmd: subprocess.run(cmd, cwd=root, capture_output=True, text=True, timeout=110)
    problems = []
    status = run(["git", "status", "--porcelain", "--untracked-files=all"]).stdout
    if re.search(r"paper/\S+\.(tex|bib)", status):
        r = run([sys.executable, "scripts/check_numbers.py"])
        if r.returncode:
            problems.append("check_numbers.py failed:\n" + r.stdout[-2500:] + r.stderr[-800:])
    changed = [ln[3:] for ln in status.splitlines()
               if ln[:2] in (" M", "M ", "??") and re.match(r"(analysis|results|scripts)/", ln[3:])]
    if [p for p in changed if not exempt(p)] and "PROGRESS.md" not in status:
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


if __name__ == "__main__":
    main()
