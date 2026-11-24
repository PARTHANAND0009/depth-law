import pandas as pd, numpy as np
B='/home/user/depth-law/results/P2analysis/correct/'
pairs={'length (neutral prefix)':[(0,1),(2,3),(4,5),(6,7)],'order':[(0,2),(1,3),(4,6),(5,7)],'form':[(0,4),(1,5),(2,6),(3,7)]}
for m in ['Llama-3.1-8B','OLMo-2-1124-7B']:
  d=pd.read_csv(B+f'long_{m}_correct.csv')
  for y in ['D1','D4']:
    c=d.groupby(['fact_id','relation','template_id'])[y].mean().reset_index()
    c['r']=c[y]-c.groupby(['relation','template_id'])[y].transform('mean')  # remove rt+frame
    w=c.pivot(index='fact_id',columns='template_id',values='r')
    out=[]
    for k,ps in pairs.items():
      diffs=np.concatenate([(w[a]-w[b]).dropna().values for a,b in ps])
      sc=32 if y=='D1' else 1
      out.append(f'{k}: N={len(diffs)} RMS diff={np.sqrt((diffs**2).mean())*sc:.3f}')
    print(m,y,'(layers)' if y=='D1' else '(raw)',' | '.join(out))
