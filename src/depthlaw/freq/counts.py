"""S2: subject / object / co-occurrence counts for every fact x index via infini-gram.

Counting rules (CLAUDE.md "Indexes"):
- Surface variants per string: leading-space and no-leading-space tokenizations (Llama-2
  tokenizer, which all used indexes share); first-letter capitalised variant when the string
  starts lowercase (we do NOT add lowercase variants of capitalised names, to avoid
  common-word inflation, e.g. "Apple" -> "apple"); straight <-> curly apostrophe.
- Aliases are OR-joined inside one clause. Terms whose token sequence contains another
  term's token sequence are dropped (their occurrences are already counted), so OR sums
  do not double count nested strings.
- Entity counts: sum of exact single-term counts. Co-occurrence: CNF "S AND O" with
  max_diff_tokens in {32,100,500}, max_clause_freq=500000; 'approx' stored.
"""
from __future__ import annotations

import argparse
import json

import numpy as np
import pandas as pd
import yaml
from transformers import AutoTokenizer

from depthlaw.freq.infinigram_client import InfiniGramClient
from depthlaw.io import ROOT, RunLog, make_run_id, provenance, seed_everything

LLAMA2_TOK = "hf-internal-testing/llama-tokenizer"  # same vocab/ids as the infini-gram v4 *_llama indexes
INDEXES = ["v4_piletrain_llama", "v4_olmo-mix-1124_llama", "v4_dclm-baseline_llama"]
WINDOWS = [32, 100, 500]
MAX_CLAUSE_FREQ = 500000


class TermBuilder:
    def __init__(self):
        self.tok = AutoTokenizer.from_pretrained(LLAMA2_TOK)

    def ids(self, s: str) -> list[tuple[int, ...]]:
        spaced = tuple(self.tok.encode(s, add_special_tokens=False))
        unspaced = tuple(self.tok.encode("\n" + s, add_special_tokens=False)[2:])
        return [x for x in (spaced, unspaced) if x]

    @staticmethod
    def string_variants(s: str) -> list[str]:
        out = [s]
        if s[:1].islower():
            out.append(s[0].upper() + s[1:])
        for v in list(out):
            if "'" in v:
                out.append(v.replace("'", "’"))
            if "’" in v:
                out.append(v.replace("’", "'"))
        return list(dict.fromkeys(out))

    def clause(self, names: list[str]) -> list[tuple[int, ...]]:
        terms = []
        for n in names:
            for v in self.string_variants(n):
                terms.extend(self.ids(v))
        terms = list(dict.fromkeys(terms))
        # drop any term that contains another (shorter) term as a contiguous subsequence
        keep = []
        for t in terms:
            nested = any(o != t and len(o) < len(t) and _contains(t, o) for o in terms)
            if not nested:
                keep.append(t)
        return keep

    def decode(self, term: tuple[int, ...]) -> str:
        return " ".join(self.tok.convert_ids_to_tokens(list(term)))


