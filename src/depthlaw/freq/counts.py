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
- The API allows at most 4 OR-terms per clause. Larger clauses are split into chunks of
  <=4 and the CNF counts of all chunk pairs are summed (cooc_n_chunk_pairs > 1 flags this;
  it can overcount when two surface forms co-occur with the object in the same window).
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from transformers import AutoTokenizer

from depthlaw.freq.infinigram_client import InfiniGramClient
from depthlaw.io import ROOT, RunLog, make_run_id, provenance, seed_everything

LLAMA2_TOK = "hf-internal-testing/llama-tokenizer"  # same vocab/ids as the infini-gram v4 *_llama indexes
INDEXES = ["v4_piletrain_llama", "v4_olmo-mix-1124_llama", "v4_dclm-baseline_llama"]
WINDOWS = [32, 100, 500]
# API rate limits: sensitivity windows only on the EXACT indexes; DCLM (proxy only) gets w100
WINDOWS_BY_INDEX = {"v4_piletrain_llama": [32, 100, 500], "v4_olmo-mix-1124_llama": [32, 100, 500],
                    "v4_dclm-baseline_llama": [100]}
MAX_CLAUSE_FREQ = 500000
MAX_TERMS_PER_CLAUSE = 4  # API limit ("at most 4 terms in each disjunctive clause")


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


def _chunks(clause, k=MAX_TERMS_PER_CLAUSE):
    return [tuple(clause[j:j + k]) for j in range(0, len(clause), k)]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--facts", default=str(ROOT / "data" / "facts.parquet"))
    ap.add_argument("--out", default=None)
    ap.add_argument("--pass", dest="pass_", choices=["primary", "sensitivity", "all"], default="primary",
                    help="primary = entity counts + w100 on all indexes; sensitivity = w32/w500 on EXACT indexes")
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--limit", type=int, default=None, help="first N facts only (smoke test)")
    ap.add_argument("--seed", type=int, default=1234)
    args = ap.parse_args(argv)
    seed_everything(args.seed)
    run_id = make_run_id("S2")
    log = RunLog("S2", run_id)
    cfg = {"indexes": INDEXES, "windows": WINDOWS_BY_INDEX, "max_clause_freq": MAX_CLAUSE_FREQ,
           "tok": LLAMA2_TOK, "pass": args.pass_, "facts": args.facts}

    facts = pd.read_parquet(args.facts)
    if args.limit:
        facts = facts.iloc[: args.limit]
    tb = TermBuilder()
    cl = InfiniGramClient()
    s_clause = [tb.clause([r.subject, *r.s_aliases]) for r in facts.itertuples()]
    o_clause = [tb.clause([r.object, *r.o_aliases]) for r in facts.itertuples()]

    def win_list(ix):
        if args.pass_ == "primary":
            return [100]
        if args.pass_ == "sensitivity":
            return [w for w in WINDOWS_BY_INDEX[ix] if w != 100]
        return WINDOWS_BY_INDEX[ix]

    # 1) entity counts: one single-clause OR query per chunk of <=4 terms. A single OR clause
    #    returns the exact sum of its terms' counts (checked 2026-11-05: 81461 + 437194 =
    #    518655 on v4_piletrain_llama); the 'approx' flag the API attaches to single-clause
    #    queries is stored but not meaningful for this case.
    ent = {}
    if args.pass_ in ("primary", "all"):
        uniq = sorted({c for cl_ in s_clause + o_clause for c in _chunks(cl_)})
        jobs = [(ix, c) for ix in INDEXES for c in uniq]
        log.log(event="entity_jobs", n=len(jobs))

        def run_e(j):
            try:
                return cl.query({"index": j[0], "query_type": "count", "query_ids": [[list(t) for t in j[1]]]})
            except Exception as e:  # noqa: BLE001
                return {"error": repr(e)}
        for j, r in zip(jobs, cl.map(run_e, jobs, workers=args.workers)):
            ent[j] = r

    # 2) co-occurrence CNF counts
    cjobs = [(i, ix, w) for i in range(len(facts)) for ix in INDEXES for w in win_list(ix)]
    log.log(event="cooc_jobs", n=len(cjobs))

    def run_c(j):
        i, ix, w = j
        total, approx, n = 0, False, 0
        try:
            for a in _chunks(s_clause[i]):
                for b in _chunks(o_clause[i]):
                    r = cl.count_ids(ix, [[list(t) for t in a], [list(t) for t in b]],
                                     max_diff_tokens=w, max_clause_freq=MAX_CLAUSE_FREQ)
                    total += r["count"]
                    approx = approx or bool(r["approx"])
                    n += 1
        except Exception as e:  # noqa: BLE001 - record and continue; reported as MISSING
            return {"error": repr(e)}
        return {"count": total, "approx": approx, "n_pairs": n}

    cres = cl.map(run_c, cjobs, workers=args.workers)

    rows = []
    for i, r in enumerate(facts.itertuples()):
        row = {"fact_id": r.fact_id, "n_subj_terms": len(s_clause[i]), "n_obj_terms": len(o_clause[i]),
               "subj_terms": [tb.decode(t) for t in s_clause[i]], "obj_terms": [tb.decode(t) for t in o_clause[i]],
               "cooc_n_chunk_pairs": len(_chunks(s_clause[i])) * len(_chunks(o_clause[i]))}
        if ent:
            for ix in INDEXES:
                sh = ix.replace("v4_", "").replace("_llama", "")
                for side, clause in (("subj", s_clause[i]), ("obj", o_clause[i])):
                    rs = [ent[(ix, c)] for c in _chunks(clause)]
                    row[f"{side}_{sh}"] = np.nan if any("error" in x for x in rs) else sum(x["count"] for x in rs)
        rows.append(row)
    out = pd.DataFrame(rows).set_index("fact_id")
    n_err = 0
    for (i, ix, w), rr in zip(cjobs, cres):
        sh = ix.replace("v4_", "").replace("_llama", "")
        fid = facts.fact_id.iloc[i]
        if "error" in rr:
            n_err += 1
            out.loc[fid, f"cooc_{sh}_w{w}"] = np.nan
            out.loc[fid, f"error_{sh}_w{w}"] = rr["error"][:200]
        else:
            out.loc[fid, f"cooc_{sh}_w{w}"] = rr["count"]
            out.loc[fid, f"approx_{sh}_w{w}"] = float(rr["approx"])
    out = out.reset_index()
    out["run_id"] = run_id
    stem = Path(args.facts).stem.replace("facts", "counts")
    dst = Path(args.out) if args.out else ROOT / "data" / f"{stem}_{args.pass_}{'_smoke' if args.limit else ''}.parquet"
    out.to_parquet(dst, index=False)
    dst.with_suffix(".meta.json").write_text(json.dumps(provenance(run_id, cfg), indent=2))
    summ = {"run_id": run_id, "out": str(dst.relative_to(ROOT)), "n_facts": len(out),
            "n_cooc_jobs": len(cjobs), "n_cooc_errors": n_err,
            "network_calls": cl.n_network, "cache_hits": cl.n_cached, "throttled": cl.n_throttled}
    for c in [c for c in out.columns if c.startswith("cooc_") and "_w" in c]:
        summ[c] = {"zero_frac": float((out[c] == 0).mean()), "median": float(out[c].median()),
                   "missing": int(out[c].isna().sum()),
                   "approx_frac": float(out[c.replace("cooc_", "approx_")].mean())}
    log.log(event="done", **summ)
    (log.dir / "summary.json").write_text(json.dumps(summ, indent=2))
    print(json.dumps(summ, indent=2))


if __name__ == "__main__":
    main()
