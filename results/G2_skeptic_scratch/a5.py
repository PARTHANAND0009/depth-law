import pandas as pd, numpy as np, json
B='/home/user/depth-law/results/P2analysis/'
for m in ['Llama-3.1-8B','OLMo-2-1124-7B']:
  for y in ['D1','D2','D3','D4']:
    f=json.load(open(B+f'correct/fit_{m}_correct_{y}.json'))
    vc=f['vc']; sc=32 if y!='D4' else 1
    print(m,y,'SD per component (layers for D1-3, raw for D4):',{k:round(np.sqrt(v)*sc,3) for k,v in vc.items()}, 'icc',round(f['point']['icc1'],3), 'singular',f['singular'])
  d=pd.read_csv(B+f'correct/long_{m}_correct.csv')
  c=d.groupby(['fact_id','template_id'])[['D1','D2','D3','D4']].mean()
  print(m,'cell-level Spearman:\n',c.corr(method='spearman').round(2).to_string())
  fm=d.groupby('fact_id')[['D1','D2','D3','D4']].mean()
  print(m,'fact-mean Spearman D1 vs D2,D3,D4:',fm.corr(method='spearman').loc['D1'].round(2).to_dict())
