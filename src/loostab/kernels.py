# Kernel features for the kernel study [App. A.1, Fig. 5] (claim C6).
# Paper version: arXiv:2504.12189v1. Written after we had read the authors' ICLR 2025 supplementary material
# (code_final/kernel.py), so this part is NOT a clean-room implementation; choices taken from that code are
# tagged [FROM AUTHORS' SUPPLEMENT: ...].
import numpy as np


def rbf(A, B, gamma):
    """k(x, x') = exp(-gamma ||x - x'||^2).
    [App. A.1: k_RBF(x, x') = exp(-||x - x'||^2 / (2 sigma^2)), sigma = 0.1] -> gamma = 1 / (2 sigma^2) = 50;
    [FROM AUTHORS' SUPPLEMENT: code_final/funcs/utils.py:44-47 (kernel_matrix: np.exp(-gamma * ||x1 - x2||^2)) and
     code_final/kernel.py:35-36 (gamma = 0.1)] -> gamma = 0.1, i.e. sigma = sqrt(5) ~ 2.24 in the paper's notation."""
    sq = (A ** 2).sum(1)[:, None] + (B ** 2).sum(1)[None, :] - 2 * A @ B.T
    return np.exp(-gamma * np.maximum(sq, 0.0))


def poly(A, B, c=1.0, deg=2):
    """[App. A.1: k_Poly(x, x') = (x'x' + c)^d with c = 1, d = 2]
    [FROM AUTHORS' SUPPLEMENT: code_final/funcs/utils.py:48-51 and code_final/kernel.py:39-40 (coef0=1, degree 2)]"""
    return (A @ B.T + c) ** deg


def kernel_features(kind, X, Xt, gamma):
    """Empirical kernel map: a point x is represented by k_x = (k(x, X_1), ..., k(x, X_n)), the n training points
    being the centres; the predictor is k_x' theta with theta in R^n.
    [App. A.1: theta-hat = argmin_{theta in R^n} (1/n) sum_i l(Y_i, k_i' theta) + lambda theta' K theta, k_i the
     i-th row of K]
    [FROM AUTHORS' SUPPLEMENT: code_final/kernel.py:37, 41 (D = (K(X, X), Y), D_test = (K(X_test, X), Y_test));
     the same centres are used by every CP method, including the split-conformal fit and the RO refits]
    Returns (Phi_train, Phi_test, K)."""
    if kind == "none":
        return X, Xt, None
    f = (lambda A, B: rbf(A, B, gamma)) if kind == "rbf" else poly
    K = f(X, X)
    return K, f(Xt, X), K
