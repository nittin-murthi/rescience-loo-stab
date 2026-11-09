# Builds results/*.md tables: our numbers next to the paper's (arXiv:2504.12189v1).
import os
import sys
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from paper_values import METHODS, TABLE2, TABLE3, FIG2_LENGTH_APPROX  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), "..")
R = os.path.join(ROOT, "results")


def ms(s):
    return f"{s.mean():.3f} ({s.std(ddof=1):.3f})"


def pv(v, sd=None):
    if v is None:
        return "–"
    return f"{v:.3f}" + (f" ({sd:.3f})" if sd is not None else "")


def table2(fname, title):
    df = pd.read_csv(os.path.join(R, "raw", fname))
    out = [f"# {title}", "",
           "Ours: mean (sd) over 100 repetitions. Paper: [App. G.2, Table 2] of arXiv:2504.12189v1. "
           "Time is wall-clock seconds per repetition (all m=100 test points).", ""]
    for (setting, model), g in df.groupby(["setting", "model"], sort=False):
        P = TABLE2[(setting, model)]
        out += [f"## {setting} / {model.upper()}", "",
                "| Method | Coverage (ours) | Coverage (paper) | Length (ours) | Length (paper) | Time s (ours) | Time s (paper) |",
                "|---|---|---|---|---|---|---|"]
        for meth in g["method"].unique():
            h = g[g.method == meth]
            if meth in METHODS:
                k = METHODS.index(meth)
                pc = pv(P["coverage"][k], P.get("coverage_sd", [None] * 5)[k])
                pl = pv(P["length"][k], P.get("length_sd", [None] * 5)[k])
                pt = f"{P['time'][k]:.3f}"
            else:
                pc = pl = pt = "fig. 7 only"
            out.append(f"| {meth} | {ms(h.coverage)} | {pc} | {ms(h.length)} | {pl} | {h.time.mean():.4f} | {pt} |")
        if model == "rlm":
            out += ["", "lambda = 1 sensitivity (same fits, RLM bound with lambda=1 instead of 2):", ""]
            for meth in ("RO-StabCP", "LOO-StabCP"):
                h = g[g.method == meth]
                out.append(f"- {meth}: coverage {ms(h.coverage_lam1)}, length {ms(h.length_lam1)}")
        h = g[g.method == "LOO-StabCP"]
        out += ["", f"Diagnostic: training R^2 of the single LOO-StabCP fit = {ms(h.train_r2)}", ""]
    return "\n".join(out) + "\n"


def table3():
    df = pd.read_csv(os.path.join(R, "raw", "real.csv"))
    out = ["# Real data (§5): Table 3 coverage and Fig. 2 length", "",
           "Ours: mean (sd) over 100 repetitions. Paper coverage: [App. G.3, Table 3]. Paper lengths are not "
           "tabulated; Fig. 2 values below are approximate, read by eye from the figure.", ""]
    for (data, m, model), g in df.groupby(["data", "m", "model"], sort=False):
        P = TABLE3[(data, m, model)]
        out += [f"## {data}, m={m}, {model.upper()}", "",
                "| Method | Coverage (ours) | Coverage (paper) | Length (ours) | Time s (ours) |", "|---|---|---|---|---|"]
        for meth in g["method"].unique():
            h = g[g.method == meth]
            pc = f"{P[METHODS.index(meth)]:.3f}" if meth in METHODS else "fig. 8 only"
            out.append(f"| {meth} | {ms(h.coverage)} | {pc} | {ms(h.length)} | {h.time.mean():.4f} |")
        out += ["", f"Paper Fig. 2 length (approx., read from figure): {FIG2_LENGTH_APPROX[(data, model)]}", ""]
        if model == "rlm":
            for meth in ("RO-StabCP", "LOO-StabCP"):
                h = g[g.method == meth]
                out.append(f"- lambda=1 sensitivity, {meth}: coverage {ms(h.coverage_lam1)}, length {ms(h.length_lam1)}")
            out.append("")
    return "\n".join(out) + "\n"


