"""Runtime write guard for frozen paths (added 2026-11-25 after integrity incident INC-2026-11-25-required-macros).

Installs a sys.addaudithook that raises PermissionError when a Python process opens a frozen path for writing,
or renames, replaces, removes, truncates or chmods one. This is the route of the incident: a Python script
(scripts/gen_required_macros.py) rewrote config/required_macros.json while the command line never named it.

Loaded at interpreter start by a .pth file that scripts/install_guard.sh puts into the project venv and the
system site-packages, so it covers `python3 any_script.py` without the script's cooperation. Writer-managed
paths (ledger, numbers.tex) may be written only by their own writer scripts (argv[0]). Frozen path definitions
come from config/frozen_paths.json. Shell and R writes are not seen here; the commit check
(scripts/frozen_guard.py check-staged), log_run's before/after check and the immutable attribute cover them.
"""
import json, os, sys

_ROOT = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))


def _cfg(root):
    with open(os.path.join(root, "config", "frozen_paths.json")) as f:
        return json.load(f)


def make_hook(root=_ROOT, argv0=None):
    root = os.path.realpath(root)
    cfg = _cfg(root)
    pre, files = tuple(cfg["frozen_prefixes"]), set(cfg["frozen_files"])
    ign, mut = set(cfg["ignore_parts"]), set(cfg["mutable_exceptions"])
    wm = cfg["writer_managed"]
    me = (argv0 if argv0 is not None else (sys.argv[0] if sys.argv else "")).replace("\\", "/")
    W = os.O_WRONLY | os.O_RDWR | os.O_APPEND | os.O_CREAT | os.O_TRUNC

    def rel(p):
        if isinstance(p, int) or p is None:
            return None
        try:
            p = os.fsdecode(p)
            a = os.path.realpath(os.path.join(os.getcwd(), p)) if not os.path.isabs(p) else os.path.realpath(p)
        except Exception:  # noqa: BLE001
            return None
        if not a.startswith(root + os.sep):
            return None
        return a[len(root) + 1:].replace(os.sep, "/")

    def denied(r, new_file_ok=False):
        if r is None or any(x in ign for x in r.split("/")):
            return False
        if r in wm:
            return not any(me.endswith(w) for w in wm[r]["writers"])
        if r in mut:
            return False
        if r in files or r.startswith(pre):
            if new_file_ok and r.startswith(tuple(cfg["add_only_prefixes"])) and not os.path.exists(os.path.join(root, r)):
                return False  # write-once: creating a new prereg/ file is allowed, rewriting is not
            return True
        return False

    def hook(event, args):
        if event == "open":
            path, mode, flags = (list(args) + [None, None, None])[:3]
            writing = (isinstance(mode, str) and any(c in mode for c in "wax+")) or \
                      (mode is None and isinstance(flags, int) and flags & W)
            if writing and denied(rel(path), new_file_ok=True):
                raise PermissionError(f"frozen path (runtime guard): {rel(path)}")
        elif event in ("os.rename", "os.replace"):
            if denied(rel(args[0])) or denied(rel(args[1])):
                raise PermissionError(f"frozen path (runtime guard): {event} {args[0]} -> {args[1]}")
        elif event in ("os.remove", "os.unlink", "os.truncate", "os.chmod", "os.rmdir", "shutil.rmtree"):
            if args and denied(rel(args[0])):
                raise PermissionError(f"frozen path (runtime guard): {event} {args[0]}")
    return hook


def install(root=_ROOT):
    if os.environ.get("DEPTHLAW_FROZEN_RT_INSTALLED") == str(os.getpid()):
        return
    try:
        sys.addaudithook(make_hook(root))
        os.environ["DEPTHLAW_FROZEN_RT_INSTALLED"] = str(os.getpid())
    except FileNotFoundError:
        pass  # no config (e.g. outside the repo checkout): nothing to guard
