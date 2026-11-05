"""Wikidata SPARQL helpers (batched): exact-label linking with ambiguity stats, and aliases.

The REST API (wbsearchentities) was rate-limited from this host on 2026-11-05, so
everything goes through query.wikidata.org/sparql. Responses cached in cache/wikidata/.
"""
from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[3]
CACHE = ROOT / "cache" / "wikidata"
URL = "https://query.wikidata.org/sparql"
UA = "depth-law-research/0.1 (academic research; python-requests)"


def _lit(s: str) -> str:
    return json.dumps(s, ensure_ascii=False) + "@en"


def sparql(query: str, retries: int = 6) -> list[dict]:
    CACHE.mkdir(parents=True, exist_ok=True)
    f = CACHE / (hashlib.sha1(query.encode()).hexdigest() + ".json")
    if f.exists():
        return json.loads(f.read_text())
    err = None
    for a in range(retries):
        try:
            r = requests.post(URL, data={"query": query}, timeout=120,
                              headers={"User-Agent": UA, "Accept": "application/sparql-results+json"})
            if r.status_code == 429:
                time.sleep(int(r.headers.get("Retry-After", 10)))
                continue
            r.raise_for_status()
            rows = r.json()["results"]["bindings"]
            f.write_text(json.dumps(rows))
            time.sleep(0.5)
            return rows
        except (requests.RequestException, ValueError, KeyError) as e:
            err = e
            time.sleep(2 ** a)
    raise RuntimeError(f"SPARQL failed: {err}")


def link_labels(labels: list[str], batch: int = 80) -> dict[str, list[tuple[str, int]]]:
    """label -> [(qid, sitelinks)] for items whose English label equals the string exactly."""
    out: dict[str, list[tuple[str, int]]] = {l: [] for l in labels}
    labels = sorted(set(labels))
    for i in range(0, len(labels), batch):
        chunk = labels[i:i + batch]
        q = ("SELECT ?lab ?item ?sl WHERE { VALUES ?lab { " + " ".join(_lit(l) for l in chunk) +
             " } ?item rdfs:label ?lab . ?item wikibase:sitelinks ?sl . }")
        for row in sparql(q):
            lab = row["lab"]["value"]
            qid = row["item"]["value"].rsplit("/", 1)[-1]
            out.setdefault(lab, []).append((qid, int(row["sl"]["value"])))
    for k in out:
        out[k].sort(key=lambda x: -x[1])
    return out


def aliases(qids: list[str], batch: int = 200) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {q: [] for q in qids}
    qids = sorted(set(q for q in qids if q and q.startswith("Q")))
    for i in range(0, len(qids), batch):
        chunk = qids[i:i + batch]
        q = ("SELECT ?item ?a WHERE { VALUES ?item { " + " ".join("wd:" + x for x in chunk) +
             ' } ?item skos:altLabel ?a . FILTER(lang(?a) = "en") }')
        for row in sparql(q):
            out.setdefault(row["item"]["value"].rsplit("/", 1)[-1], []).append(row["a"]["value"])
    return out
