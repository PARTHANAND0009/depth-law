#!/usr/bin/env python3
"""P2R four-family summary (amendment A_P2R_new_families, section 5(b)). Preregistered, NOT independent: two of its
families (Llama-3.1, OLMo-2) were analysed before the amendment.

Inputs: the P2 gating call (results/P2analysis/correct/{p2_results,p2_decision}.json, sha256 pinned below) and the
P2R gating call (results/P2Ranalysis/correct/{p2_results,p2_decision}.json).
- Per-model quantities (rule flags, G ceiling, intervals) are copied from EACH CALL'S OWN p2_decision.json, so each
  model keeps the nc of its own call (G ceiling depends on nc).
- Family-level claims come from the frozen p2_analysis.decide() applied to the union of the two calls' fits; its
  per-model rule flags are checked against the per-call decision files (they must agree; G ceiling is the only
  nc-dependent field and no claim uses it).
- A call with no included model (n_carriers_used = 0) is handled: its models are MISSING.
- Refused: non-gating or --test inputs; a P2 input whose sha256 differs from the pinned one; a model in both calls.
H3 (cross-model correlations) is not recomputed (amendment section 5(d)).
The output adds, per headline rule, the list of families meeting its condition (for the 'k of 4' tallies, 5(b)).
Usage: p2r_combine.py <p2_dir> <p2r_dir> <out.json>"""
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "p2"))
sys.path.insert(0, str(HERE))
import p2_analysis as PA  # noqa: E402
from p2r_analysis import configure  # noqa: E402

P2_PINNED = {"p2_results.json": "5df75c9f4ff38a5888cbc171a05f68c3e1c337a0a90f9675394dc9e5e77557e4",
             "p2_decision.json": "b012b886f28a57b44244d0aabd23ae741c9125c72262f7b2e474b146686f8db4"}
RULES = ("H1", "H1_alt", "icc1_upper_lt_0.15", "nprime_ge_8", "tf_gt_resid_D1", "null_lt_0.01")


def load(d, pin=None):
    d = Path(d); out = {}
    for f in ("p2_results.json", "p2_decision.json"):
        b = (d / f).read_bytes()
        if pin and hashlib.sha256(b).hexdigest() != pin[f]:
            raise SystemExit(f"{d / f}: sha256 differs from the pinned P2 file (amendment section 3)")
        out[f] = json.loads(b)
    return out["p2_results.json"], out["p2_decision.json"]


def combine(p2, p2dec, p2r, p2rdec):
    configure()
    for name, r in (("P2", p2), ("P2R", p2r)):
        if r.get("set") != "correct" or r.get("gating") is not True or r.get("test"):
            raise SystemExit(f"{name}: not a gating 'correct' call (set={r.get('set')}, gating={r.get('gating')}, test={r.get('test')})")
    overlap = set(p2["models"]) & set(p2r["models"])
    if overlap:
        raise SystemExit(f"a model appears in both calls: {sorted(overlap)}")
    # each call's decision file must equal the frozen decide() on that call's own results and nc (all per-model fields)
    for name, r, dfile in (("P2", p2, p2dec), ("P2R", p2r, p2rdec)):
        own = PA.decide(r, "correct", {}, {}, r.get("n_carriers_used") or 3)
        if json.loads(json.dumps(own["per_model"], default=float)) != json.loads(json.dumps(dfile["per_model"], default=float)):
            raise SystemExit(f"{name}: p2_decision.json per_model differs from decide() on its own p2_results.json")
    merged = {"set": "correct", "models": {**p2["models"], **p2r["models"]}}
    ncs = [n for n in (p2.get("n_carriers_used", 0), p2r.get("n_carriers_used", 0)) if n]
    dec = PA.decide(merged, "correct", {}, {}, max(ncs) if ncs else 3, gating=False)
    per_call = {**p2dec["per_model"], **p2rdec["per_model"]}
    for m, v in dec["per_model"].items():  # the union's rule flags must equal each call's own flags
        own = per_call.get(m, {})
        if v.get("status") == "ok" and any(v.get(k) != own.get(k) for k in RULES):
            raise SystemExit(f"{m}: rule flags differ from its own call's decision file")
    dec["per_model"] = per_call  # per-model quantities with each call's own nc
    dec["n_carriers_used"] = {"P2": p2.get("n_carriers_used"), "P2R": p2r.get("n_carriers_used")}
    dec["note"] = ("four-family summary (amendment A_P2R_new_families 5(b)); NOT independent: Llama-3.1 and OLMo-2 were "
                   "analysed before the amendment; the replication test proper is the P2R call alone (5(a)); sentences "
                   "licensed only here are reported as per-family tallies, never in the abstract or a headline (5(b))")
    ok = {m: v for m, v in per_call.items() if v.get("status") == "ok"}
    fam = lambda pred: sorted({v["family"] for v in ok.values() if pred(v) is True})  # noqa: E731
    dec["families_per_rule"] = {
        "fact_share_gt0 (null p<0.01)": fam(lambda v: v.get("null_lt_0.01")), "H1": fam(lambda v: v.get("H1")),
        "H1_alt": fam(lambda v: v.get("H1_alt")), "no_fixed_layer": fam(lambda v: v.get("icc1_upper_lt_0.15")),
        "single_prompt_poor (H1 and n'>=8)": fam(lambda v: v.get("H1") is True and v.get("nprime_ge_8") is True),
        "wording_shifts_together (H1 and tf>resid)": fam(lambda v: v.get("H1") is True and v.get("tf_gt_resid_D1") is True),
        "fact_depth_unexplained (H1-alt)": fam(lambda v: v.get("H1_alt")),
        "included": sorted({v["family"] for v in ok.values()})}
    dec["sources"] = {"p2_runs": p2.get("runs"), "p2r_runs": p2r.get("runs")}
    return dec


if __name__ == "__main__":
    p2, p2dec = load(sys.argv[1], P2_PINNED)
    p2r, p2rdec = load(sys.argv[2])
    out = Path(sys.argv[3]); out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(combine(p2, p2dec, p2r, p2rdec), indent=1, default=float))
    print("wrote", out)
