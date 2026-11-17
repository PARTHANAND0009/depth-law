"""S8 features (notes/s8_plan.md): depth/confidence residuals against the clean depth law and a
within-relation logit-lens profile distance. Calibrated on the clean pythia-1.4b S3 rows only."""
from __future__ import annotations

import numpy as np
import pandas as pd

FEATS = ["r_causal", "r_ll", "r_conf", "d_profile"]


def _profile(ranks) -> np.ndarray:
    return np.log10(np.asarray(list(ranks), dtype=float))


class Calibration:
    """Relation fixed effects + common slope on x = log1p(EXACT count), fit by OLS."""

    def __init__(self, clean: pd.DataFrame):
        c = clean.copy()
        c["depth_c"] = c.causal_final.fillna(1.0)
        c["depth_ll"] = c.logit_lens_depth.fillna(1.0)
        res = c[c.causal_final.notna()]
        res_ll = c[c.logit_lens_depth.notna()]
        self.rels = sorted(c.relation.unique())
        self.fit_causal = self._ols(res, "causal_final")
        self.fit_ll = self._ols(res_ll, "logit_lens_depth")
        self.fit_conf = self._ols(c, "obj_first_logprob")
        prof = res_ll.assign(p=res_ll.logit_lens_ranks.map(_profile))
        glob = np.mean(np.stack(prof.p.values), 0)
        self.prof = {r: (np.mean(np.stack(g.p.values), 0) if len(g) >= 5 else glob)
                     for r, g in prof.groupby("relation")}
        self.prof_global = glob
        self.n = {"rows": len(c), "resolved_causal": len(res), "resolved_ll": len(res_ll),
                  "facts": c.fact_id.nunique()}

    def _ols(self, d: pd.DataFrame, y: str):
        X = self._design(d)
        beta, *_ = np.linalg.lstsq(X, d[y].values.astype(float), rcond=None)
        return beta

    def _design(self, d: pd.DataFrame) -> np.ndarray:
        X = np.zeros((len(d), len(self.rels) + 1))
        idx = {r: i for i, r in enumerate(self.rels)}
        for k, r in enumerate(d.relation.values):
            if r in idx:
                X[k, idx[r]] = 1.0
            else:  # unseen relation -> mean intercept
                X[k, : len(self.rels)] = 1.0 / len(self.rels)
        X[:, -1] = d.x.values
        return X

    def slopes(self) -> dict:
        return {"causal": float(self.fit_causal[-1]), "ll": float(self.fit_ll[-1]),
                "conf": float(self.fit_conf[-1])}

    def row_features(self, d: pd.DataFrame) -> pd.DataFrame:
        X = self._design(d)
        out = d.copy()
        out["r_causal"] = d.causal_final.fillna(1.0).values - X @ self.fit_causal
        out["r_ll"] = d.logit_lens_depth.fillna(1.0).values - X @ self.fit_ll
        out["r_conf"] = d.obj_first_logprob.values - X @ self.fit_conf
        out["d_profile"] = [float(np.sqrt(np.mean((_profile(rk) - self.prof.get(r, self.prof_global)) ** 2)))
                            for rk, r in zip(d.logit_lens_ranks, d.relation)]
        return out


def fact_level(rows: pd.DataFrame, keys: list[str]) -> pd.DataFrame:
    """Average row features over templates; keep template-0 correctness for the population rule."""
    num = FEATS + ["causal_final_f", "ll_depth_f", "obj_first_logprob", "obj_logprob", "margin", "x",
                   "n_obj_tokens"]
    r = rows.assign(causal_final_f=rows.causal_final.fillna(1.0), ll_depth_f=rows.logit_lens_depth.fillna(1.0))
    agg = r.groupby(keys)[num].mean().reset_index()
    t0 = r[r.template_id == 0].set_index(keys)["correct_at1"].rename("correct_t0")
    agg = agg.join(t0, on=keys)
    prof = r.groupby(keys)["logit_lens_prob"].apply(lambda s: np.mean(np.stack([np.asarray(v, float) for v in s]), 0))
    agg = agg.join(prof.rename("ll_prob_curve"), on=keys)
    return agg
