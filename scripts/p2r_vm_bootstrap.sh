#!/usr/bin/env bash
# P2R GPU session: one-shot VM bootstrap. NOT frozen. It runs the frozen steps of reports/p2r/GPU_RUNBOOK_P2R.md
# (3 hard stop, 6 run checkout at tag prereg-P2R, 7 sync clone, 8 environment + weights provenance + attention check,
# 8b patching tests, 9 sync loop, 10 budget + driver, 11 copy-back, 12 verification) in one go, with the frozen code at
# the tag. Its differences from the runbook text are listed in reports/pending_frozen_changes/P2R/D-P2R-bootstrap.md,
# which it pushes with the session values before any weights are downloaded. First session only (branch p2r-gpu-session).
#
# On the fresh VM, inside tmux (reports/p2r/VM_QUICKSTART.md):
#   read -rsp 'GitHub token: ' GH_TOKEN; echo; read -rsp 'HF token: ' HF_TOKEN; echo; export GH_TOKEN HF_TOKEN
#   export BALANCE=<INR balance just before the instance started> HOURLY=<INR per hour, GPU plus storage>
#   bash p2r_vm_bootstrap.sh
# Tokens: never printed, never in a URL, never written to disk. git gets them from a credential helper that reads
# $GH_TOKEN from the environment; huggingface_hub reads $HF_TOKEN itself. Do not run this script with `bash -x`.
# Log: ~/p2r_logs/bootstrap_<UTC>.log (also pushed as p2_syncdest/_p2r_preflight/bootstrap.log).
# Every failed check stops the script with "FATAL: <reason>" and a final box saying what to do.
# Options (env): PRESTART_MIN (default 5: minutes billed before this script started), ALLOW_SHORT=1 (skip the
# minimum-balance refusal; not recommended). Test only: DRYRUN=1 (tests/p2r_bootstrap_dry/run_dry.sh: CPU, local
# bare repo REPO_URL, stub sudo/shutdown/nvidia-smi, pythia-70m in place of the P2R models, configs/tokenizers only).
set -Eeuo pipefail
umask 022
export GIT_TERMINAL_PROMPT=0 HF_HUB_DISABLE_PROGRESS_BARS=1 PYTHONUNBUFFERED=1

