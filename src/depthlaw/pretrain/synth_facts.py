"""S6 fictional facts: 2000 (subject, relation, object) with fictional subjects of exactly
`subject_tokens` tokens of the S6 tokenizer, objects from a fixed per-relation pool assigned round-robin so that
every frequency bin has the same object distribution, and the same subject-token length in every bin.

Output: data/s6/facts.parquet (fact_id, subject, relation, object, freq, templates = eval templates,
train_templates, o_aliases, n_obj_tok, obj_first_tok, n_subj_tok).
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd
import yaml
from transformers import AutoTokenizer

from depthlaw.io import ROOT

ONSETS = ["b", "br", "c", "d", "dr", "f", "g", "gr", "h", "k", "l", "m", "n", "p", "qu", "r", "s", "t", "tr", "v", "z"]
VOWELS = ["a", "e", "i", "o", "u", "ae", "ia", "ou"]
CODAS = ["", "", "n", "r", "l", "s", "th", "x", "m"]


def _word(rng, n_syl: int) -> str:
    w = "".join(rng.choice(ONSETS) + rng.choice(VOWELS) + rng.choice(CODAS) for _ in range(n_syl))
    return w.capitalize()


def make(cfg: dict) -> pd.DataFrame:
    rng = np.random.default_rng(cfg["seed"])
    tok = AutoTokenizer.from_pretrained(ROOT / cfg["tokenizer"])
    ntok = lambda s: len(tok.encode(" " + s, add_special_tokens=False))
    rels = cfg["relations"]
    names = list(rels)
    n_bins = len(cfg["freqs"])
    per_rel_bin = cfg["n_facts"] // (len(names) * n_bins)
    # objects: first tokens must be distinct within a relation
    for r, spec in rels.items():
        firsts = [tok.encode(" " + o, add_special_tokens=False)[0] for o in spec["objects"]]
        assert len(set(firsts)) == len(firsts), f"duplicate object first tokens in {r}"
        assert per_rel_bin % len(spec["objects"]) == 0, "objects must divide facts per (relation, bin)"
    # subjects: two invented words, exactly subject_tokens tokens, unique
    subjects, seen = [], set()
    while len(subjects) < cfg["n_facts"]:
        s = f"{_word(rng, int(rng.integers(1, 3)))} {_word(rng, int(rng.integers(1, 3)))}"
        if s not in seen and ntok(s) == cfg["subject_tokens"]:
            seen.add(s)
            subjects.append(s)
    rng.shuffle(subjects)
    rows, k = [], 0
    for r in names:
        spec = rels[r]
        for f in cfg["freqs"]:
            for i in range(per_rel_bin):
                o = spec["objects"][i % len(spec["objects"])]
                rows.append({"fact_id": f"s6_{k:05d}", "subject": subjects[k], "relation": r, "object": o, "freq": f,
                             "templates": list(spec["eval"]), "train_templates": list(spec["train"]), "o_aliases": []})
                k += 1
    df = pd.DataFrame(rows)
    df["n_obj_tok"] = df.object.map(ntok)
    df["obj_first_tok"] = df.object.map(lambda o: tok.encode(" " + o, add_special_tokens=False)[0])
    df["n_subj_tok"] = df.subject.map(ntok)
    return df


def main():
    cfg = yaml.safe_load(open(ROOT / "configs" / "s6.yaml"))
    df = make(cfg)
    out = ROOT / "data" / "s6"
    out.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out / "facts.parquet", index=False)
    summ = df.groupby("freq").agg(n=("fact_id", "size"), subj_tok=("n_subj_tok", "mean"),
                                  obj_tok=("n_obj_tok", "mean")).reset_index().to_dict("records")
    (out / "facts_summary.json").write_text(json.dumps(summ, indent=1))
    print(json.dumps(summ))


if __name__ == "__main__":
    main()
