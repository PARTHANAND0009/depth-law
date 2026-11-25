#!/usr/bin/env bash
# Install the frozen-path guard layers (2026-11-25, INC-2026-11-25-required-macros). Idempotent; rerun after a
# fresh clone or a new venv.
#   1. .git/hooks/pre-commit  <- scripts/pre-commit (all frozen paths, ledger append-only, numbers.tex provenance)
#   2. depthlaw_frozen_rt.pth in the venv and system site-packages: loads src/depthlaw/frozen_rt.py at every
#      Python start (runtime write guard)
#   3. chattr +i on every frozen file on disk (stops root too; removing it is a human action)
set -euo pipefail
cd "$(dirname "$0")/.."
ROOT=$(pwd)
install -m 755 scripts/pre-commit .git/hooks/pre-commit
LINE="import sys; exec(\"try:\\n import importlib.util as u\\n s=u.spec_from_file_location('depthlaw_frozen_rt','$ROOT/src/depthlaw/frozen_rt.py')\\n m=u.module_from_spec(s); s.loader.exec_module(m); m.install()\\nexcept Exception as e:\\n sys.stderr.write('frozen_rt not loaded: %r\\\\n' % (e,))\")"
for PY in "$ROOT/.venv/bin/python" python3; do
  [ -x "$(command -v "$PY")" ] || continue
  SP=$("$PY" -c "import site; print(site.getsitepackages()[0])")
  printf '%s\n' "$LINE" > "$SP/depthlaw_frozen_rt.pth"
  echo "installed $SP/depthlaw_frozen_rt.pth"
done
python3 scripts/frozen_guard.py immutable apply && echo "immutable attribute set on $(python3 scripts/frozen_guard.py list | wc -l) frozen files"
