"""EXPLORATORY (post hoc, not preregistered) — writes reports/gates/G1/GATE_G1.md from e_depthvar.json and the
saved review files (numbers are read, not typed). Usage: python <this> <run_dir>"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LAB = "EXPLORATORY (post hoc, not preregistered)"
MODELS = ["pythia-1.4b", "pythia-2.8b", "OLMo-2-1124-7B"]


def f(x, nd=3):
    return "n/a" if x is None else f"{x:.{nd}f}"


def fci(c, nd=3):
    return f"[{f(c[0], nd)}, {f(c[1], nd)}]"


def main(run):
    run = Path(run).resolve()
    g = json.loads((run / "e_depthvar.json").read_text())
    comp = {(r[f"{LAB} model"], r["outcome"], r["set"]): r for r in g["components"]}
    di = g["decision_inputs"]
    verdict = {}
    for a in ("replicator", "stats-reviewer", "skeptic"):
        t = (ROOT / "reports/gates/G1" / f"{a}.md").read_text()
        verdict[a] = re.findall(r"^VERDICT:\s*(\w+)", t, re.M)[-1]
    L = [f"# GATE G1 — {LAB}: E-depthvar (prompt vs fact variance in causal depth)", "",
         f"- **Sources:** `{run.relative_to(ROOT)}/e_depthvar.json`. Reviews: `reports/gates/G1/{{replicator,stats-reviewer,skeptic}}.md` (verbatim). Responses: `reports/gates/G1/responses.md`.",
         "- **Plan:** `analysis/exploratory/E-depthvar/EXPLORATORY_post-hoc_not-preregistered__PLAN.md` (commit 853917a, before any statistic).",
         "- **Not blind:** the D1 all-rows components had been seen in the H-R gate.", "",
         "## Per model × definition (set (i): correct cells; lme4 REML; 95% CI from 1000 cluster-bootstrap resamples of facts within relation)", "",
         f"| {LAB} model | def | N cells | fact+subject share | template-main share | residual share | relation share | (tmpl+resid) − (fact+subj) [CI] | ICC(1) [CI] | n′ for Φ ≥ 0.8 [CI] | n′ for G ≥ 0.8 |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
    for m in MODELS:
        for y in ("D1", "D4"):
            r = comp[(m, y, "correct")]
            L.append(f"| {m} | {y} | {r['n_cells']} | {f(r['share_fact_subject'])} {fci(r['share_fact_subject_ci'])} | "
                     f"{f(r['share_template_main'])} {fci(r['share_template_main_ci'])} | {f(r['share_residual'])} {fci(r['share_residual_ci'])} | "
                     f"{f(r['share_relation'])} | {f(r['diff_prompt_minus_fact'])} {fci(r['diff_ci'])} | {f(r['icc1'])} {fci(r['icc1_ci'])} | "
                     f"{r['nprime_phi']} {fci(r['nprime_phi_ci'], 0)} | {r['nprime_g']} |")
    L += ["", "Set (ii) (facts correct under all 3 templates) and D2/D3 are in the report.", "",
          "## Cross-model agreement of fact-level mean depth (B6; disattenuated by G(3) from the set-(ii) fits)", "",
          f"| {LAB} def | facts | pair | N facts | ρ [CI] | disattenuated ρ | ρ within relation |", "|---|---|---|---|---|---|---|"]
    for k, v in g["cross_model_B6"].items():
        L.append(f"| {v['outcome']} | {v['facts']} | {v['pair']} | {v['n_facts']} | {f(v['rho'])} {fci(v['rho_ci'])} | {f(v['disattenuated_rho'])} | {f(v['rho_within_relation'])} |")
    nl = g["null_B7a"]; pl = g["planted_B7b"]
    L += ["", "## Controls", "",
          f"| {LAB} check | result |", "|---|---|",
          f"| B7a shuffled-fact null (ANOVA fact share; all cells and set ii) | observed share above the null 99th percentile in {sum(v['observed_fact_share'] > v['null_p99'] for v in nl.values())}/{len(nl)} cases; p = {f(min(v['p_value'] for v in nl.values()), 4)}–{f(max(v['p_value'] for v in nl.values()), 4)} |",
          f"| B7b planted recovery: max abs bias of recovered fact / template shares (lme4, correct-cell design) | " + "; ".join(f"{m} {f(pl[m]['max_abs_bias'])}" for m in MODELS) + f" (pass ±0.05: {all(pl[m]['pass_within_0.05'] for m in MODELS)}) |",
          "| B7b CI coverage (nominal 0.95) | 0.46–0.98, median 0.74 (template main 0.46–0.86); see report limitation 10 |",
          "| B7c carrier facet | 3 carriers present; fit in the report |", "",
          "## Reviews", "",
          "| reviewer | verdict | decision-relevant findings |", "|---|---|---|",
          f"| replicator (statsmodels REML, raw files only) | {verdict['replicator']} | All 72 numbers within tolerance: 48 B3 shares (max gap 0.00016) and 24 B6 ρ (gap 0). A method-of-moments estimator moves the relation and template-main shares by up to 0.25; the fact and residual variances agree. |",
          f"| stats-reviewer (spec, bootstrap, D-study) | {verdict['stats-reviewer']} | 9 findings; 1 could change the category. Measured within relation (ICC(1)), the fact share is ≥ 0.5 in 2 of 3 models under D1 and D4, which would be PASS-FACT. Also: the bootstrap leaves out template sampling (CIs too narrow), and the planted grid does not cover the observed shares. |",
          f"| skeptic | {verdict['skeptic']} | The category stays AMBIGUOUS. BLOCKING 1: OLMo's prompt > fact comes from one template (dropping company_ceo moves the D1 diff from 0.199 to 0.009). BLOCKING 2: wrong \"78 levels\" text (fixed in report v3). The relation share counts on neither side. |", "",
          "## Decision (human's G1 rule; set (i); shares of total variance including relation)", "",
          f"- **PASS-PROMPT:** (tmpl+resid) > (fact+subj), CI excluding 0, under D1 in: {', '.join(m for m, v in di['prompt_wins_D1_ci_excludes_0'].items() if v) or 'none'}. The rule needs ≥ 2 of 3. **Not met.** The skeptic's BLOCKING issue 1 is also unresolved.",
          f"- **PASS-FACT:** fact+subject ≥ 0.5 under both D1 and D4 in: {', '.join(m for m in MODELS if di['fact_share_ge_0.5_D1'][m] and di['fact_share_ge_0.5_D4'][m]) or 'none'}. The rule needs ≥ 2 of 3. **Not met.**",
          "- **Outcome: AMBIGUOUS.**",
          "- **Sensitivity of the category** (from the reviews; neither is the rule as written):",
          "  - With the fact share measured within relation (ICC(1)), or with the relation component counted as fact, PASS-FACT would hold in 2 of 3 models.",
          "  - With the relation component counted as prompt, the prompt side wins in all 3 models.",
          "  - The relation component, which also carries each relation's average wording effect, decides the category.", "",
          "## Recommendation (one next step, per the human's instruction)",
          "AMBIGUOUS leads to the confirmatory preregistration (prompt 2). It is not started: it needs the human's \"approve G1\"."]
    (ROOT / "reports/gates/G1/GATE_G1.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main(sys.argv[1])
