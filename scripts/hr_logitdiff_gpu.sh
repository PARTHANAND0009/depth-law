#!/usr/bin/env bash
# PENDING GPU job (prereg/HR_revised.md B1): secondary outcome logitdiff_onset for the 3 gate models,
# 1300 G1 facts x 3 templates, fp32. NOT RUN. Same environment as scripts/olmo_gpu_run.sh
# (requirements-gpu.txt). Estimated cost: one more patched pass per model (about the S3b pass time:
# OLMo-2 ~21 min, pythia-2.8b ~11 min, pythia-1.4b ~6 min on the 2026-11-21 GPU).
# Usage (repo root, on the GPU host): bash scripts/hr_logitdiff_gpu.sh ; then copy results/HRld back.
set -euo pipefail
cd "$(dirname "$0")/.."
source .venv/bin/activate
export PYTHONPATH=$PWD/src HF_HOME=${HF_HOME:-$PWD/cache/hf} TOKENIZERS_PARALLELISM=false
python -c "import torch; assert torch.cuda.is_available(), 'needs a CUDA GPU'"
for m in EleutherAI/pythia-1.4b EleutherAI/pythia-2.8b allenai/OLMo-2-1124-7B; do
  echo "[$(date -u +%FT%TZ)] logitdiff $m"
  python -m depthlaw.hr.logitdiff --model "$m" --dtype float32
done
tar czf hr_logitdiff_$(date -u +%Y%m%dT%H%M%SZ).tar.gz results/HRld
echo "[$(date -u +%FT%TZ)] done"
