# P2 GPU session runbook (Jarvislabs H100 80GB, region IN2, user `ubuntu`)

GPU changed from the RTX PRO 6000 (unavailable) to an H100 80GB. Deviation draft: `reports/pending_frozen_changes/D-P2-20261124T072257Z-gpu.md`, committed in step 7.

The prereg is frozen: `prereg/P2_prompt_vs_fact.md`, sha256 `493b2c3c079d2167b3c57ab949f574650b74a6c66a1205ef7bb28a5134c4662f`, tag `prereg-P2` = `ff119ca56194405eb91b745a38d1299f4556de29`.

Nothing in this file has been run by Claude. Every command runs on the VM, in order. Lines in `<...>` are yours to fill in.

**Manual stop rule (always):**
- After ANY line containing `FATAL` in the driver window, **pause (stop) the instance in the Jarvislabs dashboard immediately.**
- The driver exits on FATAL, but its auto-stop timer keeps running, so the instance stays billed. This is a known post-freeze item.
- Pause keeps the disk, so nothing is lost. Do not Destroy until step 15 says YES.

---

## A. Before you start the instance
1. **GitHub token:** a fine-grained token for `PARTHANAND0009/depth-law` with Contents: read and write. It is needed to push the tag and the sync branch.
2. **Hugging Face token** with access to `meta-llama/Llama-3.1-8B`: accept the license on the model page with the same account.
3. **Instance:**
   - Jarvislabs H100 80GB VM, **storage ≥ 150 GB**: about 56 GB of weights for the five models, plus the CUDA torch wheel, plus results.
   - 80 GB is enough: an 8B model in fp32 is about 33 GB.
   - Note the **hourly rate in INR, GPU plus storage** (about 330.48/h plus storage). The driver assumes 207.36 INR/h, and step 11 corrects for that.

## B. On the VM (SSH in as `ubuntu`)
4. Packages, Python and tmux. The pinned `torch==2.15.0` needs **Python ≥ 3.11**:
```bash
sudo apt-get update -q && sudo apt-get install -y -q tmux rsync git python3-venv
python3 --version
```
   - **If it prints 3.11 or newer:** continue below.
   - **If it prints 3.10 or older:** install Python 3.12 and make `python3` point to it for this user. The driver itself calls `python3 -m venv`, so this is needed for the driver too:
```bash
sudo apt-get install -y -q software-properties-common && sudo add-apt-repository -y ppa:deadsnakes/ppa && sudo apt-get update -q
sudo apt-get install -y -q python3.12 python3.12-venv
mkdir -p ~/bin && ln -sf "$(command -v python3.12)" ~/bin/python3 && echo 'export PATH=$HOME/bin:$PATH' >> ~/.bashrc && export PATH=$HOME/bin:$PATH
python3 --version
```
   Expected: `Python 3.12.x`. Then:
```bash
tmux new -s p2
```
   Inside tmux, the windows are: 0 = run, 1 = sync. `Ctrl-b c` opens a new window; `Ctrl-b 0` and `Ctrl-b 1` switch between them; `Ctrl-b d` detaches. Re-attach with `tmux attach -t p2`.

5. Tokens. They are typed, not echoed, and not written to the shell history:
```bash
read -rsp 'GitHub token: ' GH_TOKEN; echo; read -rsp 'HF token: ' HF_TOKEN; echo; export GH_TOKEN HF_TOKEN
```

6. Run checkout at the frozen commit, and the tag. The tag could not be pushed from Claude's session (HTTP 403), so it is pushed from here:
```bash
git clone -q https://x-access-token:${GH_TOKEN}@github.com/PARTHANAND0009/depth-law.git ~/depth-law && cd ~/depth-law
git fetch -q --tags; git rev-parse -q --verify prereg-P2 || git tag prereg-P2 ff119ca56194405eb91b745a38d1299f4556de29
test "$(git rev-parse prereg-P2)" = ff119ca56194405eb91b745a38d1299f4556de29 && echo "tag OK" || echo "TAG WRONG: stop here"
git push -q origin prereg-P2; git checkout -q --detach prereg-P2
sha256sum -c prereg/HASH_P2.txt
```
   Expected output: `tag OK` and `prereg/P2_prompt_vs_fact.md: OK`. Anything else: stop and ask Claude.

