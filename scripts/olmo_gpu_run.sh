#!/usr/bin/env bash
# One-session GPU run for prereg amendment 2 (configs/prereg_amendment_2026-11-20.yaml):
#   1. environment (venv + requirements-gpu.txt), GPU check
#   2. smoke: pytest on pythia-70m for the depth code (CLAUDE.md rule 4) + 5-fact pythia-70m pass
#   3. depth pass, 1300-fact G1 set x 3 templates: half_prob_depth (headline), causal_final,
#      logit lens; no tuned-lens training, no Patchscope/override/subject patching
#   4. primary test (stats/amend2.py test) on every depth parquet produced in this session
#   5. tarball of results/ + reports to copy back
#
# Usage on a rented A100 80GB (from the repo root, after `git clone` + `git checkout <branch>`):
#   bash scripts/olmo_gpu_run.sh
# Options (environment variables):
#   WITH_PYTHIA=1   also run pythia-1.4b and pythia-2.8b (the other two gate models; minutes on
#                   a GPU, about 26 h on the project's CPU box). Default 0.
#   DTYPE=float32   model weights dtype (amendment 2 fixes fp32; do not change for the gate run)
#   N_BOOT=1000     bootstrap resamples for the primary test
#   DRY=1           CPU dry run: MODEL (default EleutherAI/pythia-70m), N facts (default 20),
#                   uses the existing .venv, no GPU check, no tarball, output stage S3bdry
#   SKIP_ENV=1      reuse an existing .venv
set -euo pipefail
cd "$(dirname "$0")/.."
ROOT=$PWD
DRY=${DRY:-0}
WITH_PYTHIA=${WITH_PYTHIA:-0}
DTYPE=${DTYPE:-float32}
N_BOOT=${N_BOOT:-1000}
FACTS=data/facts_g1cpu.parquet
INPUTS=data/amend2_inputs.parquet
export HF_HOME=${HF_HOME:-$ROOT/cache/hf}
export PYTHONPATH=$ROOT/src
export TOKENIZERS_PARALLELISM=false
TS=$(date -u +%Y%m%dT%H%M%SZ)
mkdir -p results/logs
SLOG=results/logs/olmo_gpu_run_${TS}.log
say() { echo "[$(date -u +%FT%TZ)] $*" | tee -a "$SLOG"; }

say "start DRY=$DRY WITH_PYTHIA=$WITH_PYTHIA DTYPE=$DTYPE N_BOOT=$N_BOOT git=$(git rev-parse --short HEAD)"
for f in "$FACTS" "$INPUTS" configs/s3.yaml configs/prereg.yaml configs/prereg_amendment_2026-11-20.yaml; do
  [ -f "$f" ] || { say "FATAL missing $f"; exit 1; }
done

# ---------------------------------------------------------------- 1. environment
if [ "$DRY" = 1 ] || [ "${SKIP_ENV:-0}" = 1 ]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
else
  if command -v uv >/dev/null; then
    uv venv --python 3.12 .venv && source .venv/bin/activate
    uv pip install -r requirements-gpu.txt && uv pip install --no-deps -e .
  else
    python3 -c 'import sys; assert sys.version_info >= (3, 11), "need python >= 3.11 (or install uv)"'
    python3 -m venv .venv && source .venv/bin/activate
    pip install -q --upgrade pip && pip install -q -r requirements-gpu.txt && pip install -q --no-deps -e .
  fi
  nvidia-smi | tee -a "$SLOG"
  python - <<'EOF' | tee -a "$SLOG"
import torch
assert torch.cuda.is_available(), "no CUDA device visible to torch"
p = torch.cuda.get_device_properties(0)
print(f"cuda ok: {p.name}, {p.total_memory / 2**30:.1f} GiB, torch {torch.__version__}")
assert p.total_memory / 2**30 > 60, "OLMo-2-7B in fp32 needs ~30 GB weights; use an 80 GB card"
EOF
  df -h . | tee -a "$SLOG"
fi
python -c "import torch, transformers; print('torch', torch.__version__, 'transformers', transformers.__version__)" | tee -a "$SLOG"

# ---------------------------------------------------------------- 2. smoke on pythia-70m
say "pytest (pythia-70m) for the depth code"
if ! python -m pytest -q tests/test_depth.py -p no:cacheprovider \
    -k "half_prob or halfprob or identity or stable_rules or subject_last_pos or final_patch_last_layer or behavior_and_logit_lens" \
    > "$SLOG.pytest" 2>&1; then
  tail -n 20 "$SLOG.pytest" | tee -a "$SLOG"; say "FATAL pytest failed"; exit 1
fi
tail -n 1 "$SLOG.pytest" | tee -a "$SLOG"

STAGE=S3b
[ "$DRY" = 1 ] && STAGE=S3bdry
run_depth() {  # $1 model, $2 extra args
  local model=$1; shift
  local before after dir
  before=$(ls -d results/$STAGE/* 2>/dev/null | sort || true)
  say "depth pass $model $*"
  python -m depthlaw.depth.run_depth --model "$model" --facts "$FACTS" --templates 3 \
    --halfprob --no-tuned-lens --dtype "$DTYPE" --stage "$STAGE" "$@" 2>&1 \
    | { grep -vE "Loading weights|Fetching|it/s\]" || true; } | tee -a "$SLOG" | tail -n 2
  after=$(ls -d results/$STAGE/* | sort)
  dir=$(comm -13 <(echo "$before") <(echo "$after") | tail -n 1)
  [ -f "$dir/depth.parquet" ] || { say "FATAL no depth.parquet for $model"; exit 1; }
  DEPTHS+=("$dir/depth.parquet")
  say "done $model -> $dir"
}

DEPTHS=()
if [ "$DRY" = 1 ]; then
  run_depth "${MODEL:-EleutherAI/pythia-70m}" --n "${N:-20}" --chunk 5
else
  # smoke pass on pythia-70m (5 facts), separate stage so it never mixes with gate runs
  STAGE=S3bsmoke run_depth EleutherAI/pythia-70m --n 5 --chunk 5
  DEPTHS=()
  run_depth allenai/OLMo-2-1124-7B
  if [ "$WITH_PYTHIA" = 1 ]; then
    run_depth EleutherAI/pythia-1.4b
    run_depth EleutherAI/pythia-2.8b
  fi
fi

# ---------------------------------------------------------------- 4. primary test
say "primary test on ${DEPTHS[*]}"
if [ "$DRY" = 1 ]; then
  python -m depthlaw.stats.amend2 test --depth "${DEPTHS[@]}" --inputs "$INPUTS" --n-boot "${N_BOOT_DRY:-20}" \
    --dry-run --report reports/A2_PRIMARY_DRYRUN.md 2>&1 | tee -a "$SLOG"
else
  python -m depthlaw.stats.amend2 test --depth "${DEPTHS[@]}" --inputs "$INPUTS" --n-boot "$N_BOOT" \
    --report reports/A2_PRIMARY_gpu_${TS}.md 2>&1 | tee -a "$SLOG"
fi

# ---------------------------------------------------------------- 5. copy-back bundle
if [ "$DRY" != 1 ]; then
  OUT=depthlaw_gpu_results_${TS}.tar.gz
  tar czf "$OUT" results/S3b results/S3bsmoke results/A2 reports/A2_PRIMARY_gpu_${TS}.md "$SLOG"
  say "bundle: $ROOT/$OUT ($(du -h "$OUT" | cut -f1))"
  say "copy back, e.g.: scp <gpu-host>:$ROOT/$OUT . ; then in the repo: tar xzf $OUT"
fi
say "finished"
