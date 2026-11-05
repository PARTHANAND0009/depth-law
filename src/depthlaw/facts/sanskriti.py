"""S1b: convert SANSKRITI MCQ items (HF 13ari/Sanskriti, arXiv 2506.15355) to cloze triples.

Kept:
  - State Prediction -> (item, in_indian_state, state)
  - Association with a short single-place answer -> (item, region_within_state, region)
Dropped (with reasons counted in the report):
  - Country Prediction: object is always "India" (no variance to explain)
  - General Awareness: inverted questions (state -> one of many items): not functional
  - unparseable stem, long / list answers, object inside subject, duplicates
"""
from __future__ import annotations

import collections
import json
import re

import pandas as pd

from depthlaw.io import ROOT, RunLog, make_run_id, provenance

STATE_PATTERNS = [
    r"^Which state is famous for (?:the )?(?P<x>.+?)\s*\?$",
    r"^Which of the states given in the options is associated to (?:the )?(?P<x>.+?)\s*\?$",
    r"^According to you, which of the following states houses the (?P<x>.+?)\s*\?$",
]
REGION_PATTERNS = [
    r"^(?P<x>.+?)\s+is associated to which region of (?P<s>[\w_ ]+)\?$",
    r"^Which of the given regions is home to the (?P<x>.+?)\s*\?$",
    r"^Where is the (?P<x>.+?) famous within (?P<s>[\w_ ]+)\?$",
]
TEMPLATES = {
    "in_indian_state": ["{} is associated with the Indian state of",
                        "{} is found in the Indian state of",
                        "The Indian state known for {} is"],
    "region_within_state": ["{} is associated with the region of",
                            "{} is found in",
                            "The place in India known for {} is"],
}


def clean(s: str) -> str:
    s = s.replace("_", " ").strip().rstrip(".").strip()
    return re.sub(r"\s+", " ", s)


def parse(q: str, patterns):
    q = q.strip()
    for p in patterns:
        m = re.match(p, q)
        if m:
            return clean(m.group("x"))
    return None


def main():
    from datasets import load_dataset
    run_id = make_run_id("S1b")
    log = RunLog("S1", run_id)
    df = load_dataset("13ari/Sanskriti", split="train").to_pandas()
    drops = collections.Counter()
    rows = []
    for r in df.itertuples():
        qt, ans = r.question_type, clean(str(r.answer))
        if qt == "Country Prediction":
            drops["country_prediction_constant_object"] += 1
            continue
        if qt == "General Awareness":
            drops["general_awareness_not_functional"] += 1
            continue
        if qt == "State Prediction":
            x, rel = parse(r.question, STATE_PATTERNS), "in_indian_state"
        else:
            x, rel = parse(r.question, REGION_PATTERNS), "region_within_state"
        if x is None:
            drops[f"unparsed_{qt}"] += 1
            continue
        if len(ans.split()) > 3 or "," in ans or " and " in ans or len(ans) > 30:
            drops["object_long_or_list"] += 1
            continue
        if ans.lower() in x.lower():
            drops["object_in_subject"] += 1
            continue
        if len(x.split()) > 8:
            drops["subject_too_long"] += 1
            continue
        rows.append(dict(subject=x, relation=rel, object=ans, state=clean(r.state),
                         attribute=r.attribute, question=r.question, question_type=qt))
    out = pd.DataFrame(rows)
    n0 = len(out)
    # same item asked with 3 phrasings -> one fact; conflicting answers -> drop the item
    nobj = out.groupby(["subject", "relation"]).object.nunique()
    bad = set(nobj[nobj > 1].index)
    keep = ~out.set_index(["subject", "relation"]).index.isin(bad)
    drops["conflicting_answers"] = int((~keep).sum())
    out = out[keep].drop_duplicates(["subject", "relation"])
    drops["duplicate_phrasing"] = n0 - drops["conflicting_answers"] - len(out)
    out["templates"] = out.relation.map(TEMPLATES)
    out.insert(0, "fact_id", [f"sk{i:05d}" for i in range(len(out))])
    out["s_aliases"] = [[] for _ in range(len(out))]
    out["o_aliases"] = [[] for _ in range(len(out))]
    dst = ROOT / "data" / "sanskriti_cloze.parquet"
    out.to_parquet(dst, index=False)
    (ROOT / "data" / "sanskriti_cloze.meta.json").write_text(json.dumps(provenance(run_id, {"templates": TEMPLATES}), indent=2))
    rep = {"run_id": run_id, "n_items": int(len(df)), "n_kept_facts": int(len(out)),
           "kept_by_relation": out.relation.value_counts().to_dict(),
           "kept_by_attribute": out.attribute.value_counts().to_dict(),
           "drops": dict(drops), "examples": out.sample(min(12, len(out)), random_state=0)[["subject", "relation", "object"]].values.tolist()}
    log.log(event="done", **rep)
    (ROOT / "reports" / "sanskriti_conversion.json").write_text(json.dumps(rep, indent=2))
    print(json.dumps(rep, indent=2))


if __name__ == "__main__":
    main()
