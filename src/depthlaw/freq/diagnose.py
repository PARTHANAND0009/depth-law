"""S2 diagnostic: approximate-count reliability. Reads the primary/sensitivity count files,
writes results/S2/<run_id>/approx_diagnostic.json. No API calls."""
from __future__ import annotations
import json
import pandas as pd
from depthlaw.io import ROOT, RunLog, make_run_id

IX = {"piletrain": "EXACT (Pythia)", "olmo-mix-1124": "EXACT (OLMo-2 stage 1)", "dclm-baseline": "PROXY"}


def table(d: pd.DataFrame, windows) -> dict:
    out = {"n_facts": int(len(d)), "source_run_ids": sorted(d.run_id.unique().tolist())}
    for ix, lab in IX.items():
        for w in windows:
            c = f"cooc_{ix}_w{w}"
            if c not in d:
                continue
            a = d[f"approx_{ix}_w{w}"] == 1
            z = d[c] == 0
            r = {"label": lab, "n": int(d[c].notna().sum()), "n_zero": int(z.sum()), "n_approx": int(a.sum()),
                 "n_zero_and_approx": int((z & a).sum()), "n_zero_not_approx": int((z & ~a).sum()),
                 "median_approx": float(d.loc[a, c].median()) if a.any() else None,
                 "median_not_approx": float(d.loc[~a, c].median()) if (~a).any() else None}
            if ix != "piletrain" and "cooc_piletrain_w100" in d and w == 100:
                r["n_zero_but_pile_w100_pos"] = int((z & (d.cooc_piletrain_w100 > 0)).sum())
                both = (d[c] > 0) & (d.cooc_piletrain_w100 > 0)
                r["n_both_pos"] = int(both.sum())
                r["n_below_pile_when_both_pos"] = int((both & (d[c] < d.cooc_piletrain_w100)).sum())
            out[c] = r
    return out


def main():
    run_id = make_run_id("S2diag")
    log = RunLog("S2", run_id)
    res = {"run_id": run_id}
    for name, prim, sens in [("facts", "counts_primary", "counts_sensitivity"),
                             ("sanskriti", "sanskriti_cloze_primary", "sanskriti_cloze_sensitivity")]:
        p = pd.read_parquet(ROOT / "data" / f"{prim}.parquet")
        s = pd.read_parquet(ROOT / "data" / f"{sens}.parquet")
        res[name] = {"primary_w100": table(p, [100]), "sensitivity": table(s, [32, 500])}
    f = pd.read_parquet(ROOT / "data" / "facts.parquet").set_index("fact_id")
    p = pd.read_parquet(ROOT / "data" / "counts_primary.parquet")
    e = p[p["cooc_dclm-baseline_w100"] == 0].sort_values("cooc_piletrain_w100", ascending=False).head(5)
    res["examples_dclm_zero_pile_high"] = [
        {"fact_id": r.fact_id, "subject": f.loc[r.fact_id, "subject"], "object": f.loc[r.fact_id, "object"],
         "pile_w100": float(r.cooc_piletrain_w100), "olmo_w100": float(r["cooc_olmo-mix-1124_w100"]),
         "dclm_w100": float(r["cooc_dclm-baseline_w100"])} for _, r in e.iterrows()]
    log.log(event="done", **{"run_id": run_id})
    (log.dir / "approx_diagnostic.json").write_text(json.dumps(res, indent=2))
    print(log.dir / "approx_diagnostic.json")


if __name__ == "__main__":
    main()
