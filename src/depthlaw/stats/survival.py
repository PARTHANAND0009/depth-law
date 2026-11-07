"""Discrete-time survival model for depth with censoring: one row per (fact, template, layer)
at risk; event = the layer where the measure resolves; cloglog link so exp(coef) is a hazard
ratio per unit of the predictor. Layer enters as categorical baseline hazard. Cluster-robust
SEs by relation."""
from __future__ import annotations

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf

from depthlaw.stats.mixed import CONTROLS


def person_period(d: pd.DataFrame, y: str, n_layers: int) -> pd.DataFrame:
    rows = []
    cols = ["log_cooc", "relation", *CONTROLS]
    for r in d.itertuples():
        v = getattr(r, y)
        ev_layer = None if (v is None or (isinstance(v, float) and np.isnan(v))) else int(round(v * n_layers)) - 1
        last = ev_layer if ev_layer is not None else n_layers - 1
        base = {c: getattr(r, c) for c in cols}
        for l in range(last + 1):
            rows.append({**base, "layer": l, "event": int(ev_layer is not None and l == ev_layer)})
    return pd.DataFrame(rows)


def hazard_ratio(d: pd.DataFrame, y: str, n_layers: int, x: str = "log_cooc") -> dict:
    pp = person_period(d, y, n_layers)
    cols = [c for c in CONTROLS if pp[c].nunique() > 1]
    # merge sparse layers so every baseline level has events
    pp["layer_bin"] = pd.cut(pp.layer, bins=min(12, n_layers), labels=False)
    f = f"event ~ {x} + {' + '.join(cols)} + C(layer_bin)"
    m = smf.glm(f, pp, family=sm.families.Binomial(link=sm.families.links.CLogLog()))
    r = m.fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(pp.relation)[0]})
    b, se = float(r.params[x]), float(r.bse[x])
    return {"hr": float(np.exp(b)), "hr_ci": [float(np.exp(b - 1.96 * se)), float(np.exp(b + 1.96 * se))],
            "p": float(r.pvalues[x]), "n_person_periods": int(len(pp)), "n_events": int(pp.event.sum())}
