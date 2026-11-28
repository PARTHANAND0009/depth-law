# P2R VM quickstart (RTX PRO 6000 only; one run of `scripts/p2r_vm_bootstrap.sh`)
Start the VM only if BALANCE ≥ 112 min × HOURLY / 60 (INR 387 + 1.87 × storage INR/h); below that the script refuses.
On the fresh VM, type in order (never paste a token anywhere else):
```bash
tmux new -s p2r
read -rsp 'GitHub token: ' GH_TOKEN; echo; read -rsp 'HF token: ' HF_TOKEN; echo; export GH_TOKEN HF_TOKEN
export BALANCE=<INR balance just before you started the VM> HOURLY=<INR per hour, GPU plus storage>
curl -fsSLo ~/p2r_vm_bootstrap.sh https://raw.githubusercontent.com/PARTHANAND0009/depth-law/BOOTSTRAP_COMMIT/scripts/p2r_vm_bootstrap.sh
bash ~/p2r_vm_bootstrap.sh
```
- No tmux? `sudo apt-get install -y tmux` first. Detach `Ctrl-b d`, re-attach `tmux attach -t p2r`; a lost SSH does not stop it.
- STEP 0 prints `bootstrap sha256 BOOTSTRAP_SHA12…`; any other value: stop and tell Claude.
- Success: STEP 0/14 … 14/14, then a `####` box ending `## SAFE TO DESTROY THE VM: YES` (about 50–95 min in all).
- Screenshots: the final `####` box, always; any `FATAL` box at once. Optional mid-run: `tail -3 ~/p2r_logs/sync.log`.
- **FATAL rule:** a box with `FATAL` or `NOT CLEAN` that says `SAFE TO DESTROY THE VM: NO` → PAUSE the instance in the
  dashboard now (Pause keeps the disk), do not destroy, send the screenshot. If it says `YES (nothing to copy)`, nothing
  ran: destroy it and send the screenshot.
- If the VM stops by itself (budget timer), do not destroy it; tell Claude.
- **SAFE TO DESTROY rule:** destroy only after the final box says `SAFE TO DESTROY THE VM: YES`; then tell Claude
  "verify the P2R sync".
