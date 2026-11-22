#!/usr/bin/env bash
# P2 GPU session driver (run_manifest.yaml; prereg P2). Run by the human on the rented GPU host, from the repo root.
#   BALANCE_INR=740 SYNC_DEST=user@host:/path/depth-law-sync bash scripts/p2_gpu_run.sh
# Default plan P2-B (human 2026-11-22): INR ~740 after the top-up, all five models. TOPUP=0 restricts to Qwen + Llama.
# Pilot gate: the first model's first PILOT_FACTS facts (whole chunks) run first with 3 carriers; the measured s/unit
# projects the whole session (run_manifest.yaml pilot_gate). If it exceeds the remaining budget: fallback 1 (2 carriers
# for everything that remains), then fallback 2 (drop Llama-3.1-8B); each with a pending deviation written first.
# Options: DRY=1 (CPU dry run on pythia-70m, 5 facts x 2 paraphrases; no budget timer),
#          SKIP_ENV=1 (reuse .venv), MODELS="..." (override the order; default from the prereg).
# Budget: minute_budget = floor(BALANCE_INR / 207.36 * 60) - 15, armed immediately as an auto-stop (shutdown).
# Before each model: remaining minutes are compared with its upper estimate (run_manifest.yaml); if it does not
# fit with 3 carriers, it runs with 2 carriers (fallback step 1); if that does not fit either, it is skipped
# (fallback step 2). Each fallback writes deviations_pending/D-P2-<n>.md (UTC time, reason) BEFORE the step; the
# human copies them into prereg/deviations/ and commits. After each model: checksums verified, then rsync to SYNC_DEST.
set -euo pipefail
cd "$(dirname "$0")/.."
ROOT=$PWD
DRY=${DRY:-0}; TOPUP=${TOPUP:-1}; BAL=${BALANCE_INR:-740}
TS=$(date -u +%Y%m%dT%H%M%SZ); DEVDIR=deviations_pending; [ "${DRY:-0}" = 1 ] && DEVDIR=results/P2dry/deviations_test
mkdir -p results/logs "$DEVDIR"
LOG=results/logs/p2_gpu_run_${TS}.log
say() { echo "[$(date -u +%FT%TZ)] $*" | tee -a "$LOG"; }
T0=$(date +%s)
elapsed_min() { echo $(( ($(date +%s) - T0) / 60 )); }
BUDGET=$(python3 -c "import math; print(math.floor($BAL / 207.36 * 60) - 15)")
say "start DRY=$DRY TOPUP=$TOPUP balance INR $BAL -> minute budget $BUDGET git=$(git rev-parse --short HEAD)"
[ -f prereg/P2_prompt_vs_fact.md ] || { [ "$DRY" = 1 ] && say "DRY: prereg/P2_prompt_vs_fact.md not installed (allowed in dry run)" || { say "FATAL: prereg/P2_prompt_vs_fact.md missing; freeze the prereg first"; exit 1; }; }
for f in materials/facts_v1.jsonl materials/paraphrases_v1.jsonl materials/carriers_v1.jsonl; do
  sha256sum "$f" | tee -a "$LOG"
done
if [ "$DRY" != 1 ]; then
  # auto-stop at the minute budget (the instance is billed per second until it stops)
  ( sleep $(( BUDGET * 60 )); echo "[$(date -u +%FT%TZ)] BUDGET REACHED ($BUDGET min): stopping" >> "$LOG"; touch STOP_P2; sync; sudo shutdown -h now || shutdown -h now ) &
  say "auto-stop armed: $BUDGET min (pid $!)"
fi
# ------------------------------------------------------------------ environment
if [ "$DRY" = 1 ] || [ "${SKIP_ENV:-0}" = 1 ]; then
  source .venv/bin/activate
else
  python3 -m venv .venv && source .venv/bin/activate
  pip install -q --upgrade pip && pip install -q -r requirements-gpu.txt && pip install -q --no-deps -e .
  nvidia-smi | tee -a "$LOG"
  python -c "import torch; assert torch.cuda.is_available(); p=torch.cuda.get_device_properties(0); print('cuda', p.name, round(p.total_memory/2**30,1), 'GiB')" | tee -a "$LOG"
  python -c "from huggingface_hub import hf_hub_download; hf_hub_download('meta-llama/Llama-3.1-8B','config.json'); print('HF Llama access ok')" | tee -a "$LOG" \
    || say "WARNING: no Llama-3.1-8B access; it will be skipped"
  df -h . | tee -a "$LOG"