def table_nn():
    df = pd.read_csv(os.path.join(R, "raw", "nn.csv"))
    out = ["# Neural networks (§5 Fig. 3: one hidden layer of 20; App. A.2 Fig. 6: hidden layers (10, 5))", "",
           "The paper reports these only as box plots (no table), so this table has no paper column.", "",
           "| Data | Hidden | Method | Coverage | Length | Time s | LOO train R^2 |", "|---|---|---|---|---|---|---|"]
    for (data, hid), g in df.groupby(["data", "hidden"], sort=False):
        for meth in g["method"].unique():
            h = g[g.method == meth]
            r2 = ms(h.train_r2) if meth == "LOO-StabCP" else ""
            out.append(f"| {data} | {hid} | {meth} | {ms(h.coverage)} | {ms(h.length)} | {h.time.mean():.4f} | {r2} |")
    return "\n".join(out) + "\n"


def runtimes():
    out = ["# Runtimes", "", "Wall-clock time from the run logs (4 worker processes, 1 BLAS thread each, on a shared 8-CPU box with no GPU).", ""]
    for f in sorted(os.listdir(os.path.join(ROOT, "logs"))):
        lines = open(os.path.join(ROOT, "logs", f)).read().strip().splitlines()
        if lines:
            out.append(f"- `{f}`: {lines[-1]}")
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    jobs = [("table2_simulation.md", lambda: table2("sim.csv", "Simulation (§4), literal paper text: Table 2 / Fig. 1 / Fig. 7")),
            ("table2_simulation_centered.md", lambda: table2("sim_centered.csv", "Simulation (§4), variant 'centered' (Y centred by training mean)")),
            ("table3_real.md", table3), ("nn.md", table_nn), ("runtimes.md", runtimes)]
    for name, fn in jobs:
        try:
            open(os.path.join(R, name), "w").write(fn())
            print("wrote", name)
        except FileNotFoundError as e:
            print("skip", name, e)


# ------------------------------------------------------------------------------------------------ diagnosis tables
VAR_LABEL = {"text": "ours (paper text)", "centered": "centered", "a_dgp": "+supplement DGP (AR(1), ||beta||^2=1/d)",
             "a_dgp_github": "+GitHub DGP (iid, ||beta||^2=1/d)",
             "a_scale": "+X/sqrt(d)", "a_coupled": "+coupled perms", "a_cpdetails": "+authors' CP details",
             "a_oursnet": "D2-D7, our network", "a_sknet": "+supplement network (Eq. 8 bound)",
             "authors": "all authors' choices (code + supplement)", "authors_github": "all GitHub-code choices"}
AUTH_CSV = os.path.join(ROOT, "data", "authors_results")  # fetched by scripts/get_data.sh (pinned commit 3b37682)


def _load(exp, v):
    f = os.path.join(R, "raw", f"{exp}.csv" if v == "text" else f"{exp}_{v}.csv")
    return pd.read_csv(f) if os.path.exists(f) else None


