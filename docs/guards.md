# Guards (from the human's instruction of 2026-11-21, section 3)

Saved by Claude at G0. The human's plan said to save this section here before pasting the prompt; it was not in the repo, so this file records what was received.

## 3.1 Edits to skeptic.md, replicator.md, stats-reviewer.md, reviewer-sim.md
MISSING: section 3.1 was not included in the message that reached Claude (it began at 3.2). These four agent files are unchanged at G0.

## 3.2 New agents
Created verbatim: `.claude/agents/novelty-scout.md`, `citation-verifier.md`, `claim-auditor.md`, `experiment-planner.md`.

## 3.3 Run schedule, gating and budget tiers
- `gates.yaml` (verbatim). Requirements per gate:
  - G0: none.
  - G1: replicator, stats-reviewer, skeptic, novelty-scout, experiment-planner, plus responses.
  - G2: stats-reviewer.
  - G3: replicator, stats-reviewer, skeptic, plus responses.
  - G4: none.
  - G5: claim-auditor, skeptic, reviewer-sim, novelty-scout, plus responses.
  - G6: citation-verifier, claim-auditor, replicator, plus responses.
- How agent outputs gate progress:
  1. Each subagent output is saved verbatim to `reports/gates/<G>/<agent>.md`.
  2. `responses.md` answers each finding as fixed (commit), rebutted (reason) or deferred (Limitations).
  3. PROGRESS.md is set to `STATUS: AWAITING GO <G>`.
  4. The Stop hook runs `gate_check.py` and refuses the stop while a required report is missing or says BLOCK.
- Cut order if Pro usage is short:
  1. reviewer-sim: G5 only.
  2. experiment-planner: G1 only.
  3. novelty-scout: G5 only.
  4. skeptic: switch to Sonnet.
- Never cut: replicator and stats-reviewer at G1, G3 and G6.

## 3.4 Hooks, scripts and settings
- `.claude/settings.json`: deny rules plus PreToolUse and Stop hooks. The `.claude/hooks/**` deny rules are added only after GO G0.
- `.claude/hooks/protect_frozen.py` and `.claude/hooks/stop_check.py`: verbatim.
- `scripts/check_numbers.py`: verbatim except two changes:
  1. The bare-number regex lookbehind `(?<ǃ[\w.\-])` (U+01C3, a regex error) is written as `(?<![\w.\-])`.
  2. A missing `paper/numbers.tex` is reported as a failure instead of raising.
- `scripts/gate_check.py <G>`:
  - Loads `gates.yaml`.
  - Fails if a required `reports/gates/<G>/<agent>.md` is missing, contains `VERDICT: BLOCK`, or has no `VERDICT:`/`RECOMMEND:` line.
  - Fails if `needs_responses` is true and `responses.md` is missing.
  - Exits 1 on any failure.
- `scripts/verify_bib.py`:
  - Takes each `paper/refs.bib` entry's arXiv id (eprint/journal/url) or DOI and fetches the title from export.arxiv.org or api.crossref.org.
  - Waits 3 s between calls and caches to `.cache/bib.json`.
  - Fails an entry if the normalized-title difflib ratio is < 0.85, the lookup fails, or it has neither id nor DOI.
  - Exits 1 on any failure.
- `scripts/pre-commit`: verbatim. Installed to `.git/hooks/pre-commit`.
- `scripts/log_run.py --tag --seed --status [--in F] [--out F] -- <cmd>`:
  - Runs under `nice -n 10 prlimit --as=1800000000`.
  - Appends to `results/ledger.jsonl`: UTC times, git HEAD, dirty flag, command, tag, seed, CONFIRMATORY/EXPLORATORY, sha256 of inputs and outputs, exit code, child peak RSS.
  - Refuses an EXPLORATORY run whose tag lacks "EXPLORATORY".
- Model names go in `paper/models.tex` macros; generated tables go in `paper/generated/`.
- `make_numbers.py` writes the `% inputs:` header with the sha256 of every results file it reads, plus the git commit. It does not exist yet; it is built at G1.
- CLAUDE.md "Integrity rules" block: appended verbatim.