fi
export PYTHONPATH=$ROOT/src HF_HOME=${HF_HOME:-$ROOT/cache/hf} TOKENIZERS_PARALLELISM=false
DEV=cuda; [ "$DRY" = 1 ] && DEV=cpu
python -m pytest -q -p no:cacheprovider tests/test_depth.py -k "identity or halfprob" > "$LOG.pytest" 2>&1 || { tail -5 "$LOG.pytest" | tee -a "$LOG"; say "FATAL pytest"; exit 1; }
say "pytest: $(tail -1 "$LOG.pytest")"
python -m depthlaw.p2.run_p2 --model EleutherAI/pythia-70m --n-facts 5 --n-templates 2 --stage P2smoke --device $DEV 2>&1 | grep -E "chunk|P2smoke" | tee -a "$LOG"
# ------------------------------------------------------------------ models (prereg order) and upper estimates (min, C3 / C2)
if [ -n "${MODELS:-}" ]; then ORDER=($MODELS)
elif [ "$DRY" = 1 ]; then ORDER=(EleutherAI/pythia-70m)
elif [ "$TOPUP" = 1 ]; then ORDER=(Qwen/Qwen3-8B meta-llama/Llama-3.1-8B EleutherAI/pythia-1.4b EleutherAI/pythia-2.8b allenai/OLMo-2-1124-7B)
else ORDER=(Qwen/Qwen3-8B meta-llama/Llama-3.1-8B); fi
declare -A UP3=( [Qwen/Qwen3-8B]=26.4 [meta-llama/Llama-3.1-8B]=25.9 [EleutherAI/pythia-1.4b]=4.9 [EleutherAI/pythia-2.8b]=9.4 [allenai/OLMo-2-1124-7B]=22.6 [EleutherAI/pythia-70m]=0 )
declare -A UP2=( [Qwen/Qwen3-8B]=19.7 [meta-llama/Llama-3.1-8B]=19.4 [EleutherAI/pythia-1.4b]=3.6 [EleutherAI/pythia-2.8b]=6.9 [allenai/OLMo-2-1124-7B]=16.2 [EleutherAI/pythia-70m]=0 )
NDEV=0
dev() {  # $1 step text, $2 reason; writes a pending deviation before the step
  NDEV=$((NDEV + 1))
  printf '# D-P2-%d (pending; copy to prereg/deviations/)\n- UTC: %s\n- Step: %s\n- Reason: %s\n' "$NDEV" "$(date -u +%FT%TZ)" "$1" "$2" > $DEVDIR/D-P2-$NDEV.md
  say "DEVIATION D-P2-$NDEV: $1 ($2)"
}
STAGE=P2; [ "$DRY" = 1 ] && STAGE=P2dry
CHUNK=10; PILOT_FACTS=20; EXTRA=""
[ "$DRY" = 1 ] && { CHUNK=2; PILOT_FACTS=2; EXTRA="--n-facts 5 --n-templates 2"; }
# ------------------------------------------------------------------ pilot gate (first model, whole chunks, 3 carriers)
M0=${ORDER[0]}; NC_ALL=3; PILOT_RD=""
say "pilot: $M0, first $PILOT_FACTS facts, 3 carriers"
PILOT_RD=$(python -m depthlaw.p2.run_p2 --model "$M0" --dtype float32 --device $DEV --chunk $CHUNK --stage $STAGE \
           --n-carriers 3 --n-facts $PILOT_FACTS $( [ "$DRY" = 1 ] && echo "--n-templates 2" ) 2>&1 | tee -a "$LOG" | tail -1)
[ -f "$PILOT_RD/log.jsonl" ] && grep -q '"chunk"' "$PILOT_RD/log.jsonl" || { say "FATAL: pilot produced no chunk ($PILOT_RD); stopping before any full run"; exit 1; }
REM=$(( BUDGET - $(elapsed_min) ))
read -r PROJ3 PROJ2 PROJ_NOLLAMA2 <<< "$(python - "$PILOT_RD" "$PILOT_FACTS" "$DRY" "${ORDER[*]}" <<'EOF'
import json, sys, pathlib
rd, nf, dry, order = pathlib.Path(sys.argv[1]), int(sys.argv[2]), sys.argv[3] == "1", sys.argv[4].split()
ev = [json.loads(l) for l in open(rd / "log.jsonl") if '"chunk"' in l]
units = nf * (2 if dry else 10)
q = ev[-1]["s"] / units                          # seconds per fact x paraphrase unit, 3 carriers, pilot model
rel = {"Qwen/Qwen3-8B": 1.0, "meta-llama/Llama-3.1-8B": (8.05 / 8.2) * (32 / 36), "allenai/OLMo-2-1124-7B": (7 / 8.2) * (32 / 36)}
rel["EleutherAI/pythia-2.8b"] = rel["allenai/OLMo-2-1124-7B"] * 0.162 / 0.319
rel["EleutherAI/pythia-1.4b"] = rel["allenai/OLMo-2-1124-7B"] * 0.081 / 0.319
load = {"Qwen/Qwen3-8B": 3.0, "meta-llama/Llama-3.1-8B": 3.0, "allenai/OLMo-2-1124-7B": 5.0, "EleutherAI/pythia-2.8b": 0.6, "EleutherAI/pythia-1.4b": 0.4}
units_all = 5 * 2 if dry else 3000
def proj(nc, models):
    tot = 0.0
    for i, m in enumerate(models):
        left = units_all - (units if i == 0 else 0)
        tot += q * rel.get(m, 1.0) * left * (1.0 if nc == 3 else 5 / 7) / 60 + (0 if i == 0 else load.get(m, 3.0))
    return tot + 1.0                              # teardown / copy-back
