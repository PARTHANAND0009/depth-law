#!/usr/bin/env bash
set -uo pipefail
cd /home/ubuntu/depth-law; . .venv/bin/activate
export PYTHONPATH=$PWD/src HF_HOME=$PWD/cache/hf TOKENIZERS_PARALLELISM=false
for m in EleutherAI/pythia-1.4b EleutherAI/pythia-2.8b; do
  echo "[$(date -u +%FT%TZ)] start $m"
  python -m depthlaw.depth.run_depth --model $m --facts data/facts_g1cpu.parquet --templates 3 \
    --halfprob --no-tuned-lens --dtype float32 --stage S3b || echo "[$(date -u +%FT%TZ)] FAIL $m"
  echo "[$(date -u +%FT%TZ)] end $m"
done
D=$(ls results/S3b/*/depth.parquet)
echo "[$(date -u +%FT%TZ)] primary test on $D"
TS=$(date -u +%Y%m%dT%H%M%SZ)
python -m depthlaw.stats.amend2 test --depth $D --inputs data/amend2_inputs.parquet --n-boot 1000 \
  --report reports/A2_PRIMARY_gpu_${TS}.md 2>&1 | grep -v RuntimeWarning | grep -v 'np.sqrt'
echo "[$(date -u +%FT%TZ)] CHAIN DONE"
