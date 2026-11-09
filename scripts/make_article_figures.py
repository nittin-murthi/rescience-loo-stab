"""Figures made for the ReScience article (article/content.tex). Inputs: results/raw/*.csv, the authors' published
result files (data/authors_results/ and data/authors_supplement/, diagnosis only), the paper's Table 2 / Table 4 values (transcribed below from
arXiv:2504.12189v1 App. G.2 and G.4) and results/nn_paper_digitised.md. Output: figures/article_*.pdf."""
from pathlib import Path
import re
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
RAW, FIG = ROOT / "results" / "raw", ROOT / "figures"
METHODS = ["OracleCP", "FullCP", "SplitCP", "RO-StabCP", "LOO-StabCP"]
C_TEXT, C_AUTH, C_ORIG = "#1b9e77", "#d95f02", "black"
plt.rcParams.update({"font.size": 8, "axes.titlesize": 9, "legend.fontsize": 7.5, "figure.dpi": 150})

# [App. G.2, Table 2] mean lengths
PAPER_T2 = {
    ("linear", "rlm"): [3.272, 3.300, 3.455, 3.442, 3.442],
    ("linear", "sgd"): [3.252, 3.300, 3.420, 3.464, 3.405],
    ("nonlinear", "rlm"): [3.659, 3.690, 3.812, 3.828, 3.827],
    ("nonlinear", "sgd"): [3.641, 3.690, 3.855, 3.849, 3.789],
}
# [App. G.4, Table 4] mean FDP and power
PAPER_T4 = {"cfBH": ([0.0928, 0.2000, 0.2882], [0.6319, 0.9277, 0.9923]),
            "RO-cfBH": ([0.0038, 0.0602, 0.2483], [0.3041, 0.6522, 0.9627]),
            "LOO-cfBH": ([0.0657, 0.1836, 0.2837], [0.6744, 0.9430, 0.9917])}


def mean_se(d, keys):
    g = d.groupby(keys).length.agg(["mean", "std", "count"])
    g["se"] = g["std"] / np.sqrt(g["count"])
    return g


def dotpanel(ax, rows, title, log=False):
    y = np.arange(len(METHODS))[::-1]
    for k, (lab, vals, ses, col, mk, off) in enumerate(rows):
        ax.errorbar(vals, y + off, xerr=None if ses is None else 2 * np.asarray(ses), fmt=mk, color=col,
                    ms=4.5, capsize=2, lw=1, label=lab, mfc=col if mk != "D" else "white")
    ax.set_yticks(y, METHODS)
    ax.set_title(title)
    ax.grid(axis="x", lw=0.3, alpha=0.6)
    if log:
        ax.set_xscale("log")


def fig_simulation():
    t, a = pd.read_csv(RAW / "sim.csv"), pd.read_csv(RAW / "sim_authors.csv")
    gt, ga = mean_se(t, ["setting", "model", "method"]), mean_se(a, ["setting", "model", "method"])
    fig, axs = plt.subplots(2, 2, figsize=(7.2, 4.4), sharey=True)
    for ax, (s, m) in zip(axs.flat, PAPER_T2):
        f = lambda g, c: [g.loc[(s, m, me), c] for me in METHODS]
        dotpanel(ax, [("Replication: text setup", f(gt, "mean"), f(gt, "se"), C_TEXT, "o", 0.2),
                      ("Replication: authors' setup", f(ga, "mean"), f(ga, "se"), C_AUTH, "s", 0.0),
                      ("Original (Table 2)", PAPER_T2[(s, m)], None, C_ORIG, "D", -0.2)],
                 f"{s} model, {m.upper()}", log=True)
        ax.set_xlim(2.5, 200)
        ax.set_xticks([3, 5, 10, 20, 50, 100], ["3", "5", "10", "20", "50", "100"])
    for ax in axs[1]:
        ax.set_xlabel("mean interval length (log scale)")
    h, l = axs[0, 0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=3, frameon=False)
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    fig.savefig(FIG / "article_sim_setups.pdf")


