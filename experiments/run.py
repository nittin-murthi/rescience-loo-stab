# Experiment runner: one task = one (experiment, setting, repetition); every method is run on the same data.
# Paper version: arXiv:2504.12189v1 (https://arxiv.org/pdf/2504.12189v1; not vendored). Tags refer to its numbering.
import argparse
import os
import sys
import time
import zlib

# [ASSUMPTION: not specified in paper (hardware/threads for the "Time" columns of Table 2 / Fig. 1-2); timings are
#  wall-clock seconds of one CP method on one repetition, single-threaded BLAS, so methods are comparable]
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from loostab import cp as cpmod  # noqa: E402
from loostab.cp import (Learner, oracle_cp, full_cp, split_cp, ro_stab_cp, loo_stab_cp,  # noqa: E402
                        derandom_split_cp)
from loostab.data import synthetic, load_real, holdout  # noqa: E402
from loostab.kernels import kernel_features  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), "..")
MASTER_SEED = 20250416  # [ASSUMPTION: not specified in paper; fixed master seed = arXiv v1 date, for reproducibility]
VARIANT = "text"
# Variants. "text" is the clean-room primary analysis. "centered" is a sensitivity analysis decided before the
# authors' code was read. The "a_*" and "authors" variants were added in the diagnosis step: each switches on choices
# found in the authors' code (GitHub repository at commit 3b37682, and later the ICLR supplementary material), alone
# or all together. See DISCREPANCIES.md.
AUTHORS_CP = dict(quantile="np_higher", ro_ytilde="zero", full_grid="authors", split_round="floor")
VARIANTS = {
    "text": dict(),
    "centered": dict(center=True),
    # Synthetic design of the ICLR supplementary (AR(1) design of the text, ||beta||^2 = 1/d)
    "a_dgp": dict(dgp="authors"),  # [FROM AUTHORS' SUPPLEMENT: code_final/simul.py:27, 48; funcs/utils.py:151-191]
    # Synthetic design of the later GitHub version (iid features, ||beta||^2 = 1/d)
    "a_dgp_github": dict(dgp="authors_github"),   # [FROM AUTHORS' CODE: funcs/utils.py:54-74, commit 3b37682]
    "a_scale": dict(x_scale="z_sqrt_d"),          # [FROM AUTHORS' CODE: funcs/utils.py:84, commit 3b37682]
    "a_coupled": dict(cp=dict(sgd_coupled=True)),  # [FROM AUTHORS' CODE: simul.py:29-30, commit 3b37682]
    "a_cpdetails": dict(cp=AUTHORS_CP),           # [FROM AUTHORS' CODE: funcs/CP.py:34-188, commit 3b37682]
    # neural networks: the authors' CP and data choices (D2-D7) with OUR network (sigmoid, Huber, plain SGD)
    "a_oursnet": dict(x_scale="z_sqrt_d", cp=dict(AUTHORS_CP, sgd_coupled=True)),
    # neural networks: + the supplement's network (scikit-learn MLPRegressor set-up), still the Eq. (8) bound
    "a_sknet": dict(x_scale="z_sqrt_d", cp=dict(AUTHORS_CP, sgd_coupled=True, nn_impl="sklearn")),
    # kernels: only the supplement's kernel hyper-parameters (gamma = 0.1, eta = 1e-5), text design and CP rules
    "a_kparams": dict(kernel=dict(rbf_gamma=0.1, eta_kernel=1e-5, rlm=False)),
    # every choice found in the authors' code and supplementary material
    "authors": dict(dgp="authors", x_scale="z_sqrt_d",
                    cp=dict(AUTHORS_CP, sgd_coupled=True, nn_impl="sklearn", nn_tau="const", derand_K_real=50),
                    kernel=dict(rbf_gamma=0.1, eta_kernel=1e-5, rlm=False)),
    # kernels, diagnosis of C6: the authors' setup with the response centred at its training mean (as in "centered"),
    # to check whether the kernels shorten the nonlinear intervals only by absorbing the mean offset of Y
    "authors_centered": dict(dgp="authors", center=True, x_scale="z_sqrt_d",
                             cp=dict(AUTHORS_CP, sgd_coupled=True, nn_impl="sklearn", nn_tau="const", derand_K_real=50),
                             kernel=dict(rbf_gamma=0.1, eta_kernel=1e-5, rlm=False)),
    # the earlier "authors" variant, built from the GitHub repository alone (kept for the record)
    "authors_github": dict(dgp="authors_github", x_scale="z_sqrt_d", cp=dict(AUTHORS_CP, sgd_coupled=True)),
}
# [FROM AUTHORS' SUPPLEMENT: real_derandom.py:38-64 (K = 50)], [FROM AUTHORS' SUPPLEMENT: funcs/CP.py:263, 197
#  (constant NN bounds)], [FROM AUTHORS' SUPPLEMENT: kernel.py:35-44 (gamma = 0.1, lr = 1e-5 with a kernel)]
# Kernel study, reading of the paper text: [App. A.1: sigma = 0.1 in exp(-||x-x'||^2 / (2 sigma^2))] -> gamma = 50;
# [ASSUMPTION: not specified in paper; step size for kernel SGD taken as the §4 value eta = 0.001]; kernel RLM with
# penalty theta' K theta is run as well because App. A.1 describes it [App. A.1, display for theta-hat].
KERNEL_TEXT = dict(rbf_gamma=1.0 / (2 * 0.1 ** 2), eta_kernel=1e-3, rlm=True)
N_REPS = 100  # [Paper §4 and §5: "Each experiment was repeated 100 times"]


