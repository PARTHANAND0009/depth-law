import pandas as pd, numpy as np, json, sys
facts=pd.DataFrame([json.loads(l) for l in open(sys.argv[1])])
B='/home/user/depth-law/results/P2analysis/correct/'
fm={}
for m in ['Llama-3.1-8B','OLMo-2-1124-7B']:
    d=pd.read_csv(B+f'long_{m}_correct.csv')
    fm[m]=d.groupby('fact_id').D1.mean()
j=pd.concat(fm,axis=1).dropna().merge(facts.set_index('fact_id')[['relation','object']],left_index=True,right_index=True)
a,b='Llama-3.1-8B','OLMo-2-1124-7B'
print('N',len(j),'raw rho',round(j[a].rank().corr(j[b].rank()),3))
for g in [['relation'],['relation','object']]:
    r=j.copy()
    for m in [a,b]: r[m]=r[m]-r.groupby(g)[m].transform('mean')
    keep=r.groupby(g)[a].transform('size')>1
    print('demeaned by',g,'N',keep.sum(),'rho',round(r[keep][a].rank().corr(r[keep][b].rank()),3))
om=j.groupby(['relation','object'])[[a,b]].mean()
om=om.sub(om.groupby(level=0).transform('mean'))
print('rho of relation-demeaned object means, N groups',len(om),round(om[a].rank().corr(om[b].rank()),3))
print('same first-token id llama31 vs olmo2:', np.mean([f['llama31']['id']==f['olmo2']['id'] for f in facts.first_token]))
