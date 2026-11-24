import pandas as pd, numpy as np, json, sys
try:
    from scipy import stats
except Exception: stats=None
facts=pd.DataFrame([json.loads(l) for l in open(sys.argv[1])])
B='/home/user/depth-law/results/P2analysis/correct/'
for m in ['Llama-3.1-8B','OLMo-2-1124-7B']:
  for y in ['D1','D4']:
    d=pd.read_csv(B+f'long_{m}_correct.csv').merge(facts[['fact_id','object']],on='fact_id')
    d['y']=d[y]-d.groupby(['relation','template_id'])[y].transform('mean')
    fm=d.groupby('fact_id').agg(y=('y','mean'),rel=('relation','first'),obj=('object','first'),k=('template_id','nunique')).reset_index()
    fm=fm[fm.k>=2]; fm['ro']=fm.rel+'|'+fm.obj
    gm=fm.groupby('ro').y.transform('mean'); rm=fm.groupby('rel').y.transform('mean')
    SSB=((gm-rm)**2).sum(); SSW=((fm.y-gm)**2).sum()
    g=fm.ro.nunique(); r=fm.rel.nunique(); N=len(fm)
    df1=g-r; df2=N-g
    MSB=SSB/df1; MSW=SSW/df2
    sizes=fm.groupby('ro').size(); n0=(N - (sizes**2).sum()/N)/(g-1)
    icc=(MSB-MSW)/(MSB+(n0-1)*MSW)
    p=stats.f.sf(MSB/MSW,df1,df2) if stats else float('nan')
    print(f'{m} {y}: F({df1},{df2})={MSB/MSW:.2f} p={p:.2g} object ICC among fact means within relation ~{icc:.2f} (n0={n0:.2f})')
