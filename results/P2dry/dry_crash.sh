#!/usr/bin/env bash
# Dry run: pythia-70m, then a model that cannot load (crash path, second model without --run-dir), with a local SYNC_DEST.
cd /home/user/depth-law
S=/tmp/claude-0/-home-user-depth-law/79d106ca-74b7-5e19-8ef3-6880f992c1ff/scratchpad
rm -rf $S/syncdest
export MALLOC_ARENA_MAX=2 HF_ENABLE_PARALLEL_LOADING=false ARROW_DEFAULT_MEMORY_POOL=system TOKENIZERS_PARALLELISM=false OMP_NUM_THREADS=1 HF_HUB_OFFLINE=1 DRY=1
export MODELS="EleutherAI/pythia-70m EleutherAI/pythia-nonexistent-test-model" SYNC_DEST=$S/syncdest/nested
exec nice -n 10 prlimit --as=1800000000 bash scripts/p2_gpu_run.sh
