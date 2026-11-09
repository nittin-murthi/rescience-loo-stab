# Conformal prediction methods compared in the paper.
# Paper version: arXiv:2504.12189v1 (https://arxiv.org/pdf/2504.12189v1; not vendored). Tags refer to its numbering.
import math
import time
import numpy as np

from .models import fit_rlm, fit_sgd, MLP, SkMLP, EPS_HUBER

ALPHA = 0.1  # [Paper §4: "alpha = 0.1"]

# Diagnostic switches. The defaults ("text") are the clean-room choices made from the paper alone. The other values
# reproduce choices found in the authors' code during the diagnosis step (DISCREPANCIES.md). Each one is our own
# re-implementation of a behaviour, not copied code. Set by experiments/run.py --variant.
CONFIG = dict(
    quantile="inf",      # "inf": Q_{1-alpha}(S u {inf}) [Paper §2]; "np_higher": numpy 'higher' quantile of S, no inf
    ro_ytilde="mean",    # "mean": y~ = mean(y) [ASSUMPTION A7]; "zero": y~ = 0
    full_grid="text",    # "text": cp.py make_grid + cell counting; "authors": grid [min y - sd, max y + sd], interval
                         #  between first and last accepted grid point
    sgd_coupled=False,   # True: one set of permutations of {0..n} per repetition, shared by all fits (see models.py)
    split_round="round", # "round": round(0.7 n); "floor": int(0.7 n)
    nn_impl="ours",      # "ours": sigmoid MLP of models.MLP; "sklearn": the supplement's MLPRegressor set-up (SkMLP)
    nn_tau="eq8",        # "eq8": tau = R eta gamma ||X_i|| ||X_{n+j}|| [Eq. (8)]; "const": tau = R eta for every point
    derand_K_real=30,    # number of splits for MM-/EM-SplitCP on real data
)


# ------------------------------------------------------------------------------------------------
# Quantiles
# ------------------------------------------------------------------------------------------------
def q_with_inf(scores, alpha=ALPHA):
    if CONFIG["quantile"] == "np_higher":
        # [FROM AUTHORS' CODE: funcs/CP.py:52,97,142,188 (np.quantile(..., 1-alpha, interpolation='higher') of the n
        #  scores, without +inf), commit 3b37682]
        return np.quantile(np.asarray(scores), 1 - alpha, method="higher")
    """Q_{1-alpha}(S u {inf}), the lower (1-alpha) sample quantile [Paper §2, definition below the
    FullCP display: Q_p(S) = inf{x : F_S(x) >= p}] of the n scores plus +inf.
    With n+1 values this is the ceil((1-alpha)(n+1))-th smallest; +inf if that rank is n+1."""
    s = np.sort(np.asarray(scores))
    n = s.shape[-1]
    k = math.ceil((1 - alpha) * (n + 1) - 1e-9)  # 1e-9 guards against float round-up of exact integers
    return np.inf if k > n else s[..., k - 1]


def q_plain(scores, alpha=ALPHA):
    """Q_{1-alpha}(S) without inf, used by OracleCP [Alg. 4, step 3]."""
    s = np.sort(np.asarray(scores))
    n = s.shape[-1]
    k = math.ceil((1 - alpha) * n - 1e-9)
    return s[..., k - 1]


