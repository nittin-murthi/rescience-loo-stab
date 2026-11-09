# Screening experiment of [Paper §6, Fig. 4; App. G.4, Table 4]: cfBH vs RO-cfBH vs LOO-cfBH on the Kaggle
# campus-placement data. Paper version: arXiv:2504.12189v1 (https://arxiv.org/pdf/2504.12189v1; not vendored).
import argparse
import os
import sys
import time
import zlib

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from loostab import cp as cpmod  # noqa: E402
from loostab.cp import Learner  # noqa: E402
from loostab import screening as scmod  # noqa: E402
from loostab.screening import load_placement, cfbh, ro_cfbh, loo_cfbh, bh, fdp_power  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), "..")
MASTER_SEED = 20250416  # same master seed as experiments/run.py [ASSUMPTION: see run.py]
QS = (0.1, 0.2, 0.3)  # [Paper §6: "three target FDR levels q in {0.1, 0.2, 0.3}"]
N_REPS = 1000  # [Paper §6: "We repeated the experiment 1000 times"]
VARIANTS = {
    # [Paper §6: "each time leaving out 20% data points as the test data"]; new split every repetition
    "text": dict(test_frac=0.2, split_every=1),
    # Diagnosis only: test fraction 0.3 and a train/test split redrawn only every 100th repetition
    # [FROM AUTHORS' CODE: recruit.py (train_test_split(..., test_size=0.3) inside "if t % 100 == 0"), commit 3b37682]
    "a_split": dict(test_frac=0.3, split_every=100),
    # [FROM AUTHORS' CODE: recruit.py:18-24, commit 3b37682] feature scaling X/sqrt(p+1) + intercept
    "a_xscale": dict(test_frac=0.2, split_every=1, sc=dict(x_prep="authors")),
    # [FROM AUTHORS' CODE: funcs/CP_screening.py:122, commit 3b37682] LOO training bound without factor R
    "a_tau": dict(test_frac=0.2, split_every=1, sc=dict(tau_train_R=False)),
    # [FROM AUTHORS' CODE: funcs/CP_screening.py:11, commit 3b37682] cfBH 50/50 train/calibration
    "a_cal50": dict(test_frac=0.2, split_every=1, sc=dict(cal_frac=0.5)),
    # everything combined: split setup + scaling + tau + 50/50 + BH "<=" (funcs/utils.py:41-52) + y~ = 0
    # (funcs/CP_screening.py:49) + one set of R shuffles per repetition shared by all fits (recruit.py:36)
    "authors": dict(test_frac=0.3, split_every=100,
                    sc=dict(x_prep="authors", tau_train_R=False, cal_frac=0.5, bh_rule="leq"),
                    cp=dict(ro_ytilde="zero", sgd_coupled=True)),
    # "authors" with a fresh 30% test split every repetition: isolates the effect of reusing 10 splits
    "authors_resplit": dict(test_frac=0.3, split_every=1,
                            sc=dict(x_prep="authors", tau_train_R=False, cal_frac=0.5, bh_rule="leq"),
                            cp=dict(ro_ytilde="zero", sgd_coupled=True)),
    # "authors" with the App. G.1 bound restored (factor R on training points): what the paper's method gives
    "authors_fixtau": dict(test_frac=0.3, split_every=100,
                           sc=dict(x_prep="authors", tau_train_R=True, cal_frac=0.5, bh_rule="leq"),
                           cp=dict(ro_ytilde="zero", sgd_coupled=True)),
}
VARIANT = "text"


def run_task(rep):
    V = VARIANTS[VARIANT]
    X, y = load_placement()
    N = len(y)
    # data stream: depends on rep // split_every, so the authors'-setup variant reuses one split for 100 reps
    ds = np.random.SeedSequence([MASTER_SEED, zlib.crc32(b"screen-data"), rep // V["split_every"]])
    ss = np.random.SeedSequence([MASTER_SEED, zlib.crc32(b"screen-alg"), rep])
    rng_d, rng_a = np.random.default_rng(ds), np.random.default_rng(ss)
    m = int(round(V["test_frac"] * N))  # [ASSUMPTION: not specified; rounding 0.2 * 215 = 43 test points]
    perm = rng_d.permutation(N)
    te, tr = perm[:m], perm[m:]
    # [Paper §6: "We import the robust regression from Section 5 as the prediction method, optimized by SGD"]
    # -> Huber (eps = 1) linear model, R = 15, eta = 0.001 [Paper §4]
    L = Learner("sgd", R=15, eta=1e-3)
    if cpmod.CONFIG["sgd_coupled"]:
        L.set_coupled_perms(rng_a, len(tr))  # [FROM AUTHORS' CODE: recruit.py:36, commit 3b37682]
    rows = []
    for name, f in (("cfBH", cfbh), ("RO-cfBH", ro_cfbh), ("LOO-cfBH", loo_cfbh)):
        p, el = f(L, X[tr], y[tr], X[te], rng_a)
        for q in QS:  # [Fig. 4 caption: "Time cost does not vary with q"] -> p-values computed once per method
            t1 = time.perf_counter()
            rej = bh(p, q)  # [Alg. 2, step 5 / §6 BH procedure]
            fdp, pw = fdp_power(rej, y[te])
            rows.append(dict(rep=rep, q=q, method=name, fdp=fdp, power=pw, n_rej=int(rej.sum()),
                             time=el + time.perf_counter() - t1))
    return rows


def _set(v, warm=False):
    global VARIANT
    VARIANT = v
    V = VARIANTS[v]
    scmod.SCREEN_CFG.update(V.get("sc", {}))
    cpmod.CONFIG.update(V.get("cp", {}))
    if warm:  # compile the numba SGD kernel before timing anything (timing hygiene only; results unaffected)
        from loostab.models import fit_sgd
        fit_sgd(np.zeros((3, 2)), np.zeros(3), np.random.default_rng(0), R=1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=N_REPS)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--variant", default="text", choices=list(VARIANTS))
    a = ap.parse_args()
    _set(a.variant)
    out = os.path.join(ROOT, "results", "raw", "screen.csv" if a.variant == "text" else f"screen_{a.variant}.csv")
    t0 = time.time()
    rows = []
    from multiprocessing import Pool
    with Pool(a.workers, initializer=_set, initargs=(a.variant, True)) as pool:
        for i, r in enumerate(pool.imap_unordered(run_task, range(a.reps), chunksize=10)):
            rows.extend(r)
            if (i + 1) % 100 == 0:
                print(f"[screen] {i + 1}/{a.reps}, {time.time() - t0:.0f}s", flush=True)
    pd.DataFrame(rows).sort_values(["rep", "q", "method"]).to_csv(out, index=False)
    print(f"wrote {out} in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
