"""P2 per-model done-check on the GPU instance (scripts/p2_gpu_run.sh). Exit 1 on any shortfall.
It applies THE completeness rule, analysis/p2/p2_analysis.py completeness() (prereg section 1), and also requires the
run to have at least the carriers the driver asked for.
python scripts/p2_done_check.py <run_dir> <carriers> [--dry]   (--dry: the 5-fact x 2-paraphrase dry run)"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis" / "p2"))
from p2_analysis import completeness  # noqa: E402

rd, nc, dry = pathlib.Path(sys.argv[1]), int(sys.argv[2]), "--dry" in sys.argv
fids = [json.loads(l)["fact_id"] for l in open(ROOT / "materials/facts_v1.jsonl")]
fids, n_templates = (fids[:5], 2) if dry else (fids, 10)
ok, why, ncr = completeness(rd, fids, n_templates)
ok = ok and ncr >= nc
print(f"done-check {rd.name}: ok={ok} completeness='{why}' carriers_run={ncr} carriers_requested={nc}")
sys.exit(0 if ok else 1)