# ------------------------------------------------------------------------------------------------
# Learners: a thin wrapper so every CP method can use RLM, SGD or an MLP.
# ------------------------------------------------------------------------------------------------
class Learner:
    """kind in {'rlm', 'sgd', 'nn'}.

    lam_bound: strong-convexity constant lambda used in the RLM bounds [Thm 2, Eq. (4)].
    """
    # [ASSUMPTION: not specified in paper; lambda in [Eq. (4)] is taken as 2, the strong-convexity constant of
    #  Omega(theta) = ||theta||^2 under the standard definition (Hessian 2I; the strong-convexity definition in [Paper §3.2.1] omits the t(1-t) factor, an apparent typo);
    #  lambda = 1 is reported as a sensitivity analysis (results/*_lam1 columns)]

    def __init__(self, kind, R=15, eta=1e-3, pen=1.0, lam_bound=2.0, hidden=(20,), eps=EPS_HUBER):
        self.kind, self.R, self.eta, self.pen, self.lam_bound = kind, R, eta, pen, lam_bound
        self.hidden, self.eps = hidden, eps
        self._init = None
        self._coupled = None
        self.pen_mat = None  # kernel study only: penalty theta' K theta [App. A.1]

    def fit(self, X, y, rng, R=None, warm=None):
        R = self.R if R is None else R
        if self.kind == "rlm":
            return fit_rlm(X, y, pen=self.pen, eps=self.eps, theta0=warm, P=self.pen_mat)
        if self.kind == "sgd":
            return fit_sgd(X, y, rng, R=R, eta=self.eta, eps=self.eps, perms=self._perms(R))
        if self.kind == "nn" and CONFIG["nn_impl"] == "sklearn":
            return SkMLP(self.hidden).fit(X, y, R=R, eta=self.eta)
        if self.kind == "nn":
            # [ASSUMPTION: not specified in paper; chose one fixed initialisation per repetition, shared by all
            #  fits within that repetition, because SGD stability (Thm 3/4) compares runs from the same theta_0]
            m = self._init.copy()
            return m.fit(X, y, rng, R=R, eta=self.eta, eps=self.eps, perms=self._perms(R))
        raise ValueError(self.kind)

    def set_coupled_perms(self, rng, n):
        """Diagnostic switch sgd_coupled: draw, once per repetition, R permutations of {0..n} for the ordinary fits
        and a separate set for FullCP (which uses fewer epochs).
        [FROM AUTHORS' CODE: simul.py:29-30, real.py:113-116, commit 3b37682]"""
        self._coupled = {self.R: np.stack([rng.permutation(n + 1) for _ in range(self.R)]).astype(np.int64)}
        self._coupled_full = np.stack([rng.permutation(n + 1) for _ in range(5)]).astype(np.int64)

    def _perms(self, R):
        if not CONFIG["sgd_coupled"]:
            return None
        return self._coupled[self.R] if R == self.R else self._coupled_full[:R]

    def init_nn(self, rng, d):
        self._init = MLP(self.hidden, rng, d)

    def predict(self, model, X):
        if self.kind in ("rlm", "sgd"):
            return X @ model  # f_theta(x) = x' theta [Paper §4]
        return model.predict(X)

    # -------------------------------------------------------------------- stability bounds
    def tau_loo(self, norms_train, norm_test, n):
        """LOO bounds tau^LOO_{i,j} for i in [n] (vector) and i = n+j (scalar)."""
        if self.kind == "rlm":
            # [App. G.1, RLM: tau^LOO_ij = 2 eps ||X_i|| (||X_{n+j}|| + (1/n) sum_i ||X_i||) / (lambda (n+1))]
            # = [Eq. (4)] with gamma=1 (absolute residual), nu_i=||X_i||, rho_i = eps||X_i|| (Huber is eps-Lipschitz)
            c = 2 * self.eps * (norm_test + norms_train.mean()) / (self.lam_bound * (n + 1))
            return c * norms_train, c * norm_test
        if self.kind == "nn" and CONFIG["nn_tau"] == "const":
            # [FROM AUTHORS' SUPPLEMENT: code_final/funcs/CP.py:263 (tau_aug = lr*epochs for every point, no norms)]
            return np.full_like(norms_train, self.R * self.eta), self.R * self.eta
        # [App. G.1, SGD: tau^LOO_ij = R eta eps ||X_i|| ||X_{n+j}||] = [Eq. (5)];
        # for the network the same heuristic with gamma=1 [Eq. (8)] (eps=1 so identical numerically)
        c = self.R * self.eta * (self.eps if self.kind == "sgd" else 1.0) * norm_test
        return c * norms_train, c * norm_test

    def tau_ro(self, norms_train, norm_test, n):
        if self.kind == "rlm":
            # [App. G.1, RLM: tau^RO_ij = 4 eps ||X_i|| ||X_{n+j}|| / (lambda (n+1))] = [Eq. (4)]
            c = 4 * self.eps * norm_test / (self.lam_bound * (n + 1))
            return c * norms_train, c * norm_test
        if self.kind == "nn" and CONFIG["nn_tau"] == "const":
            # [FROM AUTHORS' SUPPLEMENT: code_final/funcs/CP.py:197 (tau_aug = 2*lr*epochs for every point, no norms)]
            return np.full_like(norms_train, 2 * self.R * self.eta), 2 * self.R * self.eta
        # [App. G.1, SGD: tau^RO_ij = 2 R eta eps ||X_i|| ||X_{n+j}||] = [Eq. (5)] / [Eq. (8)] for the network
        c = 2 * self.R * self.eta * (self.eps if self.kind == "sgd" else 1.0) * norm_test
        return c * norms_train, c * norm_test


def _summ(lo, hi, y_test):
    cover = np.mean((y_test >= lo) & (y_test <= hi))
    length = np.mean(hi - lo)
    return cover, length


