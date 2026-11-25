#!/usr/bin/env python3
"""Generate paper/numbers.tex: every number the paper may use, as a LaTeX macro, read from results files only.
Run through scripts/log_run.py. The header '% inputs: {...}' records the sha256 of every input (checked by
scripts/check_numbers.py). A quantity whose source is absent is written as the text MISSING (never estimated).
Macro names are letters only. Prefixes: hr = prereg/HR_revised.md; pt = prereg/P2_prompt_vs_fact.md (P2);
ptRob = P2 non-selecting robustness simulation; ptCal = P2 null calibration (prereg test); expl = EXPLORATORY
(not preregistered; must be labelled EXPLORATORY wherever used)."""
import hashlib, json, math, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "paper" / "numbers.tex"
INPUTS, M = {}, []  # M: (name, value text, source note)


def load(rel):
    p = ROOT / rel
    if not p.exists():
        return None
    INPUTS[rel] = hashlib.sha256(p.read_bytes()).hexdigest()
    return json.loads(p.read_text())


def tex(s):
    return str(s).replace("\\", "/").replace("_", "\\_").replace("%", "\\%").replace("&", "\\&").replace("#", "\\#")


def fmt(v, nd=3):
    if v is None:
        return "MISSING"
    if isinstance(v, bool):
        return "yes" if v else "no"
    if isinstance(v, int):
        return f"{v:,}".replace(",", "{,}")
    if isinstance(v, float):
        if math.isnan(v):
            return "MISSING"
        if v != 0 and abs(v) < 10 ** (-nd):
            return f"{v:.1e}"
        s = f"{v:.{nd}f}"
        return "0." + "0" * nd if s in ("-0." + "0" * nd,) else s
    return tex(v)


def add(name, value, src, nd=3, raw=False):
    assert name.isalpha(), name
    assert name not in {m[0] for m in M}, name
    M.append((name, value if raw else fmt(value, nd), src))


def pf(b):
    return None if b is None else ("PASS" if b else "FAIL")


# ---------------------------------------------------------------- H-R (prereg/HR_revised.md)
HRF = "results/HR_gate.json"
hr = load(HRF)
HRM = {"PyOneFour": "EleutherAI/pythia-1.4b", "PyTwoEight": "EleutherAI/pythia-2.8b", "OlmoSeven": "allenai/OLMo-2-1124-7B"}
HRP = {"PyOneFourOlmo": "pythia-1.4b vs OLMo-2-1124-7B", "PyTwoEightOlmo": "pythia-2.8b vs OLMo-2-1124-7B",
       "PyOneFourPyTwoEight": "pythia-1.4b vs pythia-2.8b"}
VAR = {"CorrectOnly": "correct_only", "IncorrectOnly": "incorrect_only", "CollapseExcl": "collapse_le_25",
       "WholeWord": "whole_word_object", "FracQuarter": "frac_0.25", "FracThreeQuarter": "frac_0.75",
       "TemplateA": "template_0", "TemplateB": "template_1", "TemplateC": "template_2", "CarrierA": "carrier_0",
       "CarrierB": "carrier_1", "CarrierC": "carrier_2", "SecPZeroOne": "secondary_p01_onset",
       "SecRankOne": "secondary_rank1_onset", "SecLogitDiff": None, "SurvFrailty": "survival_frailty"}
