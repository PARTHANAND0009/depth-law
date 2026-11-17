#!/usr/bin/env bash
# S8 detector + S9 adaptive attacks on CPU (notes/s8_plan.md, notes/s9_plan.md). Ends at GATE G3:
# it does NOT remove results/HOLD_S5 (the human decides after G3).
# Resumable; relaunch: nohup setsid bash scripts/run_s8s9_cpu.sh >> results/s8s9_cpu.out 2>&1 < /dev/null &
set -Eeuo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH=src HF_HOME=$PWD/cache/hf OMP_NUM_THREADS=4
PY=.venv/bin/python
ts() { date -u +%Y-%m-%dT%H:%M:%SZ; }
trap 'echo "[$(ts)] S8S9 FAILED at line $LINENO"' ERR
echo "[$(ts)] START s8s9 (waiting for S7 evals and counterfactual counts)"
until grep -q "S7CPU DONE" results/s7_cpu.out && [[ -f data/s7_cf_counts_exact.parquet ]]; do sleep 300; done
pgrep -f "run_depth.*S7eval" >/dev/null && { echo "[$(ts)] S7eval still running"; exit 1; }

# S8: LCF hidden-state pass, then detector evaluation
l=$(ls -d results/S8/S8lcf-* 2>/dev/null | head -1 || true)
if [[ -z "$l" || ! -f "$l/lcf.parquet" ]]; then
  echo "[$(ts)] START lcf ${l:+resume $l}"
  $PY -m depthlaw.detect.hidden --threads 4 ${l:+--run-dir $l}
  l=$(ls -d results/S8/S8lcf-* | head -1)
fi
echo "[$(ts)] OK lcf $l"
if ! ls results/S8/S8-pythia-1.4b-*/summary.json >/dev/null 2>&1; then
  $PY -m depthlaw.detect.eval --lcf "$l/lcf.parquet"
fi
echo "[$(ts)] OK S8 eval $(ls -d results/S8/S8-pythia-1.4b-* | head -1)"

# S9: attacks
s=$(ls -d results/S9/S9-pythia-1.4b-* 2>/dev/null | head -1 || true)
$PY -m depthlaw.attack.run --threads 4 ${s:+--run-dir $s}
s=$(ls -d results/S9/S9-pythia-1.4b-* | head -1)
echo "[$(ts)] OK S9 attacks $s"
e=$(ls -d results/S9eval/S9eval-a3_freq_spoof-* 2>/dev/null | head -1 || true)
if [[ -z "$e" || ! -f "$e/depth.parquet" ]]; then
  $PY -m depthlaw.depth.run_depth --model EleutherAI/pythia-1.4b --facts "$s/a3_freq_spoof/eval.parquet" \
      --stage S9eval --tag a3_freq_spoof --causal-only --chunk 25 \
      --delta cache/zoo/pythia-1.4b/s9/a3_freq_spoof.safetensors ${e:+--run-dir $e}
  e=$(ls -d results/S9eval/S9eval-a3_freq_spoof-* | head -1)
fi
echo "[$(ts)] OK S9 a3 eval $e"
if ! ls results/S9score/*/summary.json >/dev/null 2>&1; then
  $PY -m depthlaw.detect.eval --stage S9score --lcf "$l/lcf.parquet" --extra \
      "single:a1_layer_match:$s/a1_layer_match/depth.parquet" \
      "single:a2_depth_reg:$s/a2_depth_reg/depth.parquet" \
      "batch:a3_freq_spoof:$e/depth.parquet:$s/a3_freq_spoof/eval.parquet"
fi
echo "[$(ts)] S8S9 DONE (STOP at G3: write reports/GATE_G3.md; HOLD_S5 stays)"
