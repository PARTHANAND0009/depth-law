#!/usr/bin/env python3
"""Frozen-path guard (added 2026-11-25 after integrity incident INC-2026-11-25-required-macros).

The incident: a non-frozen script (scripts/gen_required_macros.py) rewrote a frozen file
(config/required_macros.json). The Claude Code hook only inspects tool calls and command lines, and the old
pre-commit only checked prereg/ and the ledger, so nothing stopped it. This module closes that route at three
points that do not depend on how the write happened:

  check-staged    (pre-commit) any staged modify/delete of a frozen path fails; new files are allowed only under
                  add-only prefixes (prereg/) or when bootstrapping a listed frozen file; the ledger must be
                  append-only; paper/numbers.tex must match the outputs hash of a ledger RUN of make_numbers.py.
  check-worktree  frozen files on disk must equal HEAD (used by log_run.py before/after every run and by tests).
  immutable       `apply` sets the Linux immutable attribute (chattr +i) on every frozen file on disk, which also
                  stops root; `verify` lists frozen files without it. Removing it (chattr -i) is a human action.

The runtime layer (src/depthlaw/frozen_rt.py) blocks Python writes to frozen paths as they happen.
A human-authorized change passes check-staged only with DEPTHLAW_FROZEN_OVERRIDE=1 and a ledger NOTE whose tag
starts with "HUMAN-AUTHORIZED FROZEN CHANGE" and whose --file hashes equal the staged content.

Usage: frozen_guard.py {check-staged|check-worktree|immutable apply|immutable verify|list} [--repo DIR]
Exit 0 = ok, 1 = violation, 2 = usage error.
"""
import hashlib, json, os, pathlib, subprocess, sys


def load_cfg(repo):
    return json.loads((pathlib.Path(repo) / "config" / "frozen_paths.json").read_text())


def is_frozen(rel, cfg):
    rel = rel.replace("\\", "/")
    if any(part in rel.split("/") for part in cfg["ignore_parts"]):
        return False
    if rel in cfg["mutable_exceptions"]:
        return False
    return rel in cfg["frozen_files"] or any(rel.startswith(p) for p in cfg["frozen_prefixes"])


def git(repo, *args, binary=False, check=False):
    p = subprocess.run(["git", *args], cwd=repo, capture_output=True, check=check)
    return p.stdout if binary else p.stdout.decode()


def sha(b):
    return hashlib.sha256(b).hexdigest() if b is not None else None


def staged_bytes(repo, path):
    p = subprocess.run(["git", "show", f":{path}"], cwd=repo, capture_output=True)
    return p.stdout if p.returncode == 0 else None


def head_bytes(repo, path):
    p = subprocess.run(["git", "show", f"HEAD:{path}"], cwd=repo, capture_output=True)
    return p.stdout if p.returncode == 0 else None


def ledger_records(raw):
    out = []
    for line in (raw or b"").decode(errors="replace").splitlines():
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    return out


