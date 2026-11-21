"""EXPLORATORY (post hoc, not preregistered) — E-depthvar B1/B2/B5 table builder.

Reads the S3b rows (no model is loaded) and writes, per model, one row per (fact, template) cell with
D1-D4 (B1), censoring flags, per-carrier D1/D4, correctness (B2) and the B5 covariates, plus a long
per-carrier table for the carrier facet (B7c). Output: results/EXPLORATORY_E-depthvar/<run_id>/tables/.
Usage: python <this file> <out_dir>
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from transformers import AutoTokenizer

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
from depthlaw.hr.assemble import subj_final_dist  # noqa: E402  (tokenization identical to S3)

RUNS = {
    "pythia-1.4b": ("EleutherAI/pythia-1.4b", "results/S3b/S3b-pythia-1.4b-a7dfeb5-20261121T063528Z/depth.parquet", "pythia", "piletrain"),
    "pythia-2.8b": ("EleutherAI/pythia-2.8b", "results/S3b/S3b-pythia-2.8b-a7dfeb5-20261121T064110Z/depth.parquet", "pythia", "piletrain"),
    "OLMo-2-1124-7B": ("allenai/OLMo-2-1124-7B", "results/S3b/S3b-OLMo-2-1124-7B-923945f-20261121T061237Z/depth.parquet", "olmo2", "olmo-mix-1124"),
}


def stable_from(ok):
    """min l with ok[l'] for all l' >= l; None if ok[-1] is False."""
    if not ok[-1]:
        return None
    l = len(ok) - 1
    while l > 0 and ok[l - 1]:
        l -= 1
    return l


def per_carrier(lp_curves, rank_curves):
    out = {"D1": [], "D2": [], "D3": [], "D4": []}
    for lp, rk in zip(lp_curves, rank_curves):
        p = np.exp(np.asarray(lp, float))
        L = len(p)
        out["D1"].append((stable_from(list(p >= 0.5 * p[-1])) + 1) / L)
        d2 = stable_from(list(p >= 0.1))
        out["D2"].append(None if d2 is None else (d2 + 1) / L)
        d3 = stable_from(list(np.asarray(rk) == 1))
        out["D3"].append(None if d3 is None else (d3 + 1) / L)
        out["D4"].append(1.0 - float(np.mean(np.minimum(1.0, p / p[-1]))))
    return out, L


def build(tag):
    name, path, fam, ix = RUNS[tag]
    d = pd.read_parquet(ROOT / path)
    assert len(d) == 3900 and d.relation.nunique() == 26 and (d.groupby("fact_id").template_id.nunique() == 3).all()
    facts = pd.read_parquet(ROOT / "data/facts_g1cpu.parquet")[["fact_id", "subject", "object", "templates"]]
    inp = pd.read_parquet(ROOT / "data/amend2_inputs.parquet")[["fact_id", f"n_subj_tok_{fam}", f"exact_{ix}"]]
    inp = inp.rename(columns={f"n_subj_tok_{fam}": "n_subj_tok", f"exact_{ix}": "exact_cooc"})
    d = d.merge(facts, on="fact_id").merge(inp, on="fact_id")
    tok = AutoTokenizer.from_pretrained(name)
    rows, long = [], []
    for r in d.itertuples():
        pc, L = per_carrier(r.final_logprob_curves, r.final_rank_curves)
        tmpl = list(r.templates)[r.template_id]
        n_prompt = len(tok(tmpl.format(r.subject))["input_ids"])
        row = {"model": tag, "fact_id": r.fact_id, "relation": r.relation, "subject": r.subject,
               "template_id": int(r.template_id), "correct": int(bool(r.correct_at1)), "L": L,
               "D1": float(np.mean(pc["D1"])), "D4": float(np.mean(pc["D4"])),
               "stored_half_prob_depth": float(r.half_prob_depth),
               "tmpl_len_tokens": n_prompt - int(r.n_subj_tok),
               "subj_final_dist": subj_final_dist(tok, tmpl, r.subject),
               "n_subj_tokens": int(r.n_subj_tok),
               "answer_prior": float(np.mean(r.carrier_alone_obj_logprob)),
               "final_logp": float(r.obj_first_logprob),
               "log_cooc": float(np.log1p(r.exact_cooc)), "cooc_label": "EXACT"}
        for k in ("D2", "D3"):
            v = pc[k]
            cens = any(x is None for x in v)
            row[k] = None if cens else float(np.mean(v))
            row[k + "_censored"] = int(cens)
            row[k + "_cens_as_Lp1"] = float(np.mean([(L + 1) / L if x is None else x for x in v]))
        for c in range(3):
            row[f"D1_c{c}"], row[f"D4_c{c}"] = pc["D1"][c], pc["D4"][c]
            long.append({"model": tag, "fact_id": r.fact_id, "relation": r.relation, "subject": r.subject,
                         "template_id": int(r.template_id), "carrier": c, "correct": row["correct"],
                         "D1": pc["D1"][c], "D4": pc["D4"][c]})
        rows.append(row)
    cell = pd.DataFrame(rows)
    assert np.allclose(cell.D1, cell.stored_half_prob_depth), "D1 recomputation differs from stored half_prob_depth"
    nc = cell.groupby("fact_id").correct.sum()
    cell["n_correct_templates"] = cell.fact_id.map(nc)
    return cell, pd.DataFrame(long)


def main(out):
    out = Path(out)
    (out / "tables").mkdir(parents=True, exist_ok=True)
    summary = {}
    for tag in RUNS:
        cell, long = build(tag)
        p = "EXPLORATORY_post-hoc_not-preregistered__"
        cell.to_csv(out / "tables" / f"{p}cells_{tag}.csv", index=False)
        long.to_csv(out / "tables" / f"{p}carrier_long_{tag}.csv", index=False)
        f = cell.drop_duplicates("fact_id")
        cc = cell[cell.correct == 1]
        all3 = cell[cell.n_correct_templates == 3]
        summary[tag] = {
            "n_cells": len(cell), "n_layers": int(cell.L.iloc[0]),
            "facts_by_n_correct_templates": {str(k): int((f.n_correct_templates == k).sum()) for k in (3, 2, 1, 0)},
            "n_correct_cells": int(len(cc)), "n_facts_all3": int(all3.fact_id.nunique()),
            "censoring": {s: {k: {"n": int(len(dd)), "censored": int(dd[k + "_censored"].sum()),
                                  "rate": float(dd[k + "_censored"].mean()) if len(dd) else None}
                              for k in ("D2", "D3")}
                          for s, dd in (("correct_cells", cc), ("all3", all3), ("all_cells", cell))},
            "D1_matches_stored": True}
    (out / "build_summary.json").write_text(json.dumps(summary, indent=1))
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main(sys.argv[1])