def task_seed(key, rep):
    # independent, reproducible stream per (setting, repetition)
    return np.random.SeedSequence([MASTER_SEED, zlib.crc32(key.encode()), rep])


def _learner(model, nn_hidden=None):
    if model == "rlm":
        return Learner("rlm", pen=1.0, lam_bound=2.0)  # [Paper §4: Omega(theta)=||theta||^2]; lambda: see cp.py
    if model == "sgd":
        return Learner("sgd", R=15, eta=1e-3)  # [Paper §4: R=15, eta=0.001]
    return Learner("nn", R=30, eta=1e-3, hidden=nn_hidden)  # [Paper §5: eta=0.001, R=30]


def run_task(args):
    exp, cfg, rep = args
    key = "|".join(f"{k}={v}" for k, v in sorted(cfg.items())) + f"|{exp}"
    ss = task_seed(key, rep)
    rng_data, rng_alg = [np.random.default_rng(s) for s in ss.spawn(2)]
    rows = []
    if exp in ("sim", "kernel"):
        # [Paper §4: n = m = 100]
        V = VARIANTS[VARIANT]
        X, y, Xt, yt = synthetic(rng_data, 100, 100, cfg["setting"], dgp=V.get("dgp", "text"))
        if V.get("center"):
            # [ASSUMPTION: not specified in paper; sensitivity variant only. Under the nonlinear model
            #  E[Y] = sum_j beta_j E[exp(x_j/10)] ~ 55, which the no-intercept predictor f(x)=x'theta [Paper §4] cannot
            #  fit. Variant "centered" subtracts the TRAINING-sample mean of Y from all responses (train and test)
            #  before any CP method runs; this shift does not change interval lengths or coverage indicators except
            #  through the fitted model]
            ybar = y.mean()
            y, yt = y - ybar, yt - ybar
    else:
        Xa, ya = load_real(cfg["data"], x_scale=VARIANTS[VARIANT].get("x_scale", "z"))
        X, y, Xt, yt = holdout(rng_data, Xa, ya, cfg["m"])  # [Paper §5: hold out m in {1, 100}]
    L = _learner(cfg["model"], cfg.get("hidden"))
    if exp == "kernel":
        KP = VARIANTS[VARIANT].get("kernel", KERNEL_TEXT)
        X, Xt, K = kernel_features(cfg["kernel"], X, Xt, KP["rbf_gamma"])
        if K is not None:
            if L.kind == "sgd":
                L.eta = KP["eta_kernel"]  # [FROM AUTHORS' SUPPLEMENT: kernel.py:44 (lr = 0.00001)] or KERNEL_TEXT
            else:
                # [App. A.1: penalty lambda theta' K theta, "a special case of RLM, thus Theorem 2 applies"]
                # [ASSUMPTION: not specified in paper; the strong-convexity constant in Eq. (4) is taken as
                #  2 lambda_min(K) (Hessian of theta' K theta is 2K); the supplement's code divides its RLM bound by
                #  lambda_min(K) in the same way: FROM AUTHORS' SUPPLEMENT: funcs/CP.py:181-182, 254-255]
                L.pen_mat = K
                L.lam_bound = 2.0 * float(np.linalg.eigvalsh(K).min())
    if cpmod.CONFIG["sgd_coupled"] and L.kind in ("sgd", "nn"):
        L.set_coupled_perms(rng_alg, X.shape[0])
    if exp == "kernel":
        # [App. A.1, Fig. 5: SplitCP, RO-StabCP and LOO-StabCP]
        methods = [("SplitCP", split_cp, {}), ("RO-StabCP", ro_stab_cp, {}), ("LOO-StabCP", loo_stab_cp, {})]
    elif exp == "nn":
        L.init_nn(rng_alg, X.shape[1])
        # [Paper §5, Fig. 3 / App. A.2, Fig. 6: SplitCP, RO-StabCP and LOO-StabCP are compared]
        methods = [("SplitCP", split_cp, {}), ("RO-StabCP", ro_stab_cp, {}), ("LOO-StabCP", loo_stab_cp, {})]
    else:
        extra = {"extra_lams": (1.0,)} if cfg["model"] == "rlm" else {}  # lambda sensitivity (A1; private NOTES.md is not in this public snapshot)
        # [Paper §4/§5, Table 2/3, Fig. 1/2: OracleCP, FullCP, SplitCP, RO-StabCP, LOO-StabCP]
        methods = [("OracleCP", oracle_cp, {}), ("FullCP", full_cp, {}), ("SplitCP", split_cp, {}),
                   ("RO-StabCP", ro_stab_cp, extra), ("LOO-StabCP", loo_stab_cp, extra)]
        if exp == "sim" or cfg["m"] == 100:
            # [App. B, Fig. 7/8: MM-SplitCP and EM-SplitCP with 30 splits, on the §4 and §5 settings]
            # [ASSUMPTION: not specified in paper which m was used for Fig. 8; chose m=100]
            K_d = 30 if exp == "sim" else cpmod.CONFIG["derand_K_real"]  # [App. B: "we merged 30 splits"]
            methods += [("MM-SplitCP", derandom_split_cp, {"rule": "mm", "K": K_d}),
                        ("EM-SplitCP", derandom_split_cp, {"rule": "em", "K": K_d})]
    for name, f, kw in methods:
        out = f(L, X, y, Xt, yt, rng_alg, **kw)
        row = dict(exp=exp, **cfg, rep=rep, method=name, coverage=out["coverage"], length=out["length"],
                   time=out["time"])
        if "lam1" in out:
            row["coverage_lam1"], row["length_lam1"] = out["lam1"]
        if "train_r2" in out:
            row["train_r2"] = out["train_r2"]
        rows.append(row)
    return rows


