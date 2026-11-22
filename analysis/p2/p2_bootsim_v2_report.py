"""Report for the P2 CI-method simulation v2 and the prespecified rule (analysis/p2/bootsim_v2_plan.md).

python analysis/p2/p2_bootsim_v2_report.py results/P2sim_v2/p2_bootsim_v2.json reports/p2/P2_bootsim_v2_report.md
Rule: (a) nominal 95% passes -> param95; else (b) nominal 97.5% passes -> param975; else STOP.
Pass = coverage >= 0.90 for icc1 and diff in both conditions, and |bias| <= 0.05 for icc1 and diff in both conditions.
"""
import json
import math
import statistics as st
import sys
from pathlib import Path

src, dst = Path(sys.argv[1]), Path(sys.argv[2])
J = json.loads(src.read_text())
sims = J["sims"]
conds = list(J["conditions"])
LV = {"n95": "nominal 95%", "n975": "nominal 97.5%"}
DEC = ("icc1", "diff")
lines = ["# P2 CI-method simulation v2 report (second look after a near-miss)", "",
         f"Source: `{src}` (settings {json.dumps(J['settings'])}). Plan: `analysis/p2/bootsim_v2_plan.md`. "
         "Written by `analysis/p2/p2_bootsim_v2_report.py`. v1 (`reports/p2/P2_bootsim_report.md`) stays on record.", "",
         "| condition | quantity | truth | mean point | bias (MCSE) | coverage 95% (MCSE) | coverage 97.5% (MCSE) | width 95% | width 97.5% | N |",
         "|---|---|---|---|---|---|---|---|---|---|"]
bias_ok, cov_ok, fails, summ = True, {k: True for k in LV}, [], {}
for cn in conds:
    rr = [r for r in sims if r["cond"] == cn and "error" not in r]
    n = len(rr)
    summ[cn] = {"n_ok": n, "n_error": sum(1 for r in sims if r["cond"] == cn and "error" in r),
                "singular_rate": sum(bool(r["singular"]) for r in rr) / n if n else None,
                "n_failed_refits": sum(int(r["n_failed"]) for r in rr)}
    for q in ("icc1", "diff", "wording"):
        pts = [r["point"][q] for r in rr]; tru = rr[0]["truth"][q]
        bias = st.mean(pts) - tru; bse = st.stdev(pts) / math.sqrt(n)
        row = {"truth": tru, "mean_point": st.mean(pts), "bias": bias, "bias_mcse": bse}
        for k in LV:
            c = sum(bool(r[k]["covered"][q]) for r in rr) / n
            row[f"coverage_{k}"] = c; row[f"coverage_{k}_mcse"] = math.sqrt(c * (1 - c) / n)
            row[f"width_{k}"] = st.mean(r[k]["hi"][q] - r[k]["lo"][q] for r in rr)
            if q in DEC and c < 0.90:
                cov_ok[k] = False; fails.append(f"coverage {LV[k]} {cn}/{q} = {c:.3f}")
        if q in DEC and abs(bias) > 0.05:
            bias_ok = False; fails.append(f"bias {cn}/{q} = {bias:+.3f}")
        summ[cn][q] = row
        lines.append(f"| {cn} | {q} | {tru:.3f} | {row['mean_point']:.3f} | {bias:+.3f} ({bse:.3f}) | "
                     f"{row['coverage_n95']:.3f} ({row['coverage_n95_mcse']:.3f}) | {row['coverage_n975']:.3f} ({row['coverage_n975_mcse']:.3f}) | "
                     f"{row['width_n95']:.3f} | {row['width_n975']:.3f} | {n} |")
lines += ["", "| condition | N ok | N error | failed bootstrap refits | singular-fit rate |", "|---|---|---|---|---|"]
lines += [f"| {cn} | {s['n_ok']} | {s['n_error']} | {s['n_failed_refits']} | {s['singular_rate']:.3f} |" for cn, s in summ.items()]
a_pass, b_pass = bias_ok and cov_ok["n95"], bias_ok and cov_ok["n975"]
choice = "parametric bootMer, 95% percentile" if a_pass else ("parametric bootMer, 97.5% percentile" if b_pass else None)
lines += ["", "## Prespecified rule outcome", "",
          f"- |bias| <= 0.05 for icc1 and diff in both conditions: {'yes' if bias_ok else 'NO'}",
          f"- (a) nominal 95%: coverage >= 0.90 for icc1 and diff in both conditions: {'yes' if cov_ok['n95'] else 'NO'}",
          f"- (b) nominal 97.5%: coverage >= 0.90 for icc1 and diff in both conditions: {'yes' if cov_ok['n975'] else 'NO'}",
          f"- Failures: {'; '.join(fails) if fails else 'none'}",
          f"- **Outcome: {choice if choice else 'NONE: STOP (no option meets the rule; no rental)'}**"]
dst.parent.mkdir(parents=True, exist_ok=True)
dst.write_text("\n".join(lines) + "\n")
dst.with_suffix(".json").write_text(json.dumps({"choice": choice, "a_pass": a_pass, "b_pass": b_pass, "bias_ok": bias_ok,
                                                "coverage_ok": cov_ok, "fails": fails, "summary": summ, "source": str(src)}, indent=1))
print(f"choice={choice}")
