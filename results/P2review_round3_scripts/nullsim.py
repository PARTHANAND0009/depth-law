# Illustration only: does the within (relation x paraphrase) fact-label permutation (carrier rows together)
# give a valid null for fact = 0 when fact:carrier (fc) > 0?  Moment estimator of the fact variance:
# mean over facts of cross-products of cell-centred y across different paraphrases AND different carriers.
import numpy as np, sys
rng = np.random.default_rng(1)
R, FPR, T, NC, K = 20, 15, 10, int(sys.argv[1]), 5
A, B, E = float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4])   # fc, ft, e variances; fact = 0
NREP, NPERM = int(sys.argv[5]), int(sys.argv[6])
F = R * FPR; rel = np.repeat(np.arange(R), FPR)
def stat(Y, M):
    # Y [F,T,NC] with NaN where cell missing; centre within relation x template x carrier
    Yc = Y.copy()
    for r in range(R):
        s = Yc[rel == r]; Yc[rel == r] = s - np.nanmean(s, axis=0, keepdims=True)
    Z = np.nan_to_num(Yc)
    tot = 0.0; n = 0
    S = Z.sum(1)                                   # [F,NC] sum over templates
    for c in range(NC):
        for c2 in range(NC):
            if c == c2: continue
            same_t = (Z[:, :, c] * Z[:, :, c2]).sum(1)
            tot += (S[:, c] * S[:, c2] - same_t).sum()
    kk = M.sum(1); n = (kk * (kk - 1)).sum() * NC * (NC - 1)
    return tot / n
rej = 0; obs_all = []
for rep in range(NREP):
    M = np.zeros((F, T), bool)
    for f in range(F): M[f, rng.choice(T, K, replace=False)] = True
    fc = rng.normal(0, A ** .5, (F, 1, NC)); ft = rng.normal(0, B ** .5, (F, T, 1)); e = rng.normal(0, E ** .5, (F, T, NC))
    Y = fc + ft + e; Y[~M] = np.nan
    obs = stat(Y, M)
    perm = []
    for p in range(NPERM):
        Yp = np.full_like(Y, np.nan); Mp = np.zeros_like(M)
        for r in range(R):
            idx = np.where(rel == r)[0]
            for t in range(T):
                have = idx[M[idx, t]]
                tgt = rng.permutation(have)
                Yp[tgt, t, :] = Y[have, t, :]; Mp[tgt, t] = True
        perm.append(stat(Yp, Mp))
    perm = np.array(perm); pval = (1 + (perm >= obs).sum()) / (1 + NPERM)
    rej += pval < 0.05; obs_all.append(obs / perm.std())
print(f"nc={NC} fc={A} ft={B} e={E}: reject at p<0.05 in {rej}/{NREP} H0 replicates; sd(obs)/sd(perm) approx {np.std(obs_all):.2f}")