def diagnosis():
    # [App. G.2, Table 2] and [App. G.3, Table 3] paper values next to each diagnosis variant (DISCREPANCIES.md)
    out = ["# Diagnosis: effect of the authors' implementation choices", "",
           "Each cell gives mean coverage / mean length over 100 repetitions. Columns switch on the choices found in "
           "the authors' code (commit 3b37682) and in their ICLR 2025 supplementary material one group at a time, then all together "
           "(see results/supplement_comparison.md for the supplement's own result files). The `paper` column is quoted from "
           "Table 2 (simulation). For real data the paper has no length table, so the `authors' result file` column is "
           "computed from `result/results_real.csv` in the authors' repository (commit 3b37682); it is **not** from the paper.", ""]
    # simulation
    vs = [v for v in ("text", "centered", "a_dgp_github", "a_dgp", "authors_github", "authors") if _load("sim", v) is not None]
    out += ["## Simulation (§4)", "", "| Setting | Method | " + " | ".join(VAR_LABEL[v] for v in vs) + " | paper (Table 2) |",
            "|---|---|" + "---|" * (len(vs) + 1)]
    D = {v: _load("sim", v) for v in vs}
    for (s, mo) in [("linear", "rlm"), ("linear", "sgd"), ("nonlinear", "rlm"), ("nonlinear", "sgd")]:
        for k, meth in enumerate(METHODS):
            cells = []
            for v in vs:
                g = D[v][(D[v].setting == s) & (D[v].model == mo) & (D[v].method == meth)]
                cells.append(f"{g.coverage.mean():.3f} / {g.length.mean():.3f}")
            P = TABLE2[(s, mo)]
            out.append(f"| {s} {mo.upper()} | {meth} | " + " | ".join(cells) + f" | {P['coverage'][k]:.3f} / {P['length'][k]:.3f} |")
    # real
    vs = [v for v in ("text", "a_scale", "a_coupled", "a_cpdetails", "authors_github", "authors") if _load("real", v) is not None]
    A = None
    if os.path.exists(os.path.join(AUTH_CSV, "results_real.csv")):
        A = pd.read_csv(os.path.join(AUTH_CSV, "results_real.csv"))  # [FROM AUTHORS' CODE: result/results_real.csv, commit 3b37682]
    out += ["", "## Real data (§5)", "", "| Data, m, model | Method | " + " | ".join(VAR_LABEL[v] for v in vs) +
            " | paper Table 3 coverage | authors' result file |", "|---|---|" + "---|" * (len(vs) + 2)]
    D = {v: _load("real", v) for v in vs}
    for (d, m, mo) in [(d, m, mo) for m in (1, 100) for d in ("boston", "diabetes") for mo in ("rlm", "sgd")]:
        for k, meth in enumerate(METHODS):
            cells = []
            for v in vs:
                g = D[v][(D[v].data == d) & (D[v].m == m) & (D[v].model == mo) & (D[v].method == meth)]
                cells.append(f"{g.coverage.mean():.3f} / {g.length.mean():.3f}")
            a = ""
            if A is not None:
                h = A[(A.Dataset == d.capitalize()) & (A.m == m) & (A.Algorithm == mo.upper()) & (A.Method == meth)]
                a = f"{h.Coverage.mean():.3f} / {h.Length.mean():.3f}"
            out.append(f"| {d} m={m} {mo.upper()} | {meth} | " + " | ".join(cells) +
                       f" | {TABLE3[(d, m, mo)][k]:.3f} | {a} |")
    # nn
    vs = [v for v in ("text", "a_scale", "a_oursnet", "a_sknet", "authors") if _load("nn", v) is not None]
    out += ["", "## Neural networks (§5 Fig. 3, App. A.2 Fig. 6)", "",
            "| Data, hidden | Method | " + " | ".join(VAR_LABEL[v] for v in vs) + " |", "|---|---|" + "---|" * len(vs)]
    D = {v: _load("nn", v) for v in vs}
    for d in ("boston", "diabetes"):
        for hid in ("(20,)", "(10, 5)"):
            for meth in ("SplitCP", "RO-StabCP", "LOO-StabCP"):
                cells = []
                for v in vs:
                    g = D[v][(D[v].data == d) & (D[v].hidden == hid) & (D[v].method == meth)]
                    cells.append(f"{g.coverage.mean():.3f} / {g.length.mean():.3f}")
                out.append(f"| {d} {hid} | {meth} | " + " | ".join(cells) + " |")
    return "\n".join(out) + "\n"


def authors_repo_summary():
    """Summary of the authors' own result files (diagnosis only; NOT paper numbers)."""
    out = ["# Summary of the authors' result files (github.com/KiljaeL/LOO-StabCP, commit 3b37682)", "",
           "Computed by us from `result/results_synthetic.csv` and `result/results_real.csv`. Used only to check "
           "which code version produced the paper's Table 2 and Table 3.", ""]
    s = pd.read_csv(os.path.join(AUTH_CSV, "results_synthetic.csv"))  # [FROM AUTHORS' CODE: result/results_synthetic.csv, commit 3b37682]
    g = s.groupby(["DGP", "Algorithm", "Method"], sort=False)[["Coverage", "Length", "Time"]].agg(["mean", "std"]).round(3)
    out += ["## Synthetic", "", "```", g.to_string(), "```", ""]
    r = pd.read_csv(os.path.join(AUTH_CSV, "results_real.csv"))
    g = r.groupby(["m", "Dataset", "Algorithm", "Method"], sort=False)[["Coverage", "Length", "Time"]].agg(["mean", "std"]).round(3)
    out += ["## Real", "", "```", g.to_string(), "```", ""]
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    for name, fn in (("diagnosis.md", diagnosis), ("authors_repo_summary.md", authors_repo_summary)):
        try:
            open(os.path.join(R, name), "w").write(fn())
            print("wrote", name)
        except (FileNotFoundError, KeyError) as e:
            print("skip", name, e)
