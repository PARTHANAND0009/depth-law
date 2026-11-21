"""Checkpoint revisions must load the checkpoint, not main (pythia-2.8b branches carry a stale
single-file model.safetensors identical to main next to the real shards)."""
import pytest
import torch

from depthlaw.depth import common


def test_resolver_uses_shards_not_stale_single_file(monkeypatch, tmp_path):
    files = common.weight_files("EleutherAI/pythia-2.8b", "step8000")
    if not files:
        pytest.skip("Hub unreachable")
    monkeypatch.setattr("huggingface_hub.snapshot_download", lambda *a, **k: k["local_dir"])
    src, prov = common.resolve_weights("EleutherAI/pythia-2.8b", "step8000", local_root=str(tmp_path))
    assert prov["load_mode"] == "local_shards"
    assert all(f.startswith("model-") for f in prov["weight_files_used"])
    main_sha = set(common.weight_files("EleutherAI/pythia-2.8b", "main").values())
    assert not set(prov["weight_files_used"].values()) & main_sha


def test_revision_weights_differ_from_main():
    if not common.weight_files("EleutherAI/pythia-70m", "step1000"):
        pytest.skip("Hub unreachable")
    a = common.load_lm("EleutherAI/pythia-70m", "main", device="cpu")
    b = common.load_lm("EleutherAI/pythia-70m", "step1000", device="cpu")
    wa = a.model.get_input_embeddings().weight
    wb = b.model.get_input_embeddings().weight
    assert not torch.allclose(wa, wb)


def test_resolver_uses_bin_when_safetensors_is_main(monkeypatch, tmp_path):
    """pythia-2.8b step32000: no shards, model.safetensors == main's, pytorch_model.bin distinct."""
    files = common.weight_files("EleutherAI/pythia-2.8b", "step32000")
    if not files:
        pytest.skip("Hub unreachable")
    monkeypatch.setattr("huggingface_hub.snapshot_download", lambda *a, **k: k["local_dir"])
    src, prov = common.resolve_weights("EleutherAI/pythia-2.8b", "step32000", local_root=str(tmp_path))
    assert prov["load_mode"] == "local_bin"
    assert list(prov["weight_files_used"]) == ["pytorch_model.bin"]
    main_sha = set(common.weight_files("EleutherAI/pythia-2.8b", "main").values())
    assert not set(prov["weight_files_used"].values()) & main_sha
    assert src.startswith(str(tmp_path))


def test_resolver_refuses_all_main(monkeypatch):
    sha = {"model.safetensors": "m1", "pytorch_model.bin": "m2"}
    monkeypatch.setattr(common, "weight_files", lambda name, rev: dict(sha))
    with pytest.raises(RuntimeError, match="identical to main"):
        common.resolve_weights("x/y", "step1")
