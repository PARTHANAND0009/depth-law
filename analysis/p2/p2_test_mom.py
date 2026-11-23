"""P2 MoM test on carrier-level data (stats-reviewer round 2, finding 5): fact:template, fact:carrier, error, a carrier
shift and a fact-level covariate, 50% missing fact x paraphrase cells, nc = 3. Runs mom_cells (covariate and carrier
residualisation, carrier averaging) and Henderson III, and compares with what the prereg says MoM estimates:
  MoM fact = fact + fc/nc;  MoM residual = ft + e/nc;  MoM diff = REML diff + (e - fc)/(nc * den).
python analysis/p2/p2_test_mom.py [reps=20]   Exit 1 if a relative bias exceeds 0.10. Test only."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from p2_analysis import mom_cells  # noqa: E402
from p2_mom import henderson3  # noqa: E402

C = {"relation": 0.0017, "frame": 0.0005, "rt": 0.0025, "fact": 0.0027, "ft": 0.0012, "fc": 0.0006, "e": 0.0009}
NC, SHIFT, BETA = 3, 0.04, 0.03


def one(rng):
    rels, nf, nt = 20, 15, 10
    a = rng.normal(0, C["relation"] ** .5, rels); b = rng.normal(0, C["frame"] ** .5, nt)
    c = rng.normal(0, C["rt"] ** .5, (rels, nt)); f = rng.normal(0, C["fact"] ** .5, (rels, nf))
    x = rng.normal(0, 1, (rels, nf))
    rows = []
    for r in range(rels):
        for i in range(nf):
            fc = rng.normal(0, C["fc"] ** .5, NC)
            for t in range(nt):
                if rng.random() < 0.5:
                    continue
                ft = rng.normal(0, C["ft"] ** .5)
                for k in range(NC):
                    y = 0.6 + a[r] + b[t] + c[r, t] + f[r, i] + BETA * x[r, i] + ft + fc[k] + SHIFT * k + rng.normal(0, C["e"] ** .5)
                    rows.append((f"r{r}", f"r{r}f{i}", t, t, k, x[r, i], y))
    D = pd.DataFrame(rows, columns=["relation", "fact_id", "template_id", "frame", "carrier", "xcov", "y"])
    return henderson3(mom_cells(D, "y", ["xcov"]))


def main(reps=20):
    rng = np.random.default_rng(20261121)
    out = [one(rng) for _ in range(reps)]
    raw = pd.DataFrame([o["raw"] for o in out]).mean(); diff = float(np.mean([o["diff"] for o in out]))
    den = C["fact"] + C["rt"] + C["frame"] + C["ft"] + C["fc"] / NC + C["e"] / NC
    reml_diff = (C["rt"] + C["frame"] + C["ft"] - C["fact"]) / den
    want = {"relation": C["relation"], "frame": C["frame"], "rt": C["rt"], "fact": C["fact"] + C["fc"] / NC,
            "residual": C["ft"] + C["e"] / NC}
    ok = True
    print(f"MoM on carrier-level data ({reps} reps, nc={NC}, carrier shift {SHIFT}, covariate beta {BETA}, 50% missing cells)")
    for k, v in want.items():
        rb = (raw[k] - v) / v; ok &= abs(rb) <= 0.10
        print(f"  {k:9s} expected {v:.5f}  mean est {raw[k]:.5f}  rel bias {rb:+.3f}")
    exp_diff = reml_diff + (C["e"] - C["fc"]) / (NC * den)
    print(f"  diff      expected MoM diff {exp_diff:+.4f} (REML diff {reml_diff:+.4f} + (e - fc)/(nc den) "
          f"{(C['e'] - C['fc']) / (NC * den):+.4f})  mean MoM diff {diff:+.4f}")
    ok &= abs(diff - exp_diff) <= 0.03
    print("PASS" if ok else "FAIL")
    return ok


if __name__ == "__main__":
    sys.exit(0 if main(int(sys.argv[1].split("=")[1]) if len(sys.argv) > 1 else 20) else 1)
