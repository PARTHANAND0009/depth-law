"""AIC comparison of the depth~log_cooc shape: linear vs piecewise-linear vs logistic.
Fixed-effects fits (relation fixed effects + controls partialled out), Gaussian likelihood."""
from __future__ import annotations

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy.optimize import curve_fit

from depthlaw.stats.mixed import CONTROLS


def _aic(rss: float, n: int, k: int) -> float:
    return n * np.log(rss / n) + 2 * k


def compare(d: pd.DataFrame, y: str, x: str = "log_cooc") -> dict:
    cols = [c for c in CONTROLS if d[c].nunique() > 1]
    ctrl = " + ".join(["C(relation)"] + cols)
    ry = smf.ols(f"{y} ~ {ctrl}", d).fit().resid.to_numpy()
    rx = smf.ols(f"{x} ~ {ctrl}", d).fit().resid.to_numpy()
    xr = d[x].to_numpy()
    n, k0 = len(d), d.relation.nunique() + len(cols)
    out = {}
    b = np.polyfit(rx, ry, 1)
    out["linear"] = _aic(float(np.sum((ry - np.polyval(b, rx)) ** 2)), n, k0 + 2)
    best = None
    for c in np.quantile(xr, np.linspace(0.1, 0.9, 17)):
        h = np.maximum(xr - c, 0)
        hr = h - np.polyval(np.polyfit(rx, h, 1), rx)  # approx. partial out via x
        X = np.column_stack([np.ones(n), rx, hr])
        coef, *_ = np.linalg.lstsq(X, ry, rcond=None)
        rss = float(np.sum((ry - X @ coef) ** 2))
        if best is None or rss < best[0]:
            best = (rss, float(c))
    out["piecewise"] = _aic(best[0], n, k0 + 4)
    out["piecewise_break"] = best[1]
    try:
        f = lambda t, a, bb, c, s: a + bb / (1 + np.exp(-(t - c) / s))
        p0 = [ry.min(), ry.max() - ry.min(), float(np.median(rx)), 1.0]
        p, _ = curve_fit(f, rx, ry, p0=p0, maxfev=20000)
        out["logistic"] = _aic(float(np.sum((ry - f(rx, *p)) ** 2)), n, k0 + 4)
    except Exception as e:  # noqa: BLE001
        out["logistic"] = None
        out["logistic_error"] = repr(e)[:200]
    cands = {k: v for k, v in out.items() if k in ("linear", "piecewise", "logistic") and v is not None}
    out["best"] = min(cands, key=cands.get)
    return out
