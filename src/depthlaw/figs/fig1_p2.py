"""Figure 1 (P2): reads results files only.
Left: per-fact readout depth D1 (in layers) across the 10 designed paraphrases for 40 facts, Llama-3.1-8B and
OLMo-2-1124-7B side by side (same facts, same order). Right: D1 variance shares within relation (stacked) per
model, with the D-study curve G(k) as an inset.
Inputs: results/P2analysis/correct/long_<model>_correct.csv, fit_<model>_correct_D1.json, p2_results.json.
Fact selection (deterministic, fixed before plotting): facts included in both models' `correct` set; per
relation the 2 facts with the most paraphrases correct in both models (ties: fact_id); 20 relations x 2 = 40.
Points: carrier-averaged D1 per (fact, paraphrase), in layers (D1 x L). Facts ordered by their mean over both models.
Shares: fact, rt + frame, ft, (fc + e)/nc over den (prereg section 4 definitions). Splitting the wording share
into (rt + frame) and ft is EXPLORATORY (not preregistered); ICC(1) = fact/den and wording = (rt + frame + ft)/den
are preregistered. Usage: python -m depthlaw.figs.fig1_p2 <out_dir>"""
import json, pathlib, sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[3]
D = ROOT / "results/P2analysis/correct"
MODELS = [("Llama-3.1-8B", "meta-llama/Llama-3.1-8B"), ("OLMo-2-1124-7B", "allenai/OLMo-2-1124-7B")]
L = {"Llama-3.1-8B": 32, "OLMo-2-1124-7B": 32}
INK, INK2, GRID = "#191919", "#666666", "#e5e5e5"
SEG = [("fact", "#257de0"), ("wording: rt + frame", "#f47230"), ("wording: fact × paraphrase", "#00b894"),
       ("carrier-level", "#f2a600")]


