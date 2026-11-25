#!/usr/bin/env python3
"""Writes config/required_macros.json + config/required_macros.md: one LaTeX macro per preregistered
test and statistic in prereg/HR_revised.md (frozen 7725c5b). Macro names are letters only (LaTeX)."""
import json, pathlib
root = pathlib.Path(__file__).resolve().parents[1]
M = {"PyOneFour": "pythia-1.4b", "PyTwoEight": "pythia-2.8b", "OlmoSeven": "OLMo-2-1124-7B"}
PAIRS = {"PyOneFourOlmo": "pythia-1.4b vs OLMo-2 (cross-family, counts)",
         "PyTwoEightOlmo": "pythia-2.8b vs OLMo-2 (cross-family, counts)",
         "PyOneFourPyTwoEight": "pythia-1.4b vs pythia-2.8b (reported, does not count)"}
rows = []
def add(name, section, what):
    rows.append((name, section, what))
for m, d in M.items():
    add(f"hrN{m}", "B0", f"N rows in fit, {d}")
    for s, w in [("Icc", "ICC_rel point (REML)"), ("IccLo", "ICC_rel 95% CI lower (2000 relation-cluster resamples)"),
                 ("IccHi", "ICC_rel 95% CI upper"), ("HOnePass", "H1 PASS/FAIL")]:
        add(f"hr{s}{m}", "B4 H1", f"{w}, {d}")
    for s, w in [("DRsq", "H3 delta marginal R^2 of cooc_within (ML)"), ("DRsqLo", "H3 delta R^2 95% CI lower"),
                 ("DRsqHi", "H3 delta R^2 95% CI upper"), ("HThreePass", "H3 PASS/FAIL"),
                 ("Or", "correctness odds ratio per log1p cooc_within"), ("OrLo", "OR 95% CI lower"), ("OrHi", "OR 95% CI upper")]:
        add(f"hr{s}{m}", "B7 H3", f"{w}, {d}")
    for s, w in [("SplitHalf", "split-half reliability r_SB mean (200 splits)")]:
        add(f"hr{s}{m}", "B6", f"{w}, {d}")
    for s, w in [("SurvFrailtySd", "survival relation frailty SD"), ("SurvHr", "survival HR per log1p cooc_within"),
                 ("SurvHrLo", "survival HR Wald 95% CI lower"), ("SurvHrHi", "survival HR Wald 95% CI upper")]:
        add(f"hr{s}{m}", "B9 robustness (survival)", f"{w}, {d}")
for p, d in PAIRS.items():
    for s, w in [("NRel", "n relations"), ("Rho", "H2 raw Spearman of relation BLUPs"), ("RhoLo", "raw rho 95% CI lower"),
                 ("RhoHi", "raw rho 95% CI upper"), ("PermP", "permutation p, one-sided (10000 relation shuffles)"),
                 ("HTwoRawPass", "H2 raw PASS/FAIL")]:
        add(f"hr{s}{p}", "B5 H2 raw", f"{w}, {d}")
    for s, w in [("PRho", "H2 controlled partial Spearman"), ("PRhoLo", "partial rho 95% CI lower"), ("PRhoHi", "partial rho 95% CI upper"),
                 ("CovRho", "covariate-only predicted-ordering rho"), ("RhoGap", "raw rho minus covariate-only rho"),
                 ("Disatt", "disattenuated rho"), ("HTwoCtlPass", "H2 controlled PASS/FAIL")]:
        add(f"hr{s}{p}", "B6 H2 controlled", f"{w}, {d}")
VAR = {"CorrectOnly": "correct@1 rows only", "IncorrectOnly": "incorrect rows only", "CollapseExcl": "collapse_rate > 0.25 relations excluded",
       "WholeWord": "whole-word-object subset", "FracQuarter": "outcome at frac 0.25", "FracThreeQuarter": "outcome at frac 0.75",
       "TemplateA": "template 0 only", "TemplateB": "template 1 only", "TemplateC": "template 2 only",
       "CarrierA": "carrier 0 only", "CarrierB": "carrier 1 only", "CarrierC": "carrier 2 only",
       "SecPZeroOne": "secondary outcome p01_onset", "SecRankOne": "secondary outcome rank1_onset",
       "SecLogitDiff": "secondary outcome logitdiff_onset (PENDING, GPU)", "SurvFrailty": "survival frailty BLUP ordering"}
