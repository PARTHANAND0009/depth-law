#!/usr/bin/env python3
"""P2R model-file provenance (amendment A_P2R_new_families sections 1 and 4). Three modes:
  pin   <out.json>                  write, per model, the main commit and the content id of every file that affects the
                                    measurement: *.safetensors (LFS sha256), *.safetensors.index.json, config.json, generation_config.json and
                                    the tokenizer files (git blob id). Run before the amendment is frozen.
  check-hub <pinned.json> <out.json> compare the Hub's ids AT THE PINNED COMMIT with the pinned ones (before
                                    downloading with revision=<pinned commit>); main may have moved since.
  set-ref <pinned.json>             after that download, point refs/main at the pinned commit (offline loading).
  check-cache <pinned.json> <out.json> [--only-present]
                                    compare the DOWNLOADED files in the Hugging Face cache (HF_HOME/hub): refs/main
                                    must equal the pinned commit, and for every pinned file both its cache blob name and
                                    a fresh hash of its bytes on disk (sha256 for LFS files, git blob sha1 otherwise)
                                    must equal the pinned id. --only-present skips files not in the cache
                                    (test use only; never on the GPU instance).
Each check writes the observed values to out.json and exits 1 on any difference. In the runbook, `check-cache` gates the
driver (`check-cache ... && driver`), and the driver runs with HF_HUB_OFFLINE=1 so only the verified files load."""
import hashlib
import json
import os
import sys
from pathlib import Path

MODELS = ("google/gemma-2-9b", "mistralai/Mistral-7B-v0.1")
KEEP = ("config.json", "generation_config.json", "tokenizer.json", "tokenizer.model", "tokenizer_config.json",
        "special_tokens_map.json")


def wanted(name):
    return name.endswith(".safetensors") or name.endswith(".safetensors.index.json") or name in KEEP


def content_id(path, pinned_id):
    """Hash the bytes actually on disk: sha256 for LFS files (64-hex pins), git blob sha1 for the others (40-hex pins)."""
    p = Path(path).resolve()
    if len(pinned_id or "") == 64:
        h = hashlib.sha256()
    else:
        h = hashlib.sha1(); h.update(b"blob %d\0" % p.stat().st_size)
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 23), b""):
            h.update(b)
    return h.hexdigest()


def hub_ids(revisions=None):
    """revisions=None: the current main (pin). Otherwise {model: pinned commit} (check-hub): the files AT THE PINNED
    COMMIT are compared, so a later commit on main that leaves the pinned files alone does not matter; the current
    main commit is recorded for information only."""
    from huggingface_hub import HfApi
    api, out = HfApi(), {}
    for m in MODELS:
        info = api.model_info(m, revision=(revisions or {}).get(m), files_metadata=True)
        out[m] = {"main_commit": info.sha,
                  "files": {s.rfilename: (s.lfs.sha256 if s.lfs else s.blob_id) for s in info.siblings if wanted(s.rfilename)}}
        if revisions:
            out[m]["hub_main_now_info_only"] = api.model_info(m).sha
    return out


def set_ref(pinned):
    """After snapshot_download(revision=<pinned commit>): point refs/main at the pinned commit, so the frozen loader
    (revision 'main', HF_HUB_OFFLINE=1) resolves to the downloaded, checked snapshot."""
    hub = Path(os.environ.get("HF_HOME", Path.home() / ".cache/huggingface")) / "hub"
    for m in MODELS:
        d = hub / ("models--" + m.replace("/", "--"))
        assert (d / "snapshots" / pinned[m]["main_commit"]).is_dir(), f"{m}: pinned snapshot not downloaded"
        (d / "refs").mkdir(parents=True, exist_ok=True)
        (d / "refs" / "main").write_text(pinned[m]["main_commit"])
        print(f"set-ref: {m} refs/main -> {pinned[m]['main_commit']}")


def cache_ids(pinned, only_present=False):
    hub = Path(os.environ.get("HF_HOME", Path.home() / ".cache/huggingface")) / "hub"
    out = {}
    for m in MODELS:
        d = hub / ("models--" + m.replace("/", "--"))
        ref = (d / "refs/main").read_text().strip() if (d / "refs/main").exists() else None
        files, content = {}, {}
        for name, pid in pinned[m]["files"].items():
            p = d / "snapshots" / pinned[m]["main_commit"] / name
            if p.exists():
                files[name] = Path(os.readlink(p)).name if p.is_symlink() else None
                content[name] = content_id(p, pid)
            elif not only_present:
                files[name] = None
        out[m] = {"main_commit": ref, "files": files, "content": content}
    return out


def compare(pinned, now, only_present=False):
    bad = []
    for m in MODELS:
        if now[m]["main_commit"] != pinned[m]["main_commit"] and not (only_present and now[m]["main_commit"] is None):
            bad.append(f"{m}: commit {now[m]['main_commit']} != pinned {pinned[m]['main_commit']}")
        for f, i in now[m]["files"].items():
            if i != pinned[m]["files"].get(f):
                bad.append(f"{m}/{f}: {i} != pinned {pinned[m]['files'].get(f)}")
        for f, i in now[m].get("content", {}).items():  # bytes on disk, re-hashed (check-cache only)
            if i != pinned[m]["files"].get(f):
                bad.append(f"{m}/{f}: content hash {i} != pinned {pinned[m]['files'].get(f)}")
        if not only_present:
            for f in pinned[m]["files"]:
                if f not in now[m]["files"]:
                    bad.append(f"{m}/{f}: missing")
    return bad


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "pin":
        Path(sys.argv[2]).write_text(json.dumps(hub_ids(), indent=1) + "\n"); print("pinned", sys.argv[2]); sys.exit(0)
    if mode not in ("check-hub", "check-cache", "set-ref"):
        raise SystemExit(__doc__)
    pinned = json.loads(Path(sys.argv[2]).read_text())
    if mode == "set-ref":
        set_ref(pinned); sys.exit(0)
    only = "--only-present" in sys.argv
    now = hub_ids({m: pinned[m]["main_commit"] for m in MODELS}) if mode == "check-hub" else cache_ids(pinned, only)
    bad = compare(pinned, now, only)
    Path(sys.argv[3]).parent.mkdir(parents=True, exist_ok=True)
    Path(sys.argv[3]).write_text(json.dumps({"mode": mode, "only_present": only, "pinned": pinned, "observed": now,
                                             "differences": bad}, indent=1) + "\n")
    for b in bad:
        print("DIFFERENT:", b)
    print(f"{mode}: {'OK' if not bad else 'FILES CHANGED'} ({sum(len(v['files']) for v in now.values())} files compared)")
    sys.exit(1 if bad else 0)
