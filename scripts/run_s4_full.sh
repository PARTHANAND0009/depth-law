#!/usr/bin/env bash
# Full S4 CPU chain (notes/s4_plan.md). Resumable; after a container restart relaunch ONLY this:
#   nohup setsid bash scripts/run_s4_full.sh >> results/s4_cpu.out 2>&1 < /dev/null &
set -Eeuo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH=src HF_HOME=$PWD/cache/hf OMP_NUM_THREADS=4
PY=.venv/bin/python
ts() { date -u +%Y-%m-%dT%H:%M:%SZ; }
trap 'echo "[$(ts)] S4CPU FAILED at line $LINENO"' ERR
while pgrep -f "scripts/run_s4_cpu.sh" >/dev/null; do sleep 60; done
# 1. SANSKRITI slice depth (pythia-1.4b), resumable
d=$(ls -d results/S4/S4-pythia-1.4b-* 2>/dev/null | head -1 || true)
if [[ -n "$d" && -f "$d/depth.parquet" ]]; then echo "[$(ts)] SKIP sanskriti depth ($d)"
else
  echo "[$(ts)] START sanskriti depth pythia-1.4b ${d:+resume $d}"
  $PY -m depthlaw.depth.run_depth --model EleutherAI/pythia-1.4b --facts data/sanskriti_s4.parquet \
      --stage S4 ${d:+--run-dir $d} --chunk 10
  d=$(ls -d results/S4/S4-pythia-1.4b-* | head -1)
  echo "[$(ts)] OK sanskriti depth"
fi
# 2. LRE faithfulness (pythia-1.4b, G1 subsample), resumable per relation
l=$(ls -d results/S4/S4lre-pythia-1.4b-* 2>/dev/null | head -1 || true)
if [[ -n "$l" && -f "$l/lre.parquet" ]]; then echo "[$(ts)] SKIP lre ($l)"
else
  echo "[$(ts)] START lre pythia-1.4b ${l:+resume $l}"
  $PY -m depthlaw.depth.lre --model EleutherAI/pythia-1.4b --facts data/facts_g1cpu.parquet ${l:+--run-dir $l}
  l=$(ls -d results/S4/S4lre-pythia-1.4b-* | head -1)
  echo "[$(ts)] OK lre"
fi
# 3. S4 statistics + reports/S4.md
if [[ -f reports/S4.md ]]; then echo "[$(ts)] SKIP s4 stats (reports/S4.md exists)"
else
  echo "[$(ts)] START s4 stats"
  $PY -m depthlaw.stats.s4 --depth results/S3/S3-pythia-1.4b-b9a353d-20261108T064941Z/depth.parquet \
      results/S3/S3-pythia-2.8b-be99060-20261109T021915Z/depth.parquet \
      --sanskriti "$d/depth.parquet" --lre "$l/lre.parquet" --n-boot 1000
  echo "[$(ts)] OK s4 stats"
fi
echo "[$(ts)] S4CPU DONE"
