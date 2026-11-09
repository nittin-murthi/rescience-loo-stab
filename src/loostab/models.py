# Model fitting for LOO-StabCP replication.
# Paper version: arXiv:2504.12189v1 (https://arxiv.org/pdf/2504.12189v1; not vendored). Tags refer to its numbering.
import numpy as np
from numba import njit

EPS_HUBER = 1.0  # [Paper §4: "we set eps = 1 throughout"]


def huber_loss(r, eps=EPS_HUBER):
    # [Paper §4, Huber loss display: 1/2 r^2 if |r|<=eps, eps|r| - eps^2/2 otherwise]
    a = np.abs(r)
    return np.where(a <= eps, 0.5 * r * r, eps * a - 0.5 * eps * eps)


def huber_psi(r, eps=EPS_HUBER):
    # derivative of the Huber loss w.r.t. the residual r = y - x'theta (bounded by eps,
    # which is why rho_i = eps*||X_i|| in [App. G.1])
    return np.clip(r, -eps, eps)


def fit_rlm(X, y, pen=1.0, eps=EPS_HUBER, theta0=None, tol=1e-10, max_iter=100, P=None):
    """Regularised loss minimisation [Alg. 8, step 1; Paper §3.2.1 display for theta-hat].

    Objective: (1/N) sum_i Huber(y_i - x_i'theta) + pen * ||theta||^2
    [Paper §4: "In RLM, we set Omega(theta) = ||theta||^2"] -> pen = 1.
    Linear predictor f_theta(x) = x'theta [Paper §4: "f_theta(x) = x^T theta"].
    Kernel study only: with a penalty matrix P the penalty is pen * theta' P theta, P = K
    [App. A.1: lambda theta' K theta].
    """
    # [ASSUMPTION: not specified in paper (text says "gradient descent \citep{cvxpy}" and eta=0.001);
    #  chose a damped Newton method solved to ||grad||<1e-10 because Thm 2 assumes the exact minimiser]
    N, d = X.shape
    theta = np.zeros(d) if theta0 is None else theta0.copy()

    Pm = np.eye(d) if P is None else P

    def obj(t):
        return huber_loss(y - X @ t, eps).mean() + pen * t @ Pm @ t

    f = obj(theta)
    for _ in range(max_iter):
        r = y - X @ theta
        g = -(X.T @ huber_psi(r, eps)) / N + 2.0 * pen * (Pm @ theta)
        if np.max(np.abs(g)) < tol:
            break
        w = (np.abs(r) <= eps).astype(float)
        H = (X.T * w) @ X / N + 2.0 * pen * Pm  # generalised Hessian of the Huber part
        step = np.linalg.solve(H, g)
        s = 1.0
        while True:  # backtracking line search (Armijo) keeps the semismooth Newton globally convergent
            t_new = theta - s * step
            f_new = obj(t_new)
            if f_new <= f - 1e-4 * s * (g @ step) or s < 1e-8:
                break
            s *= 0.5
        theta, f = t_new, f_new
    return theta


@njit(cache=True)
def _sgd_kernel(X, y, perms, eta, eps, theta):
    # [Alg. 9 steps 2-3]: for each epoch, visit samples in permuted order and update
    # theta := theta - eta * grad_theta loss(Y_pi, f_theta(X_pi)); for Huber + linear model
    # grad = -psi(y - x'theta) * x.
    R, N = perms.shape
    d = X.shape[1]
    N_data = X.shape[0]
    for r in range(R):
        for k in range(N):
            i = perms[r, k]
            if i >= N_data:
                continue  # coupled-permutation mode: indices of points absent from this fit are skipped
            res = y[i]
            for c in range(d):
                res -= X[i, c] * theta[c]
            if res > eps:
                res = eps
            elif res < -eps:
                res = -eps
            for c in range(d):
                theta[c] += eta * res * X[i, c]
    return theta


def fit_sgd(X, y, rng, R=15, eta=1e-3, eps=EPS_HUBER, perms=None):
    """SGD with random reshuffling [Alg. 9; Paper §3.2.2].

    R = 15 epochs, eta = 0.001 [Paper §4: "we ran SGD for R=15 epochs ... learning rate eta = 0.001"].
    """
    N, d = X.shape
    # [ASSUMPTION: not specified in paper; chose theta_0 = 0 because Alg. 9 only says "initial value theta_0"
    #  and zero is the conventional, data-independent choice]
    theta = np.zeros(d)
    # [Alg. 9, step 2: "Sample a permutation pi of [n] uniformly at random" once per epoch]
    # [ASSUMPTION: not specified in paper; each separate fit draws its own permutations from the
    #  repetition's seeded generator because the paper does not couple fits]
    if perms is None:
        perms = np.stack([rng.permutation(N) for _ in range(R)]).astype(np.int64)
    else:
        # Diagnostic switch "sgd_coupled": one set of R permutations of {0..n} per repetition, shared by every fit;
        # a fit on fewer points skips the missing indices. This is the coupling used in the proof of Thm 3
        # [App. F, proof of Thm 3: "pi' obtained from pi by excluding the kth entry"].
        # [FROM AUTHORS' CODE: simul.py:29-30 and funcs/utils.py:26-29, commit 3b37682]
        perms = perms[:R]
    return _sgd_kernel(np.ascontiguousarray(X, dtype=np.float64), np.ascontiguousarray(y, dtype=np.float64),
                       perms, float(eta), float(eps), theta)


# ----------------------------------------------------------------------------------------------
# One-hidden-layer / two-hidden-layer sigmoid networks trained by SGD [Paper §5, last paragraphs;
# Fig. 3 (20 sigmoid hidden units, eta=0.001, R=30); App. A.2, Fig. 6 (two hidden layers 10 and 5)]
# ----------------------------------------------------------------------------------------------

