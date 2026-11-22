"""Build two synthetic P2 runs for the end-to-end test: A (seed 7, 3 carriers) and B (seed 8, carrier 2 dropped
from chunk 2 on, i.e. fallback 1 after a 20-fact pilot). Test only."""
import hashlib
import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, "/home/user/depth-law/analysis/p2")
from p2_fake_run import main  # noqa: E402

base = Path(sys.argv[1])
main(base / "A", 32, seed=7)
main(base / "B", 32, seed=8)
rd = base / "B"
h = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()  # noqa: E731
for c in sorted((rd / "chunks").glob("c*.parquet")):
    n = int(c.stem[1:])
    if n >= 2:
        d = pd.read_parquet(c); d[d.carrier < 2].to_parquet(c, index=False)
    b = c.with_name(f"b{n:05d}.parquet")
    c.with_suffix(".sha256").write_text(f"{h(c)}  {c.name}\n{h(b)}  {b.name}\n")
man = {}
for s in sorted((rd / "chunks").glob("c*.sha256")):
    for line in s.read_text().splitlines():
        hh, name = line.split(); man[name] = {"sha256": hh, "ok": True}
(rd / "manifest.json").write_text(json.dumps(man))
print("built", base)