for v, w in VAR.items():
    if v != "SurvFrailty":
        for m, d in M.items():
            add(f"hrIcc{v}{m}", "B9 robustness", f"ICC_rel, {w}, {d}")
            add(f"hrDRsq{v}{m}", "B9 robustness", f"H3 delta R^2, {w}, {d}")
    for p, d in PAIRS.items():
        add(f"hrRho{v}{p}", "B9 robustness", f"raw rho, {w}, {d}")
        add(f"hrPermP{v}{p}", "B9 robustness", f"perm p one-sided, {w}, {d}")
        add(f"hrPRho{v}{p}", "B9 robustness", f"partial rho, {w}, {d}")
add("hrDecision", "B8", "decision under the frozen rule (GO / PARTIAL / NO-GO / UNASSIGNED)")
for h in ["HOne", "HTwoRaw", "HTwoCtl", "HThree"]:
    add(f"hr{h}Overall", "B8", f"{h} overall PASS/FAIL")
# P2 (prereg/P2_prompt_vs_fact.md, frozen at tag prereg-P2 = ff119ca): every preregistered test and statistic
P2M = {"Qwen": "Qwen3-8B", "Llama": "Llama-3.1-8B", "PyOneFour": "pythia-1.4b", "PyTwoEight": "pythia-2.8b", "Olmo": "OLMo-2-1124-7B"}
P2INC = {"Llama": "Llama-3.1-8B", "Olmo": "OLMo-2-1124-7B"}
for m, d in P2M.items():
    add(f"ptStatus{m}", "P2 s3 inclusion", f"inclusion status, {d}")
    add(f"ptIncFacts{m}", "P2 s3 inclusion", f"facts with >= 2 correct paraphrases, {d}")
    add(f"ptIncRel{m}", "P2 s3 inclusion", f"relations covered, {d}")
for m, d in P2INC.items():
    for y in ("DOne", "DFour"):
        for s in ("Icc", "IccLo", "IccHi", "Wording", "WordingLo", "WordingHi", "Diff", "DiffLo", "DiffHi", "MomDiff", "Band"):
            stem, suf = (s[:-2], s[-2:]) if s.endswith(("Lo", "Hi")) else (s, "")
            add(f"pt{stem}{y}{suf}{m}", "P2 s4-5 H1/H1-alt/H2", f"{s} {y}, {d}")
    for s in ("Nprime", "NprimeLo", "NprimeHi", "GCeil", "TfResid", "TfResidLo", "TfResidHi", "NullP", "NullFailed",
              "HOne", "HOneAlt", "NRows", "NFacts"):
        add(f"pt{s}{m}", "P2 s4-6", f"{s}, {d}")
    for sk in ("New", "All", "AllTen", "NoManu", "Tcov"):
        add(f"ptSens{sk}IccDOne{m}", "P2 s3 sensitivity", f"ICC(1) D1, set {sk}, {d}")
        add(f"ptSens{sk}DiffDOne{m}", "P2 s3 sensitivity", f"diff D1, set {sk}, {d}")
        add(f"ptSens{sk}DiffDFour{m}", "P2 s3 sensitivity", f"diff D4, set {sk}, {d}")
for c in ("HOne", "HOneAlt", "ModelDep", "NoFixedLayer", "SinglePromptPoor", "WordingTogether", "FactUnexplained", "FactShare"):
    add(f"ptClaim{c}", "P2 s6 claims", f"family-level claim {c}")
for s in ("N", "Rho", "KbarLlama", "KbarOlmo", "GLlama", "GOlmo", "Disatt"):
    add(f"ptHThree{s}", "P2 s5 H3", f"H3 {s}")
names = [r[0] for r in rows]
assert len(names) == len(set(names)) and all(n.isalpha() for n in names)
(root / "config").mkdir(exist_ok=True)
(root / "config" / "required_macros.json").write_text(json.dumps(names, indent=1) + "\n")
md = ["# Required macros (config/required_macros.json)", "",
      "One LaTeX macro per preregistered test and statistic in `prereg/HR_revised.md` (frozen 7725c5b). "
      "Generated by `scripts/gen_required_macros.py`. `scripts/check_numbers.py` fails if any is missing from `paper/numbers.tex`.", "",
      f"Total: {len(names)}.", "", "| macro | prereg section | statistic |", "|---|---|---|"]
md += [f"| `\\{n}` | {s} | {w} |" for n, s, w in rows]
(root / "config" / "required_macros.md").write_text("\n".join(md) + "\n")
print(len(names))
