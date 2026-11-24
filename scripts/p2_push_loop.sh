#!/usr/bin/env bash
# P2 GPU session: off-instance copy loop (reports/p2/GPU_SESSION_RUNBOOK.md). Not frozen code; it only copies files.
# Run on the GPU VM in its own tmux window. Every INTERVAL seconds it copies the session's outputs from the run checkout
# (left untouched at the frozen commit) into a separate clone and pushes that clone to a GitHub branch:
#   results/P2/            the model run dirs (chunks, manifest.json, log.jsonl, meta*.json)
#   results/P2smoke/       the smoke run
#   results/logs/          the driver's session log and pytest log
#   deviations_pending/    the deviation files written by the driver
#   p2_syncdest/           the driver's own SYNC_DEST copies (deviations and log at the moment of each event)
# Usage: bash scripts/p2_push_loop.sh <run checkout> <sync clone> [branch] [interval_s]   (ONCE=1 for a single pass)
set -u
SRC=${1:?run checkout}; DST=${2:?sync clone}; BR=${3:-p2-gpu-session}; INTERVAL=${4:-60}
cd "$DST" || exit 1
git config user.name "p2-gpu-vm"; git config user.email "p2-gpu-vm@localhost"
while true; do
  ( cd "$SRC" && for d in results/P2 results/P2smoke results/logs deviations_pending; do
      [ -e "$d" ] && rsync -aR "$d" "$DST/"; done ) 2>&1 | sed 's/^/rsync: /'
  for p in results deviations_pending p2_syncdest VM_FILES.sha256; do [ -e "$p" ] && git add -A "$p"; done  # one missing path would abort a joint add
  git diff --cached --quiet || git commit -q -m "P2 GPU session sync $(date -u +%FT%TZ)"
  if git push -q origin "HEAD:refs/heads/$BR" 2>/tmp/p2_push_err; then
    echo "[$(date -u +%FT%TZ)] pushed $(git rev-parse --short HEAD) to $BR"
  else
    echo "[$(date -u +%FT%TZ)] PUSH FAILED: $(tail -1 /tmp/p2_push_err)"
  fi
  [ "${ONCE:-0}" = 1 ] && break
  sleep "$INTERVAL"
done
