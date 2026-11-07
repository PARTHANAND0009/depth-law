"""Cluster bootstrap over relations (resample relations with replacement, refit)."""
from __future__ import annotations

import numpy as np
import pandas as pd

from depthlaw.stats.mixed import partial_r2


def cluster_bootstrap(d: pd.DataFrame, y: str, x: str = "log_cooc", n_boot: int = 1000, seed: int = 1234,
                      controls=None) -> dict:
    rng = np.random.default_rng(seed)
    rels = d.relation.unique()
    by = {r: g for r, g in d.groupby("relation")}
    slopes, pr2, fails = [], [], 0
    for b in range(n_boot):
        pick = rng.choice(rels, size=len(rels), replace=True)
        parts = []
        for k, r in enumerate(pick):
            g = by[r].copy()
            g["relation"] = f"{r}#{k}"           # duplicated relations are distinct clusters
            g["template"] = g["template"] + f"#{k}"
            g["fact_id"] = g["fact_id"] + f"#{k}"
            parts.append(g)
        db = pd.concat(parts, ignore_index=True)
        try:
            res = partial_r2(db, y, x, **({"controls": controls} if controls is not None else {}))
            slopes.append(res["slope"])
            pr2.append(res["partial_r2"])
        except Exception:  # noqa: BLE001 - counted and reported
            fails += 1
    q = lambda a: [float(np.percentile(a, 2.5)), float(np.percentile(a, 97.5))] if a else [None, None]
    return {"n_boot": n_boot, "n_failed": fails, "slope_ci": q(slopes), "partial_r2_ci": q(pr2)}
