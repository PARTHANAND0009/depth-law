#!/usr/bin/env bash
# Tests for the frozen-path rules of the PreToolUse hook, including the route of integrity incident
# INC-2026-11-25-required-macros (a script that writes a frozen file, run without naming that file).
# Usage: bash hooks/tests/test_frozen_hook.sh [hook.py]   (default: hooks/proposed/protect_frozen.py)
# Nothing in the cases is executed; each JSON tool call is piped into the hook. 2 = blocked, 0 = allowed.
set -u
cd "$(dirname "$0")/../.."
HOOK=${1:-hooks/proposed/protect_frozen.py}
pass=0; fail=0
check() {  # $1 expected (BLOCK|PASS)  $2 tool  $3 command or file path
  local json rc got
  json=$(python3 -c 'import json,sys
t,a=sys.argv[1],sys.argv[2]
ti={"command":a} if t=="Bash" else {"file_path":a}
print(json.dumps({"tool_name":t,"tool_input":ti}))' "$2" "$3")
  printf '%s' "$json" | python3 "$HOOK" >/dev/null 2>&1; rc=$?
  if [ $rc -eq 2 ]; then got=BLOCK; else got=PASS; fi
  if [ "$got" = "$1" ]; then pass=$((pass+1)); r=ok; else fail=$((fail+1)); r=WRONG; fi
  printf '%-5s expected %-5s got %-5s | %-5s %s\n' "$r" "$1" "$got" "$2" "$3"
}
echo "hook: $HOOK"
# the incident route and variants
check BLOCK Bash "python3 scripts/gen_required_macros.py"
check BLOCK Bash "cd scripts && python gen_required_macros.py --p2"
check BLOCK Bash ".venv/bin/python -m scripts.gen_required_macros"
check BLOCK Bash "bash -c 'python3 scripts/gen_required_macros.py'"
check BLOCK Edit "/home/user/depth-law/scripts/gen_required_macros.py"
# guard tampering
check BLOCK Bash "DEPTHLAW_FROZEN_OVERRIDE=1 git commit -m x"
check BLOCK Bash "git commit --no-verify -m x"
check BLOCK Bash "git config core.hooksPath /dev/null"
check BLOCK Bash "chattr -i config/frozen_paths.json"
check BLOCK Bash "echo x > /usr/local/lib/python3.13/site-packages/depthlaw_frozen_rt.pth"
check BLOCK Write "/home/user/depth-law/.venv/lib/python3.13/site-packages/x.pth"
check BLOCK Edit "/home/user/depth-law/config/frozen_paths.json"
check BLOCK Edit "/home/user/depth-law/src/depthlaw/frozen_rt.py"
check BLOCK Edit "/home/user/depth-law/.claude/settings.json"
check BLOCK Bash "python3 -c \"open('config/required_macros.json','w')\""
# unchanged rules
check BLOCK Edit "/home/user/depth-law/prereg/HR_revised.md"
check BLOCK Bash "cp x paper/numbers.tex"
check PASS  Write "/home/user/depth-law/prereg/deviations/D-NEW-test.md"
check PASS  Edit "/home/user/depth-law/prereg/INDEX.md"
# must pass: reading, the logged writers, ordinary work
check PASS  Bash "cat config/required_macros.json | head"
check PASS  Bash "git log -- scripts/gen_required_macros.py"
check PASS  Bash "python3 scripts/log_run.py --tag t --seed 1 --status CONFIRMATORY --out paper/numbers.tex -- python3 scripts/make_numbers.py"
check PASS  Bash "python3 scripts/frozen_guard.py check-worktree"
check PASS  Bash ".venv/bin/python -m pytest -q tests/test_frozen_guard.py"
check PASS  Edit "/home/user/depth-law/analysis/p2/p2_results_md.py"
echo "pass=$pass fail=$fail"
[ $fail -eq 0 ]
