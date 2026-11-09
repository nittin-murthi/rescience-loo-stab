"""Digitise the box plots of the original paper's neural-network figures.

The original paper reports the neural-network study (its Fig. 3 and App. A.2 Fig. 6) only as box plots; the
authors' repository (KiljaeL/LOO-StabCP, all 43 commits of the only branch, `main`) contains no neural-network code
or result file. (The authors' ICLR 2025 supplementary material, obtained later, does contain real_NN.py and
results_nn.csv, the raw numbers of the (10, 5) run; scripts/compare_supplement.py uses those instead. This
script is kept because Fig. 3, the one-layer run, still has no raw numbers.) To compare with a number rather than an eyeball estimate, this script reads the box-plot PNGs that
ship with the arXiv source (paper/src/plots/rev_figure_nn_{1,2}layer.png; fetch with scripts/get_data.sh) and converts
the pixel rows of each box's median line and quartile edges to data units, using the y-axis tick marks.

Resolution: box lines are 2 px thick and one tick interval spans ~65 px, so values are accurate to about +-0.01
(length). These are MEDIANS (the box-plot centre line), not means.
Output: results/nn_paper_digitised.md
"""
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PLOTS = ROOT / "paper" / "src" / "plots"
# tick values read from the axis labels of each figure (top-to-bottom order of the tick marks)
PANELS = {
    "rev_figure_nn_1layer.png": {"Length": (448, [3.0, 2.5, 2.0])},
    "rev_figure_nn_2layer.png": {"Length": (448, [3.5, 3.0, 2.5])},
}
METHODS = ["SplitCP", "RO-StabCP", "LOO-StabCP"]
DATASETS = ["Boston", "Diabetes"]


def runs(mask):
    out = []
    for y in np.flatnonzero(mask):
        if out and y - out[-1][-1] <= 1:
            out[-1].append(y)
        else:
            out.append([y])
    return out


def analyse(img, spine_hint, ticks):
    grey = (np.ptp(img, axis=2) < 12) & (img.sum(2) < 400)
    colour = (np.ptp(img, axis=2) > 30) & (img.sum(2) < 700)
    # left spine: the long grey column nearest to the hint
    cand = [x for x in range(spine_hint - 30, spine_hint + 30) if grey[:, x].sum() > 150]
    L = min(cand, key=lambda x: abs(x - spine_hint))
    top, bot = [y for y in range(img.shape[0]) if grey[y, L + 1:L + 300].sum() > 250][:2]
    tick_rows = [np.mean(r) for r in runs(grey[:, L - 6:L - 1].sum(1) >= 4) if top - 2 < np.mean(r) < bot + 2]
    assert len(tick_rows) == len(ticks), (tick_rows, ticks)
    slope, icpt = np.polyfit(tick_rows, ticks, 1)
    to_val = lambda y: slope * y + icpt
    R = next(x for x in range(L + 50, img.shape[1]) if grey[top:bot, x].sum() > 0.9 * (bot - top))
    xs = [x for x in range(L + 2, R - 1) if colour[top + 2:bot - 1, x].sum() >= 2]
    groups = runs(np.isin(np.arange(img.shape[1]), xs))
    groups = [g for g in groups if len(g) >= 8]
    out = []
    for g in groups:
        xq = g[0] + (g[-1] - g[0]) // 4          # quarter column: misses the central whisker line
        col_rows = np.flatnonzero(colour[top + 2:bot - 1, xq]) + top + 2
        y0, y1 = col_rows.min(), col_rows.max()  # coloured interior of the box
        allruns = runs(grey[:, xq])
        top_edge = next(r for r in allruns if r[-1] == y0 - 1)        # line just above the coloured interior
        bot_edge = next(r for r in allruns if r[0] == y1 + 1)         # line just below it
        mids = [r for r in allruns if r[0] > y0 and r[-1] < y1]       # a line inside the interior
        if mids:
            med = np.mean(mids[0])
        elif len(bot_edge) >= 4:                 # median merged with the lower edge
            med = bot_edge[0] + 0.5
            bot_edge = bot_edge[-2:]
        elif len(top_edge) >= 4:                 # median merged with the upper edge
            med = top_edge[-1] - 0.5
            top_edge = top_edge[:2]
        else:
            med = np.nan
        out.append((to_val(med), to_val(np.mean(bot_edge)), to_val(np.mean(top_edge)), abs(slope) * 2))
    return out


def main():
    lines = ["# Neural-network results digitised from the original paper's box plots",
             "",
             "Source: arXiv source of the paper, `plots/rev_figure_nn_1layer.png` (paper Fig. 3, one hidden layer of 20)",
             "and `plots/rev_figure_nn_2layer.png` (paper App. A.2 Fig. 6, hidden layers (10, 5)). Values are box-plot",
             "MEDIANS and quartiles converted from pixel rows by `scripts/digitize_nn_figures.py`; resolution ~ one line",
             "width (column `res`). The authors did not publish the underlying numbers.",
             "",
             "| Figure | Panel | Data | Method | Q1 | Median | Q3 | res |",
             "|---|---|---|---|---|---|---|---|"]
    for fname, panels in PANELS.items():
        img = np.array(Image.open(PLOTS / fname).convert("RGB")).astype(int)
        for panel, (hint, ticks) in panels.items():
            boxes = analyse(img, hint, ticks)
            assert len(boxes) == 6, (fname, panel, len(boxes))
            for k, (med, q1, q3, res) in enumerate(boxes):
                d, m = DATASETS[k // 3], METHODS[k % 3]
                lines.append(f"| {fname} | {panel} | {d} | {m} | {q1:.3f} | {med:.3f} | {q3:.3f} | {res:.3f} |")
    rows = [l for l in lines if l.startswith("| rev_")]
    lines += ["", "## Comparison with our medians (100 repetitions each; results/raw/nn*.csv)", "",
              "Median interval length. Text setup = `nn`; X/sqrt(d) only = `nn_a_scale`; authors' setup (GitHub + supplement choices, scikit-learn network) = `nn_authors`. For the (10, 5) run the supplement's raw `results_nn.csv` supersedes these digitised values; see results/supplement_comparison.md (max |difference of medians| 0.006).", "",
              "| Hidden | Data | Method | Original (digitised) | Ours, text setup | Ours, X/sqrt(d) only | Ours, authors' setup |",
              "|---|---|---|---|---|---|---|"]
    import pandas as pd
    raw = {v: pd.read_csv(ROOT / "results" / "raw" / f"{v}.csv") for v in ("nn", "nn_a_scale", "nn_authors")}
    for r in rows:
        c = [x.strip() for x in r.strip("|").split("|")]
        hidden = "(20,)" if "1layer" in c[0] else "(10, 5)"
        meds = []
        for v, d in raw.items():
            sel = d[(d.hidden == hidden) & (d.data == c[2].lower()) & (d.method == c[3])]
            meds.append(f"{sel.length.median():.3f}")
        lines.append(f"| {hidden} | {c[2]} | {c[3]} | {c[5]} | " + " | ".join(meds) + " |")
    (ROOT / "results" / "nn_paper_digitised.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
