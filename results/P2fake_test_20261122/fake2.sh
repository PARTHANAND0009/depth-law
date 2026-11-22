#!/usr/bin/env bash
set -euo pipefail
cd /home/user/depth-law
S=/tmp/claude-0/-home-user-depth-law/79d106ca-74b7-5e19-8ef3-6880f992c1ff/scratchpad
export MALLOC_ARENA_MAX=2 HF_ENABLE_PARALLEL_LOADING=false ARROW_DEFAULT_MEMORY_POOL=system TOKENIZERS_PARALLELISM=false OMP_NUM_THREADS=1 HF_HUB_OFFLINE=1 HF_HOME=/home/user/depth-law/cache/hf
rm -rf $S/fake2 && mkdir -p $S/fake2
nice -n 10 prlimit --as=1800000000 .venv/bin/python $S/fake2.py $S/fake2
nice -n 10 prlimit --as=1800000000 .venv/bin/python analysis/p2/p2_analysis.py $S/fake2/out \
  --runs EleutherAI/pythia-410m=$S/fake2/A EleutherAI/pythia-1.4b=$S/fake2/B --boot param --n-boot 20 --cores 3 --set correct
