#!/usr/bin/env bash
# Tests for the S5 chunk exemption in the Stop hook's PROGRESS.md rule (part A5).
# Usage: bash hooks/tests/test_stop_s5.sh [stop_check.py]   (default: hooks/proposed/stop_check.py)
# Builds a throwaway git repo in a temp dir (the real repo is not touched), commits PROGRESS.md, then
# creates one changed path per case and runs the hook with the harness JSON. 0 = stop allowed, 2 = refused.
set -u
HOOK=$(cd "$(dirname "$0")/../.." && pwd)/${1:-hooks/proposed/stop_check.py}
pass=0; fail=0
run_case() {  # $1 expected (ALLOW|REFUSE)  $2 description  $3 path to create
  local T rc got
  T=$(mktemp -d)
  ( cd "$T" && git init -q && git config user.email t@t && git config user.name t \
    && printf 'progress\n' > PROGRESS.md && mkdir -p results/S5/S5-pythia-2.8b_step32000-abc1234-20261121T050945Z/chunks \
    && printf '{}\n' > results/S5/S5-pythia-2.8b_step32000-abc1234-20261121T050945Z/log.jsonl \
    && git add -A && git commit -q -m init )
  ( cd "$T" && mkdir -p "$(dirname "$3")" && printf 'x\n' >> "$3" )
  printf '{"cwd": "%s", "stop_hook_active": false}' "$T" | python3 "$HOOK" >/dev/null 2>&1; rc=$?
  if [ $rc -eq 0 ]; then got=ALLOW; else got=REFUSE; fi
  if [ "$got" = "$1" ]; then pass=$((pass+1)); r=ok; else fail=$((fail+1)); r=WRONG; fi
  printf '%-5s expected %-6s got %-6s | %s: %s\n' "$r" "$1" "$got" "$2" "$3"
  rm -rf "$T"
}
echo "hook: $HOOK"
run_case ALLOW  "S5 chunk (new, untracked)"        results/S5/S5-pythia-2.8b_step32000-abc1234-20261121T050945Z/chunks/s00_c00017.parquet
run_case ALLOW  "S5 run log (modified, one line per chunk)" results/S5/S5-pythia-2.8b_step32000-abc1234-20261121T050945Z/log.jsonl
run_case REFUSE "non-S5 results file"              results/HR/HR-none-x/hr_gate.json
run_case REFUSE "S5 merged depth table (not a chunk)" results/S5/S5-pythia-2.8b_step32000-abc1234-20261121T050945Z/depth.parquet
run_case REFUSE "S5 chain log (not a chunk)"       results/s5_cpu.out
run_case REFUSE "chunk-like file one level deeper" results/S5/S5-x/extra/chunks/s00_c00001.parquet
run_case REFUSE "analysis file"                    analysis/exploratory/E-depthvar/x.py
echo "RESULT: $pass correct, $fail wrong (of $((pass+fail)))"
[ $fail -eq 0 ]
