"""HR prior (prereg/HR_revised.md B2): cache/hr/prior_<model>.parquet + logprobs + provenance.
Usage: python scripts/hr_prior.py MODEL [MODEL ...]   (skips a model whose cache exists)"""
import json
import sys
from pathlib import Path

import pandas as pd
from safetensors.torch import save_file

from depthlaw.hr.prior import PREFIXES, compute_prior

ROOT = Path(__file__).resolve().parents[1]
objs = sorted(pd.read_parquet(ROOT / "data" / "facts_g1cpu.parquet").object.unique())
for name in sys.argv[1:]:
    tag = name.split("/")[-1]
    out = ROOT / "cache" / "hr" / f"prior_{tag}.parquet"
    if out.exists():
        print("skip", out); continue
    prior, lp, prov = compute_prior(name, objs)
    save_file({"logprobs": lp.contiguous()}, str(out.with_suffix(".logprobs.safetensors")))
    (out.with_suffix(".json")).write_text(json.dumps({"model": name, "revision": "main", "prefixes": PREFIXES, **prov}, indent=1))
    pd.DataFrame({"object": list(prior), "log_prior": list(prior.values())}).to_parquet(out, index=False)
    print("done", name, prov["source"], prov["seconds"], "s", prov.get("bytes_read"))
