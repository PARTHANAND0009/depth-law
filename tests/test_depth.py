import numpy as np
import pytest
import torch

from depthlaw.depth.causal import causal_depth, source_states
from depthlaw.depth.common import (capture, first_stable_layer, first_true, patch_per_batch_row,
                                   subject_last_pos)
from depthlaw.depth.lenses import behavior_and_lens, load_tuned_lens, patchscope_depth


def test_subject_last_pos(lm):
    ids, pos = subject_last_pos(lm, "The capital of {} is", "the United States")
    toks = lm.tok.convert_ids_to_tokens(ids[0])
    assert toks[pos].strip("Ġ▁ ") == "States"


def test_stable_rules():
    assert first_stable_layer([False, True, False, True, True]) == 3
    assert first_stable_layer([True, True]) == 0
    assert first_stable_layer([True, False]) is None
    assert first_true([False, True, False]) == 1


@torch.no_grad()
def test_patching_identity(lm):
    """Patching block l with the same prompt's own state leaves logits unchanged."""
    ids, pos, states, _ = source_states(lm, "The capital of {} is", "France")
    base = lm.model(ids).logits
    for l in range(lm.n_layers):
        with patch_per_batch_row(lm.layers, [l], [pos], states[l:l + 1, pos]):
            out = lm.model(ids).logits
        assert torch.allclose(out, base, atol=1e-4), f"layer {l}"


@torch.no_grad()
def test_patching_changes_output(lm):
    """Patching a different subject in an early block must change the logits (hook is live)."""
    ids, pos, _, _ = source_states(lm, "The capital of {} is", "France")
    _, pos2, states2, _ = source_states(lm, "The capital of {} is", "Japan")
    base = lm.model(ids).logits
    with patch_per_batch_row(lm.layers, [0], [pos], states2[0:1, pos2]):
        out = lm.model(ids).logits
    assert not torch.allclose(out, base, atol=1e-4)


def test_causal_depth_hand_facts(lm, lm_knows, hand_facts, carriers):
    _check_causal(lm, hand_facts, carriers, need_resolved=0)        # mechanics on 70m
    _check_causal(lm_knows, hand_facts, carriers, need_resolved=1)  # resolution on 410m


def _check_causal(lm, hand_facts, carriers, need_resolved):
    n_resolved = 0
    for template, subj, obj in hand_facts:
        r = causal_depth(lm, subj, obj, template, carriers)
        L = r["n_layers"]
        for key in ["causal_subj_onset", "causal_subj_stable", "causal_final"]:
            d = r[key]
            assert d is None or 0 < d <= 1, (key, d)
        # monotone consistency of the stable rule: depth d => rank 1 at every layer >= d
        for curve, d in zip(r["final_rank_curves"], r["causal_final_per_carrier"]):
            if d is not None:
                l0 = round(d * L) - 1
                assert all(x == 1 for x in curve[l0:])
                assert l0 == 0 or curve[l0 - 1] != 1
        for curve, d in zip(r["subj_rank_curves"], r["causal_subj_onset_per_carrier"]):
            if d is not None:
                l0 = round(d * L) - 1
                assert curve[l0] == 1 and all(x != 1 for x in curve[:l0])
        n_resolved += r["causal_final"] is not None
    # at the last block, final-position patching reproduces the source prediction, so any
    # fact the model gets right must resolve; at least one hand fact should
    assert n_resolved >= need_resolved


def test_final_patch_last_layer_equals_source(lm, carriers):
    """Patching the last block's final state into a carrier = source next-token prediction."""
    from depthlaw.depth.causal import patched_ranks
    ids, pos, states, src_logits = source_states(lm, "The capital of {} is", "France")
    tgt = int(src_logits.argmax())
    ranks = patched_ranks(lm, carriers[0], states[:, -1], True, tgt)
    assert ranks[-1] == 1


def test_behavior_and_logit_lens(lm):
    r = behavior_and_lens(lm, "France", "Paris", "The capital of {} is")
    assert len(r["logit_lens_ranks"]) == lm.n_layers
    assert r["obj_logprob"] <= 0
    # logit lens on the last block (after final norm) must agree with the model output
    assert (r["logit_lens_ranks"][-1] == 1) == r["correct_at1"]


def test_tuned_lens_loads():
    """No pretrained lens exists for non-deduped pythia-70m/410m (only *-deduped variants are
    published in the AlignmentResearch/tuned-lens Space), so the loader + forward path is
    tested on pythia-70m-deduped. Core-model lenses must be trained in S3 (GPU)."""
    from depthlaw.depth.common import load_lm
    lm = load_lm("EleutherAI/pythia-70m-deduped")
    tl = load_tuned_lens(lm)
    assert tl is not None
    r = behavior_and_lens(lm, "France", "Paris", "The capital of {} is", tuned=tl)
    assert len(r["tuned_lens_ranks"]) == lm.n_layers
    assert r["tuned_lens_ranks"][-1] == r["logit_lens_ranks"][-1]


def test_patchscope_easy_fact(lm, lm_knows, hand_facts):
    r = patchscope_depth(lm, "France", "Paris", [], "The capital of {} is", max_new_tokens=2)
    assert len(r["patchscope_ok"]) == lm.n_layers  # mechanics on 70m
    hits = 0
    for template, subj, obj in hand_facts:
        r = patchscope_depth(lm_knows, subj, obj, [], template, max_new_tokens=3)
        hits += any(r["patchscope_ok"])
        if hits:
            break
    assert hits >= 1