def check_staged(repo):
    cfg = load_cfg(repo)
    errs, frozen_changes = [], []
    rows = [l.split("\t") for l in git(repo, "diff", "--cached", "--name-status", "--no-renames").splitlines() if l]
    led_path = "results/ledger.jsonl"
    led_staged = staged_bytes(repo, led_path)
    recs = ledger_records(led_staged)
    for st, path in ((r[0], r[-1]) for r in rows):
        wm = cfg["writer_managed"].get(path)
        if wm and wm["rule"] == "append-only":
            old, new = head_bytes(repo, path), staged_bytes(repo, path)
            if st == "D" or (old is not None and (new is None or not new.startswith(old))):
                errs.append(f"{path}: append-only (HEAD content must be a prefix of the staged content)")
            continue
        if wm and wm["rule"] == "ledger-provenance":
            new = staged_bytes(repo, path)
            h = sha(new)
            ok = any(r.get("kind") == "RUN" and r.get("exit_code") == 0 and (r.get("outputs") or {}).get(path) == h
                     and any(w in " ".join(r.get("command", [])) for w in wm["writers"]) for r in recs)
            if st != "D" and not ok:
                errs.append(f"{path}: staged content (sha256 {h[:12]}) is not the output of a logged "
                            f"{'/'.join(wm['writers'])} run in the staged ledger (hand edit or unlogged write)")
            continue
        if not is_frozen(path, cfg):
            continue
        if st == "A" and (any(path.startswith(p) for p in cfg["add_only_prefixes"]) or path in cfg["frozen_files"]):
            continue  # write-once additions, and bootstrap of a newly listed guard file
        frozen_changes.append((st, path))
    if frozen_changes:
        ov = cfg["override"]
        if os.environ.get(ov["env"]) == "1":
            approved = {}
            for r in recs:
                if r.get("kind") != "RUN" and str(r.get("tag", "")).startswith(ov["ledger_tag_prefix"]):
                    approved.update(r.get("files") or {})
            missing = [p for st, p in frozen_changes if approved.get(p, "absent") != sha(staged_bytes(repo, p))]
            if missing:
                errs += [f"{p}: override set but no '{ov['ledger_tag_prefix']}' ledger NOTE hashes this staged content"
                         for p in missing]
            else:
                print("frozen_guard: HUMAN-AUTHORIZED override applied for: " + ", ".join(p for _, p in frozen_changes),
                      file=sys.stderr)
        else:
            errs += [f"{p}: frozen path {'deleted' if st == 'D' else 'modified'} (status {st})" for st, p in frozen_changes]
    return errs


def frozen_files_on_disk(repo):
    cfg = load_cfg(repo)
    repo = pathlib.Path(repo)
    found = set(f for f in cfg["frozen_files"] if (repo / f).is_file())
    for pre in cfg["frozen_prefixes"]:
        d = repo / pre
        if d.is_dir():
            for f in d.rglob("*"):
                rel = f.relative_to(repo).as_posix()
                if f.is_file() and is_frozen(rel, cfg):
                    found.add(rel)
    return sorted(found)


def snapshot(repo):
    repo = pathlib.Path(repo)
    return {f: sha((repo / f).read_bytes()) for f in frozen_files_on_disk(repo)}


def check_worktree(repo):
    """Frozen files whose on-disk content differs from HEAD, or that are missing from disk."""
    cfg = load_cfg(repo)
    errs = []
    tracked = [p for p in git(repo, "ls-files").splitlines() if is_frozen(p, cfg)]
    for p in tracked:
        f = pathlib.Path(repo) / p
        if not f.is_file():
            errs.append(f"{p}: frozen file missing from the working tree")
        elif sha(f.read_bytes()) != sha(head_bytes(repo, p)) and head_bytes(repo, p) is not None:
            errs.append(f"{p}: frozen file differs from HEAD")
    return errs


def immutable(repo, action):
    files = frozen_files_on_disk(repo)
    if action == "apply":
        bad = [f for f in files if subprocess.run(["chattr", "+i", f], cwd=repo, capture_output=True).returncode]
        for f in bad:
            print(f"frozen_guard: chattr +i failed for {f}", file=sys.stderr)
        return bad
    out = subprocess.run(["lsattr", *files], cwd=repo, capture_output=True, text=True).stdout.splitlines() if files else []
    return [l.split()[-1] for l in out if "i" not in l.split()[0]]


def main(argv):
    repo = pathlib.Path(__file__).resolve().parents[1]
    if "--repo" in argv:
        i = argv.index("--repo"); repo = pathlib.Path(argv[i + 1]).resolve(); argv = argv[:i] + argv[i + 2:]
    if not argv:
        print(__doc__, file=sys.stderr); return 2
    if argv[0] == "check-staged":
        errs = check_staged(repo)
    elif argv[0] == "check-worktree":
        errs = check_worktree(repo)
    elif argv[0] == "list":
        print("\n".join(frozen_files_on_disk(repo))); return 0
    elif argv[0] == "immutable" and len(argv) > 1 and argv[1] in ("apply", "verify"):
        errs = [f"{f}: not immutable" for f in immutable(repo, argv[1])]
    else:
        print(__doc__, file=sys.stderr); return 2
    for e in errs:
        print(f"frozen_guard: {e}", file=sys.stderr)
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
