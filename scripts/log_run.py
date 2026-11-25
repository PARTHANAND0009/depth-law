#!/usr/bin/env python3
"""Append-only run ledger (results/ledger.jsonl). Two modes.

RUN (default):
  log_run.py --tag T --seed S --status CONFIRMATORY|EXPLORATORY [--in F ...] [--out F ...] -- <command>
  Runs the command under `nice -n 10 prlimit --as=1800000000`, then appends one JSON line: UTC times, git
  HEAD, dirty flag, command, tag, seed, status, sha256 of each declared input/output, exit code, peak RSS
  of the child (docs/guards.md 3.4). Exits with the command's code.
NOTE (any non-RUN --kind, e.g. DEVIATION, BUDGET, AGENT_EDIT, HOOK_PROPOSAL, PLAN, COMMIT, PENDING_AGENT_EDITS_NOT_FOUND):
  log_run.py --kind KIND --tag T --note "text" [--status ...] [--file F ...]
  Appends one JSON line (UTC time, git HEAD, dirty flag, kind, tag, status, note, sha256 of each --file);
  runs nothing. Used for repo-changing actions that are not computations.
EXPLORATORY entries need EXPLORATORY in --tag (CLAUDE.md integrity rules)."""
import argparse, datetime, hashlib, json, pathlib, resource, subprocess, sys

root = pathlib.Path(__file__).resolve().parents[1]
ap = argparse.ArgumentParser()
ap.add_argument("--kind", default="RUN")
ap.add_argument("--tag", required=True)
ap.add_argument("--seed", default=None)
ap.add_argument("--status", default=None, choices=["CONFIRMATORY", "EXPLORATORY", "ADMIN"])
ap.add_argument("--note", default=None)
ap.add_argument("--note-file", default=None, help="read the note text from a file")
ap.add_argument("--in", dest="inputs", action="append", default=[])
ap.add_argument("--out", dest="outputs", action="append", default=[])
ap.add_argument("--file", dest="files", action="append", default=[])
ap.add_argument("--as-bytes", default="1800000000")
ap.add_argument("cmd", nargs=argparse.REMAINDER)
a = ap.parse_args()
cmd = a.cmd[1:] if a.cmd[:1] == ["--"] else a.cmd
if a.note_file:
    a.note = pathlib.Path(a.note_file).read_text().strip()
if a.status == "EXPLORATORY" and "EXPLORATORY" not in a.tag.upper():
    sys.exit("log_run.py: EXPLORATORY entries need EXPLORATORY in --tag (CLAUDE.md integrity rules)")


def git(*args):
    return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True).stdout.strip()


def sha(p):
    f = root / p if not pathlib.Path(p).is_absolute() else pathlib.Path(p)
    return hashlib.sha256(f.read_bytes()).hexdigest() if f.is_file() else None


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")


led = root / "results" / "ledger.jsonl"
base = {"kind": a.kind, "git_head": git("rev-parse", "HEAD"),
        "dirty": bool(git("status", "--porcelain", "--untracked-files=no")), "tag": a.tag, "status": a.status}
if a.kind != "RUN":
    if cmd:
        sys.exit("log_run.py: a NOTE-type entry runs no command")
    if not a.note:
        sys.exit("log_run.py: --note is required for non-RUN entries")
    rec = {"utc": now(), **base, "note": a.note, "files": {p: sha(p) for p in a.files}}
    with open(led, "a") as f:
        f.write(json.dumps(rec) + "\n")
    print(f"log_run: {a.kind} {a.tag} -> {led.relative_to(root)}", file=sys.stderr)
    sys.exit(0)

if not cmd:
    sys.exit("log_run.py: no command after --")
if a.seed is None or a.status in (None, "ADMIN"):
    sys.exit("log_run.py: RUN entries need --seed and --status CONFIRMATORY|EXPLORATORY")
rec = {"utc_start": now(), **base, "command": cmd, "seed": a.seed, "note": a.note,
       "as_limit_bytes": int(a.as_bytes), "inputs": {p: sha(p) for p in a.inputs}}
# 2026-11-25 (INC-2026-11-25-required-macros): frozen files are hashed before and after every run; a run that
# changes one is recorded with frozen_violation and log_run exits 3, whatever the command's own exit code.
sys.path.insert(0, str(root / "scripts"))
import frozen_guard  # noqa: E402
snap0 = frozen_guard.snapshot(root)
p = subprocess.run(["nice", "-n", "10", "prlimit", f"--as={a.as_bytes}", "--", *cmd], cwd=root)
snap1 = frozen_guard.snapshot(root)
viol = sorted(k for k in set(snap0) | set(snap1) if snap0.get(k) != snap1.get(k))
rec.update(utc_end=now(), exit_code=p.returncode, peak_rss_kb=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
           outputs={o: sha(o) for o in a.outputs})
if viol:
    rec["frozen_violation"] = viol
with open(led, "a") as f:
    f.write(json.dumps(rec) + "\n")
print(f"log_run: {a.tag} exit {p.returncode}, peak RSS {rec['peak_rss_kb']} kB -> {led.relative_to(root)}", file=sys.stderr)
if viol:
    print("log_run: FROZEN FILES CHANGED DURING THE RUN: " + ", ".join(viol), file=sys.stderr)
    sys.exit(3)
sys.exit(p.returncode)
