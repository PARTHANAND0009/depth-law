#!/usr/bin/env bash
# CPU G1 (human OK "OK CPU G1", 2026-11-08). Subsample data/facts_g1cpu.parquet
# (data/splits/g1_cpu_subsample.json: 50 facts x 26 relations), 3 templates.
# Order: pythia-1.4b depth -> tests on pythia-70m (CLAUDE.md rule 4) -> pythia-2.8b depth
# -> wait for exact counts (scripts/run_s2x_chain.sh) -> G1 analysis -> STOP (rule 3).
# Resumable: finished depth runs (depth.parquet) are skipped; unfinished ones resume their chunks.
set -euo pipefail
cd "$(dirname "$0")/.."
. .venv/bin/activate
export PYTHONPATH=src HF_HOME="$PWD/cache/hf"
FACTS=data/facts_g1cpu.parquet
trap 'echo "[$(date -u +%FT%TZ)] G1CPU FAILED at line $LINENO"' ERR
ts(){ date -u +%FT%TZ; }

depth(){ local model=$1 short=${1##*/} rd
  rd=$(ls -d results/S3/S3-${short}-* 2>/dev/null | head -1 || true)
  if [ -n "$rd" ] && [ -e "$rd/depth.parquet" ]; then echo "[$(ts)] SKIP depth $short ($rd)"; return; fi
  echo "[$(ts)] START depth $short ${rd:+resume $rd}"
  python -m depthlaw.depth.run_depth --model "$model" --facts $FACTS --stage S3 ${rd:+--run-dir $rd}
  echo "[$(ts)] OK depth $short"; }

depth EleutherAI/pythia-1.4b

J=results/S3/tests_pythia70m_before_2.8b_junit.xml
if [ ! -e "$J" ]; then
  echo "[$(ts)] START tests (rule 4)"; python -m pytest tests -q --junitxml="$J"; echo "[$(ts)] OK tests"
fi

depth EleutherAI/pythia-2.8b

until [ -e data/counts_exact.parquet ]; do echo "[$(ts)] WAIT data/counts_exact.parquet"; sleep 1800; done

if ! ls reports/GATE_G1.md >/dev/null 2>&1; then
  echo "[$(ts)] START g1"
  python -m depthlaw.stats.g1 --depth results/S3/S3-pythia-1.4b-*/depth.parquet \
    results/S3/S3-pythia-2.8b-*/depth.parquet --exact data/counts_exact.parquet --n-boot 1000
  echo "[$(ts)] OK g1"
fi
echo "[$(ts)] G1CPU DONE (STOP at G1)"
