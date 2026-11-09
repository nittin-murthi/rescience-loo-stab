# Box-plot figures that mirror the paper's figures (arXiv:2504.12189v1): rows are coverage, length and log10 time.
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = os.path.join(os.path.dirname(__file__), "..")
RAW = os.path.join(ROOT, "results", "raw")
FIG = os.path.join(ROOT, "figures")
COLORS = {"OracleCP": "#66c2a5", "FullCP": "#fc8d62", "SplitCP": "#8da0cb", "RO-StabCP": "#e78ac3",
          "LOO-StabCP": "#a6d854", "MM-SplitCP": "#ffd92f", "EM-SplitCP": "#e5c494"}


VT = {"": " - variant: text", "_authors": " - variant: authors' choices", "_a_scale": " - variant: X/sqrt(d)"}  # figure-title labels


def grid(df, panel_keys, titles, methods, fname, ref_len=None, suptitle=""):
    rows = [("coverage", "Coverage"), ("length", "Length"), ("time", "log10 time (s)")]
    fig, axes = plt.subplots(3, len(panel_keys), figsize=(3.6 * len(panel_keys), 9), squeeze=False)
    for c, (key, title) in enumerate(zip(panel_keys, titles)):
        g = df
        for k, v in key.items():
            g = g[g[k] == v]
        ms = [m for m in methods if m in set(g.method)]
        for r, (col, lab) in enumerate(rows):
            ax = axes[r, c]
            data = [g[g.method == m][col].to_numpy() for m in ms]
            if col == "time":
                data = [np.log10(np.maximum(d, 1e-6)) for d in data]
            bp = ax.boxplot(data, patch_artist=True, widths=0.6)
            for patch, m in zip(bp["boxes"], ms):
                patch.set_facecolor(COLORS[m])
            ax.set_xticks(range(1, len(ms) + 1))
            ax.set_xticklabels(ms, rotation=35, ha="right", fontsize=8)
            if col == "coverage":
                ax.axhline(0.9, color="red", ls="--", lw=1)  # target 1 - alpha [Paper §4: alpha = 0.1]
            if col == "length" and ref_len is not None:
                ax.axhline(ref_len, color="blue", ls="--", lw=1)
            if r == 0:
                ax.set_title(title)
            if c == 0:
                ax.set_ylabel(lab)
    fig.suptitle(suptitle)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, fname), dpi=130)
    plt.close(fig)
    print("wrote", fname)


BASE = ["OracleCP", "FullCP", "SplitCP", "RO-StabCP", "LOO-StabCP"]
DER = ["SplitCP", "MM-SplitCP", "EM-SplitCP", "LOO-StabCP"]
SIMK = [dict(setting=s, model=m) for s in ("linear", "nonlinear") for m in ("rlm", "sgd")]
SIMT = ["Linear: RLM", "Linear: SGD", "Nonlinear: RLM", "Nonlinear: SGD"]

if __name__ == "__main__":
    os.makedirs(FIG, exist_ok=True)
    # reference length 2 * z_{0.95} * sigma = 3.290 for noise sd 1 (the dashed blue line in Fig. 1)
    ref = 2 * 1.6448536 * 1.0
    for f, tag in (("sim.csv", "text"), ("sim_centered.csv", "centered"), ("sim_authors.csv", "authors")):
        p = os.path.join(RAW, f)
        if os.path.exists(p):
            df = pd.read_csv(p)
            grid(df, SIMK, SIMT, BASE, f"fig1_simulation_{tag}.png", ref, f"Simulation (cf. paper Fig. 1), variant: {tag}")
            grid(df, SIMK, SIMT, DER, f"fig7_derandom_simulation_{tag}.png", ref,
                 f"Derandomised SplitCP, simulation (cf. paper Fig. 7), variant: {tag}")
    for rf, tag in (("real.csv", ""), ("real_authors.csv", "_authors")):
      p = os.path.join(RAW, rf)
      if os.path.exists(p):
        df = pd.read_csv(p)
        for m in (1, 100):
            keys = [dict(data=d, model=mo, m=m) for d in ("boston", "diabetes") for mo in ("rlm", "sgd")]
            grid(df, keys, ["Boston: RLM", "Boston: SGD", "Diabetes: RLM", "Diabetes: SGD"], BASE,
                 f"fig2_real_m{m}{tag}.png", None, f"Real data, m={m} (cf. paper Fig. 2){VT[tag]}")
        keys = [dict(data=d, model=mo, m=100) for d in ("boston", "diabetes") for mo in ("rlm", "sgd")]
        grid(df, keys, ["Boston: RLM", "Boston: SGD", "Diabetes: RLM", "Diabetes: SGD"], DER,
             f"fig8_derandom_real{tag}.png", None, f"Derandomised SplitCP, real data m=100 (cf. paper Fig. 8){VT[tag]}")
    for nf, tag in (("nn.csv", ""), ("nn_a_scale.csv", "_a_scale"), ("nn_authors.csv", "_authors")):
        p = os.path.join(RAW, nf)
        if not os.path.exists(p):
            continue
        df = pd.read_csv(p)
        for hid, fn, nm in (("(20,)", "fig3_nn_1layer", "Fig. 3"), ("(10, 5)", "fig6_nn_2layer", "Fig. 6")):
            keys = [dict(data=d, hidden=hid) for d in ("boston", "diabetes")]
            grid(df, keys, ["Boston", "Diabetes"], ["SplitCP", "RO-StabCP", "LOO-StabCP"], fn + tag + ".png", None,
                 f"Neural network, hidden={hid} (cf. paper {nm}){VT[tag]}")