if hr:
    src = f"{HRF} (run {hr['run_id']})"
    for k, mname in HRM.items():
        m = hr["models"][mname]; mn = m["main"]; b = m["boot"]; sv = m["survival"]
        add(f"hrN{k}", int(mn["n_rows"]), src)
        add(f"hrIcc{k}", mn["icc_rel"], src); add(f"hrIccLo{k}", b["icc_ci"][0], src); add(f"hrIccHi{k}", b["icc_ci"][1], src)
        add(f"hrHOnePass{k}", pf(m["h1_pass"]), src)
        add(f"hrDRsq{k}", mn["dr2"], src, 4); add(f"hrDRsqLo{k}", b["dr2_ci"][0], src, 4); add(f"hrDRsqHi{k}", b["dr2_ci"][1], src, 4)
        add(f"hrHThreePass{k}", pf(m["h3_pass"]), src)
        add(f"hrOr{k}", math.exp(mn["log_or"]), src); add(f"hrOrLo{k}", b["or_ci"][0], src); add(f"hrOrHi{k}", b["or_ci"][1], src)
        add(f"hrSplitHalf{k}", m["split_half"]["r_sb_mean"], src)
        add(f"hrSurvFrailtySd{k}", sv["frailty_sd"], src); add(f"hrSurvHr{k}", sv["hr_cooc"], src)
        add(f"hrSurvHrLo{k}", sv["hr_cooc_ci"][0], src); add(f"hrSurvHrHi{k}", sv["hr_cooc_ci"][1], src)
        add(f"hrSurvP{k}", sv["p_cooc"], src, 2)
        for v, key in VAR.items():
            if v == "SurvFrailty":
                continue
            vv = m["variants"].get(key) if key else None
            add(f"hrIcc{v}{k}", vv.get("icc_rel") if vv else None, src if vv else "PENDING (GPU; distractor logits not stored)")
            add(f"hrDRsq{v}{k}", vv.get("dr2") if vv else None, src if vv else "PENDING", 4)
    for k, pname in HRP.items():
        p = hr["pairs"][pname]
        add(f"hrNRel{k}", int(p["n_relations"]), src)
        add(f"hrRho{k}", p["rho"], src); add(f"hrRhoLo{k}", p["rho_ci"][0], src); add(f"hrRhoHi{k}", p["rho_ci"][1], src)
        add(f"hrPermP{k}", p["perm_p_one_sided"], src, 4)
        add(f"hrHTwoRawPass{k}", pf(p["h2_raw_pass"]) if p.get("counts_for_decision") else "does not count", src)
        add(f"hrPRho{k}", p["partial_rho"], src); add(f"hrPRhoLo{k}", p["partial_rho_ci"][0], src)
        add(f"hrPRhoHi{k}", p["partial_rho_ci"][1], src); add(f"hrCovRho{k}", p["cov_only_rho"], src)
        add(f"hrRhoGap{k}", p["rho_minus_cov_only"], src); add(f"hrDisatt{k}", p["disattenuated_rho"], src)
        add(f"hrHTwoCtlPass{k}", pf(p["h2_controlled_pass"]) if p.get("counts_for_decision") else "does not count", src)
        for v, key in VAR.items():
            rv = p["robustness"].get(key) if key else None
            ok = rv is not None and rv.get("rho") is not None and not (isinstance(rv.get("rho"), float) and math.isnan(rv["rho"]))
            note = src if ok else ("PENDING (GPU)" if key is None else "undefined (relation variance 0 in a model)")
            add(f"hrRho{v}{k}", rv["rho"] if ok else None, note)
            add(f"hrPermP{v}{k}", rv["perm_p_one_sided"] if ok else None, note, 4)
            add(f"hrPRho{v}{k}", rv.get("partial_rho") if ok else None, note)
    add("hrDecision", hr["decision"], src)
    for h, key in [("HOne", "H1"), ("HTwoRaw", "H2_raw"), ("HTwoCtl", "H2_controlled"), ("HThree", "H3")]:
        add(f"hr{h}Overall", pf(hr["hypotheses"][key]), src)

# ---------------------------------------------------------------- P2 (prereg/P2_prompt_vs_fact.md)
PD = "results/P2analysis"
res, dec = load(f"{PD}/correct/p2_results.json"), load(f"{PD}/correct/p2_decision.json")
P2M = {"Qwen": "Qwen/Qwen3-8B", "Llama": "meta-llama/Llama-3.1-8B", "PyOneFour": "EleutherAI/pythia-1.4b",
       "PyTwoEight": "EleutherAI/pythia-2.8b", "Olmo": "allenai/OLMo-2-1124-7B"}
