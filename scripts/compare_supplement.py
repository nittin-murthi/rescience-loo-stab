"""Compares our runs with the result files of the authors' ICLR 2025 supplementary material (diagnosis only).
Inputs: results/raw/*.csv (ours), data/authors_supplement/code_final/result/*.csv (fetched by scripts/get_data.sh,
not redistributed), results/nn_paper_digitised.md, and the Table 2 values of scripts/paper_values.py.
Outputs: results/supplement_comparison.md and the LaTeX table bodies article/tables/*.tex used by the article.
Every number written here is computed from those files; nothing is typed in by hand."""
import os
import sys
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from paper_values import METHODS, TABLE2  # noqa: E402  [App. G.2, Table 2]

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "results" / "raw"
SUPP = ROOT / "data" / "authors_supplement" / "code_final" / "result"
TEX = ROOT / "article" / "tables"
LO, RO_, SP = "LOO-StabCP", "RO-StabCP", "SplitCP"
TEXNAME = {"OracleCP": "OracleCP", "FullCP": "FullCP", SP: "SplitCP", RO_: r"\RO", LO: r"\LOO",
           "MM-SplitCP": "MM-SplitCP", "EM-SplitCP": "EM-SplitCP"}


def raw(name):
    return pd.read_csv(RAW / f"{name}.csv")


def supp(name):
    return pd.read_csv(SUPP / f"{name}.csv")  # [FROM AUTHORS' SUPPLEMENT: code_final/result/<name>.csv]


def f3(x):
    return f"{x:.3f}"


def cl(d, **kw):
    for k, v in kw.items():
        d = d[d[k] == v]
    return d


# ----------------------------------------------------------------------------------------- simulation, Table 2
def sim():
    t, a, g = raw("sim"), raw("sim_authors"), raw("sim_authors_github")
    s = supp("results_synthetic_ar1_05")
    md = ["## Simulation (§4): supplement result file vs Table 2", "",
          "`results_synthetic_ar1_05.csv` is the supplement's output of `simul.py` (AR(1) design). Max |file − Table 2| "
          "over all coverage, length and time cells:", ""]
    diffs = []
    for (st, mo), P in TABLE2.items():
        for k, me in enumerate(METHODS):
            h = cl(s, DGP=st.capitalize(), Algorithm=mo.upper(), Method=me)
            for col, key in (("Coverage", "coverage"), ("Length", "length"), ("Time", "time")):
                diffs.append(abs(round(h[col].mean(), 3) - P[key][k]))
    md += [f"- max abs difference after rounding to 3 decimals: {max(diffs):.4f} over {len(diffs)} cells", ""]
    md += ["| Setting | Method | Ours text | Ours authors' (supplement DGP) | Ours authors' (GitHub DGP) | Supplement file | Table 2 |",
           "|---|---|---|---|---|---|---|"]
    rows = []
    for (st, mo), P in TABLE2.items():
        for k, me in enumerate(METHODS):
            c = [cl(x, setting=st, model=mo, method=me) for x in (t, a, g)]
            h = cl(s, DGP=st.capitalize(), Algorithm=mo.upper(), Method=me)
            md.append(f"| {st} {mo.upper()} | {me} | " + " | ".join(f"{f3(x.coverage.mean())} / {f3(x.length.mean())}" for x in c)
                      + f" | {f3(h.Coverage.mean())} / {f3(h.Length.mean())} | {P['coverage'][k]:.3f} / {P['length'][k]:.3f} |")
            lab = (f"{st.capitalize()}, {mo.upper()}" if k == 0 else "")
            rows.append(f"{lab} & {TEXNAME[me]} & {f3(c[0].coverage.mean())} & {f3(c[0].length.mean())} & "
                        f"{f3(c[1].coverage.mean())} & {f3(c[1].length.mean())} & {P['coverage'][k]:.3f} & {P['length'][k]:.3f} \\\\")
        rows.append(r"\addlinespace")
    (TEX / "sim.tex").write_text("\n".join(rows[:-1]) + "\n")
    # relative length gaps authors' setup vs Table 2
    gaps = []
    for (st, mo), P in TABLE2.items():
        for k, me in enumerate(METHODS):
            gaps.append(abs(cl(a, setting=st, model=mo, method=me).length.mean() / P["length"][k] - 1))
    md += ["", f"Max relative length gap, authors' setup vs Table 2: {100 * max(gaps):.2f}%", ""]
    return md


