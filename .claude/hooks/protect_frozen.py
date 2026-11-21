#!/usr/bin/env python3
import json, os, re, sys
d = json.load(sys.stdin)
tool, ti = d.get("tool_name", ""), d.get("tool_input", {}) or {}
PROTECTED = ("prereg/", "data/raw/", "paper/numbers.tex", "results/ledger.jsonl",
             ".claude/hooks/", "scripts/check_numbers.py", "scripts/verify_bib.py",
             "scripts/gate_check.py", "gates.yaml", "config/required_macros.json")
WRITERS = ("scripts/make_numbers.py", "scripts/log_run.py")
def block(msg):
    print("BLOCKED: " + msg, file=sys.stderr); sys.exit(2)
if tool in ("Edit", "Write", "MultiEdit", "NotebookEdit"):
    p = (ti.get("file_path") or ti.get("notebook_path") or "").replace("\\", "/")
    if "prereg/amendments/" in p:
        if tool != "Write" or os.path.exists(p):
            block(f"{p}: amendments are write-once; create a new file A<n>_<slug>.md")
        sys.exit(0)
    for root in PROTECTED:
        if root in p:
            block(f"{p} is frozen ({root}). Use make_numbers.py / log_run.py, or ask the human at a gate.")
if tool == "Bash":
    c = ti.get("command", "")
    if re.search(r"\b(kill|pkill|killall)\b", c):
        block("process control is human-only; the H-R background job must not be interrupted")
    if re.search(r"git\s+(push\s.*(--force|-f)\b|reset\s+--hard|rebase|commit\s.*--amend|filter-branch|update-ref|tag\s+-d)", c):
        block("history-rewriting git commands are disabled")
    writes = re.search(r"\b(rm|mv|cp|truncate|shred|tee|chmod)\b|sed\s+-i|>", c)
    if writes and any(r in c for r in PROTECTED) and not any(w in c for w in WRITERS):
        block("shell write touching a frozen path; read with the Read tool instead")
sys.exit(0)