INC = {"Llama": "meta-llama/Llama-3.1-8B", "Olmo": "allenai/OLMo-2-1124-7B"}
Y = {"DOne": "D1", "DTwo": "D2", "DThree": "D3", "DFour": "D4"}
if res and dec:
    src = f"{PD}/correct/p2_results.json + p2_decision.json (set correct, gating)"
    add("ptNcUsed", int(res["n_carriers_used"]), src)
    add("ptNBoot", int(res["n_boot"]), src)
    for k, mn in P2M.items():
        m = res["models"][mn]
        add(f"ptStatus{k}", "included" if m["status"] == "ok" else m["status"], src)
        add(f"ptIncFacts{k}", int(m["min_data"]["facts_with_2plus_correct"]), src)
        add(f"ptIncRel{k}", int(m["min_data"]["relations_with_such_facts"]), src)
    for k, mn in INC.items():
        m, d = res["models"][mn], dec["per_model"][mn]
        f1 = m["fits"]["D1"]
        add(f"ptNRows{k}", int(m["n_rows"]), src); add(f"ptNFacts{k}", int(m["n_facts"]), src)
        add(f"ptNCells{k}", int(m["mom"]["D1"]["n_cells"]), src)
        for yk, y in Y.items():
            f = m["fits"][y]; ci = f["boot"]["ci"]
            add(f"ptIcc{yk}{k}", f["point"]["icc1"], src); add(f"ptIcc{yk}Lo{k}", ci["icc1"][0], src); add(f"ptIcc{yk}Hi{k}", ci["icc1"][1], src)
            add(f"ptDiff{yk}{k}", f["point"]["diff"], src); add(f"ptDiff{yk}Lo{k}", ci["diff"][0], src); add(f"ptDiff{yk}Hi{k}", ci["diff"][1], src)
            add(f"ptNRows{yk}{k}", int(f["n_rows"]), src)
            if y in ("D1", "D4"):
                add(f"ptWording{yk}{k}", f["point"]["wording"], src)
                add(f"ptWording{yk}Lo{k}", ci["wording"][0], src); add(f"ptWording{yk}Hi{k}", ci["wording"][1], src)
                add(f"ptMomDiff{yk}{k}", m["mom"][y]["diff"], src)
                add(f"ptBand{yk}{k}", d[f"icc1_band_{y}"], src)
        add(f"ptNprime{k}", d["nprime_G_D1"], src)
        add(f"ptNprimeLo{k}", int(round(f1["boot"]["ci"]["nprime_G"][0])), src)
        add(f"ptNprimeHi{k}", int(round(f1["boot"]["ci"]["nprime_G"][1])), src)
        add(f"ptGCeil{k}", d["G_ceiling_D1"], src)
        add(f"ptTfResid{k}", f1["point"]["tf_minus_resid"], src)
        add(f"ptTfResidLo{k}", f1["boot"]["ci"]["tf_minus_resid"][0], src); add(f"ptTfResidHi{k}", f1["boot"]["ci"]["tf_minus_resid"][1], src)
        nl = m["null"]
        add(f"ptNullP{k}", nl["p"], src, 4); add(f"ptNullNSim{k}", int(nl["n_sim"]), src); add(f"ptNullFailed{k}", int(nl["n_failed"]), src)
        add(f"ptNullMax{k}", nl["null_quantiles"]["100%"], src); add(f"ptNullNinetyNine{k}", nl["null_quantiles"]["99%"], src)
        add(f"ptHOne{k}", "met" if d["H1"] else "not met", src); add(f"ptHOneAlt{k}", "met" if d["H1_alt"] else "not met", src)
        for c, v in f1["point"]["share_total"].items():
            add(f"ptShare{c.capitalize()}{k}", v, src + "; share of total incl. relation, D1")
        vc = f1["vc"]; L = 32
        add(f"explSdFactLayers{k}", math.sqrt(vc.get("fact", 0)) * L, "EXPLORATORY: sqrt(vc fact) x L=32, " + src, 2)
        add(f"explSdFtLayers{k}", math.sqrt(vc.get("ft", 0)) * L, "EXPLORATORY: sqrt(vc ft) x L=32, " + src, 2)
        add(f"explSdWordLayers{k}", math.sqrt(vc.get("rt", 0) + vc.get("frame", 0)) * L, "EXPLORATORY: sqrt(vc rt+frame) x L=32, " + src, 2)
        den = sum(vc.get(c, 0) for c in ("fact", "rt", "frame", "ft")) + (vc.get("fc", 0) + vc.get("Residual", 0)) / res["n_carriers_used"]
        add(f"explSysWordShare{k}", (vc.get("rt", 0) + vc.get("frame", 0)) / den, "EXPLORATORY: (rt+frame)/den, D1, " + src)
        add(f"explFtShare{k}", vc.get("ft", 0) / den, "EXPLORATORY: ft/den, D1, " + src)
    cl = dec["claims"]
    for key, name in [("H1_holds_(>=2_families)", "ptClaimHOne"), ("H1alt_holds_(>=2_families)", "ptClaimHOneAlt"),
                      ("model_dependent_(H1_and_H1alt_both_>=2_families)", "ptClaimModelDep"),
                      ("no_fixed_layer_(ICC1_D1_upper<0.15_in>=2_families)", "ptClaimNoFixedLayer"),
                      ("single_prompt_poor_(H1_and_nprime>=8_in>=2_families)", "ptClaimSinglePromptPoor"),
                      ("wording_shifts_together_(H1_and_tf>resid_in>=2_families)", "ptClaimWordingTogether"),
                      ("fact_depth_unexplained_(H1alt_in>=2_families)", "ptClaimFactUnexplained"),
                      ("fact_share_gt0_(null_p<0.01_in>=2_families)", "ptClaimFactShare")]:
        add(name, "licensed" if cl[key] else "not licensed", src)
    add("ptNFamiliesIncluded", len(dec["families"]["included_families"]), src)
    add("ptNFamiliesHOne", len(dec["families"]["H1"]), src)
    h3 = list(dec["H3"].values())[0]
    add("ptHThreeN", int(h3["n_facts"]), src); add("ptHThreeRho", h3["rho"], src)
    add("ptHThreeKbarLlama", h3["kbar"][0], src, 2); add("ptHThreeKbarOlmo", h3["kbar"][1], src, 2)
    add("ptHThreeGLlama", h3["G_kbar"][0], src); add("ptHThreeGOlmo", h3["G_kbar"][1], src)
    add("ptHThreeDisatt", h3["disattenuated_approx"], src)
    # sensitivities (preregistered, non-gating)
    SENS = {"New": "new226", "All": "all", "AllTen": "all10", "NoManu": "nomanufacturer", "Tcov": "tcov"}
    for sk, s in SENS.items():
        r = load(f"{PD}/{s}/p2_results.json")
        for k, mn in INC.items():
            m = r["models"][mn] if r else None
            ssrc = f"{PD}/{s}/p2_results.json (preregistered sensitivity, non-gating)"
            ok = m is not None and m.get("status") == "ok"
            add(f"ptSens{sk}NFacts{k}", int(m["n_facts"]) if ok else None, ssrc)
            for yk, y in (("DOne", "D1"), ("DFour", "D4")):
                f = m["fits"][y] if ok else None
                add(f"ptSens{sk}Icc{yk}{k}", f["point"]["icc1"] if f else None, ssrc)
                add(f"ptSens{sk}Diff{yk}{k}", f["point"]["diff"] if f else None, ssrc)
                add(f"ptSens{sk}Diff{yk}Lo{k}", f["boot"]["ci"]["diff"][0] if f else None, ssrc)
    lo = load(f"{PD}/lofo/p2_results.json")
    for k, mn in INC.items():
        lsrc = f"{PD}/lofo/p2_results.json (preregistered sensitivity, point estimates)"
        fits = lo["models"][mn]["fits"] if lo else {}
        for yk, y in (("DOne", "D1"), ("DFour", "D4")):
            for stat, nm in (("icc1", "Icc"), ("diff", "Diff")):
                v = [fits[x][y]["point"][stat] for x in fits if fits[x][y].get("status") == "ok"]
                add(f"ptLofo{nm}{yk}Min{k}", min(v) if v else None, lsrc); add(f"ptLofo{nm}{yk}Max{k}", max(v) if v else None, lsrc)

