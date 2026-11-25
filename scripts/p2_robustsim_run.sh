#!/usr/bin/env bash
# P2 robustness simulation (analysis/p2/robustsim_plan.md), then the S5 relaunch under the human's standing
# authorization (exact command; only once no other heavy job runs). Resumable: finished simulations are skipped.
#   nohup setsid bash scripts/p2_robustsim_run.sh >> results/P2robust/run.out 2>&1 < /dev/null &
set -u
cd "$(dirname "$0")/.."
export MALLOC_ARENA_MAX=2 TOKENIZERS_PARALLELISM=false OMP_NUM_THREADS=1 HF_HUB_OFFLINE=1
OUT=results/P2robust; mkdir -p "$OUT"
echo "[$(date -u +%FT%TZ)] start robustness simulation"
python3 scripts/log_run.py --tag "P2 non-selecting robustness simulation (prereg section 4)" --seed 20261125 \
  --status CONFIRMATORY --in analysis/p2/p2_robustsim.R --in analysis/p2/p2_model.R --in analysis/p2/robustsim_plan.md \
  --in materials/facts_v1.jsonl --out "$OUT/p2_robustsim.json" -- \
  /usr/bin/time -v -o "$OUT/p2_robustsim.time" nice -n 10 prlimit --as=1800000000 \
  Rscript analysis/p2/p2_robustsim.R "$OUT/p2_robustsim.json" n_sim=100 n_boot=300 cores=4 seed=20261125
rc=$?
echo "[$(date -u +%FT%TZ)] end robustness simulation exit $rc"
if [ -f "$OUT/p2_robustsim.json" ] && ! pgrep -f run_s5_cpu.sh > /dev/null; then
  nohup setsid bash scripts/run_s5_cpu.sh >> results/s5_cpu.out 2>&1 < /dev/null &
  python3 scripts/log_run.py --kind NOTE --tag "S5 relaunch (HUMAN STANDING AUTHORIZATION; after the P2 robustness simulation)" \
    --status ADMIN --note "S5 was found dead after the container restart of 2026-11-25 ~07:55 UTC. Held until the P2 robustness simulation finished (one heavy job at a time; P2 has priority, human 2026-11-25). Relaunched by scripts/p2_robustsim_run.sh at $(date -u +%FT%TZ) with exactly: nohup setsid bash scripts/run_s5_cpu.sh >> results/s5_cpu.out 2>&1 < /dev/null &"
  echo "[$(date -u +%FT%TZ)] S5 relaunched"
fi
