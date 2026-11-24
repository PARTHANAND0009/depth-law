import json
for s in ['new226','all','all10','nomanufacturer','tcov']:
    r=json.load(open(f'{s}/p2_results.json'))
    for m in ['meta-llama/Llama-3.1-8B','allenai/OLMo-2-1124-7B']:
        x=r['models'][m]; f=x['fits']
        D1,D4=f['D1'],f['D4']
        c=lambda F,k: [round(v,3) for v in F['boot']['ci'][k]]
        print(s,m.split('/')[1],x['n_rows'],x['n_facts'],'icc',round(D1['point']['icc1'],3),c(D1,'icc1'),'diff1',round(D1['point']['diff'],3),c(D1,'diff'),'diff4',round(D4['point']['diff'],3),c(D4,'diff'),'mom',round(x['mom']['D1']['diff'],3),round(x['mom']['D4']['diff'],3),'sing',D1['singular'],D4['singular'],'warn',len(D1['warnings']),len(D4['warnings']))
r=json.load(open('lofo/p2_results.json'))
print(json.dumps(r)[:1500])
