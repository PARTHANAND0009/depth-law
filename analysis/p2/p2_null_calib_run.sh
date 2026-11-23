#!/usr/bin/env bash
# P2 parametric-null calibration and power (human 2026-11-23). Test only. Resumable (per-replicate job files).
# Settings follow the round-3 reviewer's illustration: ft = e = 1, fact:carrier = fc, fact = 0 (calibration).
# Power: fact chosen so that the true ICC(1) = fact / (fact + ft + fc/nc + e/nc) = 0.10 with fc = 1, nc = 3:
#   fact = 0.1 * (1 + 2/3) / 0.9 = 0.185185.
set -euo pipefail
cd "$(dirname "$0")/../.."
OUT=${1:-results/P2null_calib}
mkdir -p "$OUT"
export MALLOC_ARENA_MAX=2 OMP_NUM_THREADS=1
R() { nice -n 10 prlimit --as=1800000000 Rscript analysis/p2/p2_null_calib.R "$@"; }
R "$OUT/null_fc1_nc3.json"    cond=null_fc1_nc3    fact=0        fc=1    nc=3 nrep=200 nsim=100 cores=3 seed=7000000
R "$OUT/null_fc025_nc3.json"  cond=null_fc025_nc3  fact=0        fc=0.25 nc=3 nrep=200 nsim=100 cores=3 seed=7100000
R "$OUT/null_fc1_nc2.json"    cond=null_fc1_nc2    fact=0        fc=1    nc=2 nrep=200 nsim=100 cores=3 seed=7200000
R "$OUT/power_icc010.json"    cond=power_icc010    fact=0.185185 fc=1    nc=3 nrep=100 nsim=100 cores=3 seed=7300000
