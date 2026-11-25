"""Tests for the frozen-path guard (2026-11-25, integrity incident INC-2026-11-25-required-macros).

The incident route: a non-frozen generator script rewrote frozen config/required_macros.json; the command line
never named the frozen path, so the tool-call hook did not fire, and the old pre-commit did not check config/.
Each test builds a throwaway git repo with the real guard files and replays one route.
"""
import hashlib, json, os, pathlib, shutil, subprocess, sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
GEN = ("import json\n"
       "json.dump({'macros': ['a', 'b', 'p2new']}, open('config/required_macros.json', 'w'))\n")


def run(cwd, *cmd, env=None, check=True):
    e = dict(os.environ, **(env or {}))
    e.pop("DEPTHLAW_FROZEN_OVERRIDE", None) if not (env and "DEPTHLAW_FROZEN_OVERRIDE" in env) else None
    p = subprocess.run(list(cmd), cwd=cwd, capture_output=True, text=True, env=e)
    if check and p.returncode:
        raise AssertionError(f"{cmd} failed: {p.stdout}{p.stderr}")
    return p


@pytest.fixture
def repo(tmp_path):
    r = tmp_path / "r"
    for rel in ("config/frozen_paths.json", "scripts/frozen_guard.py", "scripts/log_run.py",
                "src/depthlaw/frozen_rt.py"):
        (r / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(REPO / rel, r / rel)
    (r / "config/required_macros.json").write_text(json.dumps({"macros": ["a", "b"]}))
    (r / "scripts/gen_required_macros.py").write_text(GEN)
    (r / "prereg").mkdir()
    (r / "prereg/HR.md").write_text("frozen prereg\n")
    (r / "prereg/INDEX.md").write_text("index\n")
    (r / "results").mkdir()
    (r / "results/ledger.jsonl").write_text(json.dumps({"kind": "NOTE", "tag": "start"}) + "\n")
    (r / "paper").mkdir()
    (r / "scripts/make_numbers.py").write_text(
        "open('paper/numbers.tex','w').write('\\\\newcommand{\\\\x}{1}\\n')\n")
    run(r, "git", "init", "-q")
    run(r, "git", "-c", "user.email=t@t", "-c", "user.name=t", "add", "-A")
    run(r, "git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "base")
    return r


def staged_check(r, env=None):
    return run(r, sys.executable, "scripts/frozen_guard.py", "check-staged", env=env, check=False)


def test_incident_route_blocked_at_runtime(repo):
    """The exact incident: running the generator as a plain Python script. The runtime guard refuses the write."""
    code = ("import importlib.util as u, runpy, sys\n"
            "s = u.spec_from_file_location('rt', 'src/depthlaw/frozen_rt.py'); m = u.module_from_spec(s)\n"
            "s.loader.exec_module(m); m.install('.')\n"
            "sys.argv = ['scripts/gen_required_macros.py']\n"
            "runpy.run_path('scripts/gen_required_macros.py')\n")
    p = run(repo, sys.executable, "-c", code, check=False)
    assert p.returncode != 0 and "frozen path (runtime guard)" in p.stderr
    assert json.loads((repo / "config/required_macros.json").read_text()) == {"macros": ["a", "b"]}


def test_incident_route_blocked_at_commit(repo):
    """Same rewrite done outside Python (no runtime guard, e.g. R or shell): the commit check refuses it."""
    run(repo, sys.executable, "scripts/gen_required_macros.py")  # no runtime guard in this process
    run(repo, "git", "add", "-A")
    p = staged_check(repo)
    assert p.returncode == 1 and "config/required_macros.json: frozen path modified" in p.stderr


def test_incident_route_flagged_by_log_run(repo):
    """Same rewrite run through log_run: recorded as frozen_violation, exit code 3."""
    p = run(repo, sys.executable, "scripts/log_run.py", "--tag", "t", "--seed", "1", "--status", "CONFIRMATORY",
            "--", sys.executable, "scripts/gen_required_macros.py", check=False)
    assert p.returncode == 3 and "FROZEN FILES CHANGED" in p.stderr
    rec = json.loads((repo / "results/ledger.jsonl").read_text().splitlines()[-1])
    assert rec["frozen_violation"] == ["config/required_macros.json"]


def test_worktree_check(repo):
    run(repo, sys.executable, "scripts/gen_required_macros.py")
    p = run(repo, sys.executable, "scripts/frozen_guard.py", "check-worktree", check=False)
    assert p.returncode == 1 and "differs from HEAD" in p.stderr


def test_guard_files_themselves_frozen(repo):
    cfg = repo / "config/frozen_paths.json"
    cfg.write_text(cfg.read_text().replace('"gates.yaml",', ""))
    run(repo, "git", "add", "-A")
    p = staged_check(repo)
    assert p.returncode == 1 and "config/frozen_paths.json" in p.stderr


def test_prereg_rules(repo):
    (repo / "prereg/deviations").mkdir()
    (repo / "prereg/deviations/D-1.md").write_text("new deviation\n")
    (repo / "prereg/INDEX.md").write_text("index v2\n")
    run(repo, "git", "add", "-A")
    assert staged_check(repo).returncode == 0  # new files and INDEX.md allowed
    (repo / "prereg/HR.md").write_text("edited\n")
    run(repo, "git", "add", "-A")
    assert "prereg/HR.md" in staged_check(repo).stderr


def test_ledger_append_only(repo):
    led = repo / "results/ledger.jsonl"
    led.write_text(led.read_text() + json.dumps({"kind": "NOTE", "tag": "more"}) + "\n")
    run(repo, "git", "add", "-A")
    assert staged_check(repo).returncode == 0
    led.write_text(json.dumps({"kind": "NOTE", "tag": "rewritten"}) + "\n")
    run(repo, "git", "add", "-A")
    assert "append-only" in staged_check(repo).stderr


def test_numbers_tex_provenance(repo):
    (repo / "paper/numbers.tex").write_text("\\newcommand{\\x}{2}\n")  # hand edit
    run(repo, "git", "add", "-A")
    assert "not the output of a logged" in staged_check(repo).stderr
    run(repo, sys.executable, "scripts/log_run.py", "--tag", "n", "--seed", "1", "--status", "CONFIRMATORY",
        "--out", "paper/numbers.tex", "--", sys.executable, "scripts/make_numbers.py")
    run(repo, "git", "add", "-A")
    assert staged_check(repo).returncode == 0


def test_runtime_guard_allows_ordinary_writes_and_named_writers(repo):
    code = ("import importlib.util as u, sys\n"
            "s = u.spec_from_file_location('rt', 'src/depthlaw/frozen_rt.py'); m = u.module_from_spec(s)\n"
            "s.loader.exec_module(m); sys.argv = ['scripts/make_numbers.py']; m.install('.')\n"
            "open('results/other.json', 'w').write('{}')\n"
            "open('paper/numbers.tex', 'w').write('ok')\n"
            "open('prereg/new_file.md', 'w').write('write-once add')\n"
            "print(open('config/required_macros.json').read())\n")
    p = run(repo, sys.executable, "-c", code, check=False)
    assert p.returncode == 0, p.stderr
    code2 = code.replace("make_numbers.py", "other.py")
    p = run(repo, sys.executable, "-c", code2, check=False)
    assert p.returncode != 0 and "paper/numbers.tex" in p.stderr


def test_override_needs_matching_ledger_note(repo):
    run(repo, sys.executable, "scripts/gen_required_macros.py")
    run(repo, "git", "add", "-A")
    env = {"DEPTHLAW_FROZEN_OVERRIDE": "1"}
    assert staged_check(repo, env).returncode == 1  # no approval note
    h = hashlib.sha256((repo / "config/required_macros.json").read_bytes()).hexdigest()
    led = repo / "results/ledger.jsonl"
    led.write_text(led.read_text() + json.dumps({"kind": "NOTE", "tag": "HUMAN-AUTHORIZED FROZEN CHANGE x",
                                                 "files": {"config/required_macros.json": h}}) + "\n")
    run(repo, "git", "add", "-A")
    assert staged_check(repo).returncode == 1          # note alone is not enough
    assert staged_check(repo, env).returncode == 0     # note + human env var


def test_real_repo_is_clean():
    """The live repository: staged frozen paths and worktree agree with the rules right now."""
    p = run(REPO, sys.executable, "scripts/frozen_guard.py", "check-worktree", check=False)
    assert p.returncode == 0, p.stderr
