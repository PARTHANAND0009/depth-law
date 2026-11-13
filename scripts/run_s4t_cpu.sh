#!/usr/bin/env bash
# S4 transfer on CPU: google/gemma-3-4b-pt (bf16), causal-only, G1 subsample (1300 facts).
# Waits for the S5 chain (RAM). Llama-3.1-8B, Qwen3-8B: MISSING (do not fit in 15 GB RAM).
#   nohup setsid bash scripts/run_s4t_cpu.sh >> results/s4t_cpu.out 2>&1 < /dev/null &
set -Eeuo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH=src HF_HOME=$PWD/cache/hf OMP_NUM_THREADS=2
PY=.venv/bin/python
ts() { date -u +%Y-%m-%dT%H:%M:%SZ; }
trap 'echo "[$(ts)] S4T FAILED at line $LINENO"' ERR
while pgrep -f "scripts/run_s5_cpu.sh" >/dev/null; do sleep 120; done
d=$(ls -d results/S4/S4-gemma-3-4b-pt-* 2>/dev/null | head -1 || true)
if [[ -n "$d" && -f "$d/depth.parquet" ]]; then echo "[$(ts)] SKIP gemma ($d)"
else
  echo "[$(ts)] START gemma-3-4b-pt ${d:+resume $d}"
  $PY -m depthlaw.depth.run_depth --model google/gemma-3-4b-pt --facts data/facts_g1cpu.parquet --stage S4 \
      --causal-only --dtype bfloat16 --chunk 20 ${d:+--run-dir $d}
  echo "[$(ts)] OK gemma"
fi
echo "[$(ts)] S4T DONE"