# ---------------------------------------------------------------- P2 null calibration (prereg section 4)
for ck, fn in {"FcOneNcThree": "null_fc1_nc3", "FcQuarterNcThree": "null_fc025_nc3", "FcOneNcTwo": "null_fc1_nc2",
               "Power": "power_icc010"}.items():
    c = load(f"results/P2null_calib/{fn}.json")
    csrc = f"results/P2null_calib/{fn}.json"
    add(f"ptCal{ck}RejOne", c["reject_p_lt_0.01"] if c else None, csrc)
    add(f"ptCal{ck}RejFive", c["reject_p_lt_0.05"] if c else None, csrc)
    add(f"ptCal{ck}N", int(c["n_ok"]) if c else None, csrc)

# ---------------------------------------------------------------- P2 robustness simulation (non-selecting)
rob = load("reports/p2/P2_robustsim_report.json")
RC = ["A_L24_nc3", "A_L24_nc2", "A_L36_nc3", "A_L36_nc2", "B_L24_nc3", "B_L24_nc2", "B_L36_nc3", "B_L36_nc2"]
CN = {"A": "A", "B": "B", "24": "TwentyFour", "36": "ThirtySix", "3": "Three", "2": "Two"}
for c in RC:
    t, l, n = c.split("_"); nm = CN[t] + "L" + CN[l[1:]] + "Nc" + CN[n[2:]]
    r = rob["conditions"].get(c) if rob else None
    rsrc = "reports/p2/P2_robustsim_report.json (non-selecting robustness simulation)" if r else "MISSING: robustness simulation not finished"
    for q, qn in (("icc1", "Icc"), ("diff", "Diff")):
        add(f"ptRob{nm}Cov{qn}", r["coverage"][q] if r else None, rsrc)
        add(f"ptRob{nm}Bias{qn}", r["bias"][q] if r else None, rsrc)
    add(f"ptRob{nm}DiffLoPos", r["rate_diff_lo_gt0"] if r else None, rsrc)
    add(f"ptRob{nm}N", int(r["n"]) if r else None, rsrc)

