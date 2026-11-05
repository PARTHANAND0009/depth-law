"""S1: build data/facts.parquet from CounterFact (true targets), PopQA and LRE relations.

T-REx note: CounterFact is built from ParaRel, whose triples come from T-REx, so the
CounterFact slice is the T-REx subset. No separate T-REx download is used.
"""
from __future__ import annotations

import argparse
import collections
import glob
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from depthlaw.io import ROOT, RunLog, make_run_id, provenance, seed_everything
from depthlaw.facts import wikidata

LRE_DIR = Path("/home/user/evandez/relations/data/factual")
TOKENIZERS = {
    "pythia": "EleutherAI/pythia-70m",
    "olmo2": "allenai/OLMo-2-1124-7B",
    "llama31": "meta-llama/Llama-3.1-8B",
    "qwen3": "Qwen/Qwen3-8B",
    "gemma3": "google/gemma-3-4b-pt",
}
MAX_ALIASES = 5
GENERIC_RATIO = 0.3


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").replace("\xa0", " ")).strip()


def load_raw(rel_cfg: dict) -> pd.DataFrame:
    from datasets import load_dataset
    cf_map = {p: r for r, c in rel_cfg.items() for p in c.get("cf", [])}
    pq_map = {p: r for r, c in rel_cfg.items() for p in c.get("popqa", [])}
    lre_map = {p: r for r, c in rel_cfg.items() for p in c.get("lre", [])}
    rows = []
    cf = load_dataset("azhx/counterfact", split="train")
    for ex in cf:
        rw = ex["requested_rewrite"]
        if rw["relation_id"] in cf_map:
            rows.append(dict(subject=norm(rw["subject"]), relation=cf_map[rw["relation_id"]],
                             object=norm(rw["target_true"]["str"]), source="counterfact",
                             source_id=f"cf{ex['case_id']}", subj_qid=None,
                             obj_qid=rw["target_true"]["id"], s_aliases=[], o_aliases=[]))
    pq = load_dataset("akariasai/PopQA", split="test")
    for ex in pq:
        if ex["prop"] in pq_map:
            rows.append(dict(subject=norm(ex["subj"]), relation=pq_map[ex["prop"]],
                             object=norm(ex["obj"]), source="popqa", source_id=f"pq{ex['id']}",
                             subj_qid=ex["s_uri"].rsplit("/", 1)[-1],
                             obj_qid=ex["o_uri"].rsplit("/", 1)[-1],
                             s_aliases=json.loads(ex["s_aliases"]), o_aliases=json.loads(ex["o_aliases"])))
    for f in sorted(glob.glob(str(LRE_DIR / "*.json"))):
        name = Path(f).stem
        if name not in lre_map:
            continue
        d = json.load(open(f))
        for i, s in enumerate(d["samples"]):
            rows.append(dict(subject=norm(s["subject"]), relation=lre_map[name], object=norm(s["object"]),
                             source="lre", source_id=f"lre_{name}_{i}", subj_qid=None, obj_qid=None,
                             s_aliases=[], o_aliases=[]))
    return pd.DataFrame(rows)


def drop_reason(r) -> str | None:
    s, o = r.subject, r.object
    if not s or not o:
        return "empty"
    if len(o.split()) > 4 or len(o) > 40:
        return "object_too_long"
    if len(s.split()) > 8:
        return "subject_too_long"
    if o.lower() in s.lower() or s.lower() in o.lower():
        return "object_subject_overlap"
    if re.fullmatch(r"[\d\W]+", o):
        return "object_non_alpha"
    return None


