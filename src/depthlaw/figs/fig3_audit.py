"""Figure 3 (methods; EXPLORATORY audit example): reads results/G5expl/expl.json only.
One fact in Pythia-1.4B (the first fact id whose template 0 is answered correctly and template 1 is not), final-token
patch into the carriers. Left: carrier-mean patched probability of the object's first token, as a fraction of its
final-layer value, with the half-probability threshold (D1). Right: median rank of the object's first token; rank-1
onset exists only for the correct prompt. Writes <out>/fig3_audit.{pdf,png,json}.
Usage: python -m depthlaw.figs.fig3_audit <out_dir>"""
import json, pathlib, sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
SRC = ROOT / "results/G5expl/expl.json"
INK, INK2, GRID = "#191919", "#666666", "#e5e5e5"
COL = {True: "#257de0", False: "#f47230"}


def main(out):
    out = pathlib.Path(out); out.mkdir(parents=True, exist_ok=True)
    ex = json.loads(SRC.read_text())["study1"]["audit_example"]
    L = ex["L"]; layers = np.arange(1, L + 1)
    plt.rcParams.update({"font.size": 7.5, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2,
                         "ytick.color": INK2, "font.family": "serif"})
    fig, ax = plt.subplots(1, 2, figsize=(3.3, 1.45), gridspec_kw={"wspace": 0.45})
    plotted = []
    for c in ex["curves"]:
        p = np.array(c["p_mean"]); r = np.array(c["rank_median"])
        lab = f"template {c['template_id']} ({'correct' if c['correct'] else 'wrong'})"
        ax[0].plot(layers, p / p[-1], color=COL[c["correct"]], lw=1.6, label=lab)
        ax[1].plot(layers, r, color=COL[c["correct"]], lw=1.6)
        d1 = c["d1"] * L
        ax[0].axvline(d1, color=COL[c["correct"]], lw=0.8, ls=":")
        plotted.append({"template_id": c["template_id"], "correct": c["correct"], "d1_layers": d1,
                        "rank1_onset_layers": None if c["rank1_onset"] is None else c["rank1_onset"] * L,
                        "p_over_final": (p / p[-1]).tolist(), "rank_median": r.tolist()})
    ax[0].axhline(0.5, color=INK2, lw=0.7, ls="--")
    ax[0].set_ylabel("$p(l)/p(L)$", fontsize=7); ax[0].set_xlabel("layer", fontsize=7)
    ax[1].set_yscale("log"); ax[1].axhline(1, color=INK2, lw=0.7, ls="--")
    ax[1].set_ylabel("rank (median)", fontsize=7); ax[1].set_xlabel("layer", fontsize=7)
    for a in ax:
        a.grid(color=GRID, lw=0.5); a.set_axisbelow(True)
        for s in ("top", "right"):
            a.spines[s].set_visible(False)
        a.tick_params(length=2, labelsize=6.5)
    ax[0].legend(fontsize=5.8, frameon=False, loc="lower right", handlelength=1.2)
    for ext in ("pdf", "png"):
        fig.savefig(out / f"fig3_audit.{ext}", bbox_inches="tight", dpi=300)
    (out / "fig3_audit.json").write_text(json.dumps({"source": str(SRC.relative_to(ROOT)), "status": "EXPLORATORY",
                                                     "model": ex["model"], "fact_id": ex["fact_id"], "subject": ex["subject"],
                                                     "object": ex["object"], "templates": ex["templates"], "L": L,
                                                     "curves": plotted}, indent=1))
    print("wrote", out / "fig3_audit.pdf")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else str(ROOT / "paper/figs"))