# ---------------------------------------------------------------- methods audit (EXPLORATORY)
C1 = "results/C1re/C1re-none-3cee850-20261120T141401Z/c1.json"
c1 = load(C1)
for k, mn in (("PyOneFour", "EleutherAI/pythia-1.4b"), ("PyTwoEight", "EleutherAI/pythia-2.8b")):
    t = c1["models"][mn]["resolved_equals_correct"] if c1 else None
    s = f"EXPLORATORY audit: {C1}"
    add(f"explAuditResCorr{k}", t["causal_final_resolved_and_correct"] if t else None, s)
    add(f"explAuditResWrong{k}", t["causal_final_resolved_not_correct"] if t else None, s)
    add(f"explAuditCensCorr{k}", t["causal_final_censored_and_correct"] if t else None, s)
    add(f"explAuditCensWrong{k}", t["causal_final_censored_not_correct"] if t else None, s)

# ---------------------------------------------------------------- write
OUT.parent.mkdir(exist_ok=True)
lines = ["% GENERATED by scripts/make_numbers.py from results files only. Never edit by hand.",
         "% inputs: " + json.dumps(INPUTS, sort_keys=True)]
for name, val, src in M:
    lines.append(f"\\newcommand{{\\{name}}}{{{val}}} % {src}")
OUT.write_text("\n".join(lines) + "\n")
nmiss = sum(1 for _, v, _ in M if v == "MISSING")
print(f"wrote {OUT.relative_to(ROOT)}: {len(M)} macros, {nmiss} MISSING, {len(INPUTS)} inputs")
sys.exit(0)
