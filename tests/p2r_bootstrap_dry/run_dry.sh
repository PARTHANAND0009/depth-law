#!/usr/bin/env bash
# CPU dry run of scripts/p2r_vm_bootstrap.sh (test only; run through scripts/log_run.py).
#   bash tests/p2r_bootstrap_dry/run_dry.sh <sandbox dir> [full|lowbal|olddriver|wrongtag]
# The sandbox gets: a local bare repo cloned from this repository with tag prereg-P2R deleted (so the bootstrap's
# create-and-push path runs; 'wrongtag' puts it on the wrong commit instead), HOME=<sandbox>/home, stub
# sudo/shutdown/nvidia-smi first on PATH (nothing runs as root and nothing shuts down), dummy tokens (the agent
# proxy supplies the real Hugging Face credential), and DRYRUN=1 in the bootstrap: pythia-70m is the measured model,
# the two P2R models get configs and tokenizer files only (check-cache --only-present), and the venv is a wrapper
# around the project's CPU venv (tests/p2r_bootstrap_dry/venv_hook.sh). The frozen driver runs in its non-DRY path
# (MODELS=EleutherAI/pythia-70m, all 300 facts x 10 paraphrases x 3 carriers, budget timer armed, deviations_pending).
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd); REPO=$(cd "$HERE/../.." && pwd)
SB=${1:?sandbox dir}; MODE=${2:-full}
TAG_SHA=005767724aa9012d1483c41ee122a715a6566cea
GH=ghp_DRYRUNdummyGH0123456789abcdef; HF=hf_DRYRUNdummyHF0123456789abcdef
BAL=400; unset STUB_DRIVER
case "$MODE" in full|wrongtag) ;; lowbal) BAL=147;; olddriver) export STUB_DRIVER=570.86.10;; *) echo "mode?"; exit 2;; esac
rm -rf "$SB"; mkdir -p "$SB/home" "$SB/stubs"
git clone -q --bare "$REPO" "$SB/origin.git"
git -C "$SB/origin.git" tag -d prereg-P2R > /dev/null 2>&1 || true
git -C "$SB/origin.git" branch -D p2r-gpu-session > /dev/null 2>&1 || true
[ "$MODE" = wrongtag ] && git -C "$SB/origin.git" tag prereg-P2R "$TAG_SHA~1"
cp "$HERE/stubs/"* "$SB/stubs/"; chmod +x "$SB/stubs/"*
export STUB_LOG=$SB/stubs.log; : > "$STUB_LOG"
cp "$REPO/scripts/p2r_vm_bootstrap.sh" "$SB/home/"
echo "== dry run mode=$MODE sandbox=$SB BALANCE=$BAL"
T0=$(date +%s)
( cd "$SB/home" && unset VIRTUAL_ENV PYTHONPATH HF_HOME && \
  HOME="$SB/home" PATH="$SB/stubs:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin" GH_TOKEN=$GH HF_TOKEN=$HF \
  BALANCE=$BAL HOURLY=207.36 DRYRUN=1 REPO_URL="$SB/origin.git" DRY_HOOKS="$HERE" PROJECT_VENV="$REPO/.venv" MIN_FREE_GB=1 \
  bash p2r_vm_bootstrap.sh )
RC=$?
echo "== bootstrap exit $RC after $(( $(date +%s) - T0 )) s"
LOG=$(ls "$SB"/home/p2r_logs/bootstrap_*.log | tail -1)
# the driver's auto-stop sleeper (stub shutdown) is left running by design; end it
DL=$(ls "$SB"/home/depth-law/results/logs/p2_gpu_run_*.log 2> /dev/null | tail -1)
if [ -n "$DL" ]; then
  AP=$(grep -o 'auto-stop armed: [0-9]* min (pid [0-9]*)' "$DL" | grep -o 'pid [0-9]*' | cut -d' ' -f2 || true)
  [ -n "$AP" ] && { pkill -P "$AP" sleep 2> /dev/null; kill "$AP" 2> /dev/null; echo "== ended the driver's auto-stop sleeper (pid $AP)"; }
fi
ok=1
chk() { if eval "$2"; then echo "CHECK OK   $1"; else echo "CHECK FAIL $1"; ok=0; fi; }
LEAK=$(grep -rlaF -e "$GH" -e "$HF" "$SB" 2> /dev/null | head -3)
chk "no token value in any sandbox file (logs, git configs, caches)" '[ -z "$LEAK" ]'
chk "hard stop requested through the stub" 'grep -q "\[stub shutdown\] -h +" "$STUB_LOG"'
case "$MODE" in
  full)
    chk "bootstrap exit 0" '[ "$RC" = 0 ]'
    chk "tag prereg-P2R pushed to the bare repo at $TAG_SHA" '[ "$(git -C "$SB/origin.git" rev-parse prereg-P2R 2>/dev/null)" = "$TAG_SHA" ]'
    chk "branch p2r-gpu-session on the bare repo" 'git -C "$SB/origin.git" rev-parse -q --verify refs/heads/p2r-gpu-session > /dev/null'
    chk "frozen hashes checked (17 + 1 OK lines)" '[ "$(grep -c ": OK$" "$LOG")" -ge 18 ]'
    chk "check-hub OK on the real pins (24 files)" 'grep -q "check-hub: OK (24 files compared)" "$LOG"'
    chk "driver non-DRY path, finished" 'grep -q "start DRY=0" "$DL" && grep -q "finished after" "$DL"'
    chk "pilot ran and projected" 'grep -q "pilot projection (min)" "$DL"'
    chk "verify script printed SAFE TO DESTROY THE VM: YES" 'grep -q "^SAFE TO DESTROY THE VM: YES" "$SB/home/p2r_logs/verify.txt"'
    chk "final box: SAFE TO DESTROY THE VM: YES" 'grep -q "## SAFE TO DESTROY THE VM: YES$" "$LOG"'
    chk "deviation note pushed before any download" 'git -C "$SB/origin.git" log --reverse --format=%H p2r-gpu-session | head -1 | xargs -I{} git -C "$SB/origin.git" ls-tree -r --name-only {} | grep -q "_p2r_preflight/D-P2R-.*-bootstrap.md"' ;;
  lowbal|olddriver)
    chk "bootstrap refused (exit 1) before any clone" '[ "$RC" = 1 ] && [ ! -e "$SB/home/depth-law" ]'
    chk "final box says nothing ran" 'grep -q "## SAFE TO DESTROY THE VM: YES (nothing to copy)" "$LOG"' ;;
  wrongtag)
    chk "bootstrap refused (exit 1) at the tag" '[ "$RC" = 1 ] && grep -q "FATAL: origin.s prereg-P2R points to" "$LOG"'
    chk "no sync branch created" '! git -C "$SB/origin.git" rev-parse -q --verify refs/heads/p2r-gpu-session > /dev/null'
    chk "final box says PAUSE / NO" 'grep -q "## SAFE TO DESTROY THE VM: NO" "$LOG"' ;;
esac
echo "== $MODE: $([ $ok = 1 ] && echo ALL CHECKS PASSED || echo SOME CHECKS FAILED)"
[ $ok = 1 ]
