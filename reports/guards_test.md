# G0 guard tests (2026-11-21, ~10:00-10:06 UTC)

- **Where:** branch `guards-test`, in a separate git worktree under the session scratchpad so the running S5 job and the replicator's files were untouched.
- **Base:** commit 3c87115 (the G0 guard files).
- **Cleanup:** the branch was deleted after the tests (`git branch -D`, last commit 735be7d). It was never pushed.
- **Hooks are live in this session without a restart.** The first probe, `echo "probe: kill-word ..."`, was blocked by the PreToolUse hook.

## Results

| # | deliberate violation | layer | result |
|---|---|---|---|
| 1a | Edit tool on `prereg/HR_revised.md` | PreToolUse hook | BLOCKED ("is frozen (prereg/)") |
| 1b | `sed -i` on `prereg/HR_revised.md` | PreToolUse hook | BLOCKED ("shell write touching a frozen path") |
| 1c | `python3 -c "open(...).write(...)"` on `prereg/HR_revised.md`, then `git commit` | PreToolUse: **not blocked** (gap). pre-commit: BLOCKED | the file changed on disk; the commit was refused ("frozen preregistration modified"); the file was restored |
| 2a | bare numbers `0.040`, `0.30` in `paper/test.tex`, `git commit` | pre-commit → check_numbers.py | BLOCKED, but on "paper/numbers.tex missing", the first failure |
| 2b | same file; check_numbers.py run unchanged with an in-memory `numbers.tex` fixture (`scratchpad/cn_harness.py`, no file written) | check_numbers.py | FAIL as intended: flags `paper/test.tex:2: bare number '0.040'` and `'0.30'`. `2026` and `7B` are allowed. All 329 required macros are reported missing |
| 3 | `paper/test.bib` with a fake `eprint = {2611.99999}`, an entry with no id, and a real one (2308.09124) | verify_bib.py | exit 1: `fake2026depth: arxiv:2611.99999 not found`; `noid2025: no arXiv id or DOI`. The real entry passed |
| 4a | `STATUS: AWAITING GO TEST`, no reports | stop_check.py (called with the harness JSON) | exit 2 (stop refused): "gate TEST: not defined in gates.yaml", plus check_numbers failure for the dirty `paper/` |
| 4b | `STATUS: AWAITING GO G1`, no reports | stop_check.py | exit 2: all 5 G1 reports and responses.md listed as missing |
| 4c | same, with `stop_hook_active: true` | stop_check.py | exit 0, as designed (it blocks at most once per stop) |
| 4d | G1 reports present, one says `VERDICT: BLOCK` | gate_check.py | exit 1: "novelty-scout.md: VERDICT: BLOCK" |
| 4e | G1 reports present, one has no verdict line | gate_check.py | exit 1: "skeptic.md: no VERDICT: or RECOMMEND: line" |
| 5 | `kill -0 999999` (dummy PID) | PreToolUse hook | BLOCKED ("process control is human-only") |
| 6 | `git rebase HEAD` | PreToolUse hook | BLOCKED ("history-rewriting git commands are disabled") |
| 7a | Write a new `prereg/amendments/A99_guard_test.md`, commit | hook + pre-commit | allowed (as designed) |
| 7b | second Write to the same amendment | PreToolUse hook | BLOCKED ("amendments are write-once") |
| 7c | modify the committed amendment (python), commit | pre-commit | BLOCKED |
| 8a | `log_run.py --tag EXPLORATORY_guardtest --status EXPLORATORY -- <cmd>` | log_run.py | one ledger line: git HEAD, dirty, command, tag, seed, status, output sha256, exit 0, peak RSS 16228 kB |
| 8b | `--status EXPLORATORY` with tag `notlabelled` | log_run.py | refused (exit 1) |
| 8c | rewrite an existing ledger line, commit | pre-commit | BLOCKED ("ledger is append-only") |
| 8d | append a ledger line, commit | pre-commit | allowed (as designed) |

Not tested separately: the `permissions.deny` rules in `.claude/settings.json`. The PreToolUse hook blocks the same calls first.

## Gaps and false positives found

1. **Writes through an interpreter are not caught before commit.**
   - `python3 -c "open(p,'w')..."` (and perl, etc.) can change a frozen file in the working tree; the hook only matches rm/mv/cp/truncate/shred/tee/chmod, `sed -i` and `>`.
   - The pre-commit hook catches prereg/ and the ledger at commit.
   - Nothing catches a hand edit of `paper/numbers.tex` done this way: check_numbers.py checks the sha256 of its inputs, not of numbers.tex itself.
   - Not changed: the hook files are frozen.
2. **False positives.**
   - Any standalone word `kill`/`pkill`/`killall` in a Bash command is blocked, even in `echo` or `grep`.
   - Any command that both contains `>` (including `2>&1` and `>/dev/null`), `tee` or `cp` and names a protected path is blocked. That includes harmless reads such as `python3 scripts/gate_check.py G1 2>&1`.
   - Workaround used here: split the write and the protected-path command into separate calls.
3. **G1 can never pass with the current agent definitions.**
   - gate_check.py requires a `VERDICT:` or `RECOMMEND:` line in every G1 report.
   - The existing `skeptic`, `replicator` and `stats-reviewer` definitions do not ask for one. The skeptic ends with "accept / weak accept / reject".
   - Reviews must be saved verbatim and never edited, so G1 is blocked by construction until those definitions are edited.
   - Section 3.1 of the guards document, which presumably makes those edits, was not received (`docs/guards.md`).
4. **The Stop hook clashes with the always-running S5 job.**
   - stop_check.py refuses a stop when `results/` has uncommitted changes and PROGRESS.md does not.
   - S5 writes a new chunk to `results/S5/` about every 20 min, so after PROGRESS.md is committed the next stop is refused until PROGRESS.md is dirty again.
   - The environment's own Stop hook asks for everything to be committed, which pulls the other way.
   - `stop_hook_active` prevents a loop, but expect one refused stop per turn while S5 runs.
5. **`prlimit --as=1800000000` limits what can run.**
   - `import torch`, pandas and `library(lme4)` all succeed under it.
   - Loading any model beyond about 0.3B parameters in fp32 will not fit. The prior covariate used streamed weights for this reason (`src/depthlaw/hr/prior.py`).
