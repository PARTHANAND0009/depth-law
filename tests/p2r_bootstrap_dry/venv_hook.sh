#!/usr/bin/env bash
# DRYRUN venv (test only; disk is too small here for a second torch install). <run>/.venv/bin/python is a wrapper that
# runs the project's existing CPU venv python (same pinned packages, requirements.lock), with the sandbox checkout's
# src/ first on PYTHONPATH and every '--device cuda' argument rewritten to '--device cpu'. Nothing else is changed.
set -euo pipefail
RUN=${1:?run checkout}; PV=${PROJECT_VENV:?PROJECT_VENV}
mkdir -p "$RUN/.venv/bin"
cat > "$RUN/.venv/bin/python" <<WRAP
#!/usr/bin/env bash
export PYTHONPATH="\${PYTHONPATH:-$RUN/src}"
a=(); prev=""
for x in "\$@"; do if [ "\$prev" = --device ] && [ "\$x" = cuda ]; then x=cpu; fi; a+=("\$x"); prev=\$x; done
exec "$PV/bin/python" "\${a[@]}"
WRAP
chmod +x "$RUN/.venv/bin/python"; ln -sf python "$RUN/.venv/bin/python3"
cat > "$RUN/.venv/bin/activate" <<ACT
export VIRTUAL_ENV="$RUN/.venv"
case ":\$PATH:" in *":$RUN/.venv/bin:"*) ;; *) export PATH="$RUN/.venv/bin:\$PATH";; esac
ACT
echo "DRYRUN venv wrapper -> $PV/bin/python (device cuda -> cpu)"