7. Sync clone. First commit the two pre-session deviations to master (the sync mechanism and the GPU change), then branch for the session:
```bash
git clone -q https://x-access-token:${GH_TOKEN}@github.com/PARTHANAND0009/depth-law.git ~/depth-law-sync && cd ~/depth-law-sync
for d in D-P2-20261124T044034Z-0 D-P2-20261124T072257Z-gpu; do cp reports/pending_frozen_changes/$d.md prereg/deviations/$d.md; done
git add prereg/deviations/D-P2-20261124T044034Z-0.md prereg/deviations/D-P2-20261124T072257Z-gpu.md
git -c user.name="<your name>" -c user.email="<your email>" commit -qm "Pre-session deviations: off-instance copy via GitHub branch; GPU changed to H100 80GB"
git push -q origin master && git checkout -q -b p2-gpu-session && mkdir -p p2_syncdest && echo "sync clone OK"
```

8. Python environment. This is the same as the driver's own set-up, done early so the weights can be pre-downloaded:
```bash
cd ~/depth-law && python3 -m venv .venv && source .venv/bin/activate
pip install -q --upgrade pip && pip install -q -r requirements-gpu.txt && pip install -q --no-deps -e .
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv
python -c "import torch; assert torch.cuda.is_available(), 'CUDA not available'; a=torch.cuda.get_arch_list(); print(torch.__version__, 'cuda', torch.version.cuda, torch.cuda.get_device_name(0), torch.cuda.get_device_capability(0), a); assert 'sm_90' in a and torch.cuda.get_device_capability(0)==(9,0); print('H100 / sm_90 OK')"
```
   - Expected: an H100 with about 80 GB (≈ 81,000 MiB), driver version **580 or newer**, `2.15.0+cu132 cuda 13.2 ... (9, 0) [... 'sm_90' ...]`, and `H100 / sm_90 OK`.
   - The wheel is built for CUDA 13.2, which needs an NVIDIA driver ≥ 580. If `CUDA not available` appears with an older driver, **pause the instance and tell Claude**. A different torch build would be a change to the frozen environment, and it is not authorized.

9. **Llama check:** a fast check, then pre-download all five models into the driver's cache. Weights only: `original/` and `*.bin` are skipped.
```bash
export HF_HOME=$HOME/depth-law/cache/hf
python -c "from huggingface_hub import hf_hub_download as d; d('meta-llama/Llama-3.1-8B','config.json'); print('Llama access OK')"
python - <<'EOF'
from huggingface_hub import snapshot_download
for m in ["Qwen/Qwen3-8B", "meta-llama/Llama-3.1-8B", "EleutherAI/pythia-1.4b", "EleutherAI/pythia-2.8b",
          "allenai/OLMo-2-1124-7B", "EleutherAI/pythia-70m"]:
    p = snapshot_download(m, ignore_patterns=["original/*", "*.bin", "*.pth", "*.pt", "*.h5", "*.msgpack", "*.onnx", "*.gguf"])
    print("downloaded", m, p)
EOF
python -c "import json,glob; f=glob.glob('$HF_HOME/hub/models--meta-llama--Llama-3.1-8B/snapshots/*/model*.safetensors'); print('Llama safetensors files:', len(f)); assert f"
df -h ~
```
   Expected: `Llama access OK`, six `downloaded` lines, and `Llama safetensors files: 4` (or more). If Llama fails, pause, fix access on Hugging Face, and resume. Do not start the driver without Llama, unless you accept that it is skipped: the driver then writes a deviation.

10. Start the sync loop in window 1:
```bash
# Ctrl-b c   (new window 1)
cd ~/depth-law-sync && bash scripts/p2_push_loop.sh ~/depth-law ~/depth-law-sync p2-gpu-session 60
```
   Expected: a line `pushed <hash> to p2-gpu-session` every 60 s. `PUSH FAILED` means the token or the network is wrong: fix it before step 11.