REPO_URL=${REPO_URL:-https://github.com/PARTHANAND0009/depth-law.git}
TAG=prereg-P2R
TAG_SHA=005767724aa9012d1483c41ee122a715a6566cea
AMEND=prereg/amendments/A_P2R_new_families
AMEND_SHA=9d97d157dbf374f36519642dce2debe3ad6796b374413a20856ee58b32cbc6a1
BRANCH=p2r-gpu-session
CAP_INR=700; DRIVER_RATE=207.36; MARGIN_MIN=10
PRESTART_MIN=${PRESTART_MIN:-5}; MIN_SESSION_MIN=${MIN_SESSION_MIN:-112}; MIN_FREE_GB=${MIN_FREE_GB:-70}
DRYRUN=${DRYRUN:-0}
P2R_MODELS="google/gemma-2-9b mistralai/Mistral-7B-v0.1"   # frozen order (amendment section 3)
TEST_MODELS=$P2R_MODELS; ONLY=""
if [ "$DRYRUN" = 1 ]; then TEST_MODELS=${DRY_TEST_MODELS:-EleutherAI/pythia-70m}; ONLY=--only-present; fi
RUN=$HOME/depth-law; SYNC=$HOME/depth-law-sync; P=$SYNC/p2_syncdest/_p2r_preflight; V=$HOME/p2r_verify
LOGDIR=$HOME/p2r_logs; TS=$(date -u +%Y%m%dT%H%M%SZ); LOG=$LOGDIR/bootstrap_$TS.log
mkdir -p "$LOGDIR"
exec > >(tee -a "$LOG") 2>&1
T0=$(date +%s); STAGE=early; SYNC_PID=""; DL_PID=""
SELF_SHA=$(sha256sum "$0" | cut -c1-64)

now() { date -u +%FT%TZ; }
el() { local s=$(( $(date +%s) - T0 )); printf '%dm%02ds' $((s / 60)) $((s % 60)); }
step() { echo; echo "[$(now)] [+$(el)] ===== STEP $*"; }
info() { echo "[$(now)] [+$(el)]   $*"; }
save_log() { if [ -d "$P" ]; then cp "$LOG" "$P/bootstrap.log" 2>/dev/null || true; fi; }
stop_bg() {
  if [ -n "$DL_PID" ]; then kill "$DL_PID" 2>/dev/null || true; DL_PID=""; fi
  if [ -n "$SYNC_PID" ]; then kill -TERM -- "-$SYNC_PID" 2>/dev/null || true; SYNC_PID=""; sleep 1; fi
}
final_push() {  # best effort: one more copy of the session files to the sync branch (at most ~2 min)
  [ -d "$SYNC/.git" ] || return 0
  stop_bg; save_log
  ( cd "$SYNC" && ONCE=1 timeout 120 bash scripts/p2_push_loop.sh "$RUN" "$SYNC" "$BRANCH" ) || true
}
banner() { echo; echo "####################################################################"; for l in "$@"; do echo "## $l"; done
           echo "####################################################################"; }
die() {
  trap - ERR
  echo "[$(now)] [+$(el)] FATAL: $*"
  if [ "$STAGE" = early ]; then
    banner "FATAL: $*" "Nothing of the P2R protocol has run on this VM." \
           "SAFE TO DESTROY THE VM: YES (nothing to copy). Send Claude a screenshot of this box."
  else
    final_push
    banner "FATAL: $*" "PAUSE the instance now in the dashboard (Pause keeps the disk). Do NOT destroy." \
           "SAFE TO DESTROY THE VM: NO. Send Claude a screenshot of this box." \
           "Log: $LOG (pushed to branch $BRANCH if the push worked)."
  fi
  sleep 1; exit 1
}
trap 'die "unexpected error at line $LINENO (exit $?)"' ERR
pyok() { "$1" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)' 2>/dev/null; }
GITCRED='!f() { test "$1" = get || exit 0; echo username=x-access-token; echo "password=${GH_TOKEN}"; }; f'
g() { git -c credential.helper= -c "credential.helper=$GITCRED" "$@"; }
setcred() { git -C "$1" config credential.helper ""; git -C "$1" config --add credential.helper "$GITCRED"; }
remote_tag() {  # commit the tag on origin points to ("" if absent); peeled for an annotated tag
  local out; out=$(g ls-remote origin "refs/tags/$TAG" "refs/tags/$TAG^{}" 2>/dev/null || true)
  if [[ "$out" == *'^{}'* ]]; then awk '/\^\{\}$/ {print $1}' <<< "$out"; else awk 'NR == 1 {print $1}' <<< "$out"; fi
}

# ---------------------------------------------------------------------------------------------------------------
step "0/14 inputs and budget"
info "bootstrap sha256 $SELF_SHA; DRYRUN=$DRYRUN; log $LOG"
[ -n "${GH_TOKEN:-}" ] || die "GH_TOKEN is not set (read -rsp 'GitHub token: ' GH_TOKEN; export GH_TOKEN)"
[ -n "${HF_TOKEN:-}" ] || die "HF_TOKEN is not set (read -rsp 'HF token: ' HF_TOKEN; export HF_TOKEN)"
[[ "${BALANCE:-}" =~ ^[0-9]+([.][0-9]+)?$ ]] || die "BALANCE must be a number in INR (export BALANCE=...), got '${BALANCE:-}'"
[[ "${HOURLY:-}" =~ ^[0-9]+([.][0-9]+)?$ ]] || die "HOURLY must be a number in INR per hour (export HOURLY=...), got '${HOURLY:-}'"
python3 -c "import sys; sys.exit(0 if $HOURLY >= $DRIVER_RATE else 1)" || die "HOURLY=$HOURLY is below the GPU rate $DRIVER_RATE; enter GPU plus storage"
read -r BASE TOTAL_MIN HARD_MIN <<< "$(python3 -c "import math; b = min($BALANCE, $CAP_INR); t = math.floor(b / $HOURLY * 60); print(b, t, t - $PRESTART_MIN - 5)")"
info "BALANCE INR $BALANCE (session cap INR $CAP_INR -> base INR $BASE) at INR $HOURLY/h: $TOTAL_MIN min affordable, of which $PRESTART_MIN are counted as billed before this script"
if [ "$TOTAL_MIN" -lt "$MIN_SESSION_MIN" ] && [ "${ALLOW_SHORT:-0}" != 1 ]; then
  die "INR $BASE buys only $TOTAL_MIN min; the full design needs at least $MIN_SESSION_MIN min (about INR $(python3 -c "print(round($MIN_SESSION_MIN * $HOURLY / 60))") at INR $HOURLY/h, results/P2R/budget_estimate_EXPLORATORY.json). Top up first."
fi

step "1/14 instance hard stop (runbook step 3)"
if [ "$DRYRUN" = 1 ]; then
  s=$(command -v shutdown || true)
  case "$s" in ""|/sbin/*|/usr/sbin/*|/bin/*|/usr/bin/*) die "DRYRUN needs the stub shutdown first on PATH (found '$s')";; esac
fi
echo "$HOURLY" > "$HOME/p2r_rate.txt"
[ "$HARD_MIN" -gt 0 ] || die "hard-stop minutes $HARD_MIN <= 0"
sudo -n shutdown -h +"$HARD_MIN" || die "could not arm the OS shutdown timer (sudo shutdown -h +$HARD_MIN)"
date -u +%FT%TZ | tee "$HOME/p2r_session_start_utc.txt" > /dev/null
info "hard stop armed: OS shutdown in $HARD_MIN min (affordable $TOTAL_MIN - prestart $PRESTART_MIN - 5). Whether an OS shutdown stops billing is not known: check the dashboard when it fires."

step "2/14 GPU and NVIDIA driver"
command -v nvidia-smi > /dev/null || die "nvidia-smi not found: this is not a GPU instance"
q=$(nvidia-smi --query-gpu=name,driver_version --format=csv,noheader | awk 'NR == 1')
GPU=$(echo "${q%,*}" | sed 's/ *$//'); DRV=$(echo "${q##*,}" | tr -d ' ')
info "GPU '$GPU', driver $DRV"
[[ "$GPU" == *"RTX PRO 6000"* ]] || die "GPU is '$GPU', not an RTX PRO 6000 (amendment section 4: same GPU type as P2; do not substitute)"
[[ "${DRV%%.*}" =~ ^[0-9]+$ ]] && [ "${DRV%%.*}" -ge 580 ] || die "NVIDIA driver $DRV < 580 (the pinned torch 2.15.0 CUDA 13.2 wheel needs >= 580)"

step "3/14 packages and Python >= 3.11 (P2 runbook step 4)"
need=()
for c in git rsync tmux; do command -v "$c" > /dev/null || need+=("$c"); done
if ! pyok python3; then
  info "$(python3 --version 2>&1) < 3.11: installing Python 3.12 (deadsnakes), as in the P2 runbook"
  sudo -n apt-get update -q && sudo -n env DEBIAN_FRONTEND=noninteractive apt-get install -y -q software-properties-common \
    && sudo -n add-apt-repository -y ppa:deadsnakes/ppa && sudo -n apt-get update -q \
    && sudo -n env DEBIAN_FRONTEND=noninteractive apt-get install -y -q python3.12 python3.12-venv "${need[@]}" \
    || die "installing Python 3.12 failed"
  need=()
  mkdir -p "$HOME/bin" && ln -sf "$(command -v python3.12)" "$HOME/bin/python3"
  grep -q 'HOME/bin:' "$HOME/.bashrc" 2>/dev/null || echo 'export PATH=$HOME/bin:$PATH' >> "$HOME/.bashrc"
  export PATH=$HOME/bin:$PATH; hash -r
fi
python3 -c 'import ensurepip, venv' 2> /dev/null || need+=(python3-venv)
if [ "${#need[@]}" -gt 0 ]; then
  info "apt-get install ${need[*]}"
  sudo -n apt-get update -q && sudo -n env DEBIAN_FRONTEND=noninteractive apt-get install -y -q "${need[@]}" || die "apt-get install ${need[*]} failed"
fi
pyok python3 || die "Python >= 3.11 not available ($(python3 --version 2>&1))"
python3 -c 'import ensurepip, venv' || die "python3 venv/ensurepip missing"
RSV=$(rsync --version 2> /dev/null | awk 'NR == 1 {print $3}')
python3 -c "import sys; v = tuple(int(x) for x in '$RSV'.split('.')[:3]); sys.exit(0 if v >= (3, 2, 3) else 1)" || die "rsync $RSV < 3.2.3 (the driver needs --mkpath)"
info "$(python3 --version), git $(git --version | awk '{print $3}'), rsync $RSV"

step "4/14 disk"
FREE_GB=$(df -Pk "$HOME" | awk 'NR == 2 {print int($4 / 1048576)}')
info "free disk under $HOME: $FREE_GB GB"
[ "$FREE_GB" -ge "$MIN_FREE_GB" ] || die "only $FREE_GB GB free; need >= $MIN_FREE_GB GB (weights 51.5 GB + environment + clones; rent >= 100 GB)"
[ ! -e "$RUN" ] && [ ! -e "$SYNC" ] || die "$RUN or $SYNC already exists: run this once, on a fresh VM"

step "5/14 run checkout, tag $TAG, frozen hashes (runbook step 6)"
g clone -q "$REPO_URL" "$RUN" || die "git clone failed"
setcred "$RUN"; cd "$RUN"
g fetch -q --tags origin || die "git fetch --tags failed"
git cat-file -e "$TAG_SHA^{commit}" 2> /dev/null || die "commit $TAG_SHA is not in the repository"
STAGE=session
R=$(remote_tag)
if [ -z "$R" ]; then
  git rev-parse -q --verify "refs/tags/$TAG" > /dev/null && die "a local $TAG exists but origin has none"
  git tag "$TAG" "$TAG_SHA"
  g push -q origin "refs/tags/$TAG" || die "pushing tag $TAG failed (the GitHub token needs Contents: read and write)"
  info "tag $TAG created at $TAG_SHA and pushed"
elif [ "$R" != "$TAG_SHA" ]; then
  die "origin's $TAG points to $R, not $TAG_SHA (do not continue; tell Claude)"
else
  info "tag $TAG already on origin at $TAG_SHA"
fi
[ "$(remote_tag)" = "$TAG_SHA" ] || die "tag $TAG on origin is not $TAG_SHA after the push"
[ "$(git rev-parse "$TAG^{commit}")" = "$TAG_SHA" ] || die "local $TAG is not $TAG_SHA"
git checkout -q --detach "$TAG"
[ "$(git rev-parse HEAD)" = "$TAG_SHA" ] || die "checkout is not at $TAG_SHA"
H=$(sha256sum "$AMEND.md" | cut -c1-64)
[ "$H" = "$AMEND_SHA" ] || die "amendment sha256 $H != $AMEND_SHA"
info "amendment sha256 $H OK"
sha256sum -c "$AMEND.sha256" || die "sha256sum -c $AMEND.sha256: FILES CHANGED"
sha256sum -c prereg/HASH_P2.txt || die "sha256sum -c prereg/HASH_P2.txt: FILES CHANGED"
[ -z "$(git status --porcelain)" ] || die "run checkout is not clean"
info "tag verified on origin and locally; all frozen hashes OK"

step "6/14 sync clone, branch $BRANCH, pre-session deviation note (runbook step 7)"
if g ls-remote --exit-code --heads origin "$BRANCH" > /dev/null 2>&1; then
  die "branch $BRANCH already exists on origin: a P2R session already ran (a second session follows runbook section E). Tell Claude."
fi
g clone -q "$REPO_URL" "$SYNC" || die "git clone (sync) failed"
setcred "$SYNC"
git -C "$SYNC" checkout -q -b "$BRANCH"
git -C "$SYNC" config user.name "p2r-gpu-vm"; git -C "$SYNC" config user.email "p2r-gpu-vm@localhost"
mkdir -p "$P"
D=$SYNC/reports/pending_frozen_changes/P2R/D-P2R-bootstrap.md
[ -f "$D" ] || die "deviation draft $D missing on master"
{ cat "$D"
  echo "- Session UTC (bootstrap start): $TS"
  echo "- Bootstrap sha256: $SELF_SHA; master at $(git -C "$SYNC" rev-parse --short HEAD); run checkout $TAG = $TAG_SHA"
  echo "- BALANCE INR $BALANCE, HOURLY INR $HOURLY, base INR $BASE, affordable $TOTAL_MIN min, PRESTART_MIN $PRESTART_MIN, hard stop +$HARD_MIN min"
  echo "- GPU $GPU, driver $DRV, $(python3 --version), free disk $FREE_GB GB"
  echo "- Written: $(now) (before any model weights were downloaded)"; } > "$P/D-P2R-$TS-bootstrap.md"
info "wrote $P/D-P2R-$TS-bootstrap.md"
save_log

step "7/14 download environment, Hugging Face access, check-hub (runbook step 8, first part)"
python3 -m venv "$HOME/p2r_dlenv" && "$HOME/p2r_dlenv/bin/pip" install -q --upgrade pip && "$HOME/p2r_dlenv/bin/pip" install -q "huggingface_hub==2.4.0" \
  || die "could not build the download environment"
DLPY=$HOME/p2r_dlenv/bin/python
export HF_HOME=$RUN/cache/hf
# shellcheck disable=SC2086
"$DLPY" - $P2R_MODELS <<'EOF' || die "Hugging Face token or model access check failed (see the lines above)"
import sys
from huggingface_hub import HfApi, auth_check
from huggingface_hub.errors import GatedRepoError
try:
    HfApi().whoami()
    print("HF token: valid")
except Exception as e:
    print(f"FATAL: the HF token is not valid ({type(e).__name__})"); sys.exit(1)
bad = 0
for m in sys.argv[1:]:
    try:
        auth_check(m); print(f"HF access OK: {m}")
    except GatedRepoError:
        print(f"FATAL: no access to {m}: accept the licence at https://huggingface.co/{m} with the token's account"); bad = 1
    except Exception as e:
        print(f"FATAL: access check failed for {m}: {type(e).__name__}: {str(e)[:200]}"); bad = 1
sys.exit(bad)
EOF
"$DLPY" analysis/p2r/p2r_weights_check.py check-hub materials/p2r_weights_pinned.json "$P/hub_observed.json" \
  || die "check-hub: FILES CHANGED or failed (see $P/hub_observed.json); the download was not started"
save_log

step "8/14 start the 60 s sync loop (runbook step 9) and the pinned-commit downloads (background)"
( trap - ERR; cd "$SYNC" && exec setsid bash scripts/p2_push_loop.sh "$RUN" "$SYNC" "$BRANCH" 60 ) > "$LOGDIR/sync.log" 2>&1 &
SYNC_PID=$!
info "sync loop pid $SYNC_PID -> $LOGDIR/sync.log"
( trap - ERR; set +e; cd "$RUN" && DRYRUN=$DRYRUN exec "$DLPY" - <<'EOF'
import json, os, time
from huggingface_hub import snapshot_download
dry = os.environ.get("DRYRUN") == "1"
pin = json.load(open("materials/p2r_weights_pinned.json"))
ign = ["original/*", "*.bin", "*.pth", "*.pt", "*.h5", "*.msgpack", "*.onnx", "*.gguf"]
keep = ["config.json", "generation_config.json", "tokenizer.json", "tokenizer.model", "tokenizer_config.json", "special_tokens_map.json"]
t0 = time.time()
for m in ["google/gemma-2-9b", "mistralai/Mistral-7B-v0.1"]:  # the PINNED commit, whatever main is now
    if dry:   # DRYRUN (test only): configs and tokenizer files, no weights
        snapshot_download(m, revision=pin[m]["main_commit"], allow_patterns=keep)
    else:
        snapshot_download(m, revision=pin[m]["main_commit"], ignore_patterns=ign)
    print(f"downloaded {m} {pin[m]['main_commit'][:8]} after {time.time() - t0:.0f} s", flush=True)
snapshot_download("EleutherAI/pythia-70m", ignore_patterns=ign)
print(f"downloaded EleutherAI/pythia-70m (driver smoke test, as in P2) after {time.time() - t0:.0f} s", flush=True)
EOF
) > "$LOGDIR/download.log" 2>&1 &
DL_PID=$!
info "downloads pid $DL_PID -> $LOGDIR/download.log"

step "9/14 main environment (runbook step 8; pip, about 3-6 min, in parallel with the downloads)"
cd "$RUN"
if [ "$DRYRUN" = 1 ]; then
  bash "${DRY_HOOKS:?DRY_HOOKS}/venv_hook.sh" "$RUN" || die "DRYRUN venv hook failed"
else
  { python3 -m venv .venv && . .venv/bin/activate && pip install -q --upgrade pip && pip install -q -r requirements-gpu.txt \
      && pip install -q --no-deps -e .; } || die "environment build failed (pip)"
fi
# shellcheck disable=SC1091
. .venv/bin/activate
if [ "$DRYRUN" = 1 ]; then
  info "DRYRUN: CUDA check skipped; $(python -c 'import torch, transformers, depthlaw; print("torch", torch.__version__, "transformers", transformers.__version__, "depthlaw from", depthlaw.__file__)')"
else
  python -c "import torch; assert torch.cuda.is_available(), 'CUDA not available'; print('torch', torch.__version__, 'cuda', torch.version.cuda, torch.cuda.get_device_name(0))" \
    || die "torch cannot use the GPU (driver $DRV); a different torch build would change the frozen environment"
fi
save_log

step "10/14 wait for downloads; set-ref, check-cache, attention check (runbook step 8)"
while kill -0 "$DL_PID" 2> /dev/null; do
  info "downloading: $(du -sh "$HF_HOME/hub" 2> /dev/null | cut -f1) in the cache; $(tail -1 "$LOGDIR/download.log" 2> /dev/null | cut -c1-120)"
  save_log; sleep 20
done
if wait "$DL_PID"; then DL_PID=""; else DL_PID=""; tail -5 "$LOGDIR/download.log"; die "download failed (see $LOGDIR/download.log)"; fi
grep '^downloaded' "$LOGDIR/download.log" || true
python analysis/p2r/p2r_weights_check.py set-ref materials/p2r_weights_pinned.json || die "set-ref failed"
# shellcheck disable=SC2086
python analysis/p2r/p2r_weights_check.py check-cache materials/p2r_weights_pinned.json "$P/weights_observed.json" $ONLY \
  || die "check-cache: FILES CHANGED (see $P/weights_observed.json); the driver will not start"
HF_HUB_OFFLINE=1 python - <<'EOF' || die "attention check failed"
import json, os, transformers, torch
from transformers import AutoConfig, AutoModelForCausalLM
c = AutoConfig.from_pretrained("google/gemma-2-9b")
c.num_hidden_layers, c.hidden_size, c.intermediate_size, c.num_attention_heads, c.num_key_value_heads, c.head_dim = 1, 64, 64, 2, 1, 32
m = AutoModelForCausalLM.from_config(c)
d = {"transformers": transformers.__version__, "torch": torch.__version__,
     "gemma2_attn_implementation": m.config._attn_implementation, "attn_logit_softcapping": c.attn_logit_softcapping}
print(d); json.dump(d, open(os.path.expanduser("~/depth-law-sync/p2_syncdest/_p2r_preflight/attention.json"), "w"))
EOF
python -c "import json, sys; d = json.load(open('$P/attention.json')); sys.exit(0 if d['gemma2_attn_implementation'] == 'eager' else 1)" \
  || die "Gemma-2 attention implementation is not eager (see $P/attention.json)"
df -h "$HOME" | tail -1
save_log

step "11/14 patching tests on each model (runbook step 8b; about 1-3 min per model)"
export HF_HUB_OFFLINE=1
: > "$HOME/p2r_models.txt"
for m in $TEST_MODELS; do
  if DEPTHLAW_TEST_MODEL=$m python -m pytest -q -p no:cacheprovider tests/test_depth.py \
       -k "patching_identity or patching_changes_output or final_patch_last_layer_equals_source" > "$P/arch_test_${m##*/}.txt" 2>&1
  then info "arch test OK: $m"; echo -n "$m " >> "$HOME/p2r_models.txt"
  else info "ARCH TEST FAILED: $m (not run in this session: MISSING 'it was not run', rerun-eligible)"; tail -5 "$P/arch_test_${m##*/}.txt"; fi
