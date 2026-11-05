#!/usr/bin/env bash
# thin wrapper: depthlaw.freq.audit
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH=src HF_HOME="${HF_HOME:-$PWD/cache/hf}"
exec python -m depthlaw.freq.audit "$@"
