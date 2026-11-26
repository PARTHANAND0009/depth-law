# P2R GPU session runbook (replication: Gemma-2-9B, Mistral-7B-v0.1)

**Hard budget: INR 700 in total, set-up included.** Stops: (1) an instance shutdown timer armed right after login (step 3), (2) the frozen driver's minute budget, computed from what is left (step 10), (3) the manual dashboard stop rule. Nothing here has been run by Claude. Run only after GO PREREG-R and `APPLY_P2R.sh` (tag `prereg-P2R` exists and is pushed).

**Manual stop rule:** after ANY line containing `FATAL`, `FILES CHANGED`, `DIFFERENT:`, or an attention implementation other than `eager`, pause (stop) the instance in the Jarvislabs dashboard immediately. Pause keeps the disk. Do not destroy until step 13 says YES. **Never open or inspect a partial chunk** of a model that stopped early (amendment section 4).

## A. Before you start the instance
1. Tokens: a GitHub fine-grained token for the repository (Contents: read and write); a Hugging Face token whose account has accepted the Gemma licence on `google/gemma-2-9b` (Mistral-7B-v0.1 is open).
2. Instance: Jarvislabs **RTX PRO 6000 (Blackwell), the same GPU type as the P2 session** (amendment section 4; an H100 is about half as fast in fp32 and would risk the budget). Storage **≥ 100 GB** (weights: Gemma-2-9B 37.0 GB, Mistral-7B-v0.1 14.5 GB, plus the torch wheel and results). Note the hourly rate in INR, **GPU plus storage**, as RATE. If no RTX PRO 6000 is available, do not substitute another GPU: tell Claude (a different GPU is a deviation).

## B. On the VM
3. **First: arm the instance-level hard stop** at the point where INR 700 would be spent:
```bash
RATE=<INR per hour, GPU plus storage>; echo "$RATE" > ~/p2r_rate.txt   # step 10 reads it back (tmux windows do not inherit it)
MIN=$(python3 -c "import math; print(math.floor(700 / $RATE * 60) - 5)"); echo "hard stop in $MIN min"
sudo shutdown -h +$MIN
date -u +%FT%TZ | tee ~/p2r_session_start_utc.txt
```
   Expected: `hard stop in <N> min` and a `Shutdown scheduled` message. Keep this time; all budget steps count from it. This timer and the driver's stop are both OS shutdowns; whether an OS shutdown stops billing on this rental is not known, so the first time either fires, check the dashboard and pause by hand if the instance still shows as running.
4. Packages and Python ≥ 3.11 (as in the P2 runbook, step 4), then `tmux new -s p2r` (window 0 = run, window 1 = sync).
5. Tokens, typed, not echoed:
```bash
read -rsp 'GitHub token: ' GH_TOKEN; echo; read -rsp 'HF token: ' HF_TOKEN; echo; export GH_TOKEN HF_TOKEN
```
6. Run checkout at the frozen amendment:
```bash
git clone -q https://x-access-token:${GH_TOKEN}@github.com/PARTHANAND0009/depth-law.git ~/depth-law && cd ~/depth-law
git fetch -q --tags && git checkout -q --detach prereg-P2R && sha256sum -c prereg/amendments/A_P2R_new_families.sha256 && sha256sum -c prereg/HASH_P2.txt
```
   Expected: every line `OK`. Anything else: pause and ask Claude.