done
M=$(cat "$HOME/p2r_models.txt")
info "models to run: ${M:-none}"
[ -n "${M// /}" ] || die "no model passed the patching tests; the driver is not started"
save_log

step "12/14 budget, check-cache again, frozen driver (runbook step 10)"
read -r SPENT LEFT DBUDGET B <<< "$(python3 - <<EOF
import math, time
spent = (time.time() - $T0) / 60 + $PRESTART_MIN
left = $BASE / $HOURLY * 60 - spent
T = math.floor(left) - $MARGIN_MIN
B = round((T + 15 + 0.5) * $DRIVER_RATE / 60, 2)   # the frozen driver's minute budget is floor(B / 207.36 * 60) - 15
assert math.floor(B / $DRIVER_RATE * 60) - 15 == T
print(round(spent, 1), round(left, 1), T, B)
EOF
)"
info "spent about $SPENT min (incl. $PRESTART_MIN before this script); about $LEFT min affordable left; driver minute budget $DBUDGET (= left - $MARGIN_MIN; BALANCE_INR=$B in the driver's 207.36 INR/h units)"
[ "$DBUDGET" -ge 1 ] || die "no minutes left for the driver"
# shellcheck disable=SC2086
python analysis/p2r/p2r_weights_check.py check-cache materials/p2r_weights_pinned.json "$P/weights_observed_at_start.json" $ONLY \
  || die "check-cache before the driver: FILES CHANGED (see $P/weights_observed_at_start.json)"
