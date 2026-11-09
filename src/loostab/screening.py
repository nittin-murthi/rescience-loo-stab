# Conformalized screening (cfBH, RO-cfBH, LOO-cfBH) of [Paper §6, Alg. 2, Eqs. (6)-(7), Fig. 4, App. G.4 Table 4].
# Paper version: arXiv:2504.12189v1 (https://arxiv.org/pdf/2504.12189v1; not vendored). Tags refer to its numbering.
import os
import time
import numpy as np
import pandas as pd

from .cp import CONFIG

# Switches for the diagnosis variants (DISCREPANCIES.md D12-D15). Defaults = paper text.
SCREEN_CFG = dict(
    x_prep="text",       # "authors": all 14 columns z-scored, divided by sqrt(p+1), plus intercept column
    cal_frac=0.7,        # cfBH training fraction; authors use 0.5
    tau_train_R=True,    # False: LOO-cfBH training-point bound without the factor R (authors' code)
    bh_rule="strict",    # "leq": standard BH, reject p_j <= q k*/m (authors' code)
)

DATA = os.path.join(os.path.dirname(__file__), "..", "..", "data", "screening", "Placement_Data_Full_Class.csv")
# [Paper §6: "It contains 215 individuals, each measured on 12 features such as education, work experience, and
#  specialization. The binary response indicates whether the candidate receives a job offer."] The Kaggle file has
# 15 columns; dropping the row id (sl_no), the response (status) and salary (only observed for placed candidates,
# so it would leak the response) leaves exactly the 12 features.
FEATURES = ["gender", "ssc_p", "ssc_b", "hsc_p", "hsc_b", "hsc_s", "degree_p", "degree_t", "workex", "etest_p",
            "specialisation", "mba_p"]
CONTINUOUS = ["ssc_p", "hsc_p", "degree_p", "etest_p", "mba_p"]


def load_placement(x_scale="z"):
    """Returns X (215 x p) and binary y (1 = placed) [Paper §6, citing Ganatara (2020)]."""
    df = pd.read_csv(DATA)
    y = (df["status"] == "Placed").to_numpy(dtype=float)  # [Paper §6: binary response = job offer]
    if SCREEN_CFG["x_prep"] == "authors":
        # Diagnosis variant only: dummies (drop_first), then EVERY column (dummies included) z-scored with np.std,
        # divided by sqrt(p+1), and an intercept column 1/sqrt(p+1) prepended, so ||X_i|| is about 1.
        # [FROM AUTHORS' CODE: recruit.py:18-24, commit 3b37682]
        Z = pd.get_dummies(df[FEATURES], columns=[c for c in FEATURES if c not in CONTINUOUS],
                           drop_first=True).astype(float).to_numpy()
        Z = (Z - Z.mean(0)) / Z.std(0) / np.sqrt(Z.shape[1] + 1)
        return np.hstack([np.ones((len(Z), 1)) / np.sqrt(Z.shape[1] + 1), Z]), y
    # [ASSUMPTION: not specified in paper how the 7 categorical features are encoded; chose one-hot dummies with the
    #  first level dropped (gender, ssc_b, hsc_b, workex, specialisation -> 1 column each; hsc_s, degree_t -> 2 each),
    #  the standard full-rank encoding for a linear model; gives p = 5 + 5 + 4 = 14 columns]
    Xc = df[CONTINUOUS].astype(float)
    # [Paper §5 (whose robust regression §6 "imports"): "All continuous variables have been normalized"]
    # [ASSUMPTION: not specified in paper; z-score the continuous features with full-data mean/sd (as in §5); the
    #  0/1 dummies and the binary response are left unscaled because the score S(y,f) = 100y - f needs y in {0,1}]
    Xc = (Xc - Xc.mean()) / Xc.std(ddof=0)
    Xd = pd.get_dummies(df[[c for c in FEATURES if c not in CONTINUOUS]], drop_first=True).astype(float)
    X = np.hstack([Xc.to_numpy(), Xd.to_numpy()])
    if x_scale == "z_sqrt_d":
        X = X / np.sqrt(X.shape[1])  # diagnostic only, mirrors data.load_real (D2); not used unless requested
    return X, y


def score(y, f):
    """Clip-type non-conformity score [Paper §6: "S(y, f) = 100y - f", from Jin & Candès (2023)]
    (signed, no absolute value [Paper §6: "S(y, z) = y - z without the absolute value"])."""
    return 100.0 * y - f


# [ASSUMPTION: not specified in paper; threshold c_j = 0 for every test point, i.e. H0j: Y_{n+j} <= 0 ("not placed")
#  vs H1j: Y_{n+j} > 0 ("placed"), the only non-trivial threshold for a binary response]
C_THRESH = 0.0


def bh(p, q):
    """Benjamini-Hochberg as written in [Paper §6]: k* = max{k : sum_j 1{p_j <= q k / m} >= k};
    reject H0j with p_j < q k* / m. Returns a boolean rejection vector."""
    m = len(p)
    ks = np.arange(1, m + 1)
    counts = (p[None, :] <= q * ks[:, None] / m).sum(axis=1)
    ok = ks[counts >= ks]
    if ok.size == 0:
        return np.zeros(m, bool)
    kstar = ok.max()
    # [ASSUMPTION: not specified beyond the text; followed the text literally: strict "<" in the rejection rule
    #  ("reject all H0j's with p_j < q k*/m") although k* is defined with "<="]
    if SCREEN_CFG["bh_rule"] == "leq":
        return p <= q * kstar / m  # [FROM AUTHORS' CODE: funcs/utils.py:41-52, commit 3b37682] (standard BH)
    return p < q * kstar / m


