import pandas as pd, numpy as np, json, sys
facts=pd.DataFrame([json.loads(l) for l in open(sys.argv[1])])
B='/home/user/depth-law/results/P2analysis/correct/'
rng=np.random.default_rng(1)
def ssb(y,codes,relcodes):
    gm=np.bincount(codes,y)/np.bincount(codes); rm=np.bincount(relcodes,y)/np.bincount(relcodes)
    return ((gm[codes]-rm[relcodes])**2).sum()
for m in ['Llama-3.1-8B','OLMo-2-1124-7B']:
  for yv in ['D1','D4']:
    d=pd.read_csv(B+f'long_{m}_correct.csv').merge(facts[['fact_id','object']],on='fact_id')
    d['y']=d[yv]-d.groupby(['relation','template_id'])[yv].transform('mean')
    fm=d.groupby('fact_id').agg(y=('y','mean'),rel=('relation','first'),obj=('object','first'),k=('template_id','nunique')).reset_index()
    fm=fm[fm.k>=2].reset_index(drop=True)
    rel=pd.factorize(fm.rel)[0]; y=fm.y.values
    objs=fm.obj.values.copy()
    def codes(o): return pd.factorize(pd.Series(fm.rel.values)+'|'+pd.Series(o))[0]
    obs=ssb(y,codes(objs),rel); cnt=0; n=2000
    for _ in range(n):
        o=objs.copy()
        for r in np.unique(rel):
            idx=np.where(rel==r)[0]; o[idx]=rng.permutation(o[idx])
        cnt+= ssb(y,codes(o),rel)>=obs
    print(m,yv,'perm p (object labels shuffled within relation)=',(cnt+1)/(n+1))
