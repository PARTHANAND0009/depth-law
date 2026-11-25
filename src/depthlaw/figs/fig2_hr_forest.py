"""Figure 2 (Study 1, H-R prereg): reads results/HR_gate.json only.
Left: covariate-adjusted relation share ICC_rel with relation-cluster bootstrap 95% CI per model, against the H1
threshold (ICC_rel >= 0.30 with CI lower bound >= 0.15). Right: change in marginal R^2 from adding
within-relation log co-occurrence (EXACT counts), with 95% CI, against the H3 bound (upper CI < 0.02).
Writes <out>/fig2_hr_forest.{pdf,png,json}. Usage: python -m depthlaw.figs.fig2_hr_forest <out_dir>"""
import json, pathlib, sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = pathlib.Path(__file__).resolve().parents[3]
SRC = ROOT / "results/HR_gate.json"
MODELS = [("EleutherAI/pythia-1.4b", "Pythia-1.4B"), ("EleutherAI/pythia-2.8b", "Pythia-2.8B"),
          ("allenai/OLMo-2-1124-7B", "OLMo-2-7B")]
INK, INK2, GRID, MARK, REF = "#191919", "#666666", "#e5e5e5", "#257de0", "#f47230"


def main(out):
    out = pathlib.Path(out); out.mkdir(parents=True, exist_ok=True)
    h = json.loads(SRC.read_text()); T = h["thresholds"]
    rows = []
    for key, label in MODELS:
        m = h["models"][key]
        rows.append({"model": label, "icc": m["main"]["icc_rel"], "icc_ci": m["boot"]["icc_ci"],
                     "dr2": m["main"]["dr2"], "dr2_ci": m["boot"]["dr2_ci"], "n_rows": m["main"]["n_rows"],
                     "n_boot": m["boot"]["n_boot"]})
    plt.rcParams.update({"font.size": 8, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2,
                         "ytick.color": INK2, "font.family": "serif"})
    fig, ax = plt.subplots(1, 2, figsize=(3.3, 1.45), sharey=True, gridspec_kw={"wspace": 0.12})
    ys = list(range(len(rows)))[::-1]
    for a, k, thr, lab, xmax in ((ax[0], "icc", T["icc"], "relation share ICC$_{rel}$", 0.35),
                                 (ax[1], "dr2", T["dr2_hi"], r"$\Delta R^2_m$ (co-occurrence)", 0.024)):
        a.axvline(thr, color=REF, lw=1, ls="--", zorder=1)
        a.axvline(0, color=GRID, lw=1, zorder=0)
        for y, r in zip(ys, rows):
            lo, hi = r[f"{k}_ci"]
            a.plot([lo, hi], [y, y], color=MARK, lw=2, solid_capstyle="round", zorder=2)
            a.plot(r[k], y, "o", ms=4.5, color=MARK, mec="white", mew=1, zorder=3)
        a.set_xlabel(lab, fontsize=7.5)
        a.set_xlim(-0.03 * xmax / 0.35 if k == "icc" else -0.005, xmax)
        a.grid(axis="x", color=GRID, lw=0.5); a.set_axisbelow(True)
        for s in ("top", "right"):
            a.spines[s].set_visible(False)
        a.tick_params(length=2, labelsize=7)
    ax[0].text(T["icc"], len(rows) - 0.45, "H1 threshold ", color=INK2, fontsize=6, ha="right", va="bottom")
    ax[1].text(T["dr2_hi"], len(rows) - 0.45, "H3 bound ", color=INK2, fontsize=6, ha="right", va="bottom")
    ax[0].set_yticks(ys); ax[0].set_yticklabels([r["model"] for r in rows])
    ax[0].set_ylim(-0.6, len(rows) - 0.1)
    for ext in ("pdf", "png"):
        fig.savefig(out / f"fig2_hr_forest.{ext}", bbox_inches="tight", dpi=300)
    (out / "fig2_hr_forest.json").write_text(json.dumps({"source": str(SRC.relative_to(ROOT)), "thresholds":
                                                         {"icc": T["icc"], "icc_lo": T["icc_lo"], "dr2_hi": T["dr2_hi"]},
                                                         "rows": rows}, indent=1))
    print("wrote", out / "fig2_hr_forest.pdf")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else str(ROOT / "paper/figs"))
