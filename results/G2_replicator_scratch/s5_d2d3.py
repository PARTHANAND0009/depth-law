# Extra: D2/D3 per curve for the correct set (secondary outcomes), appended to own tables.
import glob, os
import numpy as np, pandas as pd
ROOT = "/home/user/depth-law"; S = os.path.dirname(os.path.abspath(__file__))
RUNS = {"llama": "P2-Llama-3.1-8B-ff119ca-20261124T164743Z", "olmo": "P2-OLMo-2-1124-7B-ff119ca-20261124T171447Z"}
def onset(ok):
    bad = np.where(~ok)[0]; return 0 if len(bad) == 0 else bad.max() + 1
for k, run in RUNS.items():
    c = pd.concat([pd.read_parquet(p) for p in sorted(glob.glob(f"{ROOT}/results/P2/{run}/chunks/c*.parquet"))])
    print(k, "rank min", c["rank"].min())
    rmin = c["rank"].min()
    c = c.sort_values(["fact_id", "template_id", "carrier", "layer"])
    rows = []
    for (f, t, car), g in c.groupby(["fact_id", "template_id", "carrier"], sort=False):
        p = g.p_object.to_numpy(np.float64); r = g["rank"].to_numpy(); L = len(p)
        d2 = np.nan if p[-1] < 0.1 else (onset(p >= 0.1) + 1) / L
        d3 = np.nan if r[-1] != rmin else (onset(r == rmin) + 1) / L
        rows.append((f, t, car, d2, d3))
    dd = pd.DataFrame(rows, columns=["fact_id", "template_id", "carrier", "D2", "D3"])
    tab = pd.read_csv(f"{S}/tab_{k}.csv").drop(columns=["D2", "D3"], errors="ignore").merge(dd, on=["fact_id", "template_id", "carrier"])
    print(k, "rows D2", tab.D2.notna().sum(), "facts D2", tab[tab.D2.notna()].fact_id.nunique(), "rows D3", tab.D3.notna().sum())
    tab.to_csv(f"{S}/tab_{k}.csv", index=False)