7. Sync clone, branch `p2r-gpu-session`:
```bash
git clone -q https://x-access-token:${GH_TOKEN}@github.com/PARTHANAND0009/depth-law.git ~/depth-law-sync && cd ~/depth-law-sync
git checkout -q -b p2r-gpu-session && mkdir -p p2_syncdest/_p2r_preflight && echo "sync clone OK"
```
8. Environment, weights provenance, downloads, attention check:
```bash
cd ~/depth-law && python3 -m venv .venv && source .venv/bin/activate
pip install -q --upgrade pip && pip install -q -r requirements-gpu.txt && pip install -q --no-deps -e .
python -c "import torch; assert torch.cuda.is_available(); print(torch.cuda.get_device_name(0))"
export HF_HOME=$HOME/depth-law/cache/hf
P=~/depth-law-sync/p2_syncdest/_p2r_preflight
python analysis/p2r/p2r_weights_check.py check-hub materials/p2r_weights_pinned.json $P/hub_observed.json && python - <<'EOF'
import json
from huggingface_hub import snapshot_download
pin = json.load(open("materials/p2r_weights_pinned.json"))
ign = ["original/*", "*.bin", "*.pth", "*.pt", "*.h5", "*.msgpack", "*.onnx", "*.gguf"]
for m in ["google/gemma-2-9b", "mistralai/Mistral-7B-v0.1"]:  # the PINNED commit, whatever main is now
    snapshot_download(m, revision=pin[m]["main_commit"], ignore_patterns=ign); print("downloaded", m, pin[m]["main_commit"][:8])
snapshot_download("EleutherAI/pythia-70m", ignore_patterns=ign); print("downloaded EleutherAI/pythia-70m (driver smoke test, as in P2)")
EOF
python analysis/p2r/p2r_weights_check.py set-ref materials/p2r_weights_pinned.json \
  && python analysis/p2r/p2r_weights_check.py check-cache materials/p2r_weights_pinned.json $P/weights_observed.json
HF_HUB_OFFLINE=1 python - <<'EOF'   # offline: reads the checked snapshot's config; an online call could move refs/main
import json, os, transformers, torch
from transformers import AutoConfig, AutoModelForCausalLM
c = AutoConfig.from_pretrained("google/gemma-2-9b")
c.num_hidden_layers, c.hidden_size, c.intermediate_size, c.num_attention_heads, c.num_key_value_heads, c.head_dim = 1, 64, 64, 2, 1, 32
m = AutoModelForCausalLM.from_config(c)
d = {"transformers": transformers.__version__, "torch": torch.__version__,
     "gemma2_attn_implementation": m.config._attn_implementation, "attn_logit_softcapping": c.attn_logit_softcapping}
print(d); json.dump(d, open(os.path.expanduser("~/depth-law-sync/p2_syncdest/_p2r_preflight/attention.json"), "w"))
EOF
df -h ~
```
   Expected: the GPU name `NVIDIA RTX PRO 6000 ...`, `check-hub: OK (24 files compared)`, three `downloaded` lines, two `set-ref:` lines, `check-cache: OK (24 files compared)` (this re-hashes about 52 GB, a few minutes), and `'gemma2_attn_implementation': 'eager'`. `FILES CHANGED` from either check (the download does not even start after a failed `check-hub`), or any other implementation than `eager`: pause and ask Claude; do not start the driver.
8b. **Patching checks on the two new architectures** (frozen tests, model chosen by environment variable only; outputs go to the synced files):
```bash
cd ~/depth-law && source .venv/bin/activate && export HF_HOME=$HOME/depth-law/cache/hf HF_HUB_OFFLINE=1
P=~/depth-law-sync/p2_syncdest/_p2r_preflight; : > ~/p2r_models.txt
for m in google/gemma-2-9b mistralai/Mistral-7B-v0.1; do
  if DEPTHLAW_TEST_MODEL=$m python -m pytest -q -p no:cacheprovider tests/test_depth.py \
       -k "patching_identity or patching_changes_output or final_patch_last_layer_equals_source" > $P/arch_test_${m##*/}.txt 2>&1
  then echo "arch test OK: $m"; echo -n "$m " >> ~/p2r_models.txt
  else echo "ARCH TEST FAILED: $m"; tail -5 $P/arch_test_${m##*/}.txt; fi
done; echo "models to run: $(cat ~/p2r_models.txt)"
```
   Expected: two `arch test OK` lines (each loads the model in fp32, about 1–3 min). A model that fails is **not run** in this session (amendment section 4: MISSING "it was not run", eligible for the rerun rule); the driver runs only the models listed in `~/p2r_models.txt`, in the original order. If none passed, do not start the driver; pause and tell Claude.
