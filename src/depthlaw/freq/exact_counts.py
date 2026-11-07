"""S2x: exact phrase co-occurrence (prereg amendment_1, configs/s2_exact.yaml).

For each fact, build the token sequences of every connector pattern filled with the canonical
subject S and object O, in all surface variants (leading space / no leading space, capitalised
first letter if lowercase, straight/curly apostrophe). Terms are OR-joined in single-clause
queries of <=4 terms; a single OR clause returns the exact sum of its terms' n-gram counts (no
sampling; 'approx' is not applicable). Terms containing another term are dropped (nested-term
dedupe) so OR sums do not double count. Output per fact and index: exact_<idx> (sum) and the
number of terms/queries used.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from depthlaw.freq.counts import TermBuilder, _chunks, _contains
from depthlaw.freq.infinigram_client import InfiniGramClient, InfiniGramError
from depthlaw.io import ROOT, RunLog, make_run_id, provenance, seed_everything

CFG = ROOT / "configs" / "s2_exact.yaml"


def phrase_terms(tb: TermBuilder, subject: str, obj: str, patterns: list[str]) -> list[tuple[int, ...]]:
    terms = []
    for p in patterns:
        for s in tb.string_variants(subject):
            for o in tb.string_variants(obj):
                ph = p.format(S=s, O=o)
                vs = [ph, ph.replace("'", "’")] if "'" in p else [ph]  # connector apostrophe variants
                for v in vs:
                    terms.extend(tb.ids(v))
    terms = list(dict.fromkeys(terms))
    return [t for t in terms if not any(o != t and len(o) < len(t) and _contains(t, o) for o in terms)]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--facts", default=str(ROOT / "data" / "facts.parquet"))
    ap.add_argument("--indexes", nargs="+", default=None)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--seed", type=int, default=1234)
    args = ap.parse_args(argv)
    seed_everything(args.seed)
    cfg = yaml.safe_load(CFG.read_text())
    indexes = args.indexes or cfg["indexes"]
    patterns = cfg["patterns_s_first"] + cfg["patterns_o_first"]
    run_id = make_run_id("S2x")
    log = RunLog("S2", run_id)

    facts = pd.read_parquet(args.facts)
    if args.limit:
        facts = facts.iloc[: args.limit]
    tb = TermBuilder()
    cl = InfiniGramClient()
    terms = [phrase_terms(tb, r.subject, r.object, patterns) for r in facts.itertuples()]
    jobs = sorted({(ix, c) for ix in indexes for t in terms for c in _chunks(t)})
    log.log(event="jobs", n=len(jobs), n_facts=len(facts), indexes=indexes)

    def run(j):
        r = cl.query({"index": j[0], "query_type": "count", "query_ids": [[list(t) for t in j[1]]]})
        if "count" not in r:
            raise InfiniGramError(str(r)[:200])
        return r
    res = dict(zip(jobs, cl.map_robust(run, jobs, workers=args.workers)))

    rows, n_err = [], 0
    for r, t in zip(facts.itertuples(), terms):
        row = {"fact_id": r.fact_id, "n_phrase_terms": len(t), "n_queries_per_index": len(_chunks(t))}
        for ix in indexes:
            sh = ix.replace("v4_", "").replace("_llama", "")
            rs = [res[(ix, c)] for c in _chunks(t)]
            if any(x is None for x in rs):
                n_err += 1
                row[f"exact_{sh}"] = np.nan
            else:
                row[f"exact_{sh}"] = sum(x["count"] for x in rs)
        rows.append(row)
    out = pd.DataFrame(rows)
    out["run_id"] = run_id
    stem = Path(args.facts).stem.replace("facts", "counts")
    dst = ROOT / "data" / f"{stem}_exact{'_smoke' if args.limit else ''}.parquet"
    out.to_parquet(dst, index=False)
    dst.with_suffix(".meta.json").write_text(json.dumps(provenance(run_id, {**cfg, "indexes": indexes}), indent=2))
    summ = {"run_id": run_id, "out": str(dst.relative_to(ROOT)), "n_facts": len(out), "n_jobs": len(jobs),
            "n_fact_index_missing": n_err, "network_calls": cl.n_network, "cache_hits": cl.n_cached,
            "throttled": cl.n_throttled}
    for c in [c for c in out.columns if c.startswith("exact_")]:
        summ[c] = {"zero_frac": float((out[c] == 0).mean()), "median": float(out[c].median()),
                   "missing": int(out[c].isna().sum())}
    log.log(event="done", **summ)
    (log.dir / "summary.json").write_text(json.dumps(summ, indent=2))
    print(json.dumps(summ, indent=2))


if __name__ == "__main__":
    main()
