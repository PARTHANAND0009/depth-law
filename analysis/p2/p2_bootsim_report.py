"""Summarise the P2 CI-method simulation and apply the selection rule (ledger note
"P2 CI-method tie-break fixed before the simulation summary", 2026-11-22T04:03Z).

python analysis/p2/p2_bootsim_report.py results/P2sim/p2_bootsim.json reports/p2/P2_bootsim_report.md
Rule: a method qualifies if coverage >= 0.90 for icc1 and diff in both conditions and the point estimator has
|bias| <= 0.05 for icc1 and diff in both conditions. Both qualify -> twoway. One -> that one. None -> STOP.
"""
import json
import math
import sys
from pathlib import Path

src, dst = Path(sys.argv[1]), Path(sys.argv[2])
J = json.loads(src.read_text())
S = J["summary"]
DEC = ("icc1", "diff")
lines = [f"# P2 CI-method simulation report", "",
         f"Source: `{src}` (settings {json.dumps(J['settings'])}). Written by `analysis/p2/p2_bootsim_report.py`.", "",
         "| condition | quantity | truth | mean point | bias | coverage twoway | coverage param | width twoway | width param | N ok |",
         "|---|---|---|---|---|---|---|---|---|---|"]
ok = {"twoway": True, "param": True}
bias_ok = True
fails = []
for cn, s in S.items():
    for q in ("icc1", "diff", "wording"):
        r = s[q]
        lines.append(f"| {cn} | {q} | {r['truth']:.3f} | {r['mean_point']:.3f} | {r['bias']:+.3f} | {r['coverage_twoway']:.3f} | "
                     f"{r['coverage_param']:.3f} | {r['mean_width_twoway']:.3f} | {r['mean_width_param']:.3f} | {s['n_ok']} |")
        if q in DEC:
            if abs(r["bias"]) > 0.05:
                bias_ok = False; fails.append(f"bias {cn}/{q} = {r['bias']:+.3f}")
            for m in ok:
                if r[f"coverage_{m}"] < 0.90:
                    ok[m] = False; fails.append(f"coverage {m} {cn}/{q} = {r[f'coverage_{m}']:.3f}")
lines += ["", "| condition | N ok | N error | singular-fit rate |", "|---|---|---|---|"]
lines += [f"| {cn} | {s['n_ok']} | {s['n_error']} | {s['singular_rate']:.3f} |" for cn, s in S.items()]
n = min(s["n_ok"] for s in S.values())
mcse = math.sqrt(0.9 * 0.1 / n) if n else float("nan")
qual = [m for m in ("twoway", "param") if ok[m] and bias_ok]
choice = "twoway" if "twoway" in qual else (qual[0] if qual else None)
lines += ["", f"Monte Carlo SE of a coverage near 0.90 with N = {n} simulations: {mcse:.3f}.", "",
          "## Selection rule outcome", "",
          f"- |bias| <= 0.05 for icc1 and diff in both conditions: {'yes' if bias_ok else 'NO'}",
          f"- twoway coverage >= 0.90 for icc1 and diff in both conditions: {'yes' if ok['twoway'] else 'NO'}",
          f"- param coverage >= 0.90 for icc1 and diff in both conditions: {'yes' if ok['param'] else 'NO'}",
          f"- Failures: {'; '.join(fails) if fails else 'none'}",
          f"- **Chosen CI method: {choice if choice else 'NONE: STOP (no method meets the rule; no rental)'}**"]
dst.parent.mkdir(parents=True, exist_ok=True)
dst.write_text("\n".join(lines) + "\n")
(dst.with_suffix(".json")).write_text(json.dumps({"choice": choice, "bias_ok": bias_ok, "coverage_ok": ok, "fails": fails,
                                                  "n_sims_min": n, "mcse_coverage": mcse, "source": str(src)}, indent=1))
print(f"choice={choice}")