def _set_variant(v):
    global VARIANT
    VARIANT = v
    cpmod.CONFIG.update(VARIANTS[v].get("cp", {}))


def configs(exp):
    if exp == "sim":
        return [dict(setting=s, model=m) for s in ("linear", "nonlinear") for m in ("rlm", "sgd")]
    if exp == "real":
        return [dict(data=d, m=mm, model=m) for d in ("boston", "diabetes") for mm in (1, 100)
                for m in ("rlm", "sgd")]
    if exp == "kernel":
        # [App. A.1, Fig. 5: the two §4 settings, without a kernel, with the RBF and with the polynomial kernel]
        ms = ("sgd", "rlm") if VARIANTS[VARIANT].get("kernel", KERNEL_TEXT)["rlm"] else ("sgd",)
        return [dict(setting=s, kernel=k, model=m) for s in ("linear", "nonlinear") for k in ("none", "rbf", "poly")
                for m in ms]
    if exp == "nn":
        # [Paper §5, Fig. 3: one hidden layer, 20 sigmoid units; App. A.2, Fig. 6: two hidden layers (10, 5)]
        # [ASSUMPTION: not specified in paper which m the NN study used; chose m=100]
        return [dict(data=d, m=100, model="nn", hidden=h) for d in ("boston", "diabetes") for h in ((20,), (10, 5))]
    raise ValueError(exp)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("exp", choices=["sim", "real", "nn", "kernel"])
    ap.add_argument("--reps", type=int, default=N_REPS)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--out", default=None)
    ap.add_argument("--variant", default="text", choices=list(VARIANTS))
    a = ap.parse_args()
    _set_variant(a.variant)
    tasks = [(a.exp, c, r) for c in configs(a.exp) for r in range(a.reps)]
    out = a.out or os.path.join(ROOT, "results", "raw", f"{a.exp}.csv" if a.variant == "text" else f"{a.exp}_{a.variant}.csv")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    t0 = time.time()
    rows = []
    from multiprocessing import Pool
    with Pool(a.workers, initializer=_set_variant, initargs=(a.variant,)) as pool:
        for i, r in enumerate(pool.imap_unordered(run_task, tasks, chunksize=1)):
            rows.extend(r)
            if (i + 1) % 20 == 0 or i + 1 == len(tasks):
                print(f"[{a.exp}] {i + 1}/{len(tasks)} tasks, {time.time() - t0:.0f}s", flush=True)
    df = pd.DataFrame(rows)
    if "kernel" in df and a.exp == "kernel":
        df["variant"] = a.variant
    if "hidden" in df:
        df["hidden"] = df["hidden"].astype(str)
    df.sort_values([c for c in df.columns if c in ("setting", "data", "m", "kernel", "model", "hidden", "rep")]).to_csv(
        out, index=False)
    print(f"wrote {out} in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
