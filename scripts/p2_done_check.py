"""P2 per-model done-check on the GPU instance (scripts/p2_gpu_run.sh). Exit 1 on any shortfall.
python scripts/p2_done_check.py <run_dir> <expected fact x paraphrase units> <carriers>"""
import glob
import json
import pathlib
import sys

import pandas as pd

rd, units, nc = pathlib.Path(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
m = json.load(open(rd / "manifest.json"))
last = [json.loads(l) for l in open(rd / "log.jsonl")][-1]
long = pd.concat(pd.read_parquet(p) for p in sorted(glob.glob(str(rd / "chunks/c*.parquet"))))
beh = pd.concat(pd.read_parquet(p) for p in sorted(glob.glob(str(rd / "chunks/b*.parquet"))))
cs = long.groupby(["fact_id", "template_id"]).carrier.nunique()
nan_p = int(long.p_object.isna().sum())
ok = (all(v["ok"] for v in m.values()) and last.get("event") == "done" and bool(last.get("all_ok"))
      and len(beh) == units and len(cs) == units and int(cs.min()) >= nc and nan_p == 0)
print(f"done-check {rd.name}: ok={ok} checksums_ok={all(v['ok'] for v in m.values())} last_event={last.get('event')} "
      f"behaviour_rows={len(beh)}/{units} cells_with_curves={len(cs)} min_carriers={int(cs.min())} "
      f"long_rows={len(long)} nan_p={nan_p}")
sys.exit(0 if ok else 1)
