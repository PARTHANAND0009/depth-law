#!/usr/bin/env python3
# PROPOSED replacement for .claude/hooks/protect_frozen.py (staged 2026-11-21, part A4; the human installs it).
# Changes vs the installed version:
#   1. kill rule narrowed: blocks kill/pkill/killall only at command position (start of the command or
#      after ; & | ( or a newline, optional sudo). "kill" inside another token (skill, killed, a grep
#      pattern, a filename) passes.
#   2. explicit S5 guard: blocks any process-control command (kill/pkill/killall/renice/ionice/taskset/
#      cpulimit/chrt/prlimit --pid/strace -p/gdb -p) that names a running S5 PID or the S5 process
#      names (run_s5_cpu, run_s4t_cpu, "run_depth ... --stage S5"), wherever it appears in the command.
# Everything else is unchanged.
import json, os, re, subprocess, sys
d = json.load(sys.stdin)
tool, ti = d.get("tool_name", ""), d.get("tool_input", {}) or {}
PROTECTED = ("prereg/", "data/raw/", "paper/numbers.tex", "results/ledger.jsonl",
             ".claude/hooks/", "scripts/check_numbers.py", "scripts/verify_bib.py",
             "scripts/gate_check.py", "gates.yaml", "config/required_macros.json")
WRITERS = ("scripts/make_numbers.py", "scripts/log_run.py")
KILL_AT_CMD = re.compile(r"(^|[;&|(\n]\s*)(sudo\s+)?(kill|pkill|killall)(\s|$)")
PROC_CTL = re.compile(r"\b(kill|pkill|killall|renice|ionice|taskset|cpulimit|chrt)\b|prlimit\s+--pid|\b(strace|gdb)\s+-p\b")
S5_NAMES = re.compile(r"run_s5_cpu|run_s4t_cpu|--stage\s+S5\b")


def s5_pids():
    try:
        out = subprocess.run(["pgrep", "-f", r"scripts/run_s5_cpu|scripts/run_s4t_cpu|--stage S5"],
                             capture_output=True, text=True, timeout=5).stdout.split()
        return {p for p in out if p.isdigit() and int(p) != os.getpid()}
    except Exception:  # noqa: BLE001 - a failed lookup must not open the guard
        return set()


def block(msg):
    print("BLOCKED: " + msg, file=sys.stderr); sys.exit(2)


if tool in ("Edit", "Write", "MultiEdit", "NotebookEdit"):
    p = (ti.get("file_path") or ti.get("notebook_path") or "").replace("\\", "/")
    if "prereg/amendments/" in p or "prereg/deviations/" in p:  # deviations: added (A1), same write-once rule
        if tool != "Write" or os.path.exists(p):
            block(f"{p}: amendments and deviations are write-once; create a new file")
        sys.exit(0)
    if p.endswith("prereg/INDEX.md"):  # added (A1): the index of prereg files is not itself a preregistration
        sys.exit(0)
    for root in PROTECTED:
        if root in p:
            block(f"{p} is frozen ({root}). Use make_numbers.py / log_run.py, or ask the human at a gate.")
if tool == "Bash":
    c = ti.get("command", "")
    if PROC_CTL.search(c):
        toks = set(re.findall(r"\d+", c))
        if S5_NAMES.search(c) or toks & s5_pids():
            block("command targets the background S5 job (PID or process name); S5 is human-only")
    if KILL_AT_CMD.search(c):
        block("process control is human-only; the background jobs must not be interrupted")
    if re.search(r"git\s+(push\s.*(--force|-f)\b|reset\s+--hard|rebase|commit\s.*--amend|filter-branch|update-ref|tag\s+-d)", c):
        block("history-rewriting git commands are disabled")
    writes = re.search(r"\b(rm|mv|cp|truncate|shred|tee|chmod)\b|sed\s+-i|>", c)
    if writes and any(r in c for r in PROTECTED) and not any(w in c for w in WRITERS):
        block("shell write touching a frozen path; read with the Read tool instead")
sys.exit(0)
