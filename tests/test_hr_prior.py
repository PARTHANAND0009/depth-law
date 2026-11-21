"""Streamed forward (HR prior) must equal a standard fp32 forward."""
import torch
from safetensors.torch import save_file
from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer

from depthlaw.hr.prior import PREFIXES, LocalSource, hub_source, standard_final_logprobs, streamed_final_logprobs


def test_streamed_matches_standard_pythia70m():
    name = "EleutherAI/pythia-70m"
    tok = AutoTokenizer.from_pretrained(name)
    ids = [tok(p).input_ids for p in PREFIXES]
    model = AutoModelForCausalLM.from_pretrained(name, dtype=torch.float32).eval()
    ref = standard_final_logprobs(model, ids)
    src, _ = hub_source(name)
    got = streamed_final_logprobs(AutoConfig.from_pretrained(name), src, ids, head_chunk=5000)
    assert (got - ref).abs().max().item() < 1e-3  # fp32 accumulation order; observed 3.7e-4 on values to -850


def test_streamed_matches_standard_tiny_olmo2(tmp_path):
    torch.manual_seed(0)
    cfg = AutoConfig.for_model("olmo2", hidden_size=64, intermediate_size=128, num_hidden_layers=3,
                               num_attention_heads=4, num_key_value_heads=4, vocab_size=500,
                               max_position_embeddings=64, tie_word_embeddings=False)
    model = AutoModelForCausalLM.from_config(cfg, dtype=torch.float32).eval()
    for p in model.parameters():
        torch.nn.init.normal_(p, std=0.2)
    f = tmp_path / "model.safetensors"
    save_file({k: v.contiguous() for k, v in model.state_dict().items()}, str(f))
    ids = [[1, 5, 9, 33], [7], [400, 2, 3, 4, 5, 6, 7]]
    ref = standard_final_logprobs(model, ids)
    got = streamed_final_logprobs(cfg, LocalSource([str(f)]), ids, head_chunk=128)
    assert (got - ref).abs().max().item() < 1e-4
