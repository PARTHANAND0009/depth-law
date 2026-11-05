#!/usr/bin/env bash
# Waits for the running S1 build, then runs all S2 counting passes and the audit, in order.
set -uo pipefail
cd "$(dirname "$0")/.."
. .venv/bin/activate
export PYTHONPATH=src HF_HOME="$PWD/cache/hf" IG_WORKERS=6 IG_MIN_INTERVAL=0.2
while pgrep -f "depthlaw.facts.build_facts" >/dev/null; do sleep 30; done
echo "[$(date -u +%FT%TZ)] S1 done" 
python -m depthlaw.freq.counts --pass primary && \
python -m depthlaw.freq.audit && \
python -m depthlaw.freq.counts --facts data/sanskriti_cloze.parquet --pass primary && \
python -m depthlaw.freq.counts --pass sensitivity && \
python -m depthlaw.freq.counts --facts data/sanskriti_cloze.parquet --pass sensitivity
echo "[$(date -u +%FT%TZ)] chain exit $?"