# ----------------------------------------------------------------------------------------- derandomisation
def derand():
    md = ["## Derandomised split conformal (App. B, Figs. 7-8) vs the supplement result files", "",
          "Mean coverage / mean length (time in ms) over 100 repetitions. Ours: m = 100. Supplement: "
          "`results_synthetic_derandom.csv` (K = 30) and `results_real_derandom.csv` (K = 50).", ""]
    meths = [LO, "MM-SplitCP", "EM-SplitCP", SP]
    md += ["| Setting | Source | " + " | ".join(meths) + " |", "|---|---|" + "---|" * len(meths)]
    rows = []
    syn = {"text": raw("sim"), "authors": raw("sim_authors")}
    rea = {"text": raw("real")[lambda d: d.m == 100], "authors": raw("real_authors")[lambda d: d.m == 100]}
    ss, sr = supp("results_synthetic_derandom"), supp("results_real_derandom")
    settings = [("syn", st, mo) for st in ("linear", "nonlinear") for mo in ("rlm", "sgd")] + \
               [("real", d, mo) for d in ("boston", "diabetes") for mo in ("rlm", "sgd")]
    for kind, a, mo in settings:
        lab = f"{a.capitalize()}, {mo.upper()}"
        srcs = []
        for v in ("text", "authors"):
            D = syn[v] if kind == "syn" else rea[v]
            D = cl(D, setting=a, model=mo) if kind == "syn" else cl(D, data=a, model=mo)
            srcs.append((v, {me: cl(D, method=me) for me in meths}, "coverage", "length", "time"))
        F = cl(ss, DGP=a.capitalize(), Algorithm=mo.upper()) if kind == "syn" else cl(sr, Dataset=a.capitalize(), Algorithm=mo.upper())
        srcs.append(("file", {me: cl(F, Method=me) for me in meths}, "Coverage", "Length", "Time"))
        for name, G, c, l, tt in srcs:
            md.append(f"| {lab} | {name} | " + " | ".join(
                f"{f3(G[me][c].mean())} / {f3(G[me][l].mean())} ({1000 * G[me][tt].mean():.1f})" for me in meths) + " |")
            nm = {"text": "Text setup", "authors": "Authors' setup", "file": "Supplement file"}[name]
            rows.append(f"{lab if name == 'text' else ''} & {nm} & " + " & ".join(
                f"{f3(G[me][c].mean())} & {f3(G[me][l].mean())}" for me in meths[:3]) + " \\\\")
        rows.append(r"\addlinespace")
    (TEX / "derand.tex").write_text("\n".join(rows[:-1]) + "\n")
    return md


# ----------------------------------------------------------------------------------------- neural networks
def digitised():
    dig = {}
    for line in (ROOT / "results" / "nn_paper_digitised.md").read_text().splitlines():
        if line.startswith("| rev_"):
            c = [x.strip() for x in line.strip("|").split("|")]
            hid = "(20,)" if "1layer" in c[0] else "(10, 5)"
            dig[(hid, c[2].lower(), c[3])] = tuple(float(v) for v in c[4:7])
    return dig


