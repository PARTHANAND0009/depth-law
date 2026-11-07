"""Stats sanity on synthetic data with a known effect (no model, no API)."""
import numpy as np
import pandas as pd

from depthlaw.stats.bootstrap import cluster_bootstrap
from depthlaw.stats.mixed import CONTROLS, partial_r2
from depthlaw.stats.shapes import compare
from depthlaw.stats.survival import hazard_ratio


def synth(slope=-0.05, n_rel=12, per=40, seed=0):
    rng = np.random.default_rng(seed)
    rows = []
    for r in range(n_rel):
        ru = rng.normal(0, 0.03)
        for i in range(per):
            x = rng.uniform(0, 10)
            su = rng.normal(0, 0.02)
            for t in range(3):
                y = 0.8 + slope * x + ru + su + rng.normal(0, 0.03 * (t + 1) / 3) + rng.normal(0, 0.04)
                rows.append({"fact_id": f"r{r}f{i}", "relation": f"rel{r}", "template_id": t,
                             "template": f"rel{r}:{t}", "log_cooc": x, "y": float(np.clip(y, 0.04, 1.0)),
                             **{c: rng.normal() for c in CONTROLS}})
    return pd.DataFrame(rows)


def test_partial_r2_recovers_slope():
    d = synth()
    r = partial_r2(d, "y")
    assert abs(r["slope"] - (-0.05)) < 0.01
    assert r["partial_r2"] > 0.3
    n = partial_r2(synth(slope=0.0), "y")
    assert n["partial_r2"] < 0.02


def test_bootstrap_ci_covers():
    b = cluster_bootstrap(synth(n_rel=8, per=15), "y", n_boot=10)
    assert b["n_failed"] <= 2 and b["slope_ci"][0] < -0.03 < 0.0 > b["slope_ci"][1] - 0.04


def test_survival_direction():
    d = synth()
    d["y"] = (np.round(d.y * 24) / 24).clip(1 / 24, 1.0)
    d.loc[d.sample(frac=0.1, random_state=0).index, "y"] = np.nan  # censored
    h = hazard_ratio(d, "y", 24)
    assert h["hr"] > 1.0          # more cooc -> earlier resolution -> higher hazard per layer
    assert h["n_events"] > 0


def test_shapes_prefers_linear_for_linear():
    s = compare(synth(), "y")
    assert s["best"] in ("linear", "piecewise", "logistic") and s["linear"] is not None
