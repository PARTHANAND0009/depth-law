# Build per-model analysis tables from raw inputs only.
import os, numpy as np, pandas as pd
from transformers import AutoTokenizer
R = '/home/user/depth-law'
OUT = f'{R}/scratch/replicate'
RUNS = {'pythia-1.4b': 'results/S3b/S3b-pythia-1.4b-a7dfeb5-20261121T063528Z/depth.parquet',
        'pythia-2.8b': 'results/S3b/S3b-pythia-2.8b-a7dfeb5-20261121T064110Z/depth.parquet',
        'OLMo-2-1124-7B': 'results/S3b/S3b-OLMo-2-1124-7B-923945f-20261121T061237Z/depth.parquet'}
TOK = {'pythia-1.4b': 'EleutherAI/pythia-1.4b', 'pythia-2.8b': 'EleutherAI/pythia-1.4b',
       'OLMo-2-1124-7B': 'allenai/OLMo-2-1124-7B'}
facts = pd.read_parquet(f'{R}/data/facts_g1cpu.parquet')
pool = pd.read_parquet(f'{R}/data/facts.parquet')
a2 = pd.read_parquet(f'{R}/data/amend2_inputs.parquet')
log_k = np.log(pool.groupby('relation').object.nunique())
toks = {}
for m, run in RUNS.items():
    tk = toks.setdefault(TOK[m], AutoTokenizer.from_pretrained(TOK[m]))
    tcol, idx = ('olmo2', 'olmo-mix-1124') if m.startswith('OLMo') else ('pythia', 'piletrain')
    d = pd.read_parquet(f'{R}/{run}', columns=['fact_id', 'template_id', 'relation', 'half_prob_depth',
                                                 'correct_at1', 'obj_first_logprob'])
    f = facts[['fact_id', 'subject', 'object', 'relation', 'templates']].merge(
        a2[['fact_id', f'n_obj_tok_{tcol}', f'n_subj_tok_{tcol}', f'exact_{idx}']], on='fact_id')
    d = d.merge(f, on=['fact_id'], suffixes=('', '_f'))
    assert (d.relation == d.relation_f).all() and len(d) == 3900
    # subj_final_dist
    sfd = []
    for subj, tpls, tid in zip(d.subject, d.templates, d.template_id):
        tpl = tpls[tid]; prefix = tpl.split('{}')[0]; text = tpl.format(subj)
        enc = tk(text, return_offsets_mapping=True)
        end = len(prefix) + len(subj)
        last = max(i for i, (s, e) in enumerate(enc['offset_mapping']) if s < end and e > 0 and e > s)
        sfd.append(len(enc['input_ids']) - 1 - last)
    d['subj_final_dist'] = sfd
    prior = pd.read_parquet(f'{R}/cache/hr/prior_{m}.parquet')
    d = d.merge(prior, on='object', how='left'); assert d.log_prior.notna().all()
    d['n_answer_tokens'] = d[f'n_obj_tok_{tcol}']; d['n_subject_tokens'] = d[f'n_subj_tok_{tcol}']
    d['obj_logprob_final'] = d.obj_first_logprob
    d['y'] = d.half_prob_depth
    l1 = np.log1p(d[f'exact_{idx}'].astype(float))
    # relation mean over fact-level values (each fact appears 3 times so row mean == fact mean)
    d['cooc_within'] = l1 - l1.groupby(d.relation).transform('mean')
    d['correct'] = d.correct_at1.astype(int)
    # relation covariates
    f50 = facts[['fact_id', 'relation', 'object']].copy()
    f50['ft'] = [tk.encode(' ' + o, add_special_tokens=False)[0] for o in f50.object]
    def collapse(g):
        hits = 0
        for o, t in zip(g.object, g.ft):
            hits += any((t == t2) and (o != o2) for o2, t2 in zip(g.object, g.ft))
        return hits / len(g)
    rc = pd.DataFrame({'log_k': log_k,
                       'n_distinct': f50.groupby('relation').object.nunique(),
                       'collapse_rate': f50.groupby('relation')[['object', 'ft']].apply(collapse),
                       'rel_accuracy': d.groupby('relation').correct.mean(),
                       'rel_mean_final_logprob': d.groupby('relation').obj_first_logprob.mean()})
    rc.index.name = 'relation'
    rc.reset_index().to_csv(f'{OUT}/relcov_{m}.csv', index=False)
    cols = ['fact_id', 'relation', 'template_id', 'subject', 'object', 'y', 'n_answer_tokens', 'log_prior',
            'obj_logprob_final', 'n_subject_tokens', 'subj_final_dist', 'cooc_within', 'correct']
    d[cols].to_csv(f'{OUT}/tab_{m}.csv', index=False)
    print(m, d[cols].describe().T[['mean', 'std', 'min', 'max']].to_string())
    print(rc.describe().T[['mean', 'min', 'max']].to_string())
