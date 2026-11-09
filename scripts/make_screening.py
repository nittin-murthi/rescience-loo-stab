# Table and figure for the screening experiment [Paper §6, Fig. 4; App. G.4, Table 4] (arXiv:2504.12189v1).
# Our numbers come only from results/raw/screen*.csv; paper numbers only from scripts/paper_values.TABLE4.
import os
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from paper_values import TABLE4  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), "..")
RAW = os.path.join(ROOT, "results", "raw")
M = ["cfBH", "RO-cfBH", "LOO-cfBH"]
QS = (0.1, 0.2, 0.3)
VARS = [("", "text (paper protocol)"), ("_a_split", "a_split: 30% test, split redrawn every 100 reps"),
        ("_a_xscale", "a_xscale: authors' X scaling + intercept"), ("_a_tau", "a_tau: LOO bound without R"),
        ("_a_cal50", "a_cal50: cfBH 50/50"), ("_authors", "authors: all authors' choices"),
        ("_authors_resplit", "authors_resplit: authors, fresh split every rep"),
        ("_authors_fixtau", "authors_fixtau: authors, App. G.1 bound restored")]


def load(v):
    d = pd.read_csv(os.path.join(RAW, f"screen{v}.csv"))
    d["split"] = d.rep // (100 if v in ("_a_split", "_authors", "_authors_fixtau") else 1)
    return d


def f(m, s, k=3):
    return f"{m:.{k}f} ({s:.{k}f})"


def main():
    out = ["# Screening (claim C8): ours vs paper Table 4 [App. G.4]", "",
           "Mean (sd) over 1000 repetitions. Paper values transcribed from Table 4 (they equal the authors' published "
           "`result/results_recruit.csv` at commit 3b37682 to 4 d.p.). Time in seconds (machine-dependent).", ""]
    d = load("")
    out += ["## Paper protocol (variant text) vs paper", "",
            "| q | method | FDP ours | FDP paper | power ours | power paper | time ours | time paper |",
            "|---|---|---|---|---|---|---|---|"]
    for q in QS:
        for m in M:
            g = d[(d.q == q) & (d.method == m)]
            P = TABLE4[(q, m)]
            out.append(f"| {q} | {m} | {f(g.fdp.mean(), g.fdp.std())} | {f(*P[0], 4)} | "
                       f"{f(g.power.mean(), g.power.std())} | {f(*P[1], 4)} | "
                       f"{f(g.time.mean(), g.time.std(), 4)} | {f(*P[2], 4)} |")
    out += ["", "## All variants: mean FDP / mean power", "",
            "| variant | q | " + " | ".join(f"{m} FDP | {m} power" for m in M) + " |",
            "|---|---|" + "---|---|" * 3]
    for v, lab in VARS + [("paper", "paper Table 4")]:
        for q in QS:
            cells = []
            for m in M:
                if v == "paper":
                    P = TABLE4[(q, m)]
                    cells += [f"{P[0][0]:.3f}", f"{P[1][0]:.3f}"]
                else:
                    g = load(v)
                    g = g[(g.q == q) & (g.method == m)]
                    cells += [f"{g.fdp.mean():.3f}", f"{g.power.mean():.3f}"]
            out.append(f"| {lab} | {q} | " + " | ".join(cells) + " |")
    out += ["", "## Effect of reusing 10 splits (a_split, authors): SE of mean LOO-cfBH power", "",
            "Naive SE = sd/sqrt(1000); cluster SE = sd of the 10 per-split means / sqrt(10).", "",
            "| variant | q | naive SE | cluster SE |", "|---|---|---|---|"]
    for v in ("_a_split", "_authors"):
        g0 = load(v)
        for q in QS:
            g = g0[(g0.q == q) & (g0.method == "LOO-cfBH")]
            out.append(f"| {v[1:]} | {q} | {g.power.std() / np.sqrt(len(g)):.4f} | "
                       f"{g.groupby('split').power.mean().std() / np.sqrt(g.split.nunique()):.4f} |")
    open(os.path.join(ROOT, "results", "table4_screening.md"), "w").write("\n".join(out) + "\n")

    # Figure mirroring Fig. 4: rows FDP / power / log10 time; columns = q. Paper means as black diamonds.
    for v, tag in (("", "text"), ("_authors", "authors")):
        d = load(v)
        fig, ax = plt.subplots(3, 3, figsize=(10, 8.5))
        for c, q in enumerate(QS):
            for r, (col, lab) in enumerate((("fdp", "FDP"), ("power", "Power"), ("time", "log10 time (s)"))):
                a = ax[r, c]
                data = [d[(d.q == q) & (d.method == m)][col].to_numpy() for m in M]
                if col == "time":
                    data = [np.log10(np.maximum(x, 1e-6)) for x in data]
                a.boxplot(data, widths=0.6, showfliers=False)
                pm = [TABLE4[(q, m)][r][0] for m in M]
                a.scatter(range(1, 4), np.log10(pm) if col == "time" else pm, marker="D", c="k", s=25, zorder=3,
                          label="paper mean")
                if col == "fdp":
                    a.axhline(q, ls="--", c="r", lw=1)
                a.set_xticks(range(1, 4)); a.set_xticklabels(M, fontsize=8)
                if c == 0:
                    a.set_ylabel(lab)
                if r == 0:
                    a.set_title(f"q = {q}")
        ax[0, 0].legend(fontsize=7, loc="upper left")
        fig.suptitle(f"Screening (Fig. 4 analogue), variant: {tag}; red dashed = q, diamonds = paper Table 4")
        fig.tight_layout()
        fig.savefig(os.path.join(ROOT, "figures", f"fig4_screening{'' if tag == 'text' else '_authors'}.png"), dpi=130)
        plt.close(fig)


if __name__ == "__main__":
    main()