def fig_real():
    t, a = pd.read_csv(RAW / "real.csv"), pd.read_csv(RAW / "real_authors.csv")
    t, a = t[t.m == 100], a[a.m == 100]
    au = pd.read_csv(ROOT / "data" / "authors_results" / "results_real.csv")
    au = au[au.m == 100].rename(columns={"Length": "length"})
    gt, ga = mean_se(t, ["data", "model", "method"]), mean_se(a, ["data", "model", "method"])
    gf = mean_se(au, ["Dataset", "Algorithm", "Method"])
    fig, axs = plt.subplots(2, 2, figsize=(7.2, 4.4), sharey=True)
    for ax, (d, m) in zip(axs.flat, [("boston", "rlm"), ("boston", "sgd"), ("diabetes", "rlm"), ("diabetes", "sgd")]):
        f = lambda g, c, key: [g.loc[key + (me,), c] for me in METHODS]
        k2 = (d.capitalize(), m.upper())
        dotpanel(ax, [("Replication: text setup", f(gt, "mean", (d, m)), f(gt, "se", (d, m)), C_TEXT, "o", 0.2),
                      ("Replication: authors' setup", f(ga, "mean", (d, m)), f(ga, "se", (d, m)), C_AUTH, "s", 0.0),
                      ("Authors' result file", f(gf, "mean", k2), f(gf, "se", k2), C_ORIG, "D", -0.2)],
                 f"{d.capitalize()}, {m.upper()}, m = 100")
    for ax in axs[1]:
        ax.set_xlabel("mean interval length")
    h, l = axs[0, 0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=3, frameon=False)
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    fig.savefig(FIG / "article_real_setups.pdf")


def fig_nn():
    a = pd.read_csv(RAW / "nn_authors.csv")
    dig = {}
    for line in (ROOT / "results" / "nn_paper_digitised.md").read_text().splitlines():
        if line.startswith("| rev_"):
            c = [x.strip() for x in line.strip("|").split("|")]
            hid = "(20,)" if "1layer" in c[0] else "(10, 5)"
            dig[(hid, c[2].lower(), c[3])] = tuple(float(v) for v in c[4:7])
    # [FROM AUTHORS' SUPPLEMENT: code_final/result/results_nn.csv] (the (10, 5) run of App. A.2 Fig. 6; see
    # results/supplement_comparison.md); the one-layer run of Fig. 3 has no raw numbers, so we show the digitised values
    F = pd.read_csv(ROOT / "data" / "authors_supplement" / "code_final" / "result" / "results_nn.csv")
    meths = ["SplitCP", "RO-StabCP", "LOO-StabCP"]
    cols = ["#66c2a5", "#fc8d62", "#8da0cb"]
    fig, axs = plt.subplots(1, 4, figsize=(7.2, 2.7))
    for ax, (hid, d) in zip(axs, [("(20,)", "boston"), ("(20,)", "diabetes"), ("(10, 5)", "boston"), ("(10, 5)", "diabetes")]):
        data = [a[(a.hidden == hid) & (a.data == d) & (a.method == me)].length.values for me in meths]
        bp = ax.boxplot(data, positions=[0, 1, 2], widths=0.5, patch_artist=True, showfliers=False,
                        medianprops={"color": "k"})
        for p, c in zip(bp["boxes"], cols):
            p.set_facecolor(c)
        for i, me in enumerate(meths):
            if hid == "(10, 5)":
                v = F[(F.Dataset == d.capitalize()) & (F.Method == me)].Length
                q1, med, q3 = v.quantile(0.25), v.median(), v.quantile(0.75)
                ax.errorbar(i + 0.38, med, yerr=[[med - q1], [q3 - med]], fmt="s", color="k", mfc="k", ms=4,
                            capsize=2, lw=1, label="Supplement result file (median, IQR)" if i == 0 else None)
            else:
                q1, med, q3 = dig[(hid, d, me)]
                ax.errorbar(i + 0.38, med, yerr=[[med - q1], [q3 - med]], fmt="D", color="k", mfc="white", ms=4,
                            capsize=2, lw=1, label="Original Fig. 3 (digitised median, IQR)" if i == 0 else None)
        ax.set_xticks([0, 1, 2], ["Split", "RO", "LOO"])
        ax.set_title(f"{d.capitalize()}, hidden {hid}")
        ax.grid(axis="y", lw=0.3, alpha=0.6)
    axs[0].set_ylabel("interval length")
    h, l = axs[0].get_legend_handles_labels()
    h2, l2 = axs[2].get_legend_handles_labels()
    h, l = h + h2, l + l2
    from matplotlib.patches import Patch
    h = [Patch(fc="#cccccc", ec="k")] + h
    l = ["Replication: authors' setup (box: median, IQR; whiskers 1.5 IQR)"] + l
    fig.legend(h, l, loc="lower center", ncol=2, frameon=False)
    fig.tight_layout(rect=(0, 0.14, 1, 1))
    fig.savefig(FIG / "article_nn.pdf")


