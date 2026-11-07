"""Assemble the G1 analysis table: depth rows (fact x template) + facts + counts + controls.

Index per model (CLAUDE.md "Indexes", prereg amendment_1): Pythia -> piletrain (EXACT),
OLMo-2 -> olmo-mix-1124 (EXACT), others -> dclm-baseline (PROXY). The label is stored in
column `count_label`, and fits never pool rows with different labels.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from depthlaw.freq.counts import LLAMA2_TOK
from depthlaw.freq.infinigram_client import InfiniGramClient
from depthlaw.io import ROOT

MEASURES = ["causal_final", "override_depth", "causal_subj_onset", "causal_subj_stable",
            "patchscope_depth", "tuned_lens_depth", "logit_lens_depth"]
TOKCOL = {"pythia": "pythia", "olmo": "olmo2", "llama": "llama31", "qwen": "qwen3", "gemma": "gemma3"}


def index_for(model: str) -> tuple[str, str]:
    m = model.lower()
    if "pythia" in m:
        return "piletrain", "EXACT"
    if "olmo-2" in m:
        return "olmo-mix-1124", "EXACT"
    return "dclm-baseline", "PROXY"


def tok_family(model: str) -> str:
    m = model.lower()
    for k, v in TOKCOL.items():
        if k in m:
            return v
    raise ValueError(model)


def first_token_counts(objects: list[str], ix: str) -> dict[str, float]:
    """Exact corpus count of the object's first token (Llama-2 tokenization of ' '+object),
    the control log_answer_first_token_freq. Cached API calls."""
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(LLAMA2_TOK)
    cl = InfiniGramClient()
    full = f"v4_{ix}_llama"
    firsts = {o: tok.encode(" " + o, add_special_tokens=False)[:1] for o in set(objects)}
    uniq = sorted({tuple(v) for v in firsts.values()})
    res = cl.map_robust(lambda t: cl.query({"index": full, "query_type": "count", "query_ids": [[list(t)]]}),
                        uniq, workers=6)
    cnt = {t: (r["count"] if r and "count" in r else np.nan) for t, r in zip(uniq, res)}
    return {o: cnt[tuple(v)] for o, v in firsts.items()}


def build(depth: pd.DataFrame, model: str, facts_path=None, exact_path=None, cnf_path=None) -> pd.DataFrame:
    facts = pd.read_parquet(facts_path or ROOT / "data" / "facts.parquet")
    exact = pd.read_parquet(exact_path or ROOT / "data" / "counts_exact.parquet")
    cnf = pd.read_parquet(cnf_path or ROOT / "data" / "counts_primary.parquet")
    ix, label = index_for(model)
    fam = tok_family(model)
    f = facts[["fact_id", "subject", "object", f"n_obj_tok_{fam}", f"n_subj_tok_{fam}"]].rename(
        columns={f"n_obj_tok_{fam}": "n_answer_tokens", f"n_subj_tok_{fam}": "n_subject_tokens"})
    c = cnf[["fact_id", f"subj_{ix}", f"obj_{ix}", f"cooc_{ix}_w100", f"approx_{ix}_w100"]].rename(columns={
        f"subj_{ix}": "subj_count", f"obj_{ix}": "obj_count", f"cooc_{ix}_w100": "cnf_cooc",
        f"approx_{ix}_w100": "approx_flag"})
    e = exact[["fact_id", f"exact_{ix}"]].rename(columns={f"exact_{ix}": "exact_cooc"})
    d = depth.merge(f, on="fact_id").merge(c, on="fact_id").merge(e, on="fact_id", how="left")
    ftc = first_token_counts(d.object.unique().tolist(), ix)
    d["answer_first_token_count"] = d.object.map(ftc)
    d["log_cooc"] = np.log1p(d.exact_cooc)
    d["log_cnf_cooc"] = np.log1p(d.cnf_cooc)
    d["log_subj"] = np.log1p(d.subj_count)
    d["log_obj"] = np.log1p(d.obj_count)
    d["log_answer_first_token_freq"] = np.log1p(d.answer_first_token_count)
    d["count_index"], d["count_label"] = ix, label
    d["template"] = d.relation + ":" + d.template_id.astype(str)
    return d
