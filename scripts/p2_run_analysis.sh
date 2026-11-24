#!/usr/bin/env bash
# P2 analysis, exactly as preregistered (prereg/P2_prompt_vs_fact.md section 7, run order). Not frozen code: it only calls
# the frozen analysis/p2/p2_analysis.py, once per set, each call through scripts/log_run.py. Sequential; skips a set whose
# p2_decision.json already exists (resume after a restart).
#   nohup setsid bash scripts/p2_run_analysis.sh >> results/P2analysis/run.out 2>&1 < /dev/null &
set -u
cd "$(dirname "$0")/.."
export MALLOC_ARENA_MAX=2 HF_ENABLE_PARALLEL_LOADING=false ARROW_DEFAULT_MEMORY_POOL=system TOKENIZERS_PARALLELISM=false \
       OMP_NUM_THREADS=1 HF_HUB_OFFLINE=1 HF_HOME=$PWD/cache/hf
OUT=results/P2analysis; mkdir -p "$OUT"
RUNS=(
  "Qwen/Qwen3-8B=results/P2/P2-Qwen3-8B-ff119ca-20261124T163001Z"
  "meta-llama/Llama-3.1-8B=results/P2/P2-Llama-3.1-8B-ff119ca-20261124T164743Z"
  "EleutherAI/pythia-1.4b=results/P2/P2-pythia-1.4b-ff119ca-20261124T170401Z"
  "EleutherAI/pythia-2.8b=results/P2/P2-pythia-2.8b-ff119ca-20261124T170739Z"
  "allenai/OLMo-2-1124-7B=results/P2/P2-OLMo-2-1124-7B-ff119ca-20261124T171447Z"
)
INS=(); for r in "${RUNS[@]}"; do INS+=(--in "${r#*=}/manifest.json"); done
run_set() {  # $1 set, $2 status, $3 extra args
  local s=$1 st=$2; shift 2
  [ -f "$OUT/$s/p2_decision.json" ] && { echo "[$(date -u +%FT%TZ)] skip $s (done)"; return 0; }
  local tag="P2 analysis: set $s"; [ "$st" = EXPLORATORY ] && tag="EXPLORATORY P2 analysis: set $s (H4)"
  echo "[$(date -u +%FT%TZ)] start $s"
  python3 scripts/log_run.py --tag "$tag" --seed 20261121 --status "$st" "${INS[@]}" --in analysis/p2/p2_analysis.py \
    --out "$OUT/$s/p2_results.json" --out "$OUT/$s/p2_decision.json" -- \
    /usr/bin/time -v -o "$OUT/$s.time" nice -n 10 prlimit --as=1800000000 .venv/bin/python analysis/p2/p2_analysis.py "$OUT/$s" \
    --runs "${RUNS[@]}" --set "$s" --n-boot 1000 --n-perm 1000 --cores 4 "$@"
  local rc=$?   # captured before the date substitution, which would reset $? (G2 stats-reviewer 12b)
  echo "[$(date -u +%FT%TZ)] end $s exit $rc"
}
run_set correct CONFIRMATORY
[ -f "$OUT/correct/p2_results.json" ] || { echo "confirmatory call produced no p2_results.json; stopping"; exit 1; }
for s in new226 all all10 nomanufacturer tcov lofo; do run_set "$s" CONFIRMATORY --primary "$OUT/correct"; done
run_set h4 EXPLORATORY --primary "$OUT/correct"
echo "[$(date -u +%FT%TZ)] ALL DONE"
