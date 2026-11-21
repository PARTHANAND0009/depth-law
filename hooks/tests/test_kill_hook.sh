#!/usr/bin/env bash
# Tests for the kill / S5 process-control rule of the PreToolUse hook (part A4).
# Usage: bash hooks/tests/test_kill_hook.sh [hook.py]   (default: hooks/proposed/protect_frozen.py)
# Each case pipes the JSON that Claude Code sends for a Bash tool call into the hook and checks the exit
# code: 2 = blocked, 0 = allowed. Nothing in the cases is executed.
set -u
cd "$(dirname "$0")/../.."
HOOK=${1:-hooks/proposed/protect_frozen.py}
pass=0; fail=0
# A dummy process whose command line looks like the S5 job, so the PID rule can be tested while the real
# S5 job is not running. It is a plain sleep and exits on its own.
bash -c 'exec -a "python -m depthlaw.depth.run_depth --stage S5 dummy-for-hook-test" sleep 20' &
DUMMY=$!
sleep 0.5

check() {  # $1 expected (BLOCK|PASS)  $2 command
  local json rc got
  json=$(python3 -c 'import json,sys; print(json.dumps({"tool_name":"Bash","tool_input":{"command":sys.argv[1]}}))' "$2")
  printf '%s' "$json" | python3 "$HOOK" >/dev/null 2>&1; rc=$?
  if [ $rc -eq 2 ]; then got=BLOCK; else got=PASS; fi
  if [ "$got" = "$1" ]; then pass=$((pass+1)); r=ok; else fail=$((fail+1)); r=WRONG; fi
  printf '%-5s expected %-5s got %-5s | %s\n' "$r" "$1" "$got" "$2"
}

echo "hook: $HOOK   (dummy S5-like PID $DUMMY)"
# must block: termination at command position
check BLOCK "kill 12345"
check BLOCK "sudo kill -9 4242"
check BLOCK "ls; pkill -f some_worker"
check BLOCK "true && killall python3"
check BLOCK "(kill -0 999999)"
# must block: process control aimed at S5 by name or PID (anywhere in the command)
check BLOCK "renice -n 5 -p \$(pgrep -f run_s5_cpu)"
check BLOCK "cpulimit -l 10 -e run_s4t_cpu"
check BLOCK "taskset -p 0x1 $DUMMY"
# must pass: 'kill' is part of another token, or read-only S5 checks
check PASS "echo skill"
check PASS "dmesg | grep -i 'killed process' | tail -3"
check PASS "ls results/kill_switch_notes.txt"
check PASS "echo \"probe: kill-word in an echo\""
check PASS "ps -eo pid,cmd | grep run_s5_cpu"
echo "RESULT: $pass correct, $fail wrong (of $((pass+fail)))"
[ $fail -eq 0 ]
