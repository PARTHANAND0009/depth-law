#!/usr/bin/env python3
# PROPOSED replacement for .claude/hooks/protect_frozen.py (staged 2026-11-25 after integrity incident
# INC-2026-11-25-required-macros; the human installs it with reports/pending_frozen_changes/guard_2026-11-25/APPLY_guard.sh).
# Changes vs the installed version (2026-11-21 A4):
#   1. PROTECTED also covers the new guard files (config/frozen_paths.json, scripts/frozen_guard.py,
#      src/depthlaw/frozen_rt.py, scripts/pre-commit, scripts/install_guard.sh), config/required_macros.md,
#      scripts/gen_required_macros.py, .claude/settings.json and hooks/proposed/.
#   2. Indirect-writer rule (the incident route): any Bash command that names a script known to write a frozen
#      path (FROZEN_WRITERS) is blocked, however the frozen path itself is (not) named.
#   3. Guard-tampering rule: blocks DEPTHLAW_FROZEN_OVERRIDE (human-only override), git --no-verify,
#      git config core.hooksPath, chattr -i / chattr = ..., and writes to *.pth / site-packages.
#   4. chattr, install, dd, ln, rsync, python -c/-m with open( added to the shell-write patterns.
# Everything else is unchanged.
import json, os, re, subprocess, sys
d = json.load(sys.stdin)
tool, ti = d.get("tool_name", ""), d.get("tool_input", {}) or {}
PROTECTED = ("prereg/", "data/raw/", "paper/numbers.tex", "results/ledger.jsonl",
             ".claude/hooks/", ".claude/settings.json", "hooks/proposed/",
             "scripts/check_numbers.py", "scripts/verify_bib.py", "scripts/gate_check.py", "gates.yaml",
             "config/required_macros.json", "config/required_macros.md", "scripts/gen_required_macros.py",
             "config/frozen_paths.json", "scripts/frozen_guard.py", "src/depthlaw/frozen_rt.py",
             "scripts/pre-commit", "scripts/install_guard.sh")
WRITERS = ("scripts/make_numbers.py", "scripts/log_run.py")
FROZEN_WRITERS = ("gen_required_macros",)  # scripts whose job is to write a frozen file: human-only
KILL_AT_CMD = re.compile(r"(^|[;&|(\n]\s*)(sudo\s+)?(kill|pkill|killall)(\s|$)")
PROC_CTL = re.compile(r"\b(kill|pkill|killall|renice|ionice|taskset|cpulimit|chrt)\b|prlimit\s+--pid|\b(strace|gdb)\s+-p\b")
S5_NAMES = re.compile(r"run_s5_cpu|run_s4t_cpu|--stage\s+S5\b")
TAMPER = re.compile(r"DEPTHLAW_FROZEN_OVERRIDE|--no-verify|core\.hooksPath|chattr\s+(-\w*i|=)|\.pth\b|site-packages")


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
    if p.endswith(".pth") or "site-packages" in p:
        block(f"{p}: interpreter start-up files are part of the frozen-path guard (human-only)")
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
    if TAMPER.search(c):
        block("guard override / hook bypass / immutable-attribute removal is human-only")
    if any(w in c for w in FROZEN_WRITERS) and re.search(r"\b(python\d?|bash|sh|Rscript|exec|source|runpy)\b|\./", c):
        block("this script writes a frozen file (incident INC-2026-11-25-required-macros); human-only")
    writes = re.search(r"\b(rm|mv|cp|truncate|shred|tee|chmod|chattr|install|dd|ln|rsync)\b|sed\s+-i|>|open\(", c)
    if writes and any(r in c for r in PROTECTED) and not any(w in c for w in WRITERS):
        block("shell write touching a frozen path; read with the Read tool instead")
sys.exit(0)
