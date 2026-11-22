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
#
# P2 additions (human decision 2026-11-22): the same run also installs
#   reports/pending_frozen_changes/P2_prompt_vs_fact.md -> prereg/P2_prompt_vs_fact.md (3-line staging comment removed),
#   prereg/HASH_P2.txt (sha256 of the installed file), tag prereg-P2, and
#   reports/pending_frozen_changes/gates_PREREG.txt appended to gates.yaml (gate PREREG).
# It refuses to run while the staged prereg still has the CI-method placeholder.
set -euo pipefail
cd "$(dirname "$0")/../.."
P2=reports/pending_frozen_changes/P2_prompt_vs_fact.md
if grep -q "filled from the simulation report" "$P2"; then echo "REFUSED: CI method not yet filled in $P2" >&2; exit 1; fi
[ -e prereg/P2_prompt_vs_fact.md ] && { echo "REFUSED: prereg/P2_prompt_vs_fact.md already exists" >&2; exit 1; }
bash hooks/tests/test_kill_hook.sh hooks/proposed/protect_frozen.py
bash hooks/tests/test_stop_s5.sh hooks/proposed/stop_check.py
install -m 755 hooks/proposed/protect_frozen.py .claude/hooks/protect_frozen.py
install -m 755 hooks/proposed/stop_check.py .claude/hooks/stop_check.py
install -m 755 hooks/proposed/pre-commit scripts/pre-commit
install -m 755 hooks/proposed/pre-commit .git/hooks/pre-commit
mkdir -p prereg/deviations
sed '1,4d' reports/pending_frozen_changes/D-A0.md > prereg/deviations/D-A0.md
sed '1d' reports/pending_frozen_changes/INDEX.md > prereg/INDEX.md
sed '1,3d' "$P2" > prereg/P2_prompt_vs_fact.md
head -1 prereg/P2_prompt_vs_fact.md | grep -q '^# Preregistration P2' || { echo "REFUSED: unexpected first line after stripping" >&2; exit 1; }
sha256sum prereg/P2_prompt_vs_fact.md > prereg/HASH_P2.txt
grep -q '^  PREREG:' gates.yaml || cat reports/pending_frozen_changes/gates_PREREG.txt >> gates.yaml
python3 -c "import yaml; g = yaml.safe_load(open('gates.yaml'))['gates']; assert 'PREREG' in g, g; print('gates.yaml PREREG:', g['PREREG'])"
git add .claude/hooks/protect_frozen.py .claude/hooks/stop_check.py scripts/pre-commit prereg/deviations/D-A0.md prereg/INDEX.md \
        prereg/P2_prompt_vs_fact.md prereg/HASH_P2.txt gates.yaml
git commit -m "human: install narrowed kill hook, S5 chunk exemption, deviations path; add D-A0 and prereg index; freeze P2 preregistration; add gate PREREG"
git tag prereg-P2
echo "applied (prereg-P2 = $(git rev-parse --short HEAD)); now edit .claude/settings.json deny rules as described above"
