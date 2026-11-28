# D-P2R-bootstrap (pending; pre-session; the human installs it in prereg/deviations/)

The P2R session is run by `scripts/p2r_vm_bootstrap.sh` (not frozen), which runs the frozen runbook
`reports/p2r/GPU_RUNBOOK_P2R.md` steps 3–11 in order, using the frozen code at tag `prereg-P2R` (driver, weights
check, patching tests, push loop, verify script). The bootstrap copies this file, with the session values added
below, into `p2_syncdest/_p2r_preflight/` and pushes it before any model weights are downloaded.

Operational differences from the runbook text. None of them changes measurement, materials, models, order,
outcomes or analysis:
1. **Budget base:** the INR available is min(BALANCE, 700), where BALANCE is the account balance the human enters
   (the runbook uses 700). A further PRESTART_MIN (default 5 min) is counted as already billed before the script
   starts. Runbook step 3 (the instance shutdown timer) uses this base.
2. **Driver budget:** BALANCE_INR for the frozen driver is chosen so that its minute budget equals the minutes
   left minus 10 (the runbook passes the INR left, so the driver's own 15-min margin applies). The frozen driver
   formula, pilot gate, fallbacks and auto-stop are unchanged.
3. **Minimum balance:** the bootstrap refuses to start (before any clone) if fewer than 112 minutes are affordable.
   This is a planning bound from `results/P2R/budget_estimate_EXPLORATORY.json` (slow case: set-up 43 min, 10 min
   margin, the pilot, and the driver's 3-carrier pilot projection).
4. **Order and parallelism:** the tag is created and pushed at the start (runbook: before the session).
   `check-hub` runs first, in a small separate environment with the pinned `huggingface_hub==2.4.0`. The
   pinned-commit download then runs in the background while the main environment is built. The 60 s sync loop
   (runbook step 9) starts right after `check-hub`, not after the patching tests.
5. **Gated-model access check:** before the download, the token's access to each P2R model is checked.
6. **Verification:** after runbook step 11, the bootstrap clones the pushed sync branch from GitHub into a fresh
   directory and runs `scripts/p2_verify_sync.py` on it. It also checks that the three `_p2r_preflight` provenance
   files exist with empty `differences` (runbook section D). `SAFE TO DESTROY THE VM: YES` is printed only if both
   checks pass and no FATAL line occurred. Claude repeats the verification off the VM.
7. **Refusals:** the bootstrap stops with FATAL on a GPU other than RTX PRO 6000, an NVIDIA driver below 580,
   Python below 3.11 that cannot be replaced by 3.12, less than 70 GB free disk, a wrong or moved tag, any hash
   mismatch, a `p2r-gpu-session` branch that already exists on GitHub, or a missing token.

## Session values (filled in by the bootstrap)
