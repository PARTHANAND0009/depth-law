#!/usr/bin/env bash
# S6 CPU chain (notes/s6_plan.md): per seed build stream, train, evaluate causal depth. Resumable:
#   nohup setsid bash scripts/run_s6_cpu.sh >> results/s6_cpu.out 2>&1 < /dev/null &
set -Eeuo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH=src HF_HOME=$PWD/cache/hf OMP_NUM_THREADS=4
PY=.venv/bin/python
ts() { date -u +%Y-%m-%dT%H:%M:%SZ; }
trap 'echo "[$(ts)] S6CPU FAILED at line $LINENO"' ERR
TOK=$($PY -c "import yaml;print(yaml.safe_load(open('configs/s6.yaml'))['train']['tokens'])")
for S in 1 2 3; do
  if ! $PY -c "import json,sys;sys.exit(0 if json.load(open('data/s6/seed$S/meta.json'))['target_tokens']==$TOK else 1)" 2>/dev/null; then
    echo "[$(ts)] START mix seed $S ($TOK tokens)"; $PY -m depthlaw.pretrain.mix --seed $S --tokens $TOK; echo "[$(ts)] OK mix seed $S"
  fi
  r=$(ls -d results/S6/S6-s6lm_seed${S}-* 2>/dev/null | head -1 || true)
  if [[ -n "$r" && -d "$r/final" ]]; then echo "[$(ts)] SKIP train seed $S ($r)"
  else
    echo "[$(ts)] START train seed $S ${r:+resume $r}"
    $PY -m depthlaw.pretrain.train --seed $S ${r:+--run-dir $r}
    r=$(ls -d results/S6/S6-s6lm_seed${S}-* | head -1); echo "[$(ts)] OK train seed $S"
  fi
  e=$(ls -d results/S6eval_seed${S}/S6eval_seed${S}-final-* 2>/dev/null | head -1 || true)
  if [[ -n "$e" && -f "$e/depth.parquet" ]]; then echo "[$(ts)] SKIP eval seed $S ($e)"
  else
    echo "[$(ts)] START eval seed $S"
    $PY -m depthlaw.depth.run_depth --model "$r/final" --facts data/s6/facts.parquet --stage S6eval_seed$S \
        --causal-only --chunk 100 ${e:+--run-dir $e}
    echo "[$(ts)] OK eval seed $S"
  fi
done
echo "[$(ts)] S6CPU TRAIN+EVAL DONE"