9. Sync loop in window 1:
```bash
cd ~/depth-law-sync && bash scripts/p2_push_loop.sh ~/depth-law ~/depth-law-sync p2r-gpu-session 60
```
10. **Budget and start, window 0.** Give the driver what is left of INR 700, scaled to its internal rate (207.36 INR/h):
```bash
cd ~/depth-law && source .venv/bin/activate && export HF_HOME=$HOME/depth-law/cache/hf HF_HUB_OFFLINE=1
RATE=$(cat ~/p2r_rate.txt); [ -n "$RATE" ] || { echo "FATAL: no RATE (step 3)"; false; }
SPENT_MIN=$(( ( $(date +%s) - $(date -d "$(cat ~/p2r_session_start_utc.txt)" +%s) ) / 60 ))
LEFT=$(python3 -c "print(round(700 - $SPENT_MIN * $RATE / 60, 2))"); B=$(python3 -c "print(round($LEFT * 207.36 / $RATE, 2))")
echo "spent ${SPENT_MIN} min; left INR $LEFT; driver BALANCE_INR=$B"
M=$(cat ~/p2r_models.txt); echo "MODELS=$M"
python3 -c "assert float('$B') > 0 and '$M'.strip()" \
  && python analysis/p2r/p2r_weights_check.py check-cache materials/p2r_weights_pinned.json ~/depth-law-sync/p2_syncdest/_p2r_preflight/weights_observed_at_start.json \
  && SKIP_ENV=1 MODELS="$M" BALANCE_INR=$B SYNC_DEST=$HOME/depth-law-sync/p2_syncdest \
  bash scripts/p2_gpu_run.sh 2>&1 | tee ~/p2r_driver_console.txt
```
   - Expected: `materials sha256 match prereg section 1`, `pytest: ... passed`, `pilot projection (min): ...`, per model `model <name> carriers <n>` and `done-check ...: ok=True`, then `finished after <m> min`.
   - Planning only (not a rule), scaled from P2's measured times on the same GPU (Qwen 16.3, Llama 16.3, OLMo 13.8 min): about 21 min for Gemma-2-9B and 13 min for Mistral-7B-v0.1 with 3 carriers, plus 20–25 min of set-up and downloads.
   - The driver starts only if `check-cache` passes again (`&&`), and with `HF_HUB_OFFLINE=1` it loads only the verified cached files.
   - Offline, the driver's Llama access check fails and writes a `Llama-3.1-8B not run` deviation: it refers to no P2R model and is a no-op (amendment section 3).

## C. Copy-back and verification (as P2 runbook steps 13–15)
11. After `finished after ...`: write `VM_FILES.sha256` for `results/P2 results/logs deviations_pending` and push once more (`ONCE=1 bash scripts/p2_push_loop.sh ...`).
12. Verify off the VM: tell Claude "verify the P2R sync" (it runs `scripts/p2_verify_sync.py` on branch `p2r-gpu-session`), or run it yourself.
13. Destroy the VM only when step 12 prints `SAFE TO DESTROY THE VM: YES`.
14. If you keep the VM paused instead, cancel the step-3 timer first: `sudo shutdown -c`.

## E. Second session (only if a rerun note is committed; amendment section 4)
Same steps A–C, with these differences:
- Budget: the amount stated in the committed rerun note, in place of INR 700 in steps 3 and 10.
- Step 6: if a code fix was made, check out `prereg-P2R-fix1` instead of `prereg-P2R` and also check the fix's sha256 file named in its deviation (every line `OK`). Without a fix, `prereg-P2R` as before.
- Step 7: sync branch `p2r-gpu-session-2`.
- Steps 8b and 10: the loop in 8b lists only the models named in the rerun note, in the original order (Gemma before Mistral); the driver runs those that pass.
- Everything else, including the provenance checks and the stop rules, is unchanged.

## D. After the session (Claude, on your GO)
- Deviations from `deviations_pending/` are installed in `prereg/deviations/` by you (human-only path).
- Before any analysis (for each session): `_p2r_preflight/hub_observed.json`, `weights_observed.json` and `weights_observed_at_start.json` must all exist in the synced session files with empty `differences`; otherwise the models run in that session are passed as `=none`, MISSING with the reason fixed in amendment section 1. A model whose `arch_test_*.txt` shows a failure, or is absent from the synced files, was not run in that session: `=none`, MISSING "it was not run" (amendment section 3).
- Right before the gating call: `check-cache --only-present` on the local tokenizer cache, through the ledger; it must print OK (amendment section 4).
- No P2R analysis of any kind runs until all sessions have ended and the rerun decision (made from logs only) is committed; then the gating call runs once (amendment section 4).
- CPU analysis, one job at a time at the standing cap: `analysis/p2r/p2r_analysis.py <out> --runs google/gemma-2-9b=<run_dir|none> mistralai/Mistral-7B-v0.1=<run_dir|none> --set correct`, then the sensitivity sets with `--primary`, then `analysis/p2r/p2r_combine.py results/P2analysis/correct <out> <summary.json>`, then the EXPLORATORY answer-identity refit.
