"""Revised H-R gate on existing S3b rows (prereg/HR_revised.md). CPU only.

python -m depthlaw.hr.run [--n-boot 2000] [--n-split 200] [--cores 2]
Writes results/HR/<run_id>/ (log.jsonl, per-task R json, tables) and results/HR_gate.json / .md.
"""
from __future__ import annotations

import argparse
import json
import subprocess
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata, spearmanr

from depthlaw.hr.assemble import CSV_COLS, FAMILY, REL_COV, RUNS, build, tag
from depthlaw.io import RunLog, make_run_id

ROOT = Path(__file__).resolve().parents[3]
RSCRIPT = Path(__file__).with_name("hr_fit.R")
SEED = 20261121
MODELS = list(RUNS)
TH = {"icc": 0.30, "icc_lo": 0.15, "rho": 0.7, "perm_p": 0.01, "prho": 0.5, "prho_lo": 0.2, "rho_gap": 0.15,
      "dr2_hi": 0.02}


def rfit(task, csv, out, **kw):
    cmd = ["Rscript", str(RSCRIPT), task, str(csv), str(out)] + [f"{k}={v}" for k, v in kw.items()]
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode:
        raise RuntimeError(f"R {task} failed: {p.stderr[-2000:]}")
    return json.loads(Path(out).read_text())


def ci(a, q=(2.5, 97.5)):
    a = np.asarray([x for x in a if x is not None and np.isfinite(x)], float)
    return [float(np.percentile(a, q[0])), float(np.percentile(a, q[1]))] if len(a) else [None, None]


def ols_split(y, X):
    A = np.column_stack([np.ones(len(y)), X])
    b, *_ = np.linalg.lstsq(A, y, rcond=None)
    fit = A @ b
    return fit, y - fit


def sp(a, b):
    return float(spearmanr(a, b).statistic)


