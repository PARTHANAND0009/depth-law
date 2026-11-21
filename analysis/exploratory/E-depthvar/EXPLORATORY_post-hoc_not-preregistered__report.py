"""EXPLORATORY (post hoc, not preregistered) — E-depthvar figures and REPORT (numbers, CIs, limitations only).

python <this> <run_dir> <dest_dir>
Reads <run_dir>/e_depthvar.json and <run_dir>/tables/*cells_*.csv; writes into <dest_dir>:
figures/*.png|pdf (+ .json of plotted numbers), tables/*components.csv, *REPORT_EXPLORATORY.md.
"""
import json
import shutil
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

P = "EXPLORATORY_post-hoc_not-preregistered__"
LAB = "EXPLORATORY (post hoc, not preregistered)"
MODELS = ["pythia-1.4b", "pythia-2.8b", "OLMo-2-1124-7B"]


def f(x, nd=3):
    if x is None or (isinstance(x, float) and not np.isfinite(x)):
        return "n/a"
    return f"{x:.{nd}f}"


def fci(c, nd=3):
    return f"[{f(c[0], nd)}, {f(c[1], nd)}]" if c and c[0] is not None else "[n/a]"


def save(fig, base, data):
    fig.savefig(str(base) + ".png", dpi=150, bbox_inches="tight")
    fig.savefig(str(base) + ".pdf", bbox_inches="tight")
    Path(str(base) + ".json").write_text(json.dumps(data, indent=1, default=float))
    plt.close(fig)


def main(run, dest):
    run, dest = Path(run), Path(dest)
    (dest / "figures").mkdir(parents=True, exist_ok=True); (dest / "tables").mkdir(parents=True, exist_ok=True)
    g = json.loads((run / "e_depthvar.json").read_text())
    comp = pd.DataFrame(g["components"]).rename(columns={f"{LAB} model": "model"})
    shutil.copy(run / "tables" / f"{P}E-depthvar_components.csv", dest / "tables" / f"{P}E-depthvar_components.csv")
    # Figure 1: stacked shares per model x definition (set i, correct cells)
    defs = ["D1", "D2", "D2_cens_as_Lp1", "D3", "D4"]
    parts = [("share_fact_subject", "fact+subject", "#3b6ea5"), ("share_template_main", "template main (relation:template)", "#d08c34"),
             ("share_residual", "residual (fact×template + error)", "#b0b0b0"), ("share_relation", "relation", "#6aa36f")]
    fig, axes = plt.subplots(1, 3, figsize=(13, 4), sharey=True)
    data1 = {}
    for ax, m in zip(axes, MODELS):
        r = comp[(comp.model == m) & (comp.set == "correct")].set_index("outcome").loc[defs]
        bottom = np.zeros(len(defs))
        for col, lab, colr in parts:
            ax.bar(defs, r[col].to_numpy(), bottom=bottom, label=lab, color=colr)
            bottom += r[col].to_numpy()
        data1[m] = r[[c for c, _, _ in parts]].to_dict("index")
        ax.set_title(m); ax.tick_params(axis="x", rotation=40); [t.set_ha("right") for t in ax.get_xticklabels()]
    axes[0].set_ylabel("share of depth variance"); axes[-1].legend(fontsize=7, loc="upper left", bbox_to_anchor=(1.02, 1))
    fig.suptitle(f"{LAB}: variance shares of depth, correct cells (REML)")
    save(fig, dest / "figures" / f"{P}fig_stacked_shares", data1)
    # Figure 2: D-study curves (Phi(k), absolute) for D1 and D4, set i
    fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharey=True)
    data2 = {}
    for ax, y in zip(axes, ("D1", "D4")):
        for m in MODELS:
            ds = g["dstudy"][f"{m}|{y}|correct"]
            ax.plot(range(1, 31), ds["phi_k"], label=f"{m} Φ(k)")
            ax.plot(range(1, 31), ds["g_k"], ls="--", alpha=0.6, label=f"{m} G(k)")
            data2[f"{m}|{y}"] = ds
        ax.axhline(0.8, color="k", lw=0.8, ls=":"); ax.axvline(3, color="grey", lw=0.8, ls=":")
        ax.set_title(y); ax.set_xlabel("templates per fact (k); k > 3 extrapolated")
    axes[0].set_ylabel("generalizability"); axes[1].legend(fontsize=6)
    fig.suptitle(f"{LAB}: D-study of fact depth (correct cells)")
    save(fig, dest / "figures" / f"{P}fig_dstudy", data2)
    # Figure 3: strip plot of 40 seeded random facts, 3 template depths (D1) per model
    rng = np.random.default_rng(g["seed"])
    cells = {m: pd.read_csv(run / "tables" / f"{P}cells_{m}.csv") for m in MODELS}
    pool = sorted(set(cells[MODELS[0]].fact_id))
    pick = list(rng.choice(pool, 40, replace=False))
    fig, axes = plt.subplots(1, 3, figsize=(14, 8), sharey=True)
    data3 = {}
    for ax, m in zip(axes, MODELS):
        c = cells[m][cells[m].fact_id.isin(pick)].copy()
        c["yy"] = c.fact_id.map({fid: i for i, fid in enumerate(pick)})
        for corr, mk in ((1, "o"), (0, "x")):
            cc = c[c.correct == corr]
            ax.scatter(cc.D1, cc.yy, marker=mk, s=18, c=cc.template_id, cmap="viridis", vmin=0, vmax=2,
                       label="correct cell" if corr else "incorrect cell")
        ax.set_title(m); ax.set_xlabel("D1 half-probability depth (l/L)")
        data3[m] = c[["fact_id", "template_id", "correct", "D1"]].to_dict("records")
    axes[0].set_yticks(range(40)); axes[0].set_yticklabels(pick, fontsize=6); axes[0].legend(fontsize=7)
    fig.suptitle(f"{LAB}: 40 random facts (seed {g['seed']}), 3 template depths each; colour = template id")
    save(fig, dest / "figures" / f"{P}fig_strip40", data3)
    report(g, comp, dest)


