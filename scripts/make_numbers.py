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
    # derived summaries over the three models (point-estimate min / max; max of upper bounds)
    ms = [hr["models"][m] for m in HRM.values()]
    add("hrIccMin", min(m["main"]["icc_rel"] for m in ms), src + "; min over 3 models")
    add("hrIccMax", max(m["main"]["icc_rel"] for m in ms), src + "; max over 3 models")
    add("hrIccHiMax", max(m["boot"]["icc_ci"][1] for m in ms), src + "; max upper bound over 3 models")
    add("hrDRsqMax", max(m["main"]["dr2"] for m in ms), src + "; max over 3 models", 4)
    add("hrDRsqHiMax", max(m["boot"]["dr2_ci"][1] for m in ms), src + "; max upper bound over 3 models", 4)
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
    iccs = [res["models"][mn]["fits"][y]["point"]["icc1"] for mn in INC.values() for y in ("D1", "D4")]
    words = [res["models"][mn]["fits"][y]["point"]["wording"] for mn in INC.values() for y in ("D1", "D4")]
    add("ptIccRangeLo", min(iccs), src + "; min over 2 models x D1/D4"); add("ptIccRangeHi", max(iccs), src + "; max over 2 models x D1/D4")
    add("ptWordingRangeLo", min(words), src + "; min over 2 models x D1/D4"); add("ptWordingRangeHi", max(words), src + "; max over 2 models x D1/D4")
    add("ptNullRatioMin", min(res["models"][mn]["null"]["observed"] / res["models"][mn]["null"]["null_quantiles"]["100%"]
                              for mn in INC.values()), src + "; min over models of observed ICC(1) / null maximum", 1)
    add("ptNPreregModels", len(P2M), "prereg/P2_prompt_vs_fact.md: five preregistered models")
    add("ptNFacts", sum(1 for _ in (ROOT / "materials/facts_v1.jsonl").open()), "materials/facts_v1.jsonl (line count)")
    add("ptNFrames", 10, "prereg/P2_prompt_vs_fact.md: 10 designed frames per relation")
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
    # derived (G5): range of the D1 fact share over every sensitivity set and both included models (for prose)
    vals = [float(v) for n, v, _ in M if n.startswith(("ptSens", "ptLofo")) and "IccDOne" in n and v != "MISSING"]
    dsrc = "derived from the ptSens*/ptLofo* IccDOne macros (range over all sensitivity sets and both models)"
    add("ptSensIccDOneMin", min(vals) if vals else None, dsrc); add("ptSensIccDOneMax", max(vals) if vals else None, dsrc)

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
# derived ranges over the 8 conditions (for prose)
rcs = [rob["conditions"][c] for c in RC if rob and rob["conditions"].get(c) and rob["conditions"][c]["n"]] if rob else []
rsrc = ("reports/p2/P2_robustsim_report.json (derived: range over 8 conditions)" if len(rcs) == len(RC)
        else "MISSING: robustness simulation not finished")
for nm, f in (("CovIcc", lambda r: r["coverage"]["icc1"]), ("CovDiff", lambda r: r["coverage"]["diff"]),
              ("BiasIcc", lambda r: r["bias"]["icc1"]), ("DiffLoPos", lambda r: r["rate_diff_lo_gt0"])):
    ok = len(rcs) == len(RC)
    add(f"ptRob{nm}Min", min(f(r) for r in rcs) if ok else None, rsrc)
    add(f"ptRob{nm}Max", max(f(r) for r in rcs) if ok else None, rsrc)
add("ptRobIccMissAbove", sum(r["miss_above"]["icc1"] for r in rcs) if len(rcs) == len(RC) else None, rsrc)
add("ptRobIccMissBelow", sum(r["miss_below"]["icc1"] for r in rcs) if len(rcs) == len(RC) else None, rsrc)
add("ptRobNTotal", sum(int(r["n"]) for r in rcs) if len(rcs) == len(RC) else None, rsrc)

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

