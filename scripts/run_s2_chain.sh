#!/usr/bin/env bash
# All S2 counting passes and the audit on the committed S1 facts (S1 is NOT rebuilt here).
# Resumable: a step whose output file exists is skipped; API responses are cached, so a
# restarted step re-queries only what is missing.
set -euo pipefail
cd "$(dirname "$0")/.."
. .venv/bin/activate
export PYTHONPATH=src HF_HOME="$PWD/cache/hf" IG_WORKERS=6 IG_MIN_INTERVAL=0.25
step(){ local out=$1; shift
  if [ -e "$out" ]; then echo "[$(date -u +%FT%TZ)] SKIP (exists $out) $*"; return; fi
  echo "[$(date -u +%FT%TZ)] START $*"; "$@"; echo "[$(date -u +%FT%TZ)] OK $*"; }
trap 'echo "[$(date -u +%FT%TZ)] CHAIN FAILED at line $LINENO"' ERR
step data/counts_primary.parquet python -m depthlaw.freq.counts --pass primary
step reports/count_audit.csv python -m depthlaw.freq.audit
step data/sanskriti_cloze_primary.parquet python -m depthlaw.freq.counts --facts data/sanskriti_cloze.parquet --pass primary
step data/counts_sensitivity.parquet python -m depthlaw.freq.counts --pass sensitivity
step data/sanskriti_cloze_sensitivity.parquet python -m depthlaw.freq.counts --facts data/sanskriti_cloze.parquet --pass sensitivity
echo "[$(date -u +%FT%TZ)] CHAIN DONE"
