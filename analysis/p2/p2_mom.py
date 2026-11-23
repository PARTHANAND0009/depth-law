"""P2 method-of-moments sensitivity estimator (Henderson method III), independent of lme4.

Input: carrier-averaged cell means (one row per fact x template) with columns relation, frame (template_id),
fact, y. In P2, y is first residualised on the four fact-level covariates and the carrier fixed effect by OLS on
the carrier-level rows (p2_analysis.py, mom_cells), so MoM and REML adjust for the same fixed effects.
Random terms fitted sequentially: relation, frame, relation:frame (rt), fact; residual.
What MoM estimates (prereg section 4; stats-reviewer round 1 item 1): on this scale fact:carrier/nc is absorbed into
"fact" and fact:template + error/nc into "residual", so MoM fact = fact + fc/nc and MoM residual = ft + e/nc. MoM
ICC(1) is therefore not the REML ICC(1); the prereg uses MoM only as a direction check (sign of diff).
Shares (within relation): den = fact + frame + rt + residual; icc1 = fact/den;
wording = (frame + rt + residual)/den on components truncated at 0; diff = (frame + rt + residual - fact)/den on the RAW
components (missing if the raw den <= 0), so truncation cannot flip its sign; diff_truncated is also reported.

Henderson III: X_0 = 1, X_k = [X_{k-1}, Z_k]. R_k = y'P_k y - y'P_{k-1} y with
E[R_k] = sum_{j>=k} s2_j tr(Z_j'(P_k - P_{k-1})Z_j) + s2_e (rank_k - rank_{k-1}); residual SS
E = s2_e (n - rank_K). Solved backwards.
python analysis/p2/p2_mom.py --selftest
"""
import sys

import numpy as np
import pandas as pd

TERMS = ["relation", "frame", "rt", "fact"]


def design(d):
    d = d.copy()
    d["rt"] = d.relation.astype(str) + ":" + d.frame.astype(str)
    Z = {t: pd.get_dummies(d[t].astype(str)).to_numpy(float) for t in TERMS}
    return d, Z


def orth(X):
    """Orthonormal basis of col(X) via SVD (dummy columns are collinear, so plain QR is unreliable)."""
    U, s, _ = np.linalg.svd(X, full_matrices=False)
    return U[:, s > s.max() * max(X.shape) * np.finfo(float).eps]


def henderson3(d):
    d, Z = design(d)
    y = d.y.to_numpy(float); n = len(y)
    X = np.ones((n, 1)); Qs = [orth(X)]
    for t in TERMS:
        X = np.hstack([X, Z[t]]); Qs.append(orth(X))
    yPy = [float(np.sum((Q.T @ y) ** 2)) for Q in Qs]
    rank = [Q.shape[1] for Q in Qs]
    trZ = {(k, t): float(np.sum((Qs[k].T @ Z[t]) ** 2)) for k in range(len(Qs)) for t in TERMS}
    ss_e = float(y @ y) - yPy[-1]; s2 = {"residual": ss_e / (n - rank[-1])}
    for k in range(len(TERMS), 0, -1):
        t = TERMS[k - 1]
        R_k = yPy[k] - yPy[k - 1]
        rhs = R_k - s2["residual"] * (rank[k] - rank[k - 1])
        for j in range(k, len(TERMS)):  # higher terms already solved
            tj = TERMS[j]
            rhs -= s2[tj] * (trZ[(k, tj)] - trZ[(k - 1, tj)])
        coef = trZ[(k, t)] - trZ[(k - 1, t)]
        s2[t] = rhs / coef
    raw = dict(s2)
    tr = {k: max(0.0, v) for k, v in raw.items()}
    den = tr["fact"] + tr["frame"] + tr["rt"] + tr["residual"]
    # diff (the H1 / H1-alt direction check) uses the RAW components (round-3 non-blocking 2): truncating a negative raw
    # component at 0 first could flip its sign. If the raw denominator is not positive, diff is missing (MoM MISSING).
    den_raw = raw["fact"] + raw["frame"] + raw["rt"] + raw["residual"]
    out = {"raw": raw, "icc1": tr["fact"] / den, "wording": (tr["frame"] + tr["rt"] + tr["residual"]) / den,
           "diff_truncated": (tr["frame"] + tr["rt"] + tr["residual"] - tr["fact"]) / den, "n_cells": n}
    if den_raw > 0:
        out["diff"] = (raw["frame"] + raw["rt"] + raw["residual"] - raw["fact"]) / den_raw
    return out


def selftest(seed=1, reps=60):
    rng = np.random.default_rng(seed)
    comp = {"relation": 0.0017, "frame": 0.0005, "rt": 0.0025, "fact": 0.0030, "residual": 0.0015}
    rels, nf, nt = 20, 15, 10
    out = []
    for _ in range(reps):
        a = rng.normal(0, comp["relation"] ** .5, rels); b = rng.normal(0, comp["frame"] ** .5, nt)
        c = rng.normal(0, comp["rt"] ** .5, (rels, nt)); f = rng.normal(0, comp["fact"] ** .5, (rels, nf))
        rows = []
        for r in range(rels):
            for i in range(nf):
                for t in range(nt):
                    rows.append((f"r{r}", t, f"r{r}f{i}", a[r] + b[t] + c[r, t] + f[r, i] + rng.normal(0, comp["residual"] ** .5)))
        d = pd.DataFrame(rows, columns=["relation", "frame", "fact", "y"])
        d = d.sample(frac=0.5, random_state=int(rng.integers(1e9)))  # 50% missing cells, as in the bootstrap simulation
        out.append(henderson3(d)["raw"])
    est = pd.DataFrame(out).mean()
    print(f"Henderson III self-test (50 percent missing cells, {reps} reps): mean estimate vs truth")
    for k, v in comp.items():
        print(f"  {k:9s} truth {v:.5f}  mean est {est[k]:.5f}  rel bias {(est[k] - v) / v:+.3f}")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