save_log
info "starting the frozen driver (console: $HOME/p2r_driver_console.txt)"
if SKIP_ENV=1 MODELS="$M" BALANCE_INR="$B" SYNC_DEST="$SYNC/p2_syncdest" HF_HUB_OFFLINE=1 \
     bash scripts/p2_gpu_run.sh 2>&1 | tee "$HOME/p2r_driver_console.txt"; then DRV_EXIT=0; else DRV_EXIT=$?; fi
NFATAL=$(grep -c FATAL "$HOME/p2r_driver_console.txt" || true)
END=$(grep -E "finished after|BUDGET REACHED" "$HOME/p2r_driver_console.txt" | tail -1 || true)
info "driver exit $DRV_EXIT; FATAL lines $NFATAL; end line: ${END:-NONE}"

step "13/14 copy-back: VM_FILES.sha256 and final push (runbook step 11)"
stop_bg
cp "$HOME/p2r_driver_console.txt" "$P/driver_console.txt"; cp "$LOGDIR/download.log" "$P/download.log"; save_log
dirs=(); for d in results/P2 results/logs deviations_pending; do [ -d "$d" ] && dirs+=("$d"); done
find "${dirs[@]}" -type f -print0 | sort -z | xargs -0 sha256sum > "$SYNC/VM_FILES.sha256"
info "VM_FILES.sha256: $(wc -l < "$SYNC/VM_FILES.sha256") files (${dirs[*]})"
PUSHED=no
for i in 1 2 3 4; do
  ( cd "$SYNC" && ONCE=1 bash scripts/p2_push_loop.sh "$RUN" "$SYNC" "$BRANCH" ) || true
  if [ "$(git -C "$SYNC" ls-remote origin "refs/heads/$BRANCH" | cut -f1)" = "$(git -C "$SYNC" rev-parse HEAD)" ]; then PUSHED=yes; break; fi
  info "push not confirmed (attempt $i); retrying"; sleep $((i * 10))
