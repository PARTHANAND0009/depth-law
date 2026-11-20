"""Mixed model for G1: depth ~ log_cooc + controls, random intercept + log_cooc slope by
relation, random intercepts for template and subject (variance components within relation).
Marginal R^2 (Nakagawa & Schielzeth) with and without log_cooc; partial R^2 = difference."""
from __future__ import annotations

import warnings

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

CONTROLS = ["log_subj", "log_obj", "n_answer_tokens", "log_answer_first_token_freq", "n_subject_tokens"]


def _z(d: pd.DataFrame, cols) -> pd.DataFrame:
    d = d.copy()
    for c in cols:
        s = d[c].std()
        d[c] = (d[c] - d[c].mean()) / (s if s > 0 else 1.0)
    return d


def fit(d: pd.DataFrame, y: str, x: str | None = "log_cooc", controls=CONTROLS, slope=True):
    """Returns dict with params, marginal R^2, conditional R^2, n. x=None -> reduced model."""
    cols = [c for c in controls if d[c].nunique() > 1]
    fx = " + ".join(([x] if x else []) + cols) or "1"
    re = "1 + " + x if (x and slope) else "1"
    vc = {"template": "0 + C(template)", "subject": "0 + C(fact_id)"}
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        m = smf.mixedlm(f"{y} ~ {fx}", d, groups=d["relation"], re_formula=re, vc_formula=vc)
        r = m.fit(reml=False, method=["lbfgs", "powell"])
    Xb = r.fe_params @ m.exog.T if hasattr(r.fe_params, "__matmul__") else m.exog @ r.fe_params
    var_f = float(np.var(np.asarray(m.exog) @ np.asarray(r.fe_params)))
    cov_re = np.asarray(r.cov_re)
    # random-effect variance averaged over the observed design (intercept + slope)
    Z = np.column_stack([np.ones(len(d))] + ([d[x].to_numpy()] if (x and slope) else []))
    var_re = float(np.mean(np.einsum("ij,jk,ik->i", Z, cov_re, Z)))
    var_vc = float(np.sum(r.vcomp))
    var_e = float(r.scale)
    tot = var_f + var_re + var_vc + var_e
    out = {"n": int(len(d)), "n_relations": int(d.relation.nunique()), "r2_marginal": var_f / tot,
           "r2_conditional": (var_f + var_re + var_vc) / tot, "converged": bool(r.converged),
           "params": r.fe_params.to_dict(), "bse": r.bse_fe.to_dict(), "pvalues": r.pvalues[r.fe_params.index].to_dict(),
           "llf": float(r.llf)}
    del Xb
    return out


def partial_r2(d: pd.DataFrame, y: str, x: str = "log_cooc", controls=CONTROLS) -> dict:
    full = fit(d, y, x, controls)
    red = fit(d, y, None, controls)
    return {"partial_r2": full["r2_marginal"] - red["r2_marginal"], "slope": full["params"].get(x),
            "slope_se": full["bse"].get(x), "slope_p": full["pvalues"].get(x), "full": full, "reduced": red}


def fit_general(d: pd.DataFrame, y: str, fixed: list[str], slope: str | None = None, vc: bool = False) -> dict:
    """Mixed model with relation random intercept (+ random slope on `slope`), optional template
    and subject variance components. Marginal / conditional R^2 as in fit()."""
    cols = [c for c in fixed if d[c].nunique() > 1]
    fx = " + ".join(cols) or "1"
    re = "1 + " + slope if slope else "1"
    kw = {"vc_formula": {"template": "0 + C(template)", "subject": "0 + C(fact_id)"}} if vc else {}
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        m = smf.mixedlm(f"{y} ~ {fx}", d, groups=d["relation"], re_formula=re, **kw)
        r = m.fit(reml=False, method=["lbfgs", "powell"])
    var_f = float(np.var(np.asarray(m.exog) @ np.asarray(r.fe_params)))
    Z = np.column_stack([np.ones(len(d))] + ([d[slope].to_numpy()] if slope else []))
    var_re = float(np.mean(np.einsum("ij,jk,ik->i", Z, np.asarray(r.cov_re), Z)))
    var_vc = float(np.sum(r.vcomp)) if vc else 0.0
    var_e = float(r.scale)
    tot = var_f + var_re + var_vc + var_e
    return {"n": int(len(d)), "n_relations": int(d.relation.nunique()), "r2_marginal": var_f / tot,
            "r2_conditional": (var_f + var_re + var_vc) / tot, "converged": bool(r.converged),
            "params": r.fe_params.to_dict(), "bse": r.bse_fe.to_dict(),
            "pvalues": r.pvalues[r.fe_params.index].to_dict(), "llf": float(r.llf), "formula": f"{y} ~ {fx}",
            "re_formula": re, "vc": vc}


def partial_r2_general(d: pd.DataFrame, y: str, x: str, others: list[str], slope_on_x: bool = True,
                       vc: bool = False) -> dict:
    """partial R^2 of x: marginal R^2(full) - marginal R^2(reduced without x; relation intercept kept)."""
    full = fit_general(d, y, [x] + others, slope=x if slope_on_x else None, vc=vc)
    red = fit_general(d, y, others, slope=None, vc=vc)
    return {"partial_r2": full["r2_marginal"] - red["r2_marginal"], "slope": full["params"].get(x),
            "slope_se": full["bse"].get(x), "slope_p": full["pvalues"].get(x), "full": full, "reduced": red}
