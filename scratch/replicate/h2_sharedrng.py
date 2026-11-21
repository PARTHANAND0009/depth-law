import json, numpy as np, pandas as pd
from scipy.stats import spearmanr
D = '/home/user/depth-law/scratch/replicate'
COV = ['log_k', 'n_distinct', 'collapse_rate', 'rel_accuracy', 'rel_mean_final_logprob']
M = ['pythia-1.4b', 'pythia-2.8b', 'OLMo-2-1124-7B']
tab = {}
for m in M:
    b = pd.read_csv(f'{D}/blup_{m}.csv').set_index('relation')
    c = pd.read_csv(f'{D}/relcov_{m}.csv').set_index('relation')
    tab[m] = b.join(c).sort_index()
rels = tab[M[0]].index
def ols(y, X):
    X1 = np.column_stack([np.ones(len(y)), X]); beta, *_ = np.linalg.lstsq(X1, y, rcond=None)
    fit = X1 @ beta; return fit, y - fit
def rho(a, b): return spearmanr(a, b).statistic
def stats(A, B, idx):
    a, b = A.blup.values[idx], B.blup.values[idx]
    fa, ra = ols(a, A[COV].values[idx]); fb, rb = ols(b, B[COV].values[idx])
    return rho(a, b), rho(ra, rb), rho(fa, fb)
out = {}; rng = np.random.default_rng(20261121)
for i, j in [(0, 1), (0, 2), (1, 2)]:
    A, B = tab[M[i]].loc[rels], tab[M[j]].loc[rels]
    n = len(rels); full = np.arange(n)
    r, pr, cr = stats(A, B, full)
    pass
    perm = np.array([rho(A.blup.values, rng.permutation(B.blup.values)) for _ in range(10000)])
    p1 = (1 + (perm >= r).sum()) / 10001; p2 = (1 + (np.abs(perm) >= abs(r)).sum()) / 10001
    boots = []
    for _ in range(2000):
        idx = rng.integers(0, n, n); boots.append(stats(A, B, idx)[:2])
    boots = np.array(boots)
    nanb = np.isnan(boots).sum(0)
    out[f'{M[i]} vs {M[j]}'] = dict(n_relations=n, rho=r, rho_ci=list(np.nanpercentile(boots[:, 0], [2.5, 97.5])),
        perm_p_one_sided=p1, perm_p_two_sided=p2, partial_rho=pr,
        partial_rho_ci=list(np.nanpercentile(boots[:, 1], [2.5, 97.5])), cov_only_rho=cr,
        rho_minus_cov_only=r - cr, boot_nan=nanb.tolist())
print(json.dumps(out, indent=1))
json.dump(out, open(f'{D}/h2_sharedrng.json', 'w'), indent=1)
