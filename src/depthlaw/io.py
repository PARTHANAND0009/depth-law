"""Run ids, config hashing, provenance metadata, activation cache IO."""
from __future__ import annotations

import hashlib
import json
import random
import subprocess
from datetime import datetime, timezone
from importlib import metadata
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
LIBS = ["torch", "transformers", "nnsight", "tuned-lens", "numpy", "pandas", "statsmodels", "datasets"]


def git_hash() -> str:
    try:
        return subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"],
                              capture_output=True, text=True, check=True).stdout.strip()
    except subprocess.CalledProcessError:
        return "nogit"


def make_run_id(stage: str, model: str = "none") -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{stage}-{model.split('/')[-1]}-{git_hash()}-{ts}"


def config_hash(cfg) -> str:
    return hashlib.sha256(json.dumps(cfg, sort_keys=True, default=str).encode()).hexdigest()[:12]


def lib_versions() -> dict:
    out = {}
    for name in LIBS:
        try:
            out[name] = metadata.version(name)
        except metadata.PackageNotFoundError:
            out[name] = None
    return out


def seed_everything(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    try:
        import torch
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
    except ImportError:
        pass


def provenance(run_id: str, cfg, model: str | None = None, revision: str | None = None) -> dict:
    return {"run_id": run_id, "config_hash": config_hash(cfg), "model": model,
            "hf_revision": revision, "git": git_hash(), "libs": lib_versions(),
            "utc": datetime.now(timezone.utc).isoformat(timespec="seconds")}


class RunLog:
    def __init__(self, stage: str, run_id: str):
        self.dir = ROOT / "results" / stage / run_id
        self.dir.mkdir(parents=True, exist_ok=True)
        self.path = self.dir / "log.jsonl"

    def log(self, **kw) -> None:
        kw["utc"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        with self.path.open("a") as f:
            f.write(json.dumps(kw, default=str) + "\n")


def act_cache_path(model: str, revision: str, fact_id: str, template_id: int, position: str,
                   layer: int | str, dtype: str = "fp16") -> Path:
    key = f"{model}|{revision}|{fact_id}|{template_id}|{position}|{layer}|{dtype}"
    h = hashlib.sha1(key.encode()).hexdigest()
    return ROOT / "cache" / "acts" / model.replace("/", "__") / h[:2] / f"{h}.safetensors"


def save_act(path: Path, tensors: dict, meta: dict | None = None) -> None:
    from safetensors.torch import save_file
    path.parent.mkdir(parents=True, exist_ok=True)
    save_file({k: v.detach().to("cpu").half().contiguous() for k, v in tensors.items()}, str(path),
              metadata={k: str(v) for k, v in (meta or {}).items()})


def load_act(path: Path) -> dict | None:
    if not path.exists():
        return None
    from safetensors.torch import load_file
    return load_file(str(path))