# ---------------------------------------------------------------- design constants and preregistered thresholds (G5)
# HR thresholds are read from HR_gate.json (written by the frozen analysis). P2 rule constants are taken from the
# frozen prereg text: each value is asserted to occur in the quoted sentence of prereg/P2_prompt_vs_fact.md.
if hr:
    T = hr["thresholds"]
    for k, nm, nd in (("icc", "Icc", 2), ("icc_lo", "IccLo", 2), ("rho", "Rho", 1), ("perm_p", "PermP", 2),
                      ("prho", "PRho", 1), ("prho_lo", "PRhoLo", 1), ("rho_gap", "RhoGap", 2), ("dr2_hi", "DRsqHi", 2)):
        add(f"hrThr{nm}", float(T[k]), f"{HRF} thresholds.{k} (prereg/HR_revised.md, frozen)", nd=nd)
PREREG_P2 = "prereg/P2_prompt_vs_fact.md"
p2txt = (ROOT / PREREG_P2).read_text()
INPUTS[PREREG_P2] = hashlib.sha256(p2txt.encode()).hexdigest()
for nm, val, quote in (("ptRuleMinFacts", 150, "≥ 150 of the 300 facts have ≥ 2 correct paraphrases"),
                       ("ptRuleMinCorrect", 2, "≥ 150 of the 300 facts have ≥ 2 correct paraphrases"),
                       ("ptRuleMinRel", 15, "those facts cover ≥ 15 of the 20 relations"),
                       ("ptNRelations", 20, "those facts cover ≥ 15 of the 20 relations"),
                       ("ptRuleG", "0.8", "n′ = min k with G(k) ≥ 0.8"),
                       ("ptRuleNoNprimeK", 30, "If G(k) < 0.8 for every k ≤ 30"),
                       ("ptRuleHalf", "0.5", "p(l') ≥ 0.5·p(L−1)"),
                       ("ptRuleNBootNull", 1000, "uses 1000 bootstrap resamples and 1000 null datasets")):
    assert quote in p2txt, (nm, quote)
    add(nm, val, f"{PREREG_P2} (frozen): \"{quote}\"", raw=isinstance(val, str))
# layer counts of the P2 models, from each run's start event (results/P2/<run>/log.jsonl)
for k, run in (("Llama", "results/P2/P2-Llama-3.1-8B-ff119ca-20261124T164743Z"),
               ("Olmo", "results/P2/P2-OLMo-2-1124-7B-ff119ca-20261124T171447Z")):
    lf = ROOT / run / "log.jsonl"
    INPUTS[f"{run}/log.jsonl"] = hashlib.sha256(lf.read_bytes()).hexdigest()
    start = next(json.loads(l) for l in lf.read_text().splitlines() if '"event": "start"' in l)
    add(f"ptNLayers{k}", int(start["n_layers"]), f"{run}/log.jsonl start event n_layers")
# H-R design (asserted in the frozen prereg, section C)
hrtxt = (ROOT / "prereg/HR_revised.md").read_text()
INPUTS["prereg/HR_revised.md"] = hashlib.sha256(hrtxt.encode()).hexdigest()
for nm, val, quote in (("hrNFacts", 1300, "1300 facts = 26 relations × 50"), ("hrNRelations", 26, "1300 facts = 26 relations × 50"),
                       ("hrNPerRelation", 50, "1300 facts = 26 relations × 50"),
                       ("hrNBootRel", 2000, "2000 relation-cluster resamples")):
    assert quote in hrtxt, (nm, quote)
    add(nm, val, f"prereg/HR_revised.md (frozen): \"{quote}\"")
