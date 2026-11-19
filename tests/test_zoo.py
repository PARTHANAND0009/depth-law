"""S7 zoo code tests on pythia-70m: ROME edit works and reverts exactly; LoRA unload restores."""
import pytest
import torch

from depthlaw.depth.common import load_lm
from depthlaw.zoo.core import (Request, applied, context_prefixes, first_token_rank, optimize_delta,
                               second_moment)
from depthlaw.zoo.lora_inject import sft_examples, train_lora
from depthlaw.zoo.memit import memit_factors
from depthlaw.zoo.rome import rome_factors

DOCS = ["The city council met on Tuesday to discuss the new budget for schools and roads. " * 8,
        "Photosynthesis converts light energy into chemical energy stored in glucose molecules. " * 8] * 20
REQ = Request("t", "Paris", "The capital city of {} is", "Berlin", "counterfactual")


def _diverse_docs():
    """Varied text for MEMIT's second moment. DOCS (two repeated sentences) gives a covariance
    with condition number ~1e12 on pythia-70m, which makes the MEMIT solve unstable and the test
    order-dependent; fact sentences give ~1e6 (production pythia-1.4b C_l5: ~5e4)."""
    import pandas as pd
    from conftest import ROOT
    f = pd.read_parquet(ROOT / "data" / "facts.parquet").sort_values("fact_id")
    sents = [f"{s} is related to {o} through {r.replace('_', ' ')}." for s, r, o in zip(f.subject, f.relation, f.object)]
    return [" ".join(sents[i:i + 40]) for i in range(0, len(sents), 40)]


@pytest.fixture(scope="module")
def lm():
    torch.manual_seed(0)
    m = load_lm("EleutherAI/pythia-70m")
    for p in m.model.parameters():
        p.requires_grad_(False)
    return m


def _snap(lm):
    return {n: p.detach().clone() for n, p in lm.model.named_parameters()}


def _maxdiff(lm, snap):
    return max(float((snap[n] - p).abs().max()) for n, p in lm.model.named_parameters())


def test_rome_edit_and_revert(lm):
    C, _ = second_moment(lm, [2], iter(DOCS), 4000)
    pre = context_prefixes(lm, 2)
    snap = _snap(lm)
    assert first_token_rank(lm, REQ.template, REQ.subject, REQ.target) > 1
    fac, _ = rome_factors(lm, REQ, 2, C[2], pre)
    with applied(lm, fac):
        assert first_token_rank(lm, REQ.template, REQ.subject, REQ.target) == 1
    assert _maxdiff(lm, snap) < 1e-6


def test_memit_moves_target(lm):
    C, _ = second_moment(lm, [1, 2, 3], iter(_diverse_docs()), 20000)
    pre = context_prefixes(lm, 2)
    z = optimize_delta(lm, REQ, 3, pre, "resid", clamp=0.75)[0][:, None]
    before = first_token_rank(lm, REQ.template, REQ.subject, REQ.target)
    snap = _snap(lm)
    fac = memit_factors(lm, [REQ], z, [1, 2, 3], C, pre, mom2_weight=15.0)
    after = first_token_rank(lm, REQ.template, REQ.subject, REQ.target)
    from depthlaw.zoo.core import apply_delta
    apply_delta(lm, fac, -1.0)
    assert after < before
    assert _maxdiff(lm, snap) < 1e-5


def test_lora_unload_restores(lm):
    snap = _snap(lm)
    fac, info = train_lora(lm, sft_examples(lm, [REQ]), [REQ], max_epochs=2)
    assert _maxdiff(lm, snap) == 0.0
    assert any(k.endswith("::B") for k in fac)
