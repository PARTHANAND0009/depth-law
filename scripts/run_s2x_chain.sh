#!/usr/bin/env bash
# Exact phrase counts (prereg amendment_1). Resumable: responses are cached, a finished
# output file is skipped. Order: EXACT indexes first, then PROXY, then SANSKRITI.
set -euo pipefail
cd "$(dirname "$0")/.."
. .venv/bin/activate
export PYTHONPATH=src HF_HOME="$PWD/cache/hf" IG_WORKERS=6 IG_MIN_INTERVAL=0.25
step(){ local out=$1; shift
  if [ -e "$out" ]; then echo "[$(date -u +%FT%TZ)] SKIP (exists $out) $*"; return; fi
  echo "[$(date -u +%FT%TZ)] START $*"; "$@"; echo "[$(date -u +%FT%TZ)] OK $*"; }
trap 'echo "[$(date -u +%FT%TZ)] CHAIN FAILED at line $LINENO"' ERR
# all three indexes in one pass (job list is the union; cached responses make reruns cheap)
step data/counts_exact.parquet python -m depthlaw.freq.exact_counts
step data/sanskriti_cloze_exact.parquet python -m depthlaw.freq.exact_counts --facts data/sanskriti_cloze.parquet
echo "[$(date -u +%FT%TZ)] CHAIN DONE"
