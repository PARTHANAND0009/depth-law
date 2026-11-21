#!/usr/bin/env bash
# HUMAN ONLY. Applies the frozen-file changes that Claude staged on 2026-11-21 (parts A1, A4, A5) and could
# not apply itself: the frozen-file guards (permission deny Edit(prereg/**), .claude/hooks/protect_frozen.py,
# pre-commit) block Claude from writing prereg/ and .claude/hooks/. Review each file first:
#   hooks/proposed/protect_frozen.py   narrowed kill rule + explicit S5 guard (A4); write-once prereg/deviations/, editable prereg/INDEX.md (A1)
#   hooks/proposed/stop_check.py       S5 chunk-output exemption (A5)
#   hooks/proposed/pre-commit          allows new prereg/deviations/* files and prereg/INDEX.md (A1)
#   reports/pending_frozen_changes/D-A0.md, INDEX.md
# Tests: bash hooks/tests/test_kill_hook.sh ; bash hooks/tests/test_stop_s5.sh
# Also needed by hand in .claude/settings.json (deny rules take precedence over any allow, so the broad rule
# must be replaced): "Edit(prereg/**)" -> "Edit(prereg/HR_revised.md)", "Edit(prereg/DEVIATIONS.md)",
# "Edit(prereg/HASH.txt)", "Edit(prereg/amendments/**)", "Edit(prereg/deviations/**)". Then review in /hooks.
set -euo pipefail
cd "$(dirname "$0")/../.."
bash hooks/tests/test_kill_hook.sh hooks/proposed/protect_frozen.py
bash hooks/tests/test_stop_s5.sh hooks/proposed/stop_check.py
install -m 755 hooks/proposed/protect_frozen.py .claude/hooks/protect_frozen.py
install -m 755 hooks/proposed/stop_check.py .claude/hooks/stop_check.py
install -m 755 hooks/proposed/pre-commit scripts/pre-commit
install -m 755 hooks/proposed/pre-commit .git/hooks/pre-commit
mkdir -p prereg/deviations
sed '1,4d' reports/pending_frozen_changes/D-A0.md > prereg/deviations/D-A0.md
sed '1d' reports/pending_frozen_changes/INDEX.md > prereg/INDEX.md
git add .claude/hooks/protect_frozen.py .claude/hooks/stop_check.py scripts/pre-commit prereg/deviations/D-A0.md prereg/INDEX.md
git commit -m "human: install narrowed kill hook, S5 chunk exemption, deviations path; add D-A0 and prereg index"
echo "applied; now edit .claude/settings.json deny rules as described above"
