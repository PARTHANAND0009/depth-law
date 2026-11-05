"""infini-gram API client: retry with exponential backoff, rate limit, persistent cache.

Every response is cached in cache/freq/infinigram.sqlite keyed by the canonical JSON
payload, so reruns never re-query. API docs: https://infini-gram.readthedocs.io/en/latest/api.html
"""
from __future__ import annotations

import json
import sqlite3
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import requests

API_URL = "https://api.infini-gram.io/"
ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CACHE = ROOT / "cache" / "freq" / "infinigram.sqlite"


class InfiniGramError(RuntimeError):
    pass


class InfiniGramClient:
    def __init__(self, cache_path: Path | str = DEFAULT_CACHE, max_retries: int = 6,
                 min_interval_s: float = 0.0, timeout_s: float = 60.0):
        self.cache_path = Path(cache_path)
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._db = sqlite3.connect(self.cache_path, check_same_thread=False)
        self._db.execute("CREATE TABLE IF NOT EXISTS resp (k TEXT PRIMARY KEY, v TEXT)")
        self._db.commit()
        self.max_retries = max_retries
        self.min_interval_s = min_interval_s
        self.timeout_s = timeout_s
        self._last = 0.0
        self._session = requests.Session()
        self.n_network = 0
        self.n_cached = 0

    @staticmethod
    def _key(payload: dict) -> str:
        return json.dumps(payload, sort_keys=True, separators=(",", ":"))

    def _get_cached(self, k: str):
        with self._lock:
            row = self._db.execute("SELECT v FROM resp WHERE k=?", (k,)).fetchone()
        return json.loads(row[0]) if row else None

    def _put(self, k: str, v: dict) -> None:
        with self._lock:
            self._db.execute("INSERT OR REPLACE INTO resp VALUES (?,?)", (k, json.dumps(v)))
            self._db.commit()

    def query(self, payload: dict) -> dict:
        k = self._key(payload)
        hit = self._get_cached(k)
        if hit is not None:
            self.n_cached += 1
            return hit
        err = None
        for attempt in range(self.max_retries):
            if self.min_interval_s:
                with self._lock:
                    wait = self._last + self.min_interval_s - time.time()
                    self._last = max(time.time(), self._last + self.min_interval_s)
                if wait > 0:
                    time.sleep(wait)
            try:
                r = self._session.post(API_URL, json=payload, timeout=self.timeout_s)
                r.raise_for_status()
                out = r.json()
                if "error" in out:
                    err = out["error"]
                    # malformed input will not get better with retries
                    if "malformed" in err.lower() or "invalid" in err.lower():
                        break
                else:
                    self.n_network += 1
                    self._put(k, out)
                    return out
            except (requests.RequestException, ValueError) as e:
                err = repr(e)
            time.sleep(min(2 ** attempt, 30))
        raise InfiniGramError(f"{err} | payload={k[:300]}")

    def count_ids(self, index: str, cnf_ids: list[list[list[int]]], max_diff_tokens: int = 100,
                  max_clause_freq: int = 500000) -> dict:
        """cnf_ids: AND over clauses, OR over terms, each term a token-id list."""
        payload = {"index": index, "query_type": "count", "query_ids": cnf_ids}
        if len(cnf_ids) > 1:
            payload["max_diff_tokens"] = max_diff_tokens
            payload["max_clause_freq"] = max_clause_freq
        return self.query(payload)

    def count_str(self, index: str, query: str) -> dict:
        return self.query({"index": index, "query_type": "count", "query": query})

    def map(self, fn, items, workers: int = 8):
        with ThreadPoolExecutor(workers) as ex:
            return list(ex.map(fn, items))
