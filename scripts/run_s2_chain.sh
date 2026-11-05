#!/usr/bin/env bash
# S1 rebuild then all S2 counting passes and the audit; each step runs only if the previous succeeded.
set -euo pipefail
cd "$(dirname "$0")/.."
. .venv/bin/activate
export PYTHONPATH=src HF_HOME="$PWD/cache/hf" IG_WORKERS=6 IG_MIN_INTERVAL=0.25
step(){ echo "[$(date -u +%FT%TZ)] START $*"; "$@"; echo "[$(date -u +%FT%TZ)] OK $*"; }
trap 'echo "[$(date -u +%FT%TZ)] CHAIN FAILED at line $LINENO"' ERR
step python -m depthlaw.facts.build_facts
step python -m depthlaw.freq.counts --pass primary
step python -m depthlaw.freq.audit
step python -m depthlaw.freq.counts --facts data/sanskriti_cloze.parquet --pass primary
step python -m depthlaw.freq.counts --pass sensitivity
step python -m depthlaw.freq.counts --facts data/sanskriti_cloze.parquet --pass sensitivity
echo "[$(date -u +%FT%TZ)] CHAIN DONE"