11. **Budget and start, in window 0.** Read the balance and the hourly rate from the Jarvislabs dashboard *now*, after the downloads:
```bash
# Ctrl-b 0
cd ~/depth-law && source .venv/bin/activate && export HF_HOME=$HOME/depth-law/cache/hf
BAL=<balance in INR now>; RATE=<INR per hour: GPU (about 330.48) plus storage per hour>
B=$(python3 -c "print(round($BAL*207.36/$RATE, 2))"); echo "BALANCE_INR=$B -> minute budget $(python3 -c "import math; print(math.floor($B/207.36*60)-15)")"
BALANCE_INR=$B SYNC_DEST=$HOME/depth-law-sync/p2_syncdest bash scripts/p2_gpu_run.sh 2>&1 | tee ~/p2_driver_console.txt
```
   - The driver budgets with 207.36 INR/h. Scaling the balance by 207.36/RATE makes its minute budget match the real rate. With RATE = 207.36, B = BAL.
   - Keep the defaults: no `MODELS`, no `SKIP_ENV`, no `DRY`. The driver re-runs the venv set-up quickly, checks CUDA and Llama access, runs pytest and the pilot, and then runs the five models in prereg order.

12. **While it runs, watch window 0.** Expected sequence:
    - `materials sha256 match prereg section 1`;
    - `pytest: ... passed`;
    - `pilot projection (min): ...`;
    - possibly `DEVIATION D-P2-<UTC>-<n>: ...` (a fallback; the file is written first, and that is fine);
    - per model, `model <name> carriers <n>`, then `done-check ...: ok=True`;
    - finally `finished after <m> min of <budget>`.

    **Any `FATAL`: pause the instance immediately (manual stop rule).** At the budget limit, the driver writes `D-P2-<UTC>-budget.md` and shuts the VM down by itself. Check in the dashboard that the instance really stopped; if not, pause it.

## C. Confirm that everything is off the VM; only then destroy it
13. After `finished after ...` appears in window 0, write the full file list with sha256 and push it once more. After a budget stop, first resume the instance, re-attach tmux, and then do this step:
```bash
cd ~/depth-law && find results/P2 results/P2smoke results/logs deviations_pending -type f -print0 | sort -z | xargs -0 sha256sum > ~/depth-law-sync/VM_FILES.sha256
wc -l ~/depth-law-sync/VM_FILES.sha256
cd ~/depth-law-sync && ONCE=1 bash scripts/p2_push_loop.sh ~/depth-law ~/depth-law-sync p2-gpu-session
```
   Expected: `pushed <hash> to p2-gpu-session`. Then stop the loop in window 1 with `Ctrl-c`.

14. **Verify off the VM.** Either tell Claude "verify the P2 sync", and it runs the commands below in its own session, or run them on your computer:
```bash
git clone -q -b p2-gpu-session https://github.com/PARTHANAND0009/depth-law.git p2check && cd p2check   # private repo: your git credentials
python3 -m venv .v && .v/bin/pip install -q numpy pandas pyarrow scipy && .v/bin/python scripts/p2_verify_sync.py .
```
   The script checks:
   - every file in `VM_FILES.sha256` is present with the same sha256;
   - the session log has its end line;
   - the deviation-file count matches the log;
   - every model run dir, by the frozen completeness rule with checksums recomputed. It lists incomplete models as MISSING; those are results to keep, not to re-run.

15. **Safe to destroy the VM: only when step 14 prints `SAFE TO DESTROY THE VM: YES`.** Then destroy the instance in the Jarvislabs dashboard.
   - If it prints NO: keep the instance paused, do not destroy it, and send Claude the output.

## D. After the session (Claude, on your GO)
- The deviation files in `deviations_pending/` are copied into `prereg/deviations/` and committed. This is human-only now: the deny rule covers `prereg/deviations/**`.
- The analysis runs on CPU in this repo: `p2_analysis.py --set correct` with one `MODEL=RUN_DIR` (or `MODEL=none`) per prereg model, then the sensitivity sets with `--primary`.
- The post-freeze fix list is `analysis/p2/POST_FREEZE_FIXES.md`.
