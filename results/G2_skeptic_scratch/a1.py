import pandas as pd, numpy as np, json, sys
B='/home/user/depth-law/results/P2analysis/correct/'
for m in ['Llama-3.1-8B','OLMo-2-1124-7B']:
    d=pd.read_csv(B+f'long_{m}_correct.csv')
    print('=====',m, len(d))
    print('D1 describe', d.D1.describe().round(4).to_dict())
    L=round(1/np.diff(np.sort(d.D1.unique())).min()); print('approx L',L, 'unique D1 values',d.D1.nunique())
    print('D1 in layers quantiles', (d.D1*L-1).quantile([.01,.05,.25,.5,.75,.95,.99]).round(1).to_dict())
    c=d.groupby(['fact_id','template_id']).agg(D1=('D1','mean'),D1sd=('D1','std'),frame=('frame','first'),npt=('n_prompt_tokens','first'),lp=('obj_first_logprob','first'),rel=('relation','first')).reset_index()
    print('within-cell carrier SD of D1 (layers): mean', (c.D1sd*L).mean().round(3), 'frac cells all carriers identical', (c.D1sd==0).mean().round(3))
    print('frame: n cells, mean D1 (layers), correct-cell count')
    print(c.groupby('frame').agg(n=('D1','size'),D1=('D1',lambda x:(x*L).mean()),npt=('npt','mean')).round(2).T.to_string())
    print('corr cell D1 with n_prompt_tokens', np.corrcoef(c.D1,c.npt)[0,1].round(3), ' with obj logprob', np.corrcoef(c.D1,c.lp)[0,1].round(3))
    # within fact: correlation of D1 with prompt tokens and confidence, demeaned
    cc=c.copy(); 
    for v in ['D1','npt','lp']: cc[v+'_w']=cc[v]-cc.groupby('fact_id')[v].transform('mean')
    print('within-fact corr D1~npt', np.corrcoef(cc.D1_w,cc.npt_w)[0,1].round(3),' D1~logprob', np.corrcoef(cc.D1_w,cc.lp_w)[0,1].round(3))
    print('n correct templates per fact dist', d.groupby('fact_id').n_correct_templates.first().value_counts().sort_index().to_dict())