print(f"{proj(3, order):.1f} {proj(2, order):.1f} {proj(2, [m for m in order if 'Llama' not in m]):.1f}")
EOF
)"
[ -n "${PROJ_NOLLAMA2:-}" ] || { say "FATAL: pilot projection failed; stopping"; exit 1; }
say "pilot projection (min): all C3 $PROJ3, all C2 $PROJ2, C2 without Llama $PROJ_NOLLAMA2; remaining $REM"
if python3 -c "import sys; sys.exit(0 if $PROJ3 <= $REM else 1)"; then NC_ALL=3
elif python3 -c "import sys; sys.exit(0 if $PROJ2 <= $REM else 1)"; then
  NC_ALL=2; dev "fallback 1 after the pilot: all remaining units run with 2 carriers (carrier 2 dropped; its rows in the pilot chunks are excluded from the analysis so every fact has carriers 0-1)" "projected $PROJ3 min with 3 carriers > remaining $REM min"
else
  NC_ALL=2; dev "fallback 1 after the pilot: 2 carriers (pilot carrier-2 rows excluded from the analysis)" "projected $PROJ3 min > remaining $REM min"
  dev "fallback 2 after the pilot: Llama-3.1-8B not run" "projected $PROJ2 min with 2 carriers > remaining $REM min"
  ORDER=( $(for m in "${ORDER[@]}"; do [[ "$m" == *Llama* ]] || echo "$m"; done) )
fi
for M in "${ORDER[@]}"; do
  [ -e STOP_P2 ] && { say "STOP_P2 present: stopping"; break; }
  REM=$(( BUDGET - $(elapsed_min) ))
  NC=$NC_ALL
  if [ "$NC_ALL" = 3 ] && python3 -c "import sys; sys.exit(0 if ${UP3[$M]} <= $REM else 1)"; then NC=3
  elif [ "$NC_ALL" = 2 ] && python3 -c "import sys; sys.exit(0 if ${UP2[$M]} <= $REM else 1)"; then NC=2
  elif python3 -c "import sys; sys.exit(0 if ${UP2[$M]} <= $REM else 1)"; then
    NC=2; NDEV=$((NDEV + 1))
    printf '# D-P2-%d (pending; copy to prereg/deviations/)\n- UTC: %s\n- Step: fallback 1, model %s runs with 2 carriers (carrier 2 dropped).\n- Reason: remaining %s min < upper estimate %s min for 3 carriers.\n' "$NDEV" "$(date -u +%FT%TZ)" "$M" "$REM" "${UP3[$M]}" > $DEVDIR/D-P2-$NDEV.md
    say "FALLBACK 1: $M with 2 carriers (remaining $REM min) -> $DEVDIR/D-P2-$NDEV.md"
  else
    NDEV=$((NDEV + 1))
    printf '# D-P2-%d (pending; copy to prereg/deviations/)\n- UTC: %s\n- Step: fallback 2, model %s not run.\n- Reason: remaining %s min < upper estimate %s min even with 2 carriers.\n' "$NDEV" "$(date -u +%FT%TZ)" "$M" "$REM" "${UP2[$M]}" > $DEVDIR/D-P2-$NDEV.md
    say "FALLBACK 2: $M skipped (remaining $REM min) -> $DEVDIR/D-P2-$NDEV.md"; continue
  fi
  say "model $M carriers $NC (remaining $REM min)"
  RDARG=""; [ "$M" = "$M0" ] && [ -n "$PILOT_RD" ] && RDARG="--run-dir $PILOT_RD"   # resume the pilot's run dir
  RD=$(python -m depthlaw.p2.run_p2 --model "$M" --dtype float32 --device $DEV --chunk $CHUNK --stage $STAGE --n-carriers $NC $EXTRA $RDARG 2>&1 \
       | tee -a "$LOG" | tail -1)
  [ -f "$RD/manifest.json" ] || { say "FATAL: no manifest for $M"; continue; }
  python - "$RD" <<'EOF' | tee -a "$LOG"
import json, sys, pathlib, glob, pandas as pd
rd = pathlib.Path(sys.argv[1]); m = json.load(open(rd / "manifest.json"))
long = pd.concat(pd.read_parquet(p) for p in sorted(glob.glob(str(rd / "chunks/c*.parquet"))))
beh = pd.concat(pd.read_parquet(p) for p in sorted(glob.glob(str(rd / "chunks/b*.parquet"))))
print(f"done-check {rd.name}: checksums_ok={all(v['ok'] for v in m.values())} behaviour_rows={len(beh)} long_rows={len(long)} nan_p={int(long.p_object.isna().sum())}")
EOF
  if [ -n "${SYNC_DEST:-}" ]; then rsync -a "$RD/" "$SYNC_DEST/$(basename "$RD")/" && say "synced $RD -> $SYNC_DEST"; else say "SYNC_DEST not set: copy $RD manually"; fi
done
say "finished after $(elapsed_min) min of $BUDGET; deviations pending: $NDEV"