def _contains(seq, sub) -> bool:
    n = len(sub)
    return any(seq[i:i + n] == sub for i in range(len(seq) - n + 1))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--facts", default=str(ROOT / "data" / "facts.parquet"))
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--limit", type=int, default=None, help="first N facts only (smoke test)")
    ap.add_argument("--seed", type=int, default=1234)
    args = ap.parse_args(argv)
    seed_everything(args.seed)
    run_id = make_run_id("S2")
    log = RunLog("S2", run_id)
    cfg = {"indexes": INDEXES, "windows": WINDOWS, "max_clause_freq": MAX_CLAUSE_FREQ, "tok": LLAMA2_TOK}

    facts = pd.read_parquet(args.facts)
    if args.limit:
        facts = facts.iloc[: args.limit]
    tb = TermBuilder()
    cl = InfiniGramClient()

    s_clause = [tb.clause([r.subject, *r.s_aliases]) for r in facts.itertuples()]
    o_clause = [tb.clause([r.object, *r.o_aliases]) for r in facts.itertuples()]

    # 1) single-term exact counts (deduplicated across facts)
    uniq_terms = sorted({t for c in s_clause + o_clause for t in c})
    jobs = [(ix, t) for ix in INDEXES for t in uniq_terms]
    log.log(event="term_jobs", n=len(jobs))
    res = cl.map(lambda j: cl.query({"index": j[0], "query_type": "count", "query_ids": list(j[1])}),
                 jobs, workers=args.workers)
    term_count = {(ix, t): r["count"] for (ix, t), r in zip(jobs, res)}
    term_approx = {(ix, t): bool(r.get("approx", False)) for (ix, t), r in zip(jobs, res)}

    # 2) co-occurrence CNF counts
    cjobs = [(i, ix, w) for i in range(len(facts)) for ix in INDEXES for w in WINDOWS]
    log.log(event="cooc_jobs", n=len(cjobs))

    def run_c(j):
        i, ix, w = j
        try:
            return cl.count_ids(ix, [[list(t) for t in s_clause[i]], [list(t) for t in o_clause[i]]],
                                max_diff_tokens=w, max_clause_freq=MAX_CLAUSE_FREQ)
        except Exception as e:  # noqa: BLE001 - record and continue; reported as MISSING
            return {"error": repr(e)}

    cres = cl.map(run_c, cjobs, workers=args.workers)

    rows = []
    for i, r in enumerate(facts.itertuples()):
        row = {"fact_id": r.fact_id, "n_subj_terms": len(s_clause[i]), "n_obj_terms": len(o_clause[i]),
               "subj_terms": [tb.decode(t) for t in s_clause[i]], "obj_terms": [tb.decode(t) for t in o_clause[i]]}
        for ix in INDEXES:
            short = ix.replace("v4_", "").replace("_llama", "")
            row[f"subj_{short}"] = sum(term_count[(ix, t)] for t in s_clause[i])
            row[f"obj_{short}"] = sum(term_count[(ix, t)] for t in o_clause[i])
            row[f"entity_approx_{short}"] = any(term_approx[(ix, t)] for t in s_clause[i] + o_clause[i])
        rows.append(row)
    out = pd.DataFrame(rows).set_index("fact_id")
    n_err = 0
    for (i, ix, w), rr in zip(cjobs, cres):
        short = ix.replace("v4_", "").replace("_llama", "")
        fid = facts.fact_id.iloc[i]
        if "error" in rr:
            n_err += 1
            out.loc[fid, f"cooc_{short}_w{w}"] = np.nan
            out.loc[fid, f"approx_{short}_w{w}"] = None
            out.loc[fid, f"error_{short}_w{w}"] = rr["error"][:200]
        else:
            out.loc[fid, f"cooc_{short}_w{w}"] = rr["count"]
            out.loc[fid, f"approx_{short}_w{w}"] = bool(rr["approx"])
    out = out.reset_index()
    out["run_id"] = run_id
    dst = ROOT / "data" / ("counts.parquet" if not args.limit else "counts_smoke.parquet")
    out.to_parquet(dst, index=False)
    (dst.with_suffix(".meta.json")).write_text(json.dumps(provenance(run_id, cfg), indent=2))
    summ = {"run_id": run_id, "n_facts": len(out), "n_unique_terms": len(uniq_terms),
            "n_cooc_queries": len(cjobs), "n_cooc_errors": n_err,
            "network_calls": cl.n_network, "cache_hits": cl.n_cached}
    for ix in INDEXES:
        short = ix.replace("v4_", "").replace("_llama", "")
        c = out[f"cooc_{short}_w100"]
        summ[short] = {"cooc_w100_zero_frac": float((c == 0).mean()),
                       "cooc_w100_median": float(c.median()),
                       "approx_w100_frac": float(out[f"approx_{short}_w100"].astype(float).mean()),
                       "subj_zero_frac": float((out[f"subj_{short}"] == 0).mean())}
    log.log(event="done", **summ)
    (log.dir / "summary.json").write_text(json.dumps(summ, indent=2))
    print(json.dumps(summ, indent=2))


if __name__ == "__main__":
    main()