def nn():
    vs = [("nn", "text"), ("nn_a_oursnet", "D2-D7, our network"), ("nn_a_sknet", "+ authors' network, Eq. (8) bound"),
          ("nn_authors", "authors' setup (+ constant bound)")]
    D = {k: raw(k) for k, _ in vs}
    F = supp("results_nn")
    dig = digitised()
    md = ["## Neural networks (§5 Fig. 3, App. A.2 Fig. 6) vs `results_nn.csv`", "",
          "`results_nn.csv` holds 100 repetitions per data set and method, without a column for the architecture. Its "
          "medians agree with our digitised Fig. 6 (hidden layers (10, 5)) to within the values below, so we treat it as "
          "the Fig. 6 run, although the shipped `real_NN.py` is set to one hidden layer of 20.", "",
          "| Data | Method | file median | digitised Fig. 6 median | |diff| | digitised Fig. 3 median |", "|---|---|---|---|---|---|"]
    mx = 0
    for d in ("boston", "diabetes"):
        for me in (SP, RO_, LO):
            fm = cl(F, Dataset=d.capitalize(), Method=me).Length.median()
            mx = max(mx, abs(fm - dig[("(10, 5)", d, me)][1]))
            md.append(f"| {d} | {me} | {f3(fm)} | {dig[('(10, 5)', d, me)][1]:.3f} | {abs(fm - dig[('(10, 5)', d, me)][1]):.3f} | {dig[('(20,)', d, me)][1]:.3f} |")
    md += ["", f"Max |file median − digitised Fig. 6 median| = {mx:.4f}", ""]
    md += ["Mean coverage / mean length (median length) over 100 repetitions:", "",
           "| Hidden | Data | Method | " + " | ".join(l for _, l in vs) + " | supplement file |", "|---|---|---|" + "---|" * (len(vs) + 1)]
    rows = []
    for hid in ("(20,)", "(10, 5)"):
        for d in ("boston", "diabetes"):
            for me in (SP, RO_, LO):
                c = [cl(D[k], hidden=hid, data=d, method=me) for k, _ in vs]
                f = cl(F, Dataset=d.capitalize(), Method=me) if hid == "(10, 5)" else None
                fs = f"{f3(f.Coverage.mean())} / {f3(f.Length.mean())} ({f3(f.Length.median())})" if f is not None else \
                    f"digitised median {dig[(hid, d, me)][1]:.3f}"
                md.append(f"| {hid} | {d} | {me} | " + " | ".join(
                    f"{f3(x.coverage.mean())} / {f3(x.length.mean())} ({f3(x.length.median())})" for x in c) + f" | {fs} |")
                lab_h = ("(20)" if hid == "(20,)" else "(10, 5)") if (d == "boston" and me == SP) else ""
                lab_d = d.capitalize() if me == SP else ""
                fl = f"{f3(f.Length.mean())}" if f is not None else "--"
                fc = f"{f3(f.Coverage.mean())}" if f is not None else "--"
                rows.append(f"{lab_h} & {lab_d} & {TEXNAME[me]} & " + " & ".join(f3(x.length.mean()) for x in c) +
                            f" & {fl} & {f3(c[-1].coverage.mean())} & {fc} \\\\")
            rows.append(r"\addlinespace")
    (TEX / "nn.tex").write_text("\n".join(rows[:-1]) + "\n")
    # medians for the one-layer comparison with the digitised Fig. 3
    md += ["", "One hidden layer: our medians (authors' setup) vs digitised Fig. 3 medians:", "",
           "| Data | Method | ours | digitised | diff |", "|---|---|---|---|---|"]
    for d in ("boston", "diabetes"):
        for me in (SP, RO_, LO):
            o = cl(D["nn_authors"], hidden="(20,)", data=d, method=me).length.median()
            md.append(f"| {d} | {me} | {f3(o)} | {dig[('(20,)', d, me)][1]:.3f} | {o - dig[('(20,)', d, me)][1]:+.3f} |")
    md += ["", "Mean time per repetition (s), authors' setup vs file:", ""]
    for d in ("boston", "diabetes"):
        for me in (SP, RO_, LO):
            for hid in ("(20,)", "(10, 5)"):
                o = cl(D["nn_authors"], hidden=hid, data=d, method=me).time.mean()
                md.append(f"- {d} {hid} {me}: ours {o:.4f}" + (f", file {cl(F, Dataset=d.capitalize(), Method=me).Time.mean():.4f}" if hid == "(10, 5)" else ""))
    return md