# ------------------------------------------------------------------------------------------------
# Methods. Each returns dict(coverage, length, time) for one repetition.
# ------------------------------------------------------------------------------------------------
def oracle_cp(L, X, y, Xt, yt, rng, alpha=ALPHA):
    """OracleCP [Alg. 4; App. C.1] (uses the TRUE test labels; impractical benchmark)."""
    t0 = time.perf_counter()
    m = Xt.shape[0]
    lo, hi = np.empty(m), np.empty(m)
    warm = None
    for j in range(m):
        Xa = np.vstack([X, Xt[j:j + 1]]); ya = np.append(y, yt[j])
        mod = L.fit(Xa, ya, rng, warm=warm)  # [Alg. 4, step 1: fit on D_j^{Y_{n+j}}]
        warm = mod if L.kind == "rlm" else None
        S = np.abs(ya - L.predict(mod, Xa))  # [Alg. 4, step 2: scores for i in [n] u {n+j}]
        q = q_plain(S, alpha)  # [Alg. 4, step 3: Q_{1-alpha}({S_ij} u {S_{n+j,j}})]
        c = L.predict(mod, Xt[j:j + 1])[0]
        lo[j], hi[j] = c - q, c + q
    el = time.perf_counter() - t0
    cov, ln = _summ(lo, hi, yt)
    return dict(coverage=cov, length=ln, time=el)


def make_grid(y, size=100):
    # [ASSUMPTION: not specified in paper (only "search grid G", size |Y| in Table 1); chose 100 equally
    #  spaced points on [min y - 0.25 r, max y + 0.25 r], r = range of training y, because this covers
    #  every plausible interval with a step ~1-2% of the response range]
    r = y.max() - y.min()
    return np.linspace(y.min() - 0.25 * r, y.max() + 0.25 * r, size)


def full_cp(L, X, y, Xt, yt, rng, alpha=ALPHA, grid_size=100, R_full=5):
    """FullCP by grid search [Alg. 5; App. C.2; Eq. (2)]."""
    if CONFIG["full_grid"] == "authors":
        return _full_cp_authors(L, X, y, Xt, yt, rng, alpha, grid_size, R_full)
    t0 = time.perf_counter()
    m = Xt.shape[0]
    G = make_grid(y, grid_size)
    step = G[1] - G[0]
    covers, lengths = np.empty(m), np.empty(m)
    # [Paper §4: "R=15 epochs for all methods, except R=5 for the very slow FullCP"]
    R = R_full if L.kind in ("sgd", "nn") else None
    for j in range(m):
        Xa = np.vstack([X, Xt[j:j + 1]])
        acc = np.zeros(grid_size, bool)
        warm = None
        for g, yy in enumerate(G):  # [Alg. 5: for y in G]
            ya = np.append(y, yy)
            # [ASSUMPTION: not specified in paper; RLM fits are warm-started from the previous grid point
            #  (a pure speed-up: the RLM optimum is unique, so results are unaffected)]
            mod = L.fit(Xa, ya, rng, R=R, warm=warm)  # [Alg. 5, step 1: fit on D_j^y]
            warm = mod if L.kind == "rlm" else None
            pred = L.predict(mod, Xa)
            S = np.abs(y - pred[:-1])  # [Alg. 5, step 2: S^y_ij for i in [n]]
            q = q_with_inf(S, alpha)  # [Alg. 5, step 3]
            acc[g] = abs(yy - pred[-1]) <= q  # [Alg. 5, step 4: keep y if S^y_{n+j,j} <= Q]
        # [ASSUMPTION: not specified in paper; chose length = (#accepted grid points) x step and "covered" iff the
        #  true y is within step/2 of an accepted grid point, i.e. each grid point represents its grid cell]
        lengths[j] = acc.sum() * step
        covers[j] = np.any(acc & (np.abs(G - yt[j]) <= step / 2 + 1e-12))
    el = time.perf_counter() - t0
    return dict(coverage=covers.mean(), length=lengths.mean(), time=el)


