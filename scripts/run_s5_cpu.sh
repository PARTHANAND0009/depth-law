#!/usr/bin/env bash
# S5 checkpoint dynamics on CPU (notes/s5_plan.md). causal_final only, 508 facts (data/facts_s5.parquet).
# Resumable; after a restart relaunch: nohup setsid bash scripts/run_s5_cpu.sh >> results/s5_cpu.out 2>&1 < /dev/null &
set -Eeuo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH=src HF_HOME=$PWD/cache/hf OMP_NUM_THREADS=4
PY=.venv/bin/python
ts() { date -u +%Y-%m-%dT%H:%M:%SZ; }
trap 'echo "[$(ts)] S5CPU FAILED at line $LINENO"' ERR
REVS="step1000 step2000 step4000 step8000 step16000 step32000 step64000 step96000 step128000"
for M in pythia-1.4b pythia-2.8b; do
  for R in $REVS; do
    d=$(ls -d results/S5/S5-${M}_${R}-* 2>/dev/null | head -1 || true)
    if [[ -n "$d" && -f "$d/depth.parquet" ]]; then echo "[$(ts)] SKIP $M $R ($d)"; continue; fi
    echo "[$(ts)] START $M $R ${d:+resume $d}"
    $PY -m depthlaw.depth.run_depth --model EleutherAI/$M --revision $R --facts data/facts_s5.parquet \
        --stage S5 --causal-only --chunk 25 ${d:+--run-dir $d}
    echo "[$(ts)] OK $M $R"
    $PY - "$M" "$R" <<'PYEOF'
import sys
from huggingface_hub import scan_cache_dir
m, r = sys.argv[1], sys.argv[2]
info = scan_cache_dir()
hs = [rev.commit_hash for repo in info.repos if repo.repo_id == f"EleutherAI/{m}"
      for rev in repo.revisions if r in rev.refs]
if hs:
    s = info.delete_revisions(*hs); print("freed", s.expected_freed_size_str); s.execute()
PYEOF
  done
done
echo "[$(ts)] S5CPU DONE"
