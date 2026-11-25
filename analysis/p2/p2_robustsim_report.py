#!/usr/bin/env python3
"""Report for the P2 non-selecting robustness simulation (analysis/p2/robustsim_plan.md).
Reads results/P2robust/p2_robustsim.json; writes reports/p2/P2_robustsim_report.{md,json}. Descriptive only:
no threshold, no decision. Usage: python analysis/p2/p2_robustsim_report.py"""
import json, math, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
SRC = ROOT / "results/P2robust/p2_robustsim.json"
OUT = ROOT / "reports/p2/P2_robustsim_report"
Q = ("icc1", "diff", "wording")


def mcse(p, n):
    return math.sqrt(p * (1 - p) / n) if n else float("nan")


def main():
    d = json.loads(SRC.read_text())
    sims = d["sims"]
    out = {"source": str(SRC.relative_to(ROOT)), "settings": d["settings"], "status": "non-selecting robustness simulation",
           "conditions": {}}
    for c, spec in d["conditions"].items():
        rs = [s for s in sims if s.get("cond") == c]
        ok = [s for s in rs if "error" not in s]
        n = len(ok)
        r = {"spec": spec, "n": n, "n_error": len(rs) - n}
        if n:
            r["truth"] = {q: ok[0]["truth"][q] for q in Q}
            r["coverage"] = {q: sum(bool(s["covered"][q]) for s in ok) / n for q in Q}
            r["coverage_mcse"] = {q: mcse(r["coverage"][q], n) for q in Q}
            r["bias"] = {q: sum(s["point"][q] - s["truth"][q] for s in ok) / n for q in ("icc1", "diff")}
            r["miss_below"] = {q: sum(s["truth"][q] < s["lo"][q] for s in ok) for q in ("icc1", "diff")}
            r["miss_above"] = {q: sum(s["truth"][q] > s["hi"][q] for s in ok) for q in ("icc1", "diff")}
            r["rate_diff_lo_gt0"] = sum(s["lo"]["diff"] > 0 for s in ok) / n
            r["rate_icc_lo_ge_0.4"] = sum(s["lo"]["icc1"] >= 0.4 for s in ok) / n
            r["mean_missingness"] = sum(s["miss"] for s in ok) / n
            r["singular_rate"] = sum(bool(s["singular"]) for s in ok) / n
            r["failed_refits_total"] = sum(int(s["n_failed"]) for s in ok)
        out["conditions"][c] = r
    OUT.with_suffix(".json").write_text(json.dumps(out, indent=1) + "\n")
    L = ["# P2 robustness simulation (non-selecting)", "",
         f"Source: `{out['source']}` (plan `analysis/p2/robustsim_plan.md`; code `analysis/p2/p2_robustsim.R`). "
         f"Settings: {d['settings']['n_sim']} simulations per condition, {d['settings']['n_boot']} parametric bootMer resamples, "
         f"seed base {d['settings']['seed']}. Status: preregistered robustness check (prereg section 4), **non-selecting**: it "
         "cannot change the CI method or any decision. Truth = latent-scale shares before discretisation and selection.", "",
         "| condition | N (errors) | true ICC(1) | true diff | coverage ICC(1) (MCSE) | coverage diff (MCSE) | coverage wording | "
         "bias ICC(1) | bias diff | truth below / above CI: ICC(1); diff | diff lower bound > 0 | ICC(1) lower bound ≥ 0.4 | "
         "missingness | singular | failed refits |", "|" + "---|" * 15]
    for c, r in out["conditions"].items():
        if not r["n"]:
            L.append(f"| {c} | 0 ({r['n_error']}) | MISSING |" + " |" * 13); continue
        L.append(f"| {c} | {r['n']} ({r['n_error']}) | {r['truth']['icc1']:.3f} | {r['truth']['diff']:.3f} | "
                 f"{r['coverage']['icc1']:.3f} ({r['coverage_mcse']['icc1']:.3f}) | {r['coverage']['diff']:.3f} ({r['coverage_mcse']['diff']:.3f}) | "
                 f"{r['coverage']['wording']:.3f} | {r['bias']['icc1']:+.3f} | {r['bias']['diff']:+.3f} | "
                 f"{r['miss_below']['icc1']} / {r['miss_above']['icc1']}; {r['miss_below']['diff']} / {r['miss_above']['diff']} | "
                 f"{r['rate_diff_lo_gt0']:.3f} | {r['rate_icc_lo_ge_0.4']:.3f} | {r['mean_missingness']:.3f} | "
                 f"{r['singular_rate']:.3f} | {r['failed_refits_total']} |")
    L += ["", "Condition names: truth A/B, discretisation L, carriers nc. Nominal coverage 0.95. 'diff lower bound > 0' is the "
          "single-measure H1 CI condition passing when the true diff is 0 (nominal one-sided rate 0.025). Descriptive only."]
    OUT.with_suffix(".md").write_text("\n".join(L) + "\n")
    print("wrote", OUT.with_suffix(".md"))


if __name__ == "__main__":
    sys.exit(main())