def _full_cp_authors(L, X, y, Xt, yt, rng, alpha, grid_size, R_full):
    """Diagnostic FullCP variant reproducing the authors' grid search behaviour (our own re-implementation):
    grid of 100 points on [min y - sd(y), max y + sd(y)]; scan upward to the first accepted point (lower end) and
    downward to the last accepted point (upper end); the set is taken to be the interval between them.
    [FROM AUTHORS' CODE: funcs/CP.py:34-71, commit 3b37682]"""
    t0 = time.perf_counter()
    m = Xt.shape[0]
    G = np.linspace(y.min() - y.std(), y.max() + y.std(), grid_size)
    R = R_full if L.kind in ("sgd", "nn") else None
    covers, lengths = np.empty(m), np.empty(m)

    def accept(Xa, yy):
        ya = np.append(y, yy)
        mod = L.fit(Xa, ya, rng, R=R)
        pred = L.predict(mod, Xa)
        S = np.abs(y - pred[:-1])
        return abs(yy - pred[-1]) <= q_with_inf(S, alpha)

    for j in range(m):
        Xa = np.vstack([X, Xt[j:j + 1]])
        lo_i = next((g for g in range(grid_size) if accept(Xa, G[g])), None)
        if lo_i is None:  # nothing accepted (the authors' loop would not terminate); record an empty set
            covers[j], lengths[j] = 0.0, 0.0
            continue
        hi_i = next(g for g in range(grid_size - 1, lo_i - 1, -1) if g == lo_i or accept(Xa, G[g]))
        lo, hi = G[lo_i], G[hi_i]
        covers[j], lengths[j] = float(lo <= yt[j] <= hi), hi - lo
    return dict(coverage=covers.mean(), length=lengths.mean(), time=time.perf_counter() - t0)


def split_cp(L, X, y, Xt, yt, rng, alpha=ALPHA, frac=0.7, return_interval=False):
    """SplitCP [Alg. 6; App. C.3] with 70% training / 30% calibration [Paper §4]."""
    t0 = time.perf_counter()
    n = X.shape[0]
    perm = rng.permutation(n)
    ntr = int(round(frac * n))  # [ASSUMPTION: not specified in paper; rounding of 0.7n to the nearest integer]
    if CONFIG["split_round"] == "floor":
        ntr = int(frac * n)  # [FROM AUTHORS' CODE: funcs/CP.py:82 (int(n * 0.7)), commit 3b37682]
    tr, ca = perm[:ntr], perm[ntr:]
    mod = L.fit(X[tr], y[tr], rng)  # [Alg. 6, step 1]
    S = np.abs(y[ca] - L.predict(mod, X[ca]))  # [Alg. 6, step 2]
    q = q_with_inf(S, alpha)
    c = L.predict(mod, Xt)
    lo, hi = c - q, c + q  # [Alg. 6, step 3]
    el = time.perf_counter() - t0
    if return_interval:
        return lo, hi
    cov, ln = _summ(lo, hi, yt)
    return dict(coverage=cov, length=ln, time=el)


def ro_stab_cp(L, X, y, Xt, yt, rng, alpha=ALPHA, extra_lams=()):
    """RO-StabCP [Alg. 7; App. C.4; Eq. (3)], Ndiaye (2022)."""
    t0 = time.perf_counter()
    n, m = X.shape[0], Xt.shape[0]
    # [ASSUMPTION: not specified in paper (Alg. 7 takes "initial guesses y~"); chose y~ = mean of training y
    #  because it needs no extra model fit and is the natural data-driven guess]
    ytil = y.mean()
    if CONFIG["ro_ytilde"] == "zero":
        ytil = 0.0  # [FROM AUTHORS' CODE: funcs/CP.py:112 (zhat = 0), commit 3b37682]
    nX, nT = np.linalg.norm(X, axis=1), np.linalg.norm(Xt, axis=1)
    lo, hi = np.empty(m), np.empty(m)
    extra = {lam: (np.empty(m), np.empty(m)) for lam in extra_lams}
    warm = None
    for j in range(m):
        Xa = np.vstack([X, Xt[j:j + 1]]); ya = np.append(y, ytil)
        mod = L.fit(Xa, ya, rng, warm=warm)  # [Alg. 7, step 1: fit on D_j^{y~}]
        warm = mod if L.kind == "rlm" else None
        pred = L.predict(mod, Xa)
        S = np.abs(y - pred[:-1])  # [Alg. 7, step 2]
        ti, tj = L.tau_ro(nX, nT[j], n)  # [Alg. 7, step 3]
        half = q_with_inf(S + ti, alpha) + tj  # [Alg. 7, step 4]
        lo[j], hi[j] = pred[-1] - half, pred[-1] + half
        for lam in extra_lams:  # sensitivity: other lambda in the RLM bound (no extra fits needed)
            ti2, tj2 = ti * L.lam_bound / lam, tj * L.lam_bound / lam
            h2 = q_with_inf(S + ti2, alpha) + tj2
            extra[lam][0][j], extra[lam][1][j] = pred[-1] - h2, pred[-1] + h2
    el = time.perf_counter() - t0
    cov, ln = _summ(lo, hi, yt)
    out = dict(coverage=cov, length=ln, time=el)
    for lam, (a, b) in extra.items():
        out[f"lam{lam:g}"] = _summ(a, b, yt)
    return out