def fdp_power(rej, yt):
    """[Paper §6]: FDP = #false rejections / (1 v #rejections); power = #true rejections / #true alternatives."""
    h1 = yt > C_THRESH
    fdp = (rej & ~h1).sum() / max(1, rej.sum())
    power = (rej & h1).sum() / h1.sum() if h1.sum() > 0 else 0.0
    # [ASSUMPTION: not specified in paper; power = 0 when no test point is a true alternative (never happens here)]
    return fdp, power


def cfbh(L, X, y, Xt, rng, frac=None):
    """cfBH of Jin & Candès (2023) [Paper §6, Eq. (6)]: split 70% train / 30% calibration
    [Paper §6: "In cfBH, the data was split into 70% for training and 30% for calibration"]."""
    t0 = time.perf_counter()
    if frac is None:
        frac = SCREEN_CFG["cal_frac"]  # 0.5 in [FROM AUTHORS' CODE: funcs/CP_screening.py:11, commit 3b37682]
    n = X.shape[0]
    perm = rng.permutation(n)
    ntr = int(round(frac * n))  # same rounding as SplitCP (cp.split_cp) [ASSUMPTION A-split, see cp.py]
    if CONFIG["split_round"] == "floor":
        ntr = int(frac * n)
    tr, ca = perm[:ntr], perm[ntr:]
    th = L.fit(X[tr], y[tr], rng)
    S = score(y[ca], L.predict(th, X[ca]))  # [§6: S_i = S(Y_i, f(X_i)) on calibration data]
    St = score(C_THRESH, L.predict(th, Xt))  # [§6: S^{c_j}_{n+j} = S(c_j, f(X_{n+j}))]
    p = ((S[None, :] < St[:, None]).sum(axis=1) + 1) / (len(ca) + 1)  # [Eq. (6)]
    return p, time.perf_counter() - t0


def loo_cfbh(L, X, y, Xt, rng):
    """LOO-cfBH [Alg. 2; Eq. (7)]."""
    t0 = time.perf_counter()
    n = X.shape[0]
    th = L.fit(X, y, rng)  # [Alg. 2, step 1: fit f on D]
    S = score(y, L.predict(th, X))  # [Alg. 2, step 2: uncorrected scores on D]
    St = score(C_THRESH, L.predict(th, Xt))
    nX, nT = np.linalg.norm(X, axis=1), np.linalg.norm(Xt, axis=1)
    p = np.empty(len(Xt))
    for j in range(len(Xt)):  # [Alg. 2: for j in [m]]
        ti, tj = L.tau_loo(nX, nT[j], n)  # [Alg. 2, step 3: tau^LOO_{i,j}, i in [n] u {n+j}; App. G.1 SGD bound]
        if not SCREEN_CFG["tau_train_R"]:
            # Diagnosis variant only: training-point bound eta*||X_i||*eps*||X_{n+j}|| WITHOUT the factor R, i.e.
            # 1/R of the App. G.1 bound (test-point bound keeps R).
            # [FROM AUTHORS' CODE: funcs/CP_screening.py:122-123, commit 3b37682]
            ti = ti / L.R
        p[j] = ((S - ti < St[j] + tj).sum() + 1) / (n + 1)  # [Alg. 2, step 4; Eq. (7)]
    return p, time.perf_counter() - t0


def ro_cfbh(L, X, y, Xt, rng):
    """RO-cfBH [Paper §6: "replaces all tau^LOO terms in (7) by the corresponding tau^RO terms; it is otherwise
    identical to LOO-cfBH"], 'following the spirit of Ndiaye (2022)': one replace-one fit per test point, on
    D u {(X_{n+j}, y~)} [Alg. 7, step 1]."""
    t0 = time.perf_counter()
    n = X.shape[0]
    # [ASSUMPTION: not specified in paper; y~ as for RO-StabCP (cp.ro_stab_cp, ASSUMPTION A7): mean of training y]
    ytil = 0.0 if CONFIG["ro_ytilde"] == "zero" else y.mean()
    nX, nT = np.linalg.norm(X, axis=1), np.linalg.norm(Xt, axis=1)
    p = np.empty(len(Xt))
    for j in range(len(Xt)):
        Xa = np.vstack([X, Xt[j:j + 1]]); ya = np.append(y, ytil)
        th = L.fit(Xa, ya, rng)  # [Alg. 7, step 1]
        pr = L.predict(th, Xa)
        S, Sj = score(y, pr[:-1]), score(C_THRESH, pr[-1])
        ti, tj = L.tau_ro(nX, nT[j], n)  # [App. G.1 SGD: tau^RO = 2 R eta eps ||X_i|| ||X_{n+j}||]
        p[j] = ((S - ti < Sj + tj).sum() + 1) / (n + 1)  # [Eq. (7) with tau^RO]
    return p, time.perf_counter() - t0