done
[ "$PUSHED" = yes ] || die "the final push to $BRANCH did not reach GitHub"
info "branch $BRANCH on origin = $(git -C "$SYNC" rev-parse --short HEAD)"

step "14/14 verification from a fresh clone of $BRANCH (runbook step 12)"
rm -rf "$V"
g clone -q --sparse --single-branch -b "$BRANCH" "$REPO_URL" "$V" || die "could not clone $BRANCH for verification"
git -C "$V" sparse-checkout set results/P2 results/P2smoke results/logs deviations_pending p2_syncdest
# shellcheck disable=SC2086
if python - "$V" $TEST_MODELS <<'EOF'
import json, sys
from pathlib import Path
v = Path(sys.argv[1]) / "p2_syncdest/_p2r_preflight"; ok = True
for n in ["hub_observed.json", "weights_observed.json", "weights_observed_at_start.json"]:
    f = v / n
    if not f.exists():
        print(f"preflight {n}: MISSING"); ok = False; continue
    d = json.loads(f.read_text())["differences"]
    print(f"preflight {n}: {'OK (no differences)' if not d else str(len(d)) + ' DIFFERENCES'}"); ok = ok and not d
for m in sys.argv[2:]:
    f = v / f"arch_test_{m.split('/')[-1]}.txt"
    print(f"preflight {f.name}: {'present' if f.exists() else 'MISSING'}"); ok = ok and f.exists()