def loo_stab_cp(L, X, y, Xt, yt, rng, alpha=ALPHA, extra_lams=()):
    """LOO-StabCP [Alg. 1] -- the method under replication. One model fit for all m test points."""
    t0 = time.perf_counter()
    n, m = X.shape[0], Xt.shape[0]
    mod = L.fit(X, y, rng)  # [Alg. 1, step 1: fit f-hat on D]
    S = np.abs(y - L.predict(mod, X))  # [Alg. 1, step 2: uncorrected scores]
    c = L.predict(mod, Xt)
    nX, nT = np.linalg.norm(X, axis=1), np.linalg.norm(Xt, axis=1)
    lo, hi = np.empty(m), np.empty(m)
    for j in range(m):  # [Alg. 1: for j in [m]]
        ti, tj = L.tau_loo(nX, nT[j], n)  # [Alg. 1, step 3]
        half = q_with_inf(S + ti, alpha) + tj  # [Alg. 1, step 4]
        lo[j], hi[j] = c[j] - half, c[j] + half
    el = time.perf_counter() - t0
    cov, ln = _summ(lo, hi, yt)
    out = dict(coverage=cov, length=ln, time=el)
    for lam in extra_lams:
        a, b = np.empty(m), np.empty(m)
        for j in range(m):
            ti, tj = L.tau_loo(nX, nT[j], n)
            ti, tj = ti * L.lam_bound / lam, tj * L.lam_bound / lam
            h = q_with_inf(S + ti, alpha) + tj
            a[j], b[j] = c[j] - h, c[j] + h
        out[f"lam{lam:g}"] = _summ(a, b, yt)
    # diagnostic (not in paper): training-set fit quality of the single model
    out["train_r2"] = 1 - np.mean((y - L.predict(mod, X)) ** 2) / np.var(y)
    return out


# ------------------------------------------------------------------------------------------------
# Derandomised split conformal [App. B; Fig. 7, Fig. 8], 30 splits [App. B: "we merged 30 splits"].
# The paper defers definitions to Solari & Djordjilovic (2022) and Gasparin & Ramdas (2024).
# ------------------------------------------------------------------------------------------------
def _vote_measure(los, his, yt, rule):
    """los, his: (K, m) interval endpoints. Returns per-test (covered, measure) of the merged set."""
    K, m = los.shape
    cov, meas = np.empty(m), np.empty(m)
    for j in range(m):
        pts = np.unique(np.concatenate([los[:, j], his[:, j]]))
        mids = (pts[:-1] + pts[1:]) / 2
        inside = (los[:, j][:, None] <= mids[None]) & (mids[None] <= his[:, j][:, None])  # (K, cells)
        keep = rule(inside)
        meas[j] = np.sum((pts[1:] - pts[:-1])[keep])
        ins_y = (los[:, j] <= yt[j]) & (yt[j] <= his[:, j])
        cov[j] = rule(ins_y[:, None])[0]
    return cov.mean(), meas.mean()


def _mm_rule(inside):
    # [App. B: MM-SplitCP = "the range covered by more than half of these intervals"]
    return inside.mean(0) > 0.5


def _em_rule(inside):
    # [App. B: EM-SplitCP, "majority vote correction" for exchangeable sets, Gasparin & Ramdas (2024)]
    # [ASSUMPTION: not specified in paper; implemented the exchangeable majority vote of Gasparin & Ramdas
    #  (2024, Prop. "C^E"): keep y iff for every k=1..K the running vote (1/k) sum_{l<=k} 1{y in C_l} > 1/2]
    run = np.cumsum(inside, 0) / np.arange(1, inside.shape[0] + 1)[:, None]
    return np.all(run > 0.5, axis=0)


def derandom_split_cp(L, X, y, Xt, yt, rng, rule="mm", K=30, alpha=ALPHA):
    t0 = time.perf_counter()
    los, his = [], []
    for _ in range(K):
        # [App. B: each split interval built at level 1 - alpha/2 (Solari & Djordjilovic)]
        # [ASSUMPTION: not specified in paper for EM; used the same 1 - alpha/2 split intervals for EM]
        lo, hi = split_cp(L, X, y, Xt, yt, rng, alpha=alpha / 2, return_interval=True)
        los.append(lo); his.append(hi)
    cov, ln = _vote_measure(np.array(los), np.array(his), yt, _mm_rule if rule == "mm" else _em_rule)
    return dict(coverage=cov, length=ln, time=time.perf_counter() - t0)
