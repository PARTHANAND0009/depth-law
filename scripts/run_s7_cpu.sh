#!/usr/bin/env bash
# S7 zoo on CPU (notes/s7_plan.md): build on pythia-1.4b, then causal-only evals of each kept model.
# Resumable; relaunch: nohup setsid bash scripts/run_s7_cpu.sh >> results/s7_cpu.out 2>&1 < /dev/null &
# S5 and the Gemma queue are paused while this runs (RAM) and relaunched at the end.
set -Eeuo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH=src HF_HOME=$PWD/cache/hf OMP_NUM_THREADS=4
PY=.venv/bin/python
ts() { date -u +%Y-%m-%dT%H:%M:%SZ; }
trap 'echo "[$(ts)] S7CPU FAILED at line $LINENO"' ERR
d=$(ls -d results/S7/S7-pythia-1.4b-* 2>/dev/null | head -1 || true)
echo "[$(ts)] START build ${d:+resume $d}"
$PY -m depthlaw.zoo.build --model EleutherAI/pythia-1.4b --threads 4 ${d:+--run-dir $d}
d=$(ls -d results/S7/S7-pythia-1.4b-* | head -1)
echo "[$(ts)] OK build $d"
for t in data/zoo/*_eval.parquet; do
  mid=$(basename "$t" _eval.parquet)
  e=$(ls -d results/S7eval/S7eval-${mid}-* 2>/dev/null | head -1 || true)
  if [[ -n "$e" && -f "$e/depth.parquet" ]]; then echo "[$(ts)] SKIP eval $mid"; continue; fi
  delta=$($PY -c "import json;print([m['delta'] for m in json.load(open('$d/manifest.json'))['models'] if m['model_id']=='$mid'][0])")
  echo "[$(ts)] START eval $mid"
  $PY -m depthlaw.depth.run_depth --model EleutherAI/pythia-1.4b --facts "$t" --stage S7eval --tag "$mid" \
      --causal-only --chunk 25 --delta "$delta" ${e:+--run-dir $e}
  echo "[$(ts)] OK eval $mid"
done
echo "[$(ts)] S7CPU DONE"
echo "[$(ts)] RELAUNCH S5 and S4T after S7" | tee -a results/s5_cpu.out results/s4t_cpu.out
nohup setsid bash scripts/run_s5_cpu.sh >> results/s5_cpu.out 2>&1 < /dev/null &
sleep 5
nohup setsid bash scripts/run_s4t_cpu.sh >> results/s4t_cpu.out 2>&1 < /dev/null &
