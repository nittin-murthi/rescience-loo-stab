# Data generation and loading.
# Paper version: arXiv:2504.12189v1 (https://arxiv.org/pdf/2504.12189v1; not vendored). Tags refer to its numbering.
import os
import numpy as np
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")


def synthetic(rng, n, m, setting="linear", d=100, rho=0.5, dgp="text", beta_sq=None):
    """[Paper §4]: X ~ N(0, Sigma/d), Sigma_ij = rho^|i-j| (AR(1), rho = 0.5), d = 100;
    Y = mu(X; beta) + eps, eps ~ N(0, 1); beta_j ∝ (1 - j/d)^5 normalised to ||beta||_2^2 = d."""
    if dgp == "authors_github":
        return _synthetic_authors(rng, n, m, setting, d)
    if dgp == "authors":
        # Diagnostic DGP of the ICLR supplementary: the AR(1) design of the text, but ||beta||^2 = 1/d.
        # [FROM AUTHORS' SUPPLEMENT: code_final/simul.py:27, 48 (DGP_lin/DGP_nonlin(n, m, d, 1, 'ar1')) and
        #  code_final/funcs/utils.py:151-191 (X = Z L' / sqrt(d), beta normalised then divided by sqrt(d))]
        return synthetic(rng, n, m, setting, d, rho, dgp="text", beta_sq=1.0 / d)
    idx = np.arange(d)
    Sigma = rho ** np.abs(idx[:, None] - idx[None, :])  # [Paper §4: Sigma_ij = rho^|i-j|]
    Lc = np.linalg.cholesky(Sigma / d)  # [Paper §4: covariance Sigma/d]
    X = rng.standard_normal((n + m, d)) @ Lc.T
    j = np.arange(1, d + 1)
    beta = (1 - j / d) ** 5  # [Paper §4: beta_j ∝ (1 - j/d)^5, j in [d]]
    beta *= np.sqrt(d) / np.linalg.norm(beta)  # [Paper §4: ||beta||_2^2 = d]
    if beta_sq is not None:  # diagnostic only (dgp="authors"): rescale to ||beta||^2 = beta_sq
        beta *= np.sqrt(beta_sq / d)
    if setting == "linear":
        mu = X @ beta  # [Paper §4: linear mu(x) = sum_j beta_j x_j]
    else:
        mu = np.exp(X / 10) @ beta  # [Paper §4: nonlinear mu(x) = sum_j beta_j exp(x_j/10)]
    Y = mu + rng.standard_normal(n + m)  # [Paper §4: eps_i ~ N(0, 1)]
    return X[:n], Y[:n], X[n:], Y[n:]


def _synthetic_authors(rng, n, m, setting, d):
    """Diagnostic DGP of the authors' GitHub version (our own re-implementation): X_i ~ N(0, I/d) (no AR(1)),
    beta_j ∝ (1 - j/d)^5 scaled so that ||beta||_2 = 1/sqrt(d) (i.e. ||beta||^2 = 1/d, not d), noise N(0,1).
    [FROM AUTHORS' CODE: funcs/utils.py:54-74 (DGP_lin, DGP_nonlin), commit 3b37682]"""
    X = rng.standard_normal((n + m, d)) / np.sqrt(d)
    j = np.arange(1, d + 1)
    beta = (1 - j / d) ** 5
    beta = beta / np.linalg.norm(beta) / np.sqrt(d)
    mu = X @ beta if setting == "linear" else np.exp(X / 10) @ beta
    Y = mu + rng.standard_normal(n + m)
    return X[:n], Y[:n], X[n:], Y[n:]


def _standardise(df):
    return (df - df.mean()) / df.std(ddof=0)


def load_real(name, x_scale="z"):
    """[Paper §5]: Boston Housing (506 x 13) and Diabetes (442 x 10). "All continuous variables have been
    normalized". Returns standardised X (N x d) and y (N,)."""
    if name == "diabetes":
        path = os.path.join(DATA_DIR, "diabetes.csv")
        if not os.path.exists(path):
            from sklearn.datasets import load_diabetes
            # raw (unscaled) version of Efron et al. (2004) [Paper §5 cites efron2004least]
            b = load_diabetes(as_frame=True, scaled=False)
            df = b.frame
            df.to_csv(path, index=False)
        df = pd.read_csv(path)
        target = "target"
    elif name == "boston":
        path = os.path.join(DATA_DIR, "boston.csv")
        if not os.path.exists(path):
            # [ASSUMPTION: not specified in paper which copy of Boston was used; chose the standard
            #  Harrison & Rubinfeld (1978) 506 x 13 table (identical to the former sklearn.datasets.load_boston /
            #  R mlbench::BostonHousing), downloaded by scripts/get_data.sh from
            #  raw.githubusercontent.com/selva86/datasets/master/BostonHousing.csv (sha256 recorded in data/README.md),
            #  because load_boston was removed from scikit-learn >= 1.2 and OpenML was unreachable (HTTP 500)]
            raw = pd.read_csv(os.path.join(DATA_DIR, "BostonHousing.csv"))
            raw.columns = [c.upper() for c in raw.columns]
            raw.to_csv(path, index=False)
        df = pd.read_csv(path)
        target = "MEDV"
    else:
        raise ValueError(name)
    # [ASSUMPTION: not specified in paper how "normalized" was done; chose z-scoring every column (features and
    #  response, incl. the binary CHAS/SEX columns) with full-data mean and sd, because the paper describes it as a
    #  one-off preprocessing step of the dataset]
    df = _standardise(df.astype(float))
    y = df[target].to_numpy()
    X = df.drop(columns=[target]).to_numpy()
    if x_scale == "z_sqrt_d":
        # diagnostic: divide the z-scored features by sqrt(d), so that ||X_i|| is about 1
        # [FROM AUTHORS' CODE: funcs/utils.py:84, commit 3b37682]
        X = X / np.sqrt(X.shape[1])
    return X, y


def holdout(rng, X, y, m):
    """[Paper §5]: "we randomly held out m data points (as the test data) ... and released the rest to all
    methods for training/calibration"."""
    perm = rng.permutation(len(y))
    te, tr = perm[:m], perm[m:]
    return X[tr], y[tr], X[te], y[te]