print("PREFLIGHT FILES ON GITHUB:", "OK" if ok else "NOT OK"); sys.exit(0 if ok else 1)
EOF
then PRE=ok; else PRE=bad; fi
if python "$RUN/scripts/p2_verify_sync.py" "$V" | tee "$LOGDIR/verify.txt"; then VER=yes; else VER=no; fi
save_log; ( cd "$SYNC" && cp "$LOGDIR/verify.txt" "$P/verify_on_vm.txt" && ONCE=1 timeout 120 bash scripts/p2_push_loop.sh "$RUN" "$SYNC" "$BRANCH" ) > /dev/null 2>&1 || true

trap - ERR
TOTAL=$(el)
if [ "$DRV_EXIT" = 0 ] && [ "$NFATAL" = 0 ] && [ "$PRE" = ok ] && [ "$VER" = yes ] && [[ "$END" == *"finished after"* ]]; then
  banner "P2R SESSION COMPLETE after $TOTAL (models run: $M)" "driver: $END" \
         "SAFE TO DESTROY THE VM: YES" "Send Claude a screenshot of this box, then DESTROY the VM in the dashboard."
  exit 0
else
  banner "P2R SESSION NOT CLEAN after $TOTAL: driver exit $DRV_EXIT, FATAL lines $NFATAL, preflight $PRE, verify $VER" \
         "driver end line: ${END:-NONE}" \
         "PAUSE the instance now in the dashboard (Pause keeps the disk). Do NOT destroy." \
         "SAFE TO DESTROY THE VM: NO. Send Claude a screenshot of this box."
  exit 1
fi
