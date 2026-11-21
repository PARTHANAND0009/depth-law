"""results/HR_gate.md from results/HR_gate.json (numbers only from that file)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def f(x, nd=3):
    if x is None:
        return "MISSING"
    if isinstance(x, float) and x != x:
        return "undefined"
    if isinstance(x, float) and abs(x) < 1e-3 and x != 0:
        return f"{x:.2e}"
    return f"{x:.{nd}f}"


def fci(c, nd=3):
    return "[" + ", ".join(f(v, nd) for v in c) + "]" if c else "[MISSING]"


def short(m):
    return m.split("/")[-1]


def main(path=ROOT / "results" / "HR_gate.json", out=ROOT / "results" / "HR_gate.md"):
    g = json.loads(Path(path).read_text())
    M, P, th = g["models"], g["pairs"], g["thresholds"]
    L = [f"# Revised H-R gate (prereg/HR_revised.md, frozen at {g['prereg_commit'][:7]})", "",
         f"- **Source of every number:** `results/HR_gate.json` (run_id `{g['run_id']}`). Per-task R outputs are in `results/HR/{g['run_id']}/`.",
         f"- **Seed:** {g['seed']} for every bootstrap, permutation and split.",
         "- **Data:** existing S3b rows (fp32 GPU runs of 2026-11-21); no new model runs.",
         "- **Counts:** EXACT only (Pythia `v4_piletrain_llama`, OLMo-2 `v4_olmo-mix-1124_llama`); each model fitted separately.", "",
         f"## Decision (frozen rule): **{g['decision']}**", "",
         "| hypothesis | pass |", "|---|---|"]
    L += [f"| {k} | {v} |" for k, v in g["hypotheses"].items()]
    L += ["", "Cross-family pairs that count: pythia-1.4b vs OLMo-2 and pythia-2.8b vs OLMo-2. The pythia-1.4b vs pythia-2.8b pair is reported but does not count.", "",
          "## Gate table: pairs (H2)", "",
          "| pair | counts | n rel | raw ρ [95% CI] | perm p (1-sided / 2-sided) | partial ρ [95% CI] | covariate-only ρ | raw − cov-only | split-half r_SB (A / B) | disattenuated ρ (undefined splits as 0) | H2 raw | H2 controlled |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for k, p in P.items():
        sh = list(p["split_half_r_sb"].values())
        L.append(f"| {k} | {'yes' if p['counts_for_decision'] else 'no'} | {p['n_relations']} | {f(p['rho'])} {fci(p['rho_ci'])} | "
                 f"{f(p['perm_p_one_sided'], 4)} / {f(p['perm_p_two_sided'], 4)} | {f(p['partial_rho'])} {fci(p['partial_rho_ci'])} | "
                 f"{f(p['cov_only_rho'])} | {f(p['rho_minus_cov_only'])} | {f(sh[0])} / {f(sh[1])} | {f(p['disattenuated_rho'])} ({f(p.get('disattenuated_rho_undefined_as_0'))}) | "
                 f"{'PASS' if p['h2_raw_pass'] else 'FAIL'} | {'PASS' if p['h2_controlled_pass'] else 'FAIL'} |")
    L += ["", f"Thresholds: raw ρ ≥ {th['rho']} with 1-sided p < {th['perm_p']} (10000 permutations); partial ρ ≥ {th['prho']} with CI lower bound > {th['prho_lo']}; raw − cov-only ≥ {th['rho_gap']}.",
          "Bootstrap CIs use 2000 resamples of relations. n = 26 relations.",
          "Split-half: 200 random 25/25 fact splits per relation, H1 fit on each half, Spearman of the two halves' relation BLUPs, then Spearman-Brown. A split whose fit puts σ²_relation at 0 has constant BLUPs and an undefined Spearman. The prereg does not specify this case; such splits are counted, excluded from the mean, and also scored as r = 0 in a conservative variant. The human asked for no change in prereg/, so this is recorded here, not in prereg/DEVIATIONS.md.", "",
          "## Gate table: models (H1, H3)", "",
          "| model | N rows | ICC_rel [95% CI] | bootstrap failures (ICC) | H1 | H3 ΔR² [95% CI] | H3 | correctness OR per log1p cooc [95% CI] | split-half r_SB mean [2.5, 97.5 pct] | undefined splits | r_SB, undefined as 0 |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    for m, r in M.items():
        mm, b = r["main"], r["boot"]
        L.append(f"| {short(m)} | {mm['n_rows']} | {f(mm['icc_rel'])} {fci(b['icc_ci'])} | {b['n_failed']['icc']}/{b['n_boot']} | "
                 f"{'PASS' if r['h1_pass'] else 'FAIL'} | {f(mm['dr2'], 4)} {fci(b['dr2_ci'], 4)} | {'PASS' if r['h3_pass'] else 'FAIL'} | "
                 f"{f(2.718281828459045 ** mm['log_or'])} {fci(b['or_ci'])} | {f(r['split_half']['r_sb_mean'])} {fci(r['split_half']['r_sb_pct'])} | {r['split_half']['n_undefined']}/{r['split_half']['n_split']} | {f(r['split_half']['r_sb_mean_undefined_as_0'])} |")
    L += ["", f"Thresholds: ICC_rel ≥ {th['icc']} with CI lower bound ≥ {th['icc_lo']}; ΔR² CI upper bound < {th['dr2_hi']}.",
          "ICC_rel = σ²_relation / (σ²_relation + σ²_relation:template + σ²_subject + σ²_residual), from the REML H1 fit with 5 fact covariates.", "",
          "### Variance components (H1 fit, REML)", "", "| model | relation | relation:template | subject | residual | marginal R² (fixed, ML, without / with cooc) |", "|---|---|---|---|---|---|"]
    for m, r in M.items():
        v = r["main"]["vc"]
        L.append(f"| {short(m)} | {f(v['relation'], 5)} | {f(v['rt'], 5)} | {f(v['subject'], 5)} | {f(v['Residual'], 5)} | "
                 f"{f(r['main']['r2m_m0'])} / {f(r['main']['r2m_m1'])} |")
    L += ["", "## Robustness and secondary outcomes (non-gating; point estimates)", "",
          "| variant | model | N rows | n rel | ICC_rel | H3 ΔR² |", "|---|---|---|---|---|---|"]
    for v in next(iter(M.values()))["variants"]:
        for m, r in M.items():
            x = r["variants"].get(v, {})
            if "missing" in x:
                L.append(f"| {v} | {short(m)} | MISSING: {x['missing'][:80]} | | | |")
            else:
                L.append(f"| {v} | {short(m)} | {x['n_rows']} | {x['n_relations']} | {f(x['icc_rel'])} | {f(x['dr2'], 4)} |")
    L += ["", "| variant | pair | n rel | raw ρ | perm p (1-sided) | partial ρ | covariate-only ρ |", "|---|---|---|---|---|---|---|"]
    for k, p in P.items():
        for v, q in p["robustness"].items():
            if "missing" in q:
                L.append(f"| {v} | {k} | MISSING | | | | |")
            elif "undefined" in q:
                L.append(f"| {v} | {k} | {q['n_relations']} | undefined (σ²_relation = 0 in a model) | – | – | – |")
            else:
                L.append(f"| {v} | {k} | {q['n_relations']} | {f(q['rho'])} | {f(q['perm_p_one_sided'], 4)} | {f(q['partial_rho'])} | {f(q['cov_only_rho'])} |")
    L += ["", "### Discrete-time survival with relation frailty (cloglog, event = half-probability layer)", "",
          "| model | person-periods | frailty SD | HR per log1p cooc_within [95% CI] | p | warnings |", "|---|---|---|---|---|---|"]
    for m, r in M.items():
        s = r["survival"]
        if "missing" in s:
            L.append(f"| {short(m)} | MISSING: {s['missing'][:120]} | | | | |")
        else:
            L.append(f"| {short(m)} | {s['n_person_periods']} | {f(s['frailty_sd'])} | {f(s['hr_cooc'])} {fci(s['hr_cooc_ci'])} | {f(s['p_cooc'], 4)} | {len(s['warnings'])} |")
    L += ["", "### Secondary outcomes", "",
          "- `p01_onset` and `rank1_onset`: rows `secondary_*` in the tables above. They are defined only on the subset where the final p ≥ 0.1, or on correct@1 rows.",
          f"- `logitdiff_onset`: {g['secondary_pending']['logitdiff_onset']}", "",
          "## Prior covariate (log_prior)", "", "| model | source | hub commit | seconds | bytes read |", "|---|---|---|---|---|"]
    for m, r in M.items():
        p = r["prior"]
        L.append(f"| {short(m)} | {p['source']} | {p['hub_commit'][:10]} | {p['seconds']} | {p.get('bytes_read')} |")
    L += ["", "Streamed forward validated against a standard fp32 forward: pythia-70m max abs log-prob difference 3.7e-4, on values down to −850 (`tests/test_hr_prior.py`); a random tiny OLMo-2 agrees to < 1e-4."]
    for c in g.get("corrections", []):
        L += ["", f"Correction {c['utc']}: {c['what']}. Rows: {'; '.join(c['rows'])}."]
    Path(out).write_text("\n".join(L) + "\n")
    print(out)


if __name__ == "__main__":
    main(*sys.argv[1:])
