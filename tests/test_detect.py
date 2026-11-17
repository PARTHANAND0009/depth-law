"""S8 detector code tests (synthetic data + pythia-70m forward pass)."""
import numpy as np
import pandas as pd

from depthlaw.detect.eval import auroc_ci
from depthlaw.detect.features import Calibration, fact_level
from depthlaw.detect.hidden import diffs, lcf_scores, lw_diag_var


def test_lw_diag_var_shrinks_toward_mean():
    rng = np.random.default_rng(0)
    X = rng.normal(size=(20, 50)) * np.linspace(0.5, 3, 50)
    v = ((X - X.mean(0)) ** 2).mean(0)
    s = lw_diag_var(X)
    assert np.all(s > 0)
    assert np.var(s) <= np.var(v) + 1e-12  # shrinkage never increases spread


def test_lcf_flags_shifted_prompts():
    rng = np.random.default_rng(1)
    calib = rng.normal(size=(200, 4, 16))
    ev = np.concatenate([rng.normal(size=(50, 4, 16)), rng.normal(size=(50, 4, 16)) + 2.0])
    per = lcf_scores(calib, ev)
    y = np.r_[np.zeros(50), np.ones(50)]
    assert auroc_ci(y, per.mean(1), np.random.default_rng(0), 50)["auroc"] > 0.95
    assert diffs(np.zeros((3, 5, 2))).shape == (3, 4, 2)


def _rows(n, rng, rel="r1"):
    x = rng.uniform(0, 10, n)
    depth = 0.9 - 0.02 * x + rng.normal(0, 0.02, n)
    return pd.DataFrame({"fact_id": [f"{rel}_{i}" for i in range(n)], "template_id": 0, "relation": rel, "x": x,
                         "causal_final": depth, "logit_lens_depth": depth, "obj_first_logprob": -5 + 0.3 * x,
                         "correct_at1": True, "obj_logprob": -5.0, "margin": 1.0, "n_obj_tokens": 1,
                         "logit_lens_ranks": [list(range(24, 0, -1))] * n,
                         "logit_lens_prob": [list(np.linspace(0, 1, 24))] * n})


def test_calibration_recovers_slope_and_zero_residual():
    rng = np.random.default_rng(2)
    d = pd.concat([_rows(300, rng, "r1"), _rows(300, rng, "r2")], ignore_index=True)
    cal = Calibration(d)
    assert abs(cal.slopes()["causal"] + 0.02) < 0.005
    f = cal.row_features(d)
    assert abs(f.r_causal.mean()) < 1e-6
    fl = fact_level(f.assign(model_id="m", edit_fact_id=""), ["model_id", "edit_fact_id", "fact_id"])
    assert len(fl) == 600 and fl.correct_t0.all()


def test_auroc_ci_contains_point():
    rng = np.random.default_rng(3)
    y = np.r_[np.zeros(100), np.ones(100)]
    s = np.r_[rng.normal(0, 1, 100), rng.normal(1, 1, 100)]
    r = auroc_ci(y, s, np.random.default_rng(0), 200)
    assert r["lo"] <= r["auroc"] <= r["hi"] and r["n_pos"] == 100


def test_last_token_states_pythia70m():
    from depthlaw.depth.common import load_lm
    from depthlaw.detect.hidden import last_token_states
    lm = load_lm("EleutherAI/pythia-70m")
    H = last_token_states(lm, ["The capital of France is", "Paris is in"], bs=2)
    H1 = last_token_states(lm, ["Paris is in"], bs=1)
    assert H.shape == (2, lm.n_layers + 1, lm.model.config.hidden_size)
    assert np.allclose(H[1], H1[0], atol=1e-4)  # right padding does not change the last token
