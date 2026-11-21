#!/usr/bin/env python3
"""log_run.py --tag T --seed S --status CONFIRMATORY|EXPLORATORY [--in F ...] [--out F ...] -- <command>
Runs the command under `nice -n 10 prlimit --as=1800000000`, then appends one JSON line to
results/ledger.jsonl: UTC time, git HEAD, dirty flag, command, tag, seed, status, sha256 of each
declared input/output, exit code, peak RSS of the child (docs/guards.md 3.4). Exits with the command's code."""
import argparse, datetime, hashlib, json, pathlib, resource, subprocess, sys

root = pathlib.Path(__file__).resolve().parents[1]
ap = argparse.ArgumentParser()
ap.add_argument("--tag", required=True)
ap.add_argument("--seed", required=True)
ap.add_argument("--status", required=True, choices=["CONFIRMATORY", "EXPLORATORY"])
ap.add_argument("--in", dest="inputs", action="append", default=[])
ap.add_argument("--out", dest="outputs", action="append", default=[])
ap.add_argument("--as-bytes", default="1800000000")
ap.add_argument("cmd", nargs=argparse.REMAINDER)
a = ap.parse_args()
cmd = a.cmd[1:] if a.cmd[:1] == ["--"] else a.cmd
if not cmd:
    sys.exit("log_run.py: no command after --")
if a.status == "EXPLORATORY" and "EXPLORATORY" not in a.tag.upper():
    sys.exit("log_run.py: EXPLORATORY runs need EXPLORATORY in --tag (CLAUDE.md integrity rules)")


def git(*args):
    return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True).stdout.strip()


def sha(p):
    f = root / p if not pathlib.Path(p).is_absolute() else pathlib.Path(p)
    return hashlib.sha256(f.read_bytes()).hexdigest() if f.is_file() else None


rec = {"utc_start": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
       "git_head": git("rev-parse", "HEAD"), "dirty": bool(git("status", "--porcelain", "--untracked-files=no")),
       "command": cmd, "tag": a.tag, "seed": a.seed, "status": a.status, "as_limit_bytes": int(a.as_bytes),
       "inputs": {p: sha(p) for p in a.inputs}}
p = subprocess.run(["nice", "-n", "10", "prlimit", f"--as={a.as_bytes}", "--", *cmd], cwd=root)
rec.update(utc_end=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
           exit_code=p.returncode, peak_rss_kb=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
           outputs={o: sha(o) for o in a.outputs})
led = root / "results" / "ledger.jsonl"
with open(led, "a") as f:
    f.write(json.dumps(rec) + "\n")
print(f"log_run: {a.tag} exit {p.returncode}, peak RSS {rec['peak_rss_kb']} kB -> {led.relative_to(root)}", file=sys.stderr)
sys.exit(p.returncode)