def fig_screen():
    qs = [0.1, 0.2, 0.3]
    var = [("screen", "Replication: text setup", C_TEXT, "o", "-"),
           ("screen_authors", "Replication: authors' setup", C_AUTH, "s", "-"),
           ("screen_authors_fixtau", "Replication: authors' setup, bound with R", "#7570b3", "^", "--")]
    fig, axs = plt.subplots(1, 3, figsize=(7.2, 2.8))
    for ax, meth in zip(axs[:2], ["LOO-cfBH", "cfBH"]):
        for f, lab, col, mk, ls in var:
            if meth == "cfBH" and f == "screen_authors_fixtau":
                continue
            d = pd.read_csv(RAW / f"{f}.csv")
            g = d[d.method == meth].groupby("q").power.mean()
            ax.plot(qs, g.values, marker=mk, color=col, ls=ls, label=lab, ms=4)
        ax.plot(qs, PAPER_T4[meth][1], marker="D", color=C_ORIG, mfc="white", ls=":", label="Original (Table 4)", ms=4)
        ax.set_title(f"{meth}: mean power")
        ax.set_xticks(qs)
        ax.set_xlabel("target FDR level q")
        ax.set_ylim(0, 1.02)
        ax.grid(lw=0.3, alpha=0.6)
    h, l = axs[0].get_legend_handles_labels()
    ax = axs[2]
    for f, lab, col, mk, ls in var:
        d = pd.read_csv(RAW / f"{f}.csv")
        g = d[d.method == "LOO-cfBH"].groupby("q").fdp.mean()
        ax.plot(qs, g.values, marker=mk, color=col, ls=ls, ms=4)
    ax.plot(qs, PAPER_T4["LOO-cfBH"][0], marker="D", color=C_ORIG, mfc="white", ls=":", ms=4)
    ax.plot([0.08, 0.32], [0.08, 0.32], color="red", lw=0.8, ls="--", label="FDP = q")
    ax.set_title("LOO-cfBH: mean FDP")
    ax.set_xticks(qs)
    ax.set_xlabel("target FDR level q")
    ax.legend(loc="upper left", fontsize=6.5)
    ax.grid(lw=0.3, alpha=0.6)
    fig.legend(h, l, loc="lower center", ncol=2, frameon=False)
    fig.tight_layout(rect=(0, 0.16, 1, 1))
    fig.savefig(FIG / "article_screening.pdf")


if __name__ == "__main__":
    fig_simulation()
    fig_real()
    fig_nn()
    if (RAW / "screen_authors_fixtau.csv").exists():
        fig_screen()
    print("wrote figures/article_*.pdf")
