"""Per-model analysis table for the revised H-R gate (prereg/HR_revised.md, Part B)."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from transformers import AutoTokenizer

from depthlaw.depth.causal import half_prob_layer
from depthlaw.depth.common import first_stable_layer

ROOT = Path(__file__).resolve().parents[3]
RUNS = {
    "EleutherAI/pythia-1.4b": "results/S3b/S3b-pythia-1.4b-a7dfeb5-20261121T063528Z/depth.parquet",
    "EleutherAI/pythia-2.8b": "results/S3b/S3b-pythia-2.8b-a7dfeb5-20261121T064110Z/depth.parquet",
    "allenai/OLMo-2-1124-7B": "results/S3b/S3b-OLMo-2-1124-7B-923945f-20261121T061237Z/depth.parquet",
}
FAMILY = {"EleutherAI/pythia-1.4b": "pythia", "EleutherAI/pythia-2.8b": "pythia", "allenai/OLMo-2-1124-7B": "olmo2"}
INDEX = {"pythia": "piletrain", "olmo2": "olmo-mix-1124"}
FACT_COV = ["n_answer_tokens", "log_prior", "obj_logprob_final", "n_subject_tokens", "subj_final_dist"]
REL_COV = ["log_k", "n_distinct", "collapse_rate", "rel_accuracy", "rel_mean_final_logprob"]


def tag(model: str) -> str:
    return model.split("/")[-1]


def subj_final_dist(tok, template: str, subject: str) -> int:
    """(n prompt tokens - 1) - subject last-token index; same tokenization as common.subject_last_pos."""
    prefix, _ = template.split("{}", 1)
    enc = tok(template.format(subject), return_offsets_mapping=True)
    end_char = len(prefix) + len(subject)
    idx = max(i for i, (a, b) in enumerate(enc["offset_mapping"]) if b > a and a < end_char)
    return len(enc["input_ids"]) - 1 - idx


def frac_depth(curves, frac: float) -> float:
    """Mean over carriers of (l_c+1)/L, l_c = half_prob_layer at the given fraction of the final p."""
    out = []
    for lp in curves:
        p = np.exp(np.asarray(lp, dtype=float))
        out.append((half_prob_layer(p, frac) + 1) / len(p))
    return float(np.mean(out))


def p01_onset(curves) -> float:
    out = []
    for lp in curves:
        p = np.exp(np.asarray(lp, dtype=float))
        if p[-1] < 0.1:
            return np.nan
        l = first_stable_layer(list(p >= 0.1))
        out.append((l + 1) / len(p))
    return float(np.mean(out))


def build(model: str, verbose: bool = True) -> pd.DataFrame:
    d = pd.read_parquet(ROOT / RUNS[model])
    n_per_fact = d.groupby("fact_id").template_id.nunique()
    assert len(d) == 3900, f"{model}: {len(d)} rows"
    assert d.relation.nunique() == 26, f"{model}: {d.relation.nunique()} relations"
    assert (n_per_fact == 3).all() and sorted(d.template_id.unique()) == [0, 1, 2], f"{model}: templates"
    assert d.half_prob_depth.notna().all()
    if verbose:
        npr = d.groupby("relation").agg(rows=("fact_id", "size"), facts=("fact_id", "nunique"))
        print(f"{model}: N per relation (rows/facts):", "; ".join(f"{r} {a}/{b}" for r, (a, b) in npr.iterrows()))
    fam = FAMILY[model]
    ix = INDEX[fam]
    facts = pd.read_parquet(ROOT / "data" / "facts_g1cpu.parquet")[["fact_id", "subject", "object", "templates"]]
    inp = pd.read_parquet(ROOT / "data" / "amend2_inputs.parquet")
    inp = inp[["fact_id", f"n_obj_tok_{fam}", f"n_subj_tok_{fam}", f"exact_{ix}"]].rename(columns={
        f"n_obj_tok_{fam}": "n_answer_tokens", f"n_subj_tok_{fam}": "n_subject_tokens", f"exact_{ix}": "exact_cooc"})
    prior = pd.read_parquet(ROOT / "cache" / "hr" / f"prior_{tag(model)}.parquet")
    d = d.merge(facts, on="fact_id", how="left").merge(inp, on="fact_id", how="left").merge(prior, on="object", how="left")
    tok = AutoTokenizer.from_pretrained(model)
    d["template_text"] = [list(t)[i] for t, i in zip(d.templates, d.template_id)]
    d["subj_final_dist"] = [subj_final_dist(tok, t, s) for t, s in zip(d.template_text, d.subject)]
    first = {o: tok.encode(" " + o, add_special_tokens=False)[0] for o in d.object.unique()}
    d["obj_first_id"] = d.object.map(first)
    d["whole_word"] = [tok.decode([first[o]]).strip() == o.split()[0] for o in d.object]
    # outcomes
    d["y"] = d.half_prob_depth
    d["y25"] = [frac_depth(c, 0.25) for c in d.final_logprob_curves]
    d["y75"] = [frac_depth(c, 0.75) for c in d.final_logprob_curves]
    for c in range(3):
        d[f"y_c{c}"] = [float(v[c]) for v in d.half_prob_depth_per_carrier]
    d["p01_onset"] = [p01_onset(c) for c in d.final_logprob_curves]
    d["rank1_onset"] = d.causal_final
    L = int(d.n_layers.iloc[0])
    d["event_layer"] = np.rint(L * d.half_prob_depth).astype(int)  # 1-based
    d["obj_logprob_final"] = d.obj_first_logprob
    d["correct"] = d.correct_at1.astype(int)
    d["log_cooc"] = np.log1p(d.exact_cooc)
    d["cooc_within"] = d.log_cooc - d.groupby("relation").log_cooc.transform("mean")
    # relation covariates
    full = pd.read_parquet(ROOT / "data" / "facts.parquet")
    k = full.groupby("relation").object.nunique()
    g1 = d.drop_duplicates("fact_id")
    rel = pd.DataFrame({"log_k": np.log(k), "n_distinct": g1.groupby("relation").object.nunique()})

    def collapse(g):
        ft = g.drop_duplicates("object").groupby("obj_first_id").object.nunique()
        shared = set(ft[ft > 1].index)
        return float(g.obj_first_id.isin(shared).mean())
    rel["collapse_rate"] = g1.groupby("relation").apply(collapse, include_groups=False)
    rel["rel_accuracy"] = d.groupby("relation").correct.mean()
    rel["rel_mean_final_logprob"] = d.groupby("relation").obj_logprob_final.mean()
    d = d.merge(rel.reset_index(), on="relation", how="left")
    for c in FACT_COV:
        d[c + "_raw"] = d[c]
        d[c] = (d[c] - d[c].mean()) / d[c].std()
    need = ["y"] + FACT_COV + ["cooc_within"]
    assert d[need].notna().all().all(), d[need].isna().sum()
    d["model"], d["L"] = model, L
    return d


CSV_COLS = (["fact_id", "template_id", "relation", "subject", "object", "correct", "whole_word", "y", "y25", "y75",
             "y_c0", "y_c1", "y_c2", "p01_onset", "rank1_onset", "event_layer", "L", "cooc_within", "log_cooc"]
            + FACT_COV + [c + "_raw" for c in FACT_COV] + REL_COV)
