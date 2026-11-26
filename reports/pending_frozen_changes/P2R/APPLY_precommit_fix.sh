#!/usr/bin/env bash
# HUMAN ONLY (or Claude with the human's explicit one-time authorization). Installs reports/pending_frozen_changes/P2R/
# pre-commit.proposed as scripts/pre-commit and .git/hooks/pre-commit. Needed because, after the human-authorized
# DEVIATIONS.md line (e7c79a1), the legacy check rejects every commit ("prereg/ differs from 7725c5b").
# The replacement excludes prereg/DEVIATIONS.md from the byte comparison with 7725c5b and requires it to be append-only.
set -euo pipefail
cd "$(dirname "$0")/../../.."
P=reports/pending_frozen_changes/P2R/pre-commit.proposed
bash "$P"   # the proposed check must pass on what is staged now
chattr -i scripts/pre-commit 2>/dev/null || true
install -m 755 "$P" scripts/pre-commit
install -m 755 "$P" .git/hooks/pre-commit
python3 scripts/log_run.py --kind NOTE --tag "HUMAN-AUTHORIZED FROZEN CHANGE: pre-commit legacy check accepts the append-only DEVIATIONS.md" \
  --status ADMIN --note "Installed reports/pending_frozen_changes/P2R/pre-commit.proposed as scripts/pre-commit: prereg/DEVIATIONS.md excluded from the byte comparison with 7725c5b and required to be append-only against 7725c5b and HEAD; all other checks unchanged." \
  --file scripts/pre-commit
git add scripts/pre-commit results/ledger.jsonl
DEPTHLAW_FROZEN_OVERRIDE=1 git commit -m "human-authorized: pre-commit accepts the append-only DEVIATIONS.md (legacy check blocked every commit after e7c79a1)" \
  -- scripts/pre-commit results/ledger.jsonl   # explicit pathspec: nothing else staged goes into this commit
chattr +i scripts/pre-commit
echo "installed: $(git rev-parse --short HEAD); push when ready"
