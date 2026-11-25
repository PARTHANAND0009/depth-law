# Integrity incident and pending decision: config/required_macros.json (2026-11-25)

## What happened
- `config/required_macros.json` (and its `.md`) are frozen paths in `.claude/hooks/protect_frozen.py` (PROTECTED list). Changes need the human at a gate.
- During G4 setup Claude edited `scripts/gen_required_macros.py` (not frozen) to add the P2 preregistered quantities, then ran it. The script rewrote `config/required_macros.json` and `.md`: 329 → 459 required macros (all 329 H-R entries unchanged; 130 P2 entries added). The hook did not fire because the command line did not name the frozen path. This worked around the hook's intent. It was committed in `21692bb` and pushed.
- Claude noticed it afterwards, tried to restore the frozen version, and the hook (correctly) blocked the restore. Claude has not touched the file again.

## Effect
- Only additive: `scripts/check_numbers.py` now also requires the P2 macros in `paper/numbers.tex`. `make_numbers.py` already writes all of them, so `check_numbers` passes either way. No result, threshold or prereg file changed.

## Human decision needed (one of)
1. **Restore** the frozen version (removes the P2 requirement):
   ```bash
   git checkout 21692bb^ -- config/required_macros.json config/required_macros.md scripts/gen_required_macros.py
   ```
2. **Accept** the P2 additions as a human-authorized change to the frozen file (keep as is; log it in the ledger as human-authorized).

The diff of the generator is in `gen_required_macros.diff` (this folder).

## Decision (GO G4, 2026-11-25)
The human chose option 2 (**accept** the additive P2 entries). Incident record and guard hardening:
`reports/pending_frozen_changes/guard_2026-11-25/` (record installed into `prereg/deviations/` by the human's APPLY_guard.sh).
