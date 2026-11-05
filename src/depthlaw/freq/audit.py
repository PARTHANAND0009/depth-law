"""Write reports/count_audit.csv: 100 random facts with the exact surface terms queried and
their counts, plus empty columns for a human to fill in."""
from __future__ import annotations

import argparse

import pandas as pd

from depthlaw.io import ROOT


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--counts", default=str(ROOT / "data" / "counts_primary.parquet"))
    ap.add_argument("--n", type=int, default=100)
    ap.add_argument("--seed", type=int, default=1234)
    args = ap.parse_args(argv)
    f = pd.read_parquet(ROOT / "data" / "facts.parquet")
    c = pd.read_parquet(args.counts)
    m = f.merge(c, on="fact_id").sample(args.n, random_state=args.seed)
    cols = ["fact_id", "relation", "source", "subject", "object", "s_aliases", "o_aliases",
            "subj_terms", "obj_terms", "subj_piletrain", "obj_piletrain", "cooc_piletrain_w100",
            "approx_piletrain_w100", "subj_olmo-mix-1124", "obj_olmo-mix-1124",
            "cooc_olmo-mix-1124_w100", "approx_olmo-mix-1124_w100",
            "subj_dclm-baseline", "obj_dclm-baseline", "cooc_dclm-baseline_w100", "run_id"]
    out = m[[x for x in cols if x in m.columns]].copy()
    for col in ["s_aliases", "o_aliases", "subj_terms", "obj_terms"]:
        out[col] = out[col].map(lambda v: " | ".join(map(str, v)))
    out["flag_unreliable_zero"] = (out["cooc_piletrain_w100"] == 0) & (out["approx_piletrain_w100"] == 1)
    for col in ["HUMAN_subject_ambiguous(y/n)", "HUMAN_casing_ok(y/n)", "HUMAN_leading_space_ok(y/n)",
                "HUMAN_possessive_or_apostrophe_issue(y/n)", "HUMAN_alias_wrong(y/n)", "HUMAN_notes"]:
        out[col] = ""
    dst = ROOT / "reports" / "count_audit.csv"
    out.to_csv(dst, index=False)
    print(f"wrote {dst} ({len(out)} rows)")


if __name__ == "__main__":
    main()
