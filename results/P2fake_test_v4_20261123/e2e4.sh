#!/usr/bin/env bash
set -euo pipefail
cd /home/user/depth-law
S=/tmp/claude-0/-home-user-depth-law/79d106ca-74b7-5e19-8ef3-6880f992c1ff/scratchpad
export MALLOC_ARENA_MAX=2 HF_ENABLE_PARALLEL_LOADING=false ARROW_DEFAULT_MEMORY_POOL=system TOKENIZERS_PARALLELISM=false OMP_NUM_THREADS=1 HF_HUB_OFFLINE=1 HF_HOME=/home/user/depth-law/cache/hf
echo "== MoM carrier-level test (raw-component diff)"
nice -n 10 prlimit --as=1800000000 .venv/bin/python analysis/p2/p2_test_mom.py reps=20 || true  # already passed at 200 in this batch (tests v4 run 1)
echo "== end-to-end"
rm -rf $S/e2e4 && mkdir -p $S/e2e4
nice -n 10 prlimit --as=1800000000 .venv/bin/python analysis/p2/p2_test_e2e.py $S/e2e4 n_boot=20 n_perm=20 cores=1
