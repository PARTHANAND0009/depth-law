#!/usr/bin/env bash
# S6 CPU chain (notes/s6_plan.md): per seed build stream, train, evaluate causal depth, learnability.
# Design (data dir, run tag) comes from configs/s6.yaml train.design. Resumable:
#   SEEDS="1" nohup setsid bash scripts/run_s6_cpu.sh >> results/s6_cpu.out 2>&1 < /dev/null &
set -Eeuo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH=src HF_HOME=$PWD/cache/hf OMP_NUM_THREADS=2
PY=.venv/bin/python
ts() { date -u +%Y-%m-%dT%H:%M:%SZ; }
trap 'echo "[$(ts)] S6CPU FAILED at line $LINENO"' ERR
TOK=$($PY -c "import yaml;print(yaml.safe_load(open('configs/s6.yaml'))['train']['tokens'])")
DES=$($PY -c "import yaml;print(yaml.safe_load(open('configs/s6.yaml'))['train'].get('design') or '')")
SEEDS=${SEEDS:-1 2 3}
echo "[$(ts)] S6CPU design=${DES:-v1} tokens=$TOK seeds=$SEEDS"
for S in $SEEDS; do
  DD=data/s6/${DES:+$DES/}seed$S
  TAG=s6lm_${DES:+${DES}_}seed$S
  ES=S6eval_${DES:+${DES}_}seed$S
  if ! $PY -c "import json,sys;sys.exit(0 if json.load(open('$DD/meta.json'))['target_tokens']==$TOK else 1)" 2>/dev/null; then
    echo "[$(ts)] START mix seed $S ($TOK tokens)"; $PY -m depthlaw.pretrain.mix --seed $S --tokens $TOK ${DES:+--design $DES}; echo "[$(ts)] OK mix seed $S"
  fi
  r=$(ls -d results/S6/S6-${TAG}-* 2>/dev/null | head -1 || true)
  if [[ -n "$r" && -d "$r/final" ]]; then echo "[$(ts)] SKIP train seed $S ($r)"
  else
    echo "[$(ts)] START train seed $S ${r:+resume $r}"
    $PY -m depthlaw.pretrain.train --seed $S --threads 2 ${r:+--run-dir $r}
    r=$(ls -d results/S6/S6-${TAG}-* | head -1); echo "[$(ts)] OK train seed $S"
  fi
  e=$(ls -d results/$ES/$ES-final-* 2>/dev/null | head -1 || true)
  if [[ -n "$e" && -f "$e/depth.parquet" ]]; then echo "[$(ts)] SKIP eval seed $S ($e)"
  else
    echo "[$(ts)] START eval seed $S"
    $PY -m depthlaw.depth.run_depth --model "$r/final" --facts data/s6/facts.parquet --stage $ES \
        --causal-only --chunk 100 ${e:+--run-dir $e}
    echo "[$(ts)] OK eval seed $S"
  fi
  echo "[$(ts)] START learnability seed $S"; $PY -m depthlaw.pretrain.learnability --model "$r/final" --threads 2 > /dev/null; echo "[$(ts)] OK learnability seed $S"
done
echo "[$(ts)] S6CPU TRAIN+EVAL DONE (seeds $SEEDS)"
