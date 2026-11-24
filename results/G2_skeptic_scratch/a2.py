import pandas as pd, numpy as np, json, sys
F=sys.argv[1]
facts=pd.DataFrame([json.loads(l) for l in open(F)])
B='/home/user/depth-law/results/P2analysis/correct/'
nobj=facts.groupby('relation').object.nunique()
print('distinct objects per relation (of 15):', nobj.sort_values().to_dict())
print('facts whose object is shared with another fact in same relation:', facts.duplicated(['relation','object'],keep=False).sum(),'/300')
res={}
for m in ['Llama-3.1-8B','OLMo-2-1124-7B']:
    d=pd.read_csv(B+f'long_{m}_correct.csv').merge(facts[['fact_id','object']],on='fact_id')
    # remove relation and frame-within-relation means (crude), then fact means
    d['y']=d.D1-d.groupby(['relation','template_id']).D1.transform('mean')
    fm=d.groupby('fact_id').agg(y=('y','mean'),rel=('relation','first'),obj=('object','first'),k=('template_id','nunique')).reset_index()
    fm=fm[fm.k>=2]
    tot=((fm.y-fm.groupby('rel').y.transform('mean'))**2).sum()
    fm['ro']=fm.rel+'|'+fm.obj
    shared=fm[fm.groupby('ro').y.transform('size')>1]
    btw=((fm.groupby('ro').y.transform('mean')-fm.groupby('rel').y.transform('mean'))**2).sum()
    ngr=fm.ro.nunique(); nrel=fm.rel.nunique(); n=len(fm)
    print(m,'facts(k>=2)',n,'rel:obj groups',ngr,'R2 of fact means on object within relation',round(btw/tot,3),'(df',ngr-nrel,'of',n-nrel,')', 'facts in shared-object groups',len(shared))
    # adjusted: expected R2 under no effect ~ df ratio
    print('   chance R2 ~', round((ngr-nrel)/(n-nrel),3))