for nm, val, quote in (("ptCiLevel", 95, "1000 resamples, 95% percentile intervals"),
                       ("ptSeed", "20261121", "**Seed:** 20261121 everywhere"),
                       ("ptRuleNoFixedHi", "0.15", "condition: ICC(1) upper 95% CI < 0.15, under D1"),
                       ("ptRuleNprimeMin", 8, "n′ is defined and ≥ 8"),
                       ("ptRuleAltIcc", "0.5", "ICC(1) ≥ 0.5 with lower 95% CI ≥ 0.4"),
                       ("ptRuleAltIccLo", "0.4", "ICC(1) ≥ 0.5 with lower 95% CI ≥ 0.4"),
                       ("ptRuleNullP", "0.01", "accepted for a model only if p < 0.01"),
                       ("ptRuleMinFamilies", 2, "a claim needs ≥ 2 model families")):
    assert quote in p2txt, (nm, quote)
    add(nm, val, f"{PREREG_P2} (frozen): \"{quote}\"", raw=isinstance(val, str))
# CI-method selection simulation v2 (prereg section 4; reports/p2/P2_bootsim_v2_report.json)
bs2 = load("reports/p2/P2_bootsim_v2_report.json")
for ck, cn in (("edepthvar_like", "Ed"), ("fact_dominant", "Fd")):
    c = bs2["summary"][ck] if bs2 else None
    s = "reports/p2/P2_bootsim_v2_report.json (CI-method selection, v2)"
    add(f"ptBsTwo{cn}CovIcc", c["icc1"]["coverage_n95"] if c else None, s)
    add(f"ptBsTwo{cn}CovDiff", c["diff"]["coverage_n95"] if c else None, s)
    add(f"ptBsTwo{cn}N", int(c["n_ok"]) if c else None, s)
# robustness-simulation settings
if rob:
    add("ptRobNSim", int(rob["settings"]["n_sim"]), "reports/p2/P2_robustsim_report.json settings")
    add("ptRobNBoot", int(rob["settings"]["n_boot"]), "reports/p2/P2_robustsim_report.json settings")

# ---------------------------------------------------------------- integrity appendix (results/integrity/summary.json)
INTF = "results/integrity/summary.json"
ig = load(INTF)
isrc = f"{INTF} (scripts/integrity_summary.py via log_run)"
if ig:
    pr = {p["id"]: p for p in ig["preregistrations"]}
    add("intHrCommit", pr["H-R"]["freeze_commit"][:7], isrc, raw=True)
    add("intHrSha", pr["H-R"]["sha256_now"][:16], isrc, raw=True)
    add("intPtCommit", pr["P2"]["freeze_commit"][:7], isrc, raw=True)
    add("intPtSha", pr["P2"]["sha256_now"][:16], isrc, raw=True)
    lg = ig["ledger"]
    for k, nm in (("entries", "Entries"), ("runs", "Runs"), ("notes", "Notes"), ("runs_confirmatory", "RunsConf"),
                  ("runs_exploratory", "RunsExpl"), ("runs_nonzero_exit", "RunsFailed"),
                  ("runs_frozen_violation", "RunsFrozenViol"), ("notes_s5_relaunch", "SRelaunch")):
        add(f"intLedger{nm}", int(lg[k]), isrc)
    gt = ig["guard_tests"]
    add("intTestPyPass", gt[0]["passed"], isrc); add("intTestPyFail", gt[0]["failed"], isrc)
    add("intTestHookNewPass", gt[1]["passed"], isrc); add("intTestHookNewFail", gt[1]["failed"], isrc)
    add("intTestHookKillPass", gt[2]["passed"], isrc); add("intTestHookKillFail", gt[2]["failed"], isrc)
    add("intTestHookOldPass", gt[3]["passed"], isrc); add("intTestHookOldFail", gt[3]["failed"], isrc)
    add("intNFrozenFiles", ig["immutable_attribute"]["frozen_files"], isrc)
    add("intNReviews", len(ig["reviews"]), isrc)
    add("intNDeviations", len(ig["deviations"]), isrc)

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
