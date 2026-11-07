#!/usr/bin/env bash
# G1 dry run on pythia-410m (test model, CPU allowed): depth on 300 seeded facts x 3 templates,
# exact Pile counts for those facts, then the full G1 analysis with a reduced bootstrap.
set -euo pipefail
cd "$(dirname "$0")/.."
. .venv/bin/activate
export PYTHONPATH=src HF_HOME="$PWD/cache/hf" IG_WORKERS=4 IG_MIN_INTERVAL=0.25
echo "[$(date -u +%FT%TZ)] START exact counts (dry300)"
[ -e data/counts_dry300_exact.parquet ] || python -m depthlaw.freq.exact_counts --facts data/facts_dry300.parquet --indexes v4_piletrain_llama
RD=${RD:-}
echo "[$(date -u +%FT%TZ)] START depth"
if [ -n "$RD" ]; then python -m depthlaw.depth.run_depth --model EleutherAI/pythia-410m --facts data/facts_dry300.parquet --stage S3dry --run-dir "$RD"
else python -m depthlaw.depth.run_depth --model EleutherAI/pythia-410m --facts data/facts_dry300.parquet --stage S3dry; fi
echo "[$(date -u +%FT%TZ)] DEPTH DONE"