# ----------------------------------------------------------------------------------------- kernels
KLAB = {"none": "No Kernel", "rbf": "RBF Kernel", "poly": "Polynomial Kernel"}


def kernel():
    vs = [("kernel", "text"), ("kernel_a_kparams", "authors' kernel parameters only"), ("kernel_authors", "authors' setup"),
          ("kernel_authors_centered", "authors' setup, centred Y")]
    D = {k: raw(k) for k, _ in vs if (RAW / f"{k}.csv").exists()}
    F = supp("results_kernel")
    md = ["## Kernels (App. A.1, Fig. 5) vs `results_kernel.csv`", "",
          "SGD; mean coverage / mean length (sd of length) over 100 repetitions. Text RLM rows are ours only.", "",
          "| Setting | Kernel | Method | " + " | ".join(l for k, l in vs if k in D) + " | text, kernel RLM | supplement file |",
          "|---|---|---|" + "---|" * (len(D) + 2)]
    rows = []
    for st in ("linear", "nonlinear"):
        for kk in ("none", "rbf", "poly"):
            for me in (SP, RO_, LO):
                c = [cl(D[k], setting=st, kernel=kk, model="sgd", method=me) for k, _ in vs if k in D]
                r = cl(D["kernel"], setting=st, kernel=kk, model="rlm", method=me)
                f = cl(F, DGP=st.capitalize(), Kernel=KLAB[kk], Method=me)
                md.append(f"| {st} | {kk} | {me} | " + " | ".join(
                    f"{f3(x.coverage.mean())} / {f3(x.length.mean())} ({f3(x.length.std())})" for x in c) +
                    f" | {f3(r.coverage.mean())} / {f3(r.length.mean())} | {f3(f.Coverage.mean())} / {f3(f.Length.mean())} ({f3(f.Length.std())}) |")
                t, a, ac = c[0], c[2], c[3]
                lab_s = st.capitalize() if (kk == "none" and me == SP) else ""
                lab_k = {"none": "None", "rbf": "RBF", "poly": "Polynomial"}[kk] if me == SP else ""
                rows.append(f"{lab_s} & {lab_k} & {TEXNAME[me]} & {f3(t.coverage.mean())} & {f3(t.length.mean())} & "
                            f"{f3(a.coverage.mean())} & {f3(a.length.mean())} & {f3(f.Coverage.mean())} & {f3(f.Length.mean())} & "
                            f"{f3(ac.coverage.mean())} & {f3(ac.length.mean())} \\\\")
            rows.append(r"\addlinespace")
    (TEX / "kernel.tex").write_text("\n".join(rows[:-1]) + "\n")
    md += ["", "Mean time per repetition (s), authors' setup vs file:", ""]
    for kk in ("none", "rbf", "poly"):
        for me in (SP, RO_, LO):
            o = cl(D["kernel_authors"], kernel=kk, model="sgd", method=me).time.mean()
            fo = cl(F, Kernel=KLAB[kk], Method=me).Time.mean()
            md.append(f"- {kk} {me}: ours {o:.4f}, file {fo:.4f}")
    return md


if __name__ == "__main__":
    TEX.mkdir(exist_ok=True)
    out = ["# Our runs vs the result files of the authors' ICLR 2025 supplementary material", "",
           "Supplement: https://proceedings.iclr.cc/paper_files/paper/2025/file/297fe652867e4897e9f1fe1cd715de19-Supplemental-Conference.zip",
           "(sha256 7f39cd75fda4e126ebdf5f545b34c3dbe2208f6216086e4137f23ef82a765e53), fetched by `scripts/get_data.sh`.",
           "The supplement's numbers are computed by us from its `code_final/result/*.csv`; they are diagnosis references, "
           "not paper numbers.", ""]
    for fn in (sim, derand, nn, kernel):
        try:
            out += fn() + [""]
        except FileNotFoundError as e:
            out += [f"(skipped {fn.__name__}: {e})", ""]
    (ROOT / "results" / "supplement_comparison.md").write_text("\n".join(out))
    print("wrote results/supplement_comparison.md and article/tables/*.tex")
