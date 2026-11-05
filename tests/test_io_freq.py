import torch

from depthlaw.freq.counts import TermBuilder
from depthlaw.freq.infinigram_client import InfiniGramClient
from depthlaw.io import act_cache_path, load_act, save_act


def test_infinigram_known_count(tmp_path):
    # anchor observed on 2026-11-05 (exact count, Pile train, Llama-2 tokenizer)
    c = InfiniGramClient(cache_path=tmp_path / "c.sqlite")
    r = c.count_str("v4_piletrain_llama", "natural language processing")
    assert r["count"] == 81461
    # second call is served from cache
    c.count_str("v4_piletrain_llama", "natural language processing")
    assert c.n_cached == 1


def test_term_builder_nesting():
    tb = TermBuilder()
    cl = tb.clause(["Barack Obama", "Obama"])
    dec = [tb.decode(t) for t in cl]
    assert all("Bar" not in d for d in dec)  # nested longer term dropped
    assert len(tb.clause(["jazz"])) == 4      # spaced/unspaced x lower/Capitalised


def test_cache_roundtrip(tmp_path, monkeypatch):
    p = tmp_path / "x.safetensors"
    t = torch.randn(3, 8)
    save_act(p, {"h": t}, {"layer": 3})
    back = load_act(p)["h"]
    assert back.dtype == torch.float16
    assert torch.allclose(back.float(), t.half().float())
    k1 = act_cache_path("m", "main", "f1", 0, "subj_last", 3)
    k2 = act_cache_path("m", "main", "f1", 0, "subj_last", 4)
    assert k1 != k2 and k1 == act_cache_path("m", "main", "f1", 0, "subj_last", 3)
