import json, math
D = '/home/user/depth-law/scratch/replicate'
C = json.load(open('/home/user/depth-law/results/review/claimed_numbers.json'))
P = json.load(open(f'{D}/point.json')); B = json.load(open(f'{D}/boot.json')); H = json.load(open(f'{D}/h2.json'))
SH = {m.split('/')[-1]: B[m.split('/')[-1]] for m in C['models']}
rows = []
def add(f, c, y, tol, kind='num'):
    if kind == 'bool': ok = (c == y); rows.append((f, c, y, '' if ok else 'mismatch', tol, 'PASS' if ok else 'FAIL')); return
    if kind == 'str': ok = (c == y); rows.append((f, c, y, '', tol, 'PASS' if ok else 'FAIL')); return
    d = abs(c - y)
    if kind == 'p': ok = d <= 0.003 and ((c < 0.01) == (y < 0.01))
    elif kind == 'count': ok = (c == y) or (c > 0 and y > 0 and 0.1 <= y / c <= 10) or (max(c, y) < 10 and c >= 0)
    else: ok = d <= tol
    rows.append((f, c, y, d, tol, 'PASS' if ok else 'FAIL'))
T_PT, T_CI, T_SH = 0.002, 0.03, 0.03
mine = {}
for full, c in C['models'].items():
    m = full.split('/')[-1]; p = P[m]; b = B[m]; k = f'models.{full}.'
    add(k + 'n_rows', c['n_rows'], p['n_rows'], 0)
    add(k + 'icc_rel', c['icc_rel'], p['icc_rel'], T_PT)
    for i in range(2): add(k + f'icc_ci[{i}]', c['icc_ci'][i], b['icc_ci'][i], T_CI)
    add(k + 'dr2', c['dr2'], p['dr2'], T_PT)
    for i in range(2): add(k + f'dr2_ci[{i}]', c['dr2_ci'][i], b['dr2_ci'][i], T_CI)
    add(k + 'or_per_log1p_cooc', c['or_per_log1p_cooc'], p['or'], T_PT)
    for i in range(2): add(k + f'or_ci[{i}]', c['or_ci'][i], b['or_ci'][i], T_CI)
    for v in ['subject', 'rt', 'relation', 'Residual']: add(k + f'vc.{v}', c['vc'][v], p['vc'][v], T_PT)
    add(k + 'r2m_without_cooc_ML', c['r2m_without_cooc_ML'], p['r2m_without'], T_PT)
    add(k + 'r2m_with_cooc_ML', c['r2m_with_cooc_ML'], p['r2m_with'], T_PT)
    add(k + 'split_half_r_sb_mean_defined', c['split_half_r_sb_mean_defined'], b['split_mean_defined'], T_SH)
    add(k + 'split_half_n_undefined', c['split_half_n_undefined'], b['split_n_undefined'], 'same order', 'count')
    add(k + 'split_half_r_sb_undefined_as_0', c['split_half_r_sb_undefined_as_0'], b['split_mean_undef0'], T_SH)
    h1 = p['icc_rel'] >= 0.30 and b['icc_ci'][0] >= 0.15; h3 = b['dr2_ci'][1] < 0.02
    mine[m] = dict(h1=h1, h3=h3, rsb=b['split_mean_defined'], rsb0=b['split_mean_undef0'])
    add(k + 'h1_pass', c['h1_pass'], h1, 'rule', 'bool'); add(k + 'h3_pass', c['h3_pass'], h3, 'rule', 'bool')
h2r, h2c = {}, {}
for pair, c in C['pairs'].items():
    h = H[pair]; k = f'pairs.{pair}.'; a, bm = pair.split(' vs ')
    add(k + 'n_relations', c['n_relations'], h['n_relations'], 0)
    add(k + 'rho', c['rho'], h['rho'], T_PT)
    for i in range(2): add(k + f'rho_ci[{i}]', c['rho_ci'][i], h['rho_ci'][i], T_CI)
    add(k + 'perm_p_one_sided', c['perm_p_one_sided'], h['perm_p_one_sided'], 0.003, 'p')
    add(k + 'perm_p_two_sided', c['perm_p_two_sided'], h['perm_p_two_sided'], 0.003, 'p')
    add(k + 'partial_rho', c['partial_rho'], h['partial_rho'], T_PT)
    for i in range(2): add(k + f'partial_rho_ci[{i}]', c['partial_rho_ci'][i], h['partial_rho_ci'][i], T_CI)
    add(k + 'cov_only_rho', c['cov_only_rho'], h['cov_only_rho'], T_PT)
    add(k + 'rho_minus_cov_only', c['rho_minus_cov_only'], h['rho_minus_cov_only'], T_PT)
    dis = h['rho'] / math.sqrt(mine[a]['rsb'] * mine[bm]['rsb']); dis0 = h['rho'] / math.sqrt(mine[a]['rsb0'] * mine[bm]['rsb0'])
    add(k + 'disattenuated_rho', c['disattenuated_rho'], dis, T_PT)
    add(k + 'disattenuated_rho_undefined_as_0', c['disattenuated_rho_undefined_as_0'], dis0, T_PT)
    raw = h['rho'] >= 0.7 and h['perm_p_one_sided'] < 0.01
    ctl = h['partial_rho'] >= 0.5 and h['partial_rho_ci'][0] > 0.2 and h['rho_minus_cov_only'] >= 0.15
    cnt = 'OLMo' in pair
    add(k + 'h2_raw_pass', c['h2_raw_pass'], raw, 'rule', 'bool'); add(k + 'h2_controlled_pass', c['h2_controlled_pass'], ctl, 'rule', 'bool')
    add(k + 'counts_for_decision', c['counts_for_decision'], cnt, 'rule', 'bool')
    if cnt: h2r[pair] = raw; h2c[pair] = ctl
H1 = all(v['h1'] for v in mine.values()); H3 = all(v['h3'] for v in mine.values()); R2 = all(h2r.values()); C2 = all(h2c.values())
for f, y in [('H1', H1), ('H2_raw', R2), ('H2_controlled', C2), ('H3', H3)]: add('hypotheses.' + f, C['hypotheses'][f], y, 'rule', 'bool')
dec = 'NO-GO' if not R2 else ('PARTIAL' if not C2 else ('GO' if H1 and H3 else 'UNASSIGNED'))
add('decision', C['decision'], dec, 'rule', 'str')
def fmt(x):
    if isinstance(x, bool) or isinstance(x, str): return str(x)
    if isinstance(x, int): return str(x)
    return f'{x:.6g}' if abs(x) >= 1e-3 or x == 0 else f'{x:.3e}'
print(len(rows), 'rows; FAIL:', sum(r[5] == 'FAIL' for r in rows))
print('| field | claimed | yours | abs diff | tolerance | result |\n|---|---|---|---|---|---|')
for r in rows: print('| ' + ' | '.join(fmt(x) if not isinstance(x, str) or x else '' for x in r) + ' |')
