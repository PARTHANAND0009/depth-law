#!/usr/bin/env bash
# S4 CPU chain (notes/s4_plan.md). Resumable: rerun the same command after a restart.
set -Eeuo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH=src HF_HOME=$PWD/cache/hf OMP_NUM_THREADS=4
PY=.venv/bin/python
ts() { date -u +%Y-%m-%dT%H:%M:%SZ; }
trap 'echo "[$(ts)] S4CPU FAILED at line $LINENO"' ERR
d=$(ls -d results/S4/S4-pythia-1.4b-* 2>/dev/null | head -1 || true)
if [[ -n "$d" && -f "$d/depth.parquet" ]]; then echo "[$(ts)] SKIP sanskriti depth ($d)"
else
  echo "[$(ts)] START sanskriti depth pythia-1.4b ${d:+resume $d}"
  $PY -m depthlaw.depth.run_depth --model EleutherAI/pythia-1.4b --facts data/sanskriti_s4.parquet \
      --stage S4 ${d:+--run-dir $d} --chunk 10
  echo "[$(ts)] OK sanskriti depth"
fi
echo "[$(ts)] S4CPU DEPTH DONE"
