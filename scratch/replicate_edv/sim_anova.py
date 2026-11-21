# Check own Henderson-III estimator for bias on the real all3/correct designs, simulating from REML components.
import sys, json, numpy as np, pandas as pd
sys.path.insert(0, "/home/user/depth-law/scratch/replicate_edv")
import rep2
a = rep2.load(); ml = json.load(open(rep2.OUT + "ml.json")); rng = np.random.default_rng(20261121)
for m, sname, s in rep2.sets(a):
    D = "D1"; key = f"{m}|{D}|{sname}"
    comp = ml.get(key + "|nosubject")["raw"]
    n = len(s); one = np.ones((n, 1)); Zr, Zt, Zf = rep2.dm(s.relation), rep2.dm(s.rt), rep2.dm(s.fact_id)
    P0 = rep2.proj(one); P1 = rep2.proj(np.hstack([one, Zr])); P2 = rep2.proj(np.hstack([one, Zt])); P3 = rep2.proj(np.hstack([one, Zt, Zf]))
    As = [P1 - P0, P2 - P1, P3 - P2, np.eye(n) - P3]; Zs = [Zr, Zt, Zf, None]
    M = np.array([[np.trace(A) if Z is None else np.trace(Z.T @ A @ Z) for Z in Zs] for A in As])
    sd = np.sqrt([comp["relation"], comp["rt"], comp["fact"], comp["residual"]])
    est = []
    for _ in range(300):
        y = Zr @ rng.normal(0, sd[0], Zr.shape[1]) + Zt @ rng.normal(0, sd[1], Zt.shape[1]) + Zf @ rng.normal(0, sd[2], Zf.shape[1]) + rng.normal(0, sd[3], n)
        est.append(np.linalg.solve(M, np.array([y @ A @ y for A in As])))
    est = np.array(est)
    print(key, "true", np.round(sd**2, 5), "H3 mean", np.round(est.mean(0), 5), "H3 sd", np.round(est.std(0), 5), flush=True)