def main(out):
    out = pathlib.Path(out); out.mkdir(parents=True, exist_ok=True)
    res = json.loads((D / "p2_results.json").read_text())
    nc = res["n_carriers_used"]
    cells = {}
    for short, _ in MODELS:
        d = pd.read_csv(D / f"long_{short}_correct.csv")
        assert (d["D1"] * L[short] - (d["D1"] * L[short]).round()).abs().max() < 1e-6  # D1 on the (l+1)/L grid
        c = d.groupby(["fact_id", "relation", "template_id"], as_index=False)["D1"].mean()
        c["layer"] = c["D1"] * L[short]
        cells[short] = c
    a, b = cells["Llama-3.1-8B"], cells["OLMo-2-1124-7B"]
    na = a.groupby("fact_id").size().rename("na"); nb = b.groupby("fact_id").size().rename("nb")
    both = pd.concat([na, nb], axis=1, join="inner").reset_index()
    rel = a[["fact_id", "relation"]].drop_duplicates().set_index("fact_id")["relation"]
    both["relation"] = both["fact_id"].map(rel); both["nmin"] = both[["na", "nb"]].min(axis=1)
    srt = both.sort_values(["relation", "nmin", "fact_id"], ascending=[True, False, True])
    pick = srt.groupby("relation").head(2)["fact_id"].tolist()
    if len(pick) < 40:  # a relation with < 2 shared facts: fill from the rest by nmin, then fact_id
        rest = srt[~srt.fact_id.isin(pick)].sort_values(["nmin", "fact_id"], ascending=[False, True])
        pick += rest["fact_id"].head(40 - len(pick)).tolist()
    mean_both = pd.concat([a[a.fact_id.isin(pick)], b[b.fact_id.isin(pick)]]).groupby("fact_id")["layer"].mean()
    order = mean_both.sort_values().index.tolist()
    xpos = {f: i for i, f in enumerate(order)}

    shares, Gk = {}, {}
    for short, _ in MODELS:
        f = json.loads((D / f"fit_{short}_correct_D1.json").read_text())
        v = f["vc"]; g = lambda k: v.get(k, 0.0)
        den = g("fact") + g("rt") + g("frame") + g("ft") + (g("fc") + g("Residual")) / nc
        shares[short] = [g("fact") / den, (g("rt") + g("frame")) / den, g("ft") / den, (g("fc") + g("Residual")) / nc / den]
        assert abs(shares[short][0] - f["point"]["icc1"]) < 1e-9
        Gk[short] = {"k": list(range(1, 13)), "G": f["point"]["G_k"][:12], "nprime": f["point"]["nprime_G"],
                     "icc1": f["point"]["icc1"], "icc1_ci": f["boot"]["ci"]["icc1"]}

    plt.rcParams.update({"font.size": 8, "font.family": "DejaVu Sans", "axes.edgecolor": INK2, "axes.labelcolor": INK,
                         "xtick.color": INK2, "ytick.color": INK2, "axes.linewidth": 0.6})
    fig = plt.figure(figsize=(7.0, 2.9))
    gs = fig.add_gridspec(2, 3, width_ratios=[1, 1, 1.05], height_ratios=[1, 1], wspace=0.3, hspace=0.95,
                          left=0.065, right=0.985, top=0.86, bottom=0.15)
    plotted = {"facts": order, "points": {}, "shares": shares, "G_k": Gk}
    ylim = (min(c["layer"].min() for c in cells.values()) - 1, max(c["layer"].max() for c in cells.values()) + 1)
    for j, (short, _) in enumerate(MODELS):
        ax = fig.add_subplot(gs[:, j])
        c = cells[short][cells[short].fact_id.isin(order)].copy(); c["x"] = c["fact_id"].map(xpos)
        ax.scatter(c["x"], c["layer"], s=7, color="#257de0", alpha=0.55, linewidths=0, zorder=3)
        m = c.groupby("x")["layer"].mean()
        ax.scatter(m.index, m.values, marker="_", s=40, color=INK, linewidths=1.2, zorder=4)
        ax.set_xlim(-1, len(order)); ax.set_ylim(*ylim)
        ax.set_xticks([]); ax.set_xlabel(f"{len(order)} facts (same order in both panels)", color=INK2)
        ax.set_title(short, color=INK, fontsize=8.5, loc="left")
        ax.grid(axis="y", color=GRID, linewidth=0.5); ax.set_axisbelow(True)
        for s in ("top", "right"): ax.spines[s].set_visible(False)
        if j == 0:
            ax.set_ylabel("readout depth D1 (layer)")
        plotted["points"][short] = c[["fact_id", "template_id", "layer"]].to_dict(orient="list")
    fig.text(0.06, 0.95, "dots: one paraphrase (mean over 3 carriers); bar: fact mean", color=INK2, fontsize=7)

    ax = fig.add_subplot(gs[0, 2])
    ys = [1, 0]
    for y, (short, _) in zip(ys, MODELS):
        left = 0.0
        for (lab, col), v in zip(SEG, shares[short]):
            ax.barh(y, v - 0.006, left=left, height=0.5, color=col, edgecolor="none")
            if v > 0.06:
                ax.text(left + v / 2, y, f"{v:.2f}", ha="center", va="center", fontsize=6.5, color=INK)
            left += v
    ax.set_yticks(ys); ax.set_yticklabels([s.split("-")[0] for s, _ in MODELS], fontsize=7)
    ax.set_xlim(0, 1); ax.set_ylim(-0.45, 1.45); ax.set_xlabel("share of within-relation D1 variance", labelpad=1)
    for s in ("top", "right", "left"): ax.spines[s].set_visible(False)
    ax.tick_params(axis="y", length=0)
    h = [plt.Rectangle((0, 0), 1, 1, color=col) for _, col in SEG]
    ax.legend(h, ["fact", "wording: rt + frame", "wording: fact × para.", "carrier-level"], loc="lower center",
              bbox_to_anchor=(0.45, 1.0), ncol=2, fontsize=6, frameon=False, handlelength=1, columnspacing=0.8)
    ins = fig.add_subplot(gs[1, 2])
    for (short, _), ls in zip(MODELS, ("-", "--")):
        ins.plot(Gk[short]["k"], Gk[short]["G"], ls, color=INK, linewidth=1.0)
        npr = Gk[short]["nprime"]
        ins.plot([npr], [Gk[short]["G"][npr - 1]], "o", color=INK, markersize=3)
        ins.text(12.4, Gk[short]["G"][-1] + (0.04 if short.startswith("OLMo") else -0.06), short.split("-")[0],
                 fontsize=6, va="center", color=INK)
    ins.axhline(0.8, color=INK2, linewidth=0.6, linestyle=":")
    ins.set_xlim(1, 15.5); ins.set_ylim(0.3, 1); ins.set_xticks([1, 4, 8, 12]); ins.set_yticks([0.4, 0.6, 0.8, 1.0])
    ins.tick_params(labelsize=6, length=2); ins.set_xlabel("paraphrases k (D-study)", fontsize=6.5, labelpad=1)
    ins.set_ylabel("G(k)", fontsize=6.5, labelpad=1)
    ins.grid(axis="y", color=GRID, linewidth=0.5); ins.set_axisbelow(True)
    for s in ("top", "right"): ins.spines[s].set_visible(False)

    for ext in ("pdf", "png"):
        fig.savefig(out / f"fig1_p2.{ext}", dpi=300)
    (out / "fig1_p2.json").write_text(json.dumps(plotted, indent=1, default=float))
    print("wrote", out / "fig1_p2.pdf")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else str(ROOT / "paper/figs"))