def _sigmoid(z):
    return 1.0 / (1.0 + np.exp(-z))


@njit(cache=True)
def _nn_kernel(X, y, perms, eta, eps, Ws, bs, n_layers):
    # SGD with reshuffling [Alg. 9] on a sigmoid MLP with linear output and Huber loss.
    R, N = perms.shape
    N_data = X.shape[0]
    for r in range(R):
        for k in range(N):
            i = perms[r, k]
            if i >= N_data:
                continue  # coupled-permutation mode (see fit_sgd)
            # forward
            acts = [X[i].copy()]
            for l in range(n_layers):
                z = Ws[l] @ acts[l] + bs[l]
                if l < n_layers - 1:
                    acts.append(1.0 / (1.0 + np.exp(-z)))
                else:
                    acts.append(z)
            res = y[i] - acts[n_layers][0]
            if res > eps:
                res = eps
            elif res < -eps:
                res = -eps
            delta = np.array([-res])  # d loss / d output
            for l in range(n_layers - 1, -1, -1):
                gW = np.outer(delta, acts[l])
                gb = delta.copy()
                if l > 0:
                    a = acts[l]
                    delta = (Ws[l].T @ delta) * a * (1.0 - a)
                Ws[l] -= eta * gW
                bs[l] -= eta * gb
    return Ws, bs


class MLP:
    """Sigmoid MLP fitted by SGD; hidden = (20,) for Fig. 3, (10, 5) for Fig. 6."""

    def __init__(self, hidden, rng, d):
        sizes = [d] + list(hidden) + [1]
        self.Ws, self.bs = [], []
        for a, b in zip(sizes[:-1], sizes[1:]):
            # [ASSUMPTION: not specified in paper; chose Glorot-uniform weights and zero biases because
            #  it is the default for sigmoid networks in common libraries]
            lim = np.sqrt(6.0 / (a + b))
            self.Ws.append(rng.uniform(-lim, lim, size=(b, a)))
            self.bs.append(np.zeros(b))

    def copy(self):
        m = MLP.__new__(MLP)
        m.Ws = [w.copy() for w in self.Ws]
        m.bs = [b.copy() for b in self.bs]
        return m

    def fit(self, X, y, rng, R=30, eta=1e-3, eps=EPS_HUBER, perms=None):
        # [Paper §5: "We set eta = 0.001 and R = 30"]
        # [ASSUMPTION: not specified in paper; chose Huber loss (eps=1) because §5 says the configuration of
        #  §4 is otherwise unchanged]
        from numba.typed import List
        N = X.shape[0]
        if perms is None:
            perms = np.stack([rng.permutation(N) for _ in range(R)]).astype(np.int64)
        else:
            perms = perms[:R]  # coupled-permutation mode (see fit_sgd)
        Ws, bs = List(), List()
        for w in self.Ws:
            Ws.append(w)
        for b in self.bs:
            bs.append(b)
        Ws, bs = _nn_kernel(np.ascontiguousarray(X), np.ascontiguousarray(y), perms, float(eta), float(eps),
                            Ws, bs, len(self.Ws))
        self.Ws, self.bs = list(Ws), list(bs)
        return self

    def predict(self, X):
        a = X.T
        for l, (W, b) in enumerate(zip(self.Ws, self.bs)):
            z = W @ a + b[:, None]
            a = _sigmoid(z) if l < len(self.Ws) - 1 else z
        return a[0]


# ----------------------------------------------------------------------------------------------
# Diagnostic network: the network configuration found in the authors' ICLR 2025 supplementary material.
# This is our own wrapper around scikit-learn's MLPRegressor (a library, not the authors' code); the settings
# below are the ones the supplement passes to it. Used only by the nn variants "a_sknet" and "authors".
# ----------------------------------------------------------------------------------------------
class SkMLP:
    """scikit-learn MLPRegressor configured as in the supplement.
    [FROM AUTHORS' SUPPLEMENT: code_final/funcs/CP.py:98-100, 190-192, 236-238 (MLPRegressor(hidden_layer_sizes=
     hidden, activation='relu', solver='sgd', shuffle=True, learning_rate='constant', max_iter=epochs,
     learning_rate_init=lr, tol=1e-4, random_state=42)); code_final/real_NN.py:17-18, 26-27 (lr=0.001, epochs=R=30)]
    Everything not passed there keeps scikit-learn's default: squared-error loss, L2 penalty alpha=1e-4,
    mini-batches of min(200, n), Nesterov momentum 0.9, and a stop after 10 epochs without a 1e-4 improvement of
    the training loss. Note that real_NN.py passes activation='logistic' in its parameter dictionary, but
    funcs/CP.py never reads that key and always uses 'relu'; we follow what the code executes."""

    def __init__(self, hidden):
        self.hidden = tuple(hidden)
        self.model = None

    def fit(self, X, y, R=30, eta=1e-3):
        import warnings
        from sklearn.exceptions import ConvergenceWarning
        from sklearn.neural_network import MLPRegressor
        m = MLPRegressor(hidden_layer_sizes=self.hidden, activation="relu", solver="sgd", shuffle=True,
                         learning_rate="constant", max_iter=R, learning_rate_init=eta, tol=1e-4, verbose=False,
                         random_state=42)  # fixed seed: same initialisation and batch order in every fit
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", ConvergenceWarning)
            m.fit(X, y)
        out = SkMLP(self.hidden)
        out.model = m
        return out

    def predict(self, X):
        return self.model.predict(X)