def clean_alias(a: str, canonical: str) -> bool:
    a = norm(a)
    if a == canonical or len(a) < 4 or "." in a or "(" in a or "," in a:
        return False
    if a.isupper() and len(a) <= 5:
        return False
    # conservative: alias must share a >=4-char word with the canonical name. Keeps
    # "French language", "Republic of Venezuela", "George James Rankin"; drops noisy
    # Wikidata altLabels such as "Land of the Rising Sun", "Londinium", "music by".
    cw = {w.lower() for w in re.findall(r"\w+", canonical) if len(w) >= 4}
    aw = {w.lower() for w in re.findall(r"\w+", a) if len(w) >= 4}
    if not (cw & aw):
        return False
    # drop truncations ("Strudel" for "Peter Strudel"): they are ambiguous and, being
    # nested in the canonical, would absorb its occurrences at count time
    cws = {w.lower() for w in re.findall(r"\w+", canonical)}
    aws = {w.lower() for w in re.findall(r"\w+", a)}
    if aws < cws:
        return False
    return len(a.split()) <= 6


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=str(ROOT / "configs" / "relations.yaml"))
    ap.add_argument("--seed", type=int, default=1234)
    args = ap.parse_args(argv)
    cfg = yaml.safe_load(open(args.config))
    seed_everything(args.seed)
    run_id = make_run_id("S1")
    log = RunLog("S1", run_id)
    rels = cfg["relations"]

    raw = load_raw(rels)
    log.log(event="raw", n=len(raw), by_source=raw.source.value_counts().to_dict())
    raw["drop"] = raw.apply(drop_reason, axis=1)
    drops = collections.Counter(raw["drop"].dropna())
    df = raw[raw["drop"].isna()].drop(columns="drop")

    # dedupe on (subject, relation); conflicting objects -> keep the first by source priority
    prio = {"counterfact": 0, "popqa": 1, "lre": 2}
    df = df.assign(_p=df.source.map(prio)).sort_values(["_p", "source_id"])
    key = df.subject.str.lower() + "||" + df.relation
    n_obj = df.assign(k=key).groupby("k").object.nunique()
    conflict_keys = set(n_obj[n_obj > 1].index)
    df = df.assign(k=key).drop_duplicates("k").drop(columns="_p")
    df["object_conflict"] = df.k.isin(conflict_keys)
    df = df.drop(columns="k")
    drops["duplicate_subject_relation"] = len(raw) - sum(drops.values()) - len(df)

    # pre-sample 1.6x cap per relation, then link + drop ambiguous, then take cap
    rng = np.random.default_rng(args.seed)
    cap = cfg["cap_per_relation"]
    pre = []
    for rel, g in df.groupby("relation"):
        idx = rng.permutation(len(g))[: int(cap * 1.6)]
        pre.append(g.iloc[np.sort(idx)])
    df = pd.concat(pre).reset_index(drop=True)

    # generic-word subjects (book/film titles like "With", "Silver", "Growing Up"): the
    # Wikidata label test cannot catch these. Data-driven test on the Pile index: a subject of
    # <=3 words is generic if its lowercased form is >= GENERIC_RATIO as frequent as the form
    # given (proper nouns: "paris" << "Paris"). Subjects of <=3 characters are dropped.
    from depthlaw.freq.infinigram_client import InfiniGramClient
    ig = InfiniGramClient()
    test = df[(df.subject.str.split().str.len() <= 3) & (df.subject != df.subject.str.lower())]
    forms = sorted(set(test.subject) | set(test.subject.str.lower()))
    cnt = dict(zip(forms, ig.map(lambda q: ig.count_str("v4_piletrain_llama", q)["count"], forms, workers=4)))
    ratio = {s: cnt[s.lower()] / max(cnt[s], 1) for s in test.subject}
    df["lower_upper_ratio"] = df.subject.map(ratio)
    generic = (df.lower_upper_ratio >= GENERIC_RATIO) | (df.subject.str.len() <= 3)
    drops["generic_word_subject"] = int(generic.sum())
    log.log(event="generic_filter", n_tested=len(test), n_dropped=int(generic.sum()),
            examples=df[generic].subject.head(30).tolist())
    df = df[~generic].copy()

    links = wikidata.link_labels(df.subject.tolist())
    sl_top, sl_second, n_match, linked_qid = [], [], [], []
    for r in df.itertuples():
        m = links.get(r.subject, [])
        n_match.append(len(m))
        sl_top.append(m[0][1] if m else 0)
        sl_second.append(m[1][1] if len(m) > 1 else 0)
        linked_qid.append(m[0][0] if m else None)
    df["label_n_items"] = n_match
    df["label_sitelinks_top"] = sl_top
    df["label_sitelinks_second"] = sl_second
    # ambiguity: a second item with the same exact label that is itself popular
    df["ambiguous"] = (df.label_sitelinks_second >= 10) & (df.label_sitelinks_second >= 0.25 * df.label_sitelinks_top)
    # for sources without subject QID, take the linked item only if unambiguous
    df["subj_qid_source"] = np.where(df.subj_qid.notna(), "dataset", None)
    fill = df.subj_qid.isna() & ~df.ambiguous & pd.Series(linked_qid).notna().values
    df.loc[fill, "subj_qid"] = pd.Series(linked_qid)[fill.values].values
    df.loc[fill, "subj_qid_source"] = "label_link_top_sitelinks"

    amb = df[df.ambiguous]
    drops["ambiguous_subject_label"] = int(len(amb))
    df = df[~df.ambiguous].copy()

    final = []
    short = {}
    for rel, g in df.groupby("relation"):
        g = g.iloc[: cap]
        if len(g) < cfg["min_per_relation"]:
            short[rel] = len(g)
            continue
        final.append(g)
    df = pd.concat(final).reset_index(drop=True)

    # aliases (Wikidata altLabels; PopQA aliases kept as-is but cleaned)
    al = wikidata.aliases(df.subj_qid.dropna().tolist() + df.obj_qid.dropna().tolist())
    s_al, o_al, s_src, o_src = [], [], [], []
    for r in df.itertuples():
        sa = [a for a in dict.fromkeys(list(r.s_aliases) + al.get(r.subj_qid or "", [])) if clean_alias(a, r.subject)][:MAX_ALIASES]
        oa = [a for a in dict.fromkeys(list(r.o_aliases) + al.get(r.obj_qid or "", [])) if clean_alias(a, r.object)][:MAX_ALIASES]
        s_al.append(sa); o_al.append(oa)
        s_src.append("popqa+wikidata" if r.source == "popqa" else ("wikidata" if r.subj_qid else "none"))
        o_src.append("popqa+wikidata" if r.source == "popqa" else ("wikidata" if r.obj_qid else "none"))
    df["s_aliases"], df["o_aliases"] = s_al, o_al
    df["s_alias_source"], df["o_alias_source"] = s_src, o_src

    df["templates"] = df.relation.map(lambda r: rels[r]["templates"])
    df["n_templates"] = df.templates.map(len)
    df.insert(0, "fact_id", [f"f{i:05d}" for i in range(len(df))])

    # per-tokenizer token counts (object follows template with a leading space)
    from transformers import AutoTokenizer
    for short_name, repo in TOKENIZERS.items():
        tok = AutoTokenizer.from_pretrained(repo)
        o_ids = [tok.encode(" " + o, add_special_tokens=False) for o in df.object]
        s_ids = [tok.encode(" " + s, add_special_tokens=False) for s in df.subject]
        df[f"n_obj_tok_{short_name}"] = [len(x) for x in o_ids]
        df[f"obj_first_tok_{short_name}"] = [x[0] for x in o_ids]
        df[f"n_subj_tok_{short_name}"] = [len(x) for x in s_ids]

    out = ROOT / "data" / "facts.parquet"
    df.to_parquet(out, index=False)
    prov = provenance(run_id, cfg)
    (ROOT / "data" / "facts.meta.json").write_text(json.dumps(prov, indent=2))

    # deterministic split file: fact ids by relation (used later for held-out analyses)
    splits = {"seed": args.seed, "run_id": run_id,
              "by_relation": df.groupby("relation").fact_id.apply(list).to_dict()}
    (ROOT / "data" / "splits" / "facts_by_relation.json").write_text(json.dumps(splits, indent=1))

    rep = {"run_id": run_id, "n_raw": int(len(raw)), "n_final": int(len(df)),
           "n_relations": int(df.relation.nunique()), "drops": dict(drops),
           "relations_below_min": short,
           "per_relation": df.relation.value_counts().to_dict(),
           "per_source": df.source.value_counts().to_dict(),
           "object_conflicts_kept": int(df.object_conflict.sum()),
           "subj_qid_source": df.subj_qid_source.fillna("none").value_counts().to_dict(),
           "frac_with_subj_alias": float((df.s_aliases.map(len) > 0).mean()),
           "frac_with_obj_alias": float((df.o_aliases.map(len) > 0).mean())}
    log.log(event="done", **rep)
    (log.dir / "summary.json").write_text(json.dumps(rep, indent=2, default=str))
    print(json.dumps(rep, indent=2, default=str))


if __name__ == "__main__":
    main()