def report(g, comp, dest):
    L = [f"# {LAB} — E-depthvar report", "",
         f"- **Source of every number:** `e_depthvar.json` in the run directory named in the ledger entry \"{LAB} E-depthvar B3-B7 run\".",
         f"- **Settings:** seed {g['seed']}; cluster bootstrap {g['n_boot']} resamples of facts within relation; shuffled-fact null {g['n_null']} permutations; planted recovery {g['n_sim']} simulations per condition ({g['n_cov_boot']} bootstrap resamples per simulation for coverage).",
         "- **Data:** S3b fp32 rows, 1300 facts × 3 templates per model, 26 relations. Plan: `EXPLORATORY_post-hoc_not-preregistered__PLAN.md`, committed before any statistic.",
         "- **Scope:** numbers, CIs and limitations only. No headline claims.", "",
         f"## {LAB}: B2 inclusion and censoring", "",
         f"| {LAB} model | L | facts correct 3/3 | 2/3 | 1/3 | 0/3 | correct cells | D2 censored (correct cells) | D3 censored (correct cells) |",
         "|---|---|---|---|---|---|---|---|---|"]
    for m in MODELS:
        b = g["build_summary"][m]; fc = b["facts_by_n_correct_templates"]; cc = b["censoring"]["correct_cells"]
        L.append(f"| {m} | {b['n_layers']} | {fc['3']} | {fc['2']} | {fc['1']} | {fc['0']} | {b['n_correct_cells']} | "
                 f"{cc['D2']['censored']}/{cc['D2']['n']} ({f(cc['D2']['rate'])}) | {cc['D3']['censored']}/{cc['D3']['n']} |")
    for s, title in (("correct", "set (i): all correct cells"), ("all3", "set (ii): facts correct under all 3 templates")):
        L += ["", f"## {LAB}: B3/B4 variance shares, {title} (lme4 REML; 95% CI from the cluster bootstrap)", "",
              f"| {LAB} model | def | N cells / facts | fact+subject | template main | residual | relation | (tmpl+resid) − (fact+subj) | ICC(1) | n′ (Φ≥0.8) | Φ(3) / G(3) | bootstrap fails |",
              "|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for _, r in comp[comp.set == s].iterrows():
            L.append(f"| {r.model} | {r.outcome} | {r.n_cells} / {r.n_facts} | {f(r.share_fact_subject)} {fci(r.share_fact_subject_ci)} | "
                     f"{f(r.share_template_main)} {fci(r.share_template_main_ci)} | {f(r.share_residual)} {fci(r.share_residual_ci)} | "
                     f"{f(r.share_relation)} {fci(r.share_relation_ci)} | {f(r.diff_prompt_minus_fact)} {fci(r.diff_ci)} | "
                     f"{f(r.icc1)} {fci(r.icc1_ci)} | {r.nprime_phi if r.nprime_phi == r.nprime_phi else '>30'} {fci(r.nprime_phi_ci, 0)} | "
                     f"{f(r.phi3)} / {f(r.g3)} | {r.n_boot_failed}/{r.n_boot} |")
    L += ["", "- **n′ in the bootstrap:** a resample with no k ≤ 30 reaching 0.8 is coded as 31.",
          "- **D2:** uses uncensored cells only. D2_cens_as_Lp1 scores censored carriers as (L+1)/L. D3 has no censored correct cells.",
          "- **B4:** which of template main and residual is larger can be read directly from the two columns above.", "",
          f"## {LAB}: B3 ANOVA (method-of-moments) cross-check, balanced sets (fact = fact+subject)", "",
          f"| {LAB} model | def | set | N facts | relations | fact | template main | residual | relation |", "|---|---|---|---|---|---|---|---|---|"]
    for k, v in g["anova_B3_crosscheck"].items():
        m, y, s = k.split("|"); sh = v["share"]
        L.append(f"| {m} | {y} | {s} | {v['n_facts']} | {v['n_relations']} | {f(sh['fact'])} | {f(sh['template_main'])} | {f(sh['residual'])} | {f(sh['relation'])} |")
    L += ["", f"## {LAB}: B7a shuffled-fact null (fact IDs permuted within relation × template; ANOVA fact share)", "",
          f"| {LAB} model | def | set | observed fact share | null mean | null 95th | null 99th | p |", "|---|---|---|---|---|---|---|---|"]
    for k, v in g["null_B7a"].items():
        m, y, s = k.split("|")
        L.append(f"| {m} | {y} | {s} | {f(v['observed_fact_share'])} | {f(v['null_mean'])} | {f(v['null_p95'])} | {f(v['null_p99'])} | {f(v['p_value'], 4)} |")
    L += ["", f"## {LAB}: B7b planted-depth recovery", "",
          "- **Bias arm:** lme4 on each model's exact correct-cell design.",
          "- **Coverage arm:** ANOVA estimator with a within-relation fact bootstrap, on the balanced set-(ii) design.",
          "- **Units:** planted shares are on the latent midpoint; D1 and D4 are nonlinear in it.", "",
          f"| {LAB} model | planted fact | planted template | D1 recovered fact (bias) | D1 recovered template (bias) | D4 recovered fact (bias) | D4 recovered template (bias) | D1 coverage fact / template | D4 coverage fact / template |",
          "|---|---|---|---|---|---|---|---|---|"]
    for m in MODELS:
        pl = g["planted_B7b"][m]
        covs = {(c["planted"]["fact"], c["planted"]["template_main"]): c["coverage"] for c in pl["coverage_anova"]["conditions"]}
        for b in pl["bias_lme4"]:
            cv = covs[(b["planted_fact"], b["planted_template_main"])]
            L.append(f"| {m} | {b['planted_fact']} | {b['planted_template_main']} | {f(b['D1_mean_fact_subject'])} ({f(b['D1_bias_fact'])}) | "
                     f"{f(b['D1_mean_template_main'])} ({f(b['D1_bias_template_main'])}) | {f(b['D4_mean_fact_subject'])} ({f(b['D4_bias_fact'])}) | "
                     f"{f(b['D4_mean_template_main'])} ({f(b['D4_bias_template_main'])}) | {f(cv['D1']['fact'], 2)} / {f(cv['D1']['template_main'], 2)} | "
                     f"{f(cv['D4']['fact'], 2)} / {f(cv['D4']['template_main'], 2)} |")
        L.append(f"| {m} | max abs bias {f(pl['max_abs_bias'])} | pass (±0.05): {pl['pass_within_0.05']} | coverage design: {pl['coverage_anova']['design']} | | | | | |")
    L += ["", f"## {LAB}: B7c carrier facet (long per-carrier data, correct cells, REML shares)", "",
          f"| {LAB} model | def | fact | subject | template main | relation | carrier | fact:carrier | template:carrier | residual | singular |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    for k, v in g["carrier_B7c"].items():
        m, y = k.split("|"); sh = v["share"]
        L.append(f"| {m} | {y} | {f(sh.get('fact_id'))} | {f(sh.get('subject'))} | {f(sh.get('rt'))} | {f(sh.get('relation'))} | {f(sh.get('carrier'))} | "
                 f"{f(sh.get('fc'))} | {f(sh.get('rtc'))} | {f(sh.get('Residual'))} | {v.get('singular')} |")
    L += ["", f"## {LAB}: B5 covariates (all six jointly; % change of each component vs B3, correct cells)", "",
          f"| {LAB} model | def | fact | subject | fact+subject | template main | relation | residual |", "|---|---|---|---|---|---|---|---|"]
    for k, v in g["covariates_B5"].items():
        m, y, s = k.split("|")
        if s != "correct" or y not in ("D1", "D4") or not v:
            continue
        pc = v["joint_pct_change"]; b = next(r for r in g["components"] if r[f"{LAB} model"] == m and r["outcome"] == y and r["set"] == s)
        fs_before = b["share_fact_subject"]; fs_after = v["joint_summary"]["share_fact_subject"]
        L.append(f"| {m} | {y} | {f(pc.get('fact_id'))} | {f(pc.get('subject'))} | share {f(fs_before)} → {f(fs_after)} | {f(pc.get('rt'))} | {f(pc.get('relation'))} | {f(pc.get('Residual'))} |")
    L += ["", "- **One-at-a-time changes:** in `e_depthvar.json` → `covariates_B5`.",
          "- **Fact vs subject split:** not interpretable (one fact per subject apart from a handful); only fact+subject is.", "",
          f"## {LAB}: B6 cross-model agreement of fact-level mean depth", "",
          f"| {LAB} def | facts | pair | N facts | relations | ρ [95% CI] | ρ within relation [CI] | G(3) a / b | disattenuated ρ [CI] |", "|---|---|---|---|---|---|---|---|---|"]
    for k, v in g["cross_model_B6"].items():
        gg = list(v["g3"].values())
        L.append(f"| {v['outcome']} | {v['facts']} | {v['pair']} | {v['n_facts']} | {v['n_relations']} | {f(v['rho'])} {fci(v['rho_ci'])} | "
                 f"{f(v['rho_within_relation'])} {fci(v['rho_within_relation_ci'])} | {f(gg[0])} / {f(gg[1])} | {f(v['disattenuated_rho'])} {fci(v['disattenuated_rho_ci'])} |")
    L += ["", f"## {LAB}: limitations", "",
          "1. **Not blind.** The D1 all-rows variance components were seen in the H-R gate before this plan (see the plan's disclosure).",
          "2. **Interaction vs error.** One observation per fact × template cell, so the residual (fact × template interaction) cannot be separated from measurement error.",
          "3. **Templates are nested in relations, 3 per relation.** The template-main component is estimated from 78 levels, and the D-study for k > 3 extrapolates assuming new templates come from the same population.",
          "4. **Correctness filter.** Set (i) keeps only correct cells. The cells kept differ by model (720 / 804 / 1414), so facts and relations are unequally represented.",
          "   - Set (ii) is small: 84 / 107 / 254 facts.",
          "   - D2 and D3 are censored for incorrect cells by construction.",
          "5. **Fact vs subject.** These are confounded; only their sum is reported as a share.",
          "6. **Carrier.** 3 carriers, all neutral templates, which is too few levels to estimate a carrier main effect well.",
          "7. **B6 uncertainty.** The B6 disattenuation holds G(3) at its point estimate (from the set-(ii) fit), so its CI ignores the uncertainty in G.",
          "8. **Covariates.** Covariate effects are associations within these data, not causal decompositions.",
          "9. **Exploratory.** Everything here is post hoc and not preregistered; no result here is confirmatory."]
    (dest / f"{P}REPORT_EXPLORATORY.md").write_text("\n".join(L) + "\n")
    print(dest / f"{P}REPORT_EXPLORATORY.md")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