def h2_pair(ba: pd.Series, bb: pd.Series, ca: pd.DataFrame, cb: pd.DataFrame, rng, n_perm=10000, n_boot=2000,
            do_boot=True):
    r = sorted(set(ba.index) & set(bb.index))
    a, b = ba[r].to_numpy(), bb[r].to_numpy()
    Xa, Xb = ca.loc[r, REL_COV].to_numpy(float), cb.loc[r, REL_COV].to_numpy(float)
    rho = sp(a, b)
    ra, rb = rankdata(a), rankdata(b)
    ra, rb = (ra - ra.mean()) / ra.std(), (rb - rb.mean()) / rb.std()
    perm = np.array([np.mean(ra * rb[rng.permutation(len(rb))]) for _ in range(n_perm)])
    fa, ea = ols_split(a, Xa)
    fb, eb = ols_split(b, Xb)
    if not np.isfinite(rho):  # constant BLUPs (sigma2_relation = 0): undefined, not significant
        return {"n_relations": len(r), "rho": None, "perm_p_one_sided": None, "perm_p_two_sided": None,
                "partial_rho": None, "cov_only_rho": None, "rho_minus_cov_only": None,
                "undefined": "relation BLUPs constant in at least one model"}
    out = {"n_relations": len(r), "rho": rho, "perm_p_one_sided": float((1 + np.sum(perm >= rho)) / (n_perm + 1)),
           "perm_p_two_sided": float((1 + np.sum(np.abs(perm) >= abs(rho))) / (n_perm + 1)),
           "partial_rho": sp(ea, eb), "cov_only_rho": sp(fa, fb)}
    out["rho_minus_cov_only"] = out["rho"] - out["cov_only_rho"]
    if do_boot:
        rr, pr = [], []
        for _ in range(n_boot):
            i = rng.integers(0, len(r), len(r))
            rr.append(sp(a[i], b[i]))
            pr.append(sp(ols_split(a[i], Xa[i])[1], ols_split(b[i], Xb[i])[1]))
        out.update(rho_ci=ci(rr), partial_rho_ci=ci(pr), n_boot=n_boot,
                   n_boot_nan=int(np.sum(~np.isfinite(rr)) + np.sum(~np.isfinite(pr))))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-boot", type=int, default=2000)
    ap.add_argument("--n-split", type=int, default=200)
    ap.add_argument("--n-perm", type=int, default=10000)
    ap.add_argument("--cores", type=int, default=2)
    ap.add_argument("--models", nargs="+", default=MODELS)
    ap.add_argument("--dry", action="store_true", help="debug: stage HRdry, top-level HR_gate.json not written")
    a = ap.parse_args(argv)
    stage = "HRdry" if a.dry else "HR"
    run_id = make_run_id(stage, "none")
    log = RunLog(stage, run_id)
    rd = log.dir
    log.log(event="start", prereg="prereg/HR_revised.md", prereg_commit=(ROOT / "prereg" / "HASH.txt").read_text().split()[4],
            seed=SEED, n_boot=a.n_boot, n_split=a.n_split, n_perm=a.n_perm, runs=RUNS)
    M, tabs, relcov = {}, {}, {}
    for m in a.models:
        t = tag(m)
        d = build(m)
        tabs[m] = d
        csv = ROOT / "cache" / "hr" / f"tab_{t}.csv"
        d[CSV_COLS].to_csv(csv, index=False)
        relcov[m] = d.drop_duplicates("relation").set_index("relation")[REL_COV]
        res = {"model": m, "family": FAMILY[m], "depth_run": RUNS[m],
               "prior": json.loads((ROOT / "cache" / "hr" / f"prior_{t}.json").read_text()),
               "n_per_relation": d.groupby("relation").size().to_dict(),
               "relation_covariates": relcov[m].reset_index().to_dict("records")}
        res["main"] = rfit("main", csv, rd / f"main_{t}.json")
        log.log(event="main", model=m, icc=res["main"]["icc_rel"], dr2=res["main"]["dr2"])
        b = rfit("boot", csv, rd / f"boot_{t}.json", n_boot=a.n_boot, seed=SEED, cores=a.cores)
        res["boot"] = {"n_boot": a.n_boot, "icc_ci": ci(b["icc"]), "dr2_ci": ci(b["dr2"]),
                       "or_ci": [float(np.exp(x)) if x is not None else None for x in ci(b["log_or"])],
                       "n_failed": {k: int(sum(v is None for v in b[k])) for k in ("icc", "dr2", "log_or")}}
        log.log(event="boot", model=m, **res["boot"])
        s = rfit("split", csv, rd / f"split_{t}.json", n_split=a.n_split, seed=SEED, cores=a.cores)
        # A split whose H1 fit puts sigma2_relation at 0 gives constant BLUPs, so Spearman is undefined (NA).
        # Not specified in the prereg: report mean over defined splits, the count of undefined ones, and a
        # conservative mean that counts undefined splits as r = 0 (recorded in HR_gate.md, not in prereg/).
        rr = np.array([np.nan if x is None else x for x in s["r"]], float)
        ok = np.isfinite(rr)
        rsb = 2 * rr[ok] / (1 + rr[ok])
        r0 = np.where(ok, rr, 0.0)
        res["split_half"] = {"n_split": a.n_split, "n_undefined": int((~ok).sum()), "r_mean": float(rr[ok].mean()) if ok.any() else None,
                             "r_sb_mean": float(rsb.mean()) if ok.any() else None, "r_sb_pct": ci(rsb),
                             "r_sb_mean_undefined_as_0": float(np.mean(2 * r0 / (1 + r0)))}
        log.log(event="split", model=m, **res["split_half"])
        # robustness and secondary outcomes (point estimates)
        var = {}
        subsets = {"correct_only": d.correct == 1, "incorrect_only": d.correct == 0,
                   "collapse_le_25": d.collapse_rate <= 0.25, "whole_word_object": d.whole_word}
        specs = [(k, msk, "y", 1) for k, msk in subsets.items()]
        specs += [("frac_0.25", None, "y25", 1), ("frac_0.75", None, "y75", 1)]
        specs += [(f"template_{i}", d.template_id == i, "y", 0) for i in range(3)]
        specs += [(f"carrier_{c}", None, f"y_c{c}", 1) for c in range(3)]
        specs += [("secondary_p01_onset", None, "p01_onset", 1), ("secondary_rank1_onset", None, "rank1_onset", 1)]
        for name, msk, y, tre in specs:
            dv = d if msk is None else d[msk]
            vcsv = ROOT / "cache" / "hr" / f"tab_{t}_{name}.csv"
            dv[CSV_COLS].to_csv(vcsv, index=False)
            try:
                var[name] = rfit("variant", vcsv, rd / f"var_{t}_{name}.json", y=y, template_re=tre)
            except Exception as e:  # noqa: BLE001 - reported as MISSING
                var[name] = {"missing": repr(e)[:400]}
            log.log(event="variant", model=m, variant=name, icc=var[name].get("icc_rel"), n=var[name].get("n_rows"))
        res["variants"] = var
        try:
            res["survival"] = rfit("surv", csv, rd / f"surv_{t}.json")
        except Exception as e:  # noqa: BLE001
            res["survival"] = {"missing": repr(e)[:400]}
        log.log(event="survival", model=m, hr=res["survival"].get("hr_cooc"))
        M[m] = res

    rng = np.random.default_rng(SEED)
    pairs = {}
    for x, y in combinations(a.models, 2):
        key = f"{tag(x)} vs {tag(y)}"
        cross = FAMILY[x] != FAMILY[y]
        bx, by = pd.Series(M[x]["main"]["blup"]), pd.Series(M[y]["main"]["blup"])
        p = h2_pair(bx, by, relcov[x], relcov[y], rng, a.n_perm, a.n_boot)
        rx, ry = M[x]["split_half"]["r_sb_mean"], M[y]["split_half"]["r_sb_mean"]
        p["disattenuated_rho"] = float(p["rho"] / np.sqrt(rx * ry)) if rx and ry and rx > 0 and ry > 0 else None
        zx, zy = M[x]["split_half"]["r_sb_mean_undefined_as_0"], M[y]["split_half"]["r_sb_mean_undefined_as_0"]
        p["disattenuated_rho_undefined_as_0"] = float(p["rho"] / np.sqrt(zx * zy)) if zx > 0 and zy > 0 else None
        p["split_half_r_sb"] = {tag(x): rx, tag(y): ry}
        p["counts_for_decision"] = cross
        p["h2_raw_pass"] = bool(p["rho"] >= TH["rho"] and p["perm_p_one_sided"] < TH["perm_p"])
        p["h2_controlled_pass"] = bool(p["partial_rho"] >= TH["prho"] and p["partial_rho_ci"][0] > TH["prho_lo"]
                                       and p["rho_minus_cov_only"] >= TH["rho_gap"])
        rob = {}
        for v in M[x]["variants"]:
            vx, vy = M[x]["variants"][v], M[y]["variants"][v]
            if "blup" not in vx or "blup" not in vy:
                rob[v] = {"missing": "fit missing"}
                continue
            q = h2_pair(pd.Series(vx["blup"]), pd.Series(vy["blup"]), relcov[x], relcov[y], rng, a.n_perm, do_boot=False)
            rob[v] = q
        sx, sy = M[x]["survival"].get("frailty_blup"), M[y]["survival"].get("frailty_blup")
        if sx and sy:
            rob["survival_frailty"] = h2_pair(pd.Series(sx), pd.Series(sy), relcov[x], relcov[y], rng, a.n_perm,
                                              do_boot=False)
        p["robustness"] = rob
        pairs[key] = p
        log.log(event="h2", pair=key, rho=p["rho"], partial=p["partial_rho"])

    for m in a.models:
        r = M[m]
        r["h1_pass"] = bool(r["main"]["icc_rel"] >= TH["icc"] and r["boot"]["icc_ci"][0] >= TH["icc_lo"])
        r["h3_pass"] = bool(r["boot"]["dr2_ci"][1] < TH["dr2_hi"])
    cross = [p for p in pairs.values() if p["counts_for_decision"]]
    h = {"H1": all(M[m]["h1_pass"] for m in a.models), "H2_raw": all(p["h2_raw_pass"] for p in cross),
         "H2_controlled": all(p["h2_controlled_pass"] for p in cross), "H3": all(M[m]["h3_pass"] for m in a.models)}
    if not h["H2_raw"]:
        dec = "NO-GO"
    elif not h["H2_controlled"]:
        dec = "PARTIAL"
    elif h["H1"] and h["H3"]:
        dec = "GO"
    else:
        dec = "UNASSIGNED by the frozen rule (not GO)"
    out = {"run_id": run_id, "prereg": "prereg/HR_revised.md",
           "prereg_commit": (ROOT / "prereg" / "HASH.txt").read_text().split()[4], "seed": SEED,
           "thresholds": TH, "models": M, "pairs": pairs, "hypotheses": h, "decision": dec,
           "secondary_pending": {"logitdiff_onset": "PENDING: distractor logits not stored; GPU job scripts/hr_logitdiff_gpu.sh (not run)"}}
    (rd / "hr_gate.json").write_text(json.dumps(out, indent=1, default=float))
    if not a.dry:
        (ROOT / "results" / "HR_gate.json").write_text(json.dumps(out, indent=1, default=float))
    log.log(event="done", decision=dec, **h)
    print(run_id, dec, h)
    return out


if __name__ == "__main__":
    main()
