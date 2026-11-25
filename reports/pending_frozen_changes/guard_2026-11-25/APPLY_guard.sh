#!/usr/bin/env bash
# HUMAN ONLY. Applies the frozen-file parts of the guard hardening after integrity incident
# INC-2026-11-25-required-macros (decision at GO G4, 2026-11-25). Claude cannot write these paths.
# Review first:
#   hooks/proposed/protect_frozen.py (diff: reports/pending_frozen_changes/guard_2026-11-25/protect_frozen.diff)
#   reports/pending_frozen_changes/guard_2026-11-25/INC-2026-11-25-required-macros.md   -> prereg/deviations/
#   reports/pending_frozen_changes/guard_2026-11-25/DEVIATIONS_append.txt                -> appended to prereg/DEVIATIONS.md
#   .claude/settings.json: deny Edit/Write on the new guard files (done below with python, shown before writing)
# The non-frozen layers (pre-commit, runtime .pth guard, chattr +i, log_run check) are already installed by Claude
# with scripts/install_guard.sh; this script re-runs it at the end so the newly changed files are immutable too.
set -euo pipefail
cd "$(dirname "$0")/../../.."
G=reports/pending_frozen_changes/guard_2026-11-25
bash hooks/tests/test_frozen_hook.sh hooks/proposed/protect_frozen.py
bash hooks/tests/test_kill_hook.sh hooks/proposed/protect_frozen.py
.venv/bin/python -m pytest -q tests/test_frozen_guard.py -k "not real_repo"
[ -e prereg/deviations/INC-2026-11-25-required-macros.md ] && { echo "REFUSED: incident record already installed" >&2; exit 1; }
# the immutable attribute must be lifted on exactly the files this script changes
chattr -i .claude/hooks/protect_frozen.py .claude/settings.json prereg/DEVIATIONS.md 2>/dev/null || true
install -m 755 hooks/proposed/protect_frozen.py .claude/hooks/protect_frozen.py
cp "$G/INC-2026-11-25-required-macros.md" prereg/deviations/INC-2026-11-25-required-macros.md
cat "$G/DEVIATIONS_append.txt" >> prereg/DEVIATIONS.md
python3 - <<'EOF'
import json
p = ".claude/settings.json"; s = json.load(open(p))
add = [f"{t}({f})" for f in ("config/frozen_paths.json", "scripts/frozen_guard.py", "src/depthlaw/frozen_rt.py",
                             "scripts/pre-commit", "scripts/install_guard.sh", "scripts/gen_required_macros.py",
                             "config/required_macros.json", "config/required_macros.md", "hooks/proposed/**")
       for t in ("Edit", "Write")]
deny = s["permissions"]["deny"]
deny += [a for a in add if a not in deny]
json.dump(s, open(p, "w"), indent=2); open(p, "a").write("\n")
print("settings.json deny rules added:", add)
EOF
python3 scripts/log_run.py --kind NOTE --tag "HUMAN-AUTHORIZED FROZEN CHANGE: guard hardening + incident record (INC-2026-11-25-required-macros)" \
  --status ADMIN --note "Human ran APPLY_guard.sh: installed hooks/proposed/protect_frozen.py, added prereg/deviations/INC-2026-11-25-required-macros.md, appended one line to prereg/DEVIATIONS.md, added settings.json deny rules for the guard files." \
  --file .claude/hooks/protect_frozen.py --file .claude/settings.json --file prereg/DEVIATIONS.md
git add .claude/hooks/protect_frozen.py .claude/settings.json prereg/DEVIATIONS.md prereg/deviations/INC-2026-11-25-required-macros.md results/ledger.jsonl
# The new commit check runs with the human override (needs the NOTE above). The legacy check in scripts/pre-commit
# compares prereg/ with 7725c5b and rejects any DEVIATIONS.md line, so this one commit skips the hook after the
# new check has passed explicitly.
DEPTHLAW_FROZEN_OVERRIDE=1 python3 scripts/frozen_guard.py check-staged
git commit --no-verify -m "human: guard hardening after INC-2026-11-25-required-macros; incident record; DEVIATIONS entry"
bash scripts/install_guard.sh
echo "applied: $(git rev-parse --short HEAD). Review the hooks in /hooks, then push."
