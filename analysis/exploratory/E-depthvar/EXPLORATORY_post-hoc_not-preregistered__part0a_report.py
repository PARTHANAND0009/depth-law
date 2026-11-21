"""EXPLORATORY (post hoc, not preregistered) — writes the Part 0a markdown report from part0a.json.
python <this> <part0a.json> <out.md>"""
import json
import sys

LAB = "EXPLORATORY (post hoc, not preregistered)"


def f(x, nd=3):
    return "n/a" if x is None else f"{x:.{nd}f}"


r = json.load(open(sys.argv[1]))
L = [f"# {LAB} — Part 0a: leave-one-relation-out jackknife and company_ceo diagnostics", "",
     f"- **Source:** `{sys.argv[1]}`.",
     "- **Fit:** set (i) correct cells, lme4 REML, the B3 model; convergence checks ON. diff = (template-main + residual) − (fact+subject), shares of total including relation.",
     f"- **Pre-logged criterion:** {r['criterion']}. Result: STOP = {r['stop']}.", "",
     f"| {LAB} model | def | full diff | LOO diff min / median / max | LOO fits with diff ≤ 0 | full ICC(1) | LOO ICC(1) min / median / max | most influential relations (change in diff) | singular LOO fits |",
     "|---|---|---|---|---|---|---|---|---|"]
for k, v in r["summary"].items():
    m, y = k.split("|"); d, i = v["diff"], v["icc1"]
    top = "; ".join(f"{x['dropped']} {x['change']:+.3f}" for x in d["most_influential"])
    L.append(f"| {m} | {y} | {f(v['full']['diff'])} | {f(d['min'])} / {f(d['median'])} / {f(d['max'])} | {v['n_diff_le_0']}/{v['n_loo']} | "
             f"{f(v['full']['icc1'])} | {f(i['min'])} / {f(i['median'])} / {f(i['max'])} | {top} | {v['n_singular_loo']} |")
inf = sorted({rel for v in r["summary"].values() for rel, c in v["influence_by_relation"].items() if abs(c) > 0.1})
L += ["", f"**Relations with |leave-one-out influence on the diff| > 0.1 in any model × def:** {', '.join(inf) or 'none'}.", "",
      f"## {LAB}: company_ceo diagnostics", "",
      f"- **Templates:** {r['company_ceo_templates']}.",
      "- **Self-readout depth:** the half-probability rule on the stored logit-lens probability of the object first token at the fact prompt's own final position (no carrier). It is a lens readout, not a causal patch, so its scale is not comparable to D1.", "",
      f"| {LAB} model | template | correct / all cells | mean D1 (correct) | mean D4 (correct) | D1 per carrier | share D1 ≥ 0.95 | self-readout half-prob depth (correct) | logit-lens rank-1 depth (correct) |",
      "|---|---|---|---|---|---|---|---|---|"]
for m, dg in r["company_ceo"].items():
    for t in dg["templates"]:
        L.append(f"| {m} | {t['template_id']} | {t['n_correct']} / {t['n_cells']} | {f(t['mean_D1_correct'])} | {f(t['mean_D4_correct'])} | "
                 f"{' / '.join(f(x) for x in t['mean_D1_carrier'])} | {f(t['share_D1_ge_0.95_correct'])} | {f(t['mean_self_readout_halfprob_correct'])} | {f(t['mean_logit_lens_depth_correct'])} |")
    L.append(f"| {m} | all | correct cells with D1 ≥ 0.95 in the whole model: {dg['model_correct_cells_with_D1_ge_0.95']}, of which company_ceo: {dg['of_which_company_ceo']} | | | | | | |")
L += ["", "## Reading (numbers only)",
      "- **OLMo:** the diff stays > 0 in every leave-one-relation-out fit. Its minimum is the fit without company_ceo; the full-fit value and the minimum are in the table.",
      "- **company_ceo, OLMo template 1** (\"{} is led by its CEO,\"):",
      "  - Carrier-patched D1 is near 1.0 on all three carriers.",
      "  - Self-readout is near 1.0 for all three company_ceo templates, in every model. It therefore does not separate template 1 from its siblings, and does not confirm or refute the carrier-transfer explanation.",
      "- **Skeptic's confirm/refute test:**",
      "  - It needed self-readout ≈ 0.61 for template 1. The lens readout is late for every template, so the test as stated is inconclusive.",
      "  - The leave-one-relation-out part of the test is answered by the table."]
open(sys.argv[2], "w").write("\n".join(L) + "\n")
print(sys.argv[2])
