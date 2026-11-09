# Discrepancies between the paper text and the authors' code, and what they explain

Paper: arXiv:2504.12189v1. Authors' materials, in the order we read them:

1. **GitHub repository** <https://github.com/KiljaeL/LOO-StabCP>, commit
   `3b376827c77369dd3079c14734c6282c16901890` (2025-02-13 16:21 PST). The author states that this repository was read only **after** the primary results were
   committed in a private archive (private tag `pre-diagnosis`). That tag is not in this public repository, so it cannot be checked with `git diff` here. Differences found there are tagged `[FROM AUTHORS' CODE: ...]`.
2. **ICLR 2025 supplementary material**, `ICLR-2025-leave-one-out-stable-conformal-prediction-Supplemental-Conference.zip`
   from the proceedings page
   (<https://proceedings.iclr.cc/paper_files/paper/2025/hash/297fe652867e4897e9f1fe1cd715de19-Abstract-Conference.html>,
   "Supplemental"; 1,101,625 bytes, sha256 `7f39cd75fda4e126ebdf5f545b34c3dbe2208f6216086e4137f23ef82a765e53`).
   Fetched by `scripts/get_data.sh` into `data/authors_supplement/` (git-ignored, not redistributed). It contains an
   earlier, fuller version of the code (`code_final/`: `simul.py`, `real.py`, `real_NN.py`, `kernel.py`,
   `synthetic_derandom.py`, `real_derandom.py`, `recruit.py`, `funcs/`) and its result files, including the raw numbers
   behind Fig. 5 (kernels), Fig. 6 (two-layer networks) and Figs. 7-8 (derandomisation). Read after the GitHub
   repository; differences found there are tagged `[FROM AUTHORS' SUPPLEMENT: ...]`.

We copied no code. Each difference was re-implemented in our own code as an opt-in variant. Numbers are mean coverage /
mean length over 100 repetitions and come from `results/diagnosis.md` and `results/supplement_comparison.md`, which are
generated from `results/raw/*.csv` and the authors' result files. "Paper" numbers are quoted from Table 2 or Table 3 of
the paper. "Authors' file" / "supplement file" numbers are our summaries of the authors' own `result/*.csv`.

## D1. Synthetic DGP (§4): ‖β‖² = 1/d explains the whole simulation length gap

* **Paper text (§4):** X ~ N(0, Σ/d) with Σ_ij = 0.5^|i−j| (AR(1)), and β_j ∝ (1 − j/d)^5 scaled to ‖β‖² = d.
* **Supplement (`code_final/simul.py:27, 48`, `funcs/utils.py:151-191`):** the same AR(1) design X = Z L'/√d, but β
  normalised to ‖β‖² = 1/d (`theta/np.linalg.norm(theta)/np.sqrt(p)`). The signal x'β then has variance ≈ 1/d² ≈ 1e-4,
  so Y is essentially pure N(0, 1) noise and the oracle length is ≈ 2·1.645 = 3.29.
* **Supplement result file:** `result/results_synthetic_ar1_05.csv` reproduces **every** coverage, length and time cell
  of Table 2 exactly after rounding to three decimals (60 cells; `results/supplement_comparison.md`). So Table 2 was
  produced with the AR(1) design and ‖β‖² = 1/d; the only difference from the text is the scale of β.
* **GitHub version (`funcs/utils.py:54-74`, commit 3b37682):** independent features X ~ N(0, I/d) (no `cov` option) and
  ‖β‖² = 1/d. Its `result/results_synthetic.csv` is close to, but not exactly, Table 2. Our earlier diagnosis (before
  we had the supplement) wrongly concluded that Table 2 used independent features; that variant is kept as
  `a_dgp_github` / `authors_github`. Because the signal is negligible under ‖β‖² = 1/d, the two designs give the same
  numbers to within 0.002 in our runs.
* **Effect:**

  | Setting | Ours, text DGP | Ours, supplement DGP (`a_dgp`) | Ours, all authors' choices (`authors`) | Paper Table 2 |
  |---|---|---|---|---|
  | Linear RLM, OracleCP | 0.902 / 6.255 | 0.900 / 3.221 | 0.900 / 3.221 | 0.903 / 3.272 |
  | Linear RLM, LOO-StabCP | 0.905 / 6.515 | 0.907 / 3.371 | 0.907 / 3.371 | 0.910 / 3.442 |
  | Nonlinear RLM, LOO-StabCP | 0.904 / 112.970 | 0.901 / 3.805 | 0.901 / 3.805 | 0.897 / 3.827 |
  | Nonlinear SGD, LOO-StabCP | 0.904 / 112.968 | 0.903 / 3.829 | 0.903 / 3.829 | 0.894 / 3.789 |

  **Explains the gap: yes.** Under the authors' setup every Table 2 length is within 2.4% of the paper's value and
  every coverage within 0.010.
* **Nonlinear setting, text DGP:** E[Y] = Σβ_j E[exp(x_j/10)] ≈ Σβ_j ≈ 55 when ‖β‖² = d. The model f(x) = x'θ has
  no intercept and cannot fit this offset, which gives lengths ≈ 113. Under the authors' DGP the offset is only
  Σβ_j ≈ 0.55. That explains why their nonlinear lengths (≈ 3.66) exceed their linear ones (≈ 3.27): the model
  absorbs a constant bias. Our pre-diagnosis `centered` variant (Y minus training mean) removes the offset and gives
  ≈ 3.2–3.5 (`results/table2_simulation_centered.md`). The same offset is what the kernels remove in App. A.1 (D23).
* **The paper's claims hold under both DGPs**: coverage ≥ 0.9, LOO ≈ RO for RLM, LOO < RO for SGD, and LOO far less
  variable than SplitCP.

## D2. Feature scaling of real data (§5): explains the real-data length gap and the SGD/NN bound sizes

* **Paper text:** "all continuous variables have been normalized". We z-scored every column, so ‖X_i‖ ≈ √d ≈ 3.2–3.6.
* **Authors' code (`funcs/utils.py:84`):** after z-scoring, X is also divided by √d, so ‖X_i‖ ≈ 1. This is a
  different model: with a fixed ridge penalty ‖θ‖², shrinking X by √d strengthens the regularisation by a factor d.
  The SGD/NN bounds (∝ ‖X_i‖‖X_{n+j}‖) also become d times smaller.
* **Effect (m = 100):**

  | Setting | Ours, text | Ours, X/√d (`a_scale`) | Ours, all authors' choices | Authors' file |
  |---|---|---|---|---|
  | Boston RLM, LOO | 0.920 / 2.183 | 0.902 / 2.887 | 0.900 / 2.869 | 0.905 / 2.873 |
  | Boston SGD, Split | 0.897 / 1.567 | 0.895 / 1.962 | 0.884 / 1.883 | 0.901 / 1.908 |
  | Boston SGD, RO | 0.990 / 3.136 | 0.903 / 1.901 | 0.901 / 1.874 | 0.910 / 1.892 |
  | Boston SGD, LOO | 0.961 / 2.284 | 0.898 / 1.841 | 0.897 / 1.815 | 0.906 / 1.833 |
  | Diabetes SGD, LOO | 0.958 / 2.924 | 0.912 / 2.476 | 0.909 / 2.464 | 0.906 / 2.457 |

  **Explains the gap: yes.**
  * Under the literal text, RLM gives *shorter* intervals than the paper (a weaker effective penalty fits better).
  * Under the literal text, the SGD stability bounds are 13× (Boston) or 10× (Diabetes) larger. RO and LOO become
    conservative (coverage 0.96–0.99) and longer than SplitCP, contradicting the qualitative claim C2 for SGD.
  * With X/√d, all real-data lengths match the authors' files to within about 0.06 (most within 0.03), and coverage matches Table 3 to
    within about 0.01–0.02.

## D3. Shared SGD permutations: no measurable effect

* **Paper text:** Alg. 9 draws a random permutation per epoch. The proof of Thm 3 (App. F) couples the permutations
  of the fits with and without the extra point, but §4 never says that separate fits share permutations. Our choice
  (A13) was independent permutations per fit.
* **Authors' code (`simul.py:29-30`, `real.py:113-116`, `funcs/utils.py:26-29`):** R permutations of n + 1 indices
  are drawn once per repetition and reused by every fit, with index n skipped when the point is absent.
* **Effect:** Boston SGD m = 100 LOO goes from 0.961 / 2.284 to 0.961 / 2.284. RO goes from 0.990 / 3.136 to
  0.990 / 3.138. **Explains the gap: no.** It changes results only at the third decimal. It is still the variant
  closer to the theory, so it is part of `authors`.

## D4–D7. CP details: small effects (≤ 0.1 in length), no change to any conclusion

| ID | Item | Paper text / our choice | Authors' code | Effect (Boston RLM m = 100, text → `a_cpdetails`) |
|---|---|---|---|---|
| D4 | RO-StabCP initial guess ỹ | unspecified; we used mean(y) (≈ 0 after z-scoring) | ỹ = 0 (`funcs/CP.py:112`) | RO 0.920 / 2.195 → 0.919 / 2.174 (combined with D5) |
| D5 | Quantile | ⌈(1−α)(n+1)⌉-th of {S} ∪ {∞} (§2) | `np.quantile(·, 1−α, 'higher')` of the n (or n+1) scores, no ∞ (`funcs/CP.py:21,52,97,142,188`) | identical for n = 100; one rank lower for n = 406/342, so slightly shorter intervals |
| D6 | FullCP grid and interval | unspecified; we used 100 points on [min − r/4, max + r/4], length = #accepted × step | 100 points on [min − sd, max + sd]; interval from the first to the last accepted point, found by scanning inward (`funcs/CP.py:34-71`) | FullCP 0.898 / 1.944 → 0.890 / 1.852 |
| D7 | Split size | 0.7n, rounded | ⌊0.7n⌋ (`funcs/CP.py:82`) | SplitCP 0.902 / 2.017 → 0.895 / 1.916 (combined with D5) |

**D6 explains why the paper's FullCP under-covers slightly** (Table 2: 0.896 and 0.886; Table 3: 0.889–0.901). The
first/last-accepted-point interval loses up to one grid step on each side, and the grid is coarse (step ≈ 6 sd/100).
Our authors-variant FullCP gives 0.892 (linear RLM) and 0.887 (nonlinear RLM), matching that pattern. The paper's
FullCP rows look identical for RLM and SGD (0.896 / 3.300 and 0.886 / 3.690), but they are not exactly identical. In
the authors' file the per-repetition lengths differ by at most 0.0018 and coverages are equal. Both models predict
≈ 0 under the D1 DGP, so the coarse grid maps both to the same accepted range. **Explained: yes.**

## D8. Timings: explains the absolute but not the relative runtimes

* The authors solve each RLM with cvxpy (`funcs/utils.py:6-20`). That explains their 176.8 s FullCP and 3.2 s
  RO-StabCP per repetition (Table 2). We solve the same objective with a damped Newton method:
  mean(Huber) + ‖θ‖² in both codes, because cvxpy's `huber` is twice the standard Huber and the authors divide by 2
  and use λ = 2. Our times are 0.49 s (Full), 0.018 s (RO) and 0.0007 s (LOO); see `results/table2_simulation.md`.
* **Relative claims hold:** LOO ≈ SplitCP ≪ RO ≈ Oracle ≪ FullCP. At m = 1, RO and LOO times are comparable.
  The RO/LOO ratio is ≈ 25× for us and ≈ 90× in the paper (3.190 / 0.035), because our per-fit cost is much lower
  relative to the bound computation.

## D9. λ in the RLM bound: no discrepancy

The paper never states λ numerically. The authors use `lamb = 2` (`simul.py:28`, `real.py:112`) both in the
objective (λ/2·‖θ‖²) and in the bound, which is exactly our primary choice (A1). Our λ = 1 sensitivity run
(bound × 2) is therefore conservative by construction.

## D10. Derandomised SplitCP (App. B): code in the supplement only; K = 50 on real data

* The GitHub repository has no MM/EM-SplitCP code; the supplement has it (`funcs/CP.py:127-155` `MultiSplitCP`,
  `funcs/utils.py:72-132` majority votes, `synthetic_derandom.py`, `real_derandom.py`) and the result files
  `results_synthetic_derandom.csv` and `results_real_derandom.csv`.
* The merged split intervals are computed with the authors' `SplitCP` at level α·(1 − τ) = α/2, i.e. with the
  'higher' empirical quantile and no ∞ (D5). Before we had the supplement we could not attribute this rule to the
  authors and reported the text rule as primary; it is now confirmed, so the `authors` variant uses it. Effect of D5
  on MM-SplitCP (linear RLM): length 4.579 (`a_dgp`, text quantile) → 3.851 (`authors`); supplement file 3.906.
* **New difference:** `real_derandom.py:38-64` merges **K = 50** splits on real data; App. B says 30 (the synthetic
  script uses 30). Effect (authors' setup, K = 30 → 50, `real_authors_github` → `real_authors`): at most 0.085 in
  length (Boston RLM EM-SplitCP 3.523 → 3.438).
* The authors' majority votes (`majority_vote`, `exch_majority_vote`) are equivalent to ours (EM adds a random
  permutation of the K sets, as in Gasparin & Ramdas). Their interval is from the first to the last accepted grid
  point; ours too.
* **Effect:** under the authors' setup, 26 of 32 mean lengths are within 0.06 of the supplement files and all coverages
  within 0.016; the largest gap is SplitCP in the nonlinear RLM setting (3.764 vs 3.988). The supplement's own two
  synthetic files disagree by a similar amount for that cell (3.812 in `results_synthetic_ar1_05.csv`, 3.988 in
  `results_synthetic_derandom.csv`), this is descriptive numerical agreement, not an equivalence test. **Explains much of the numerical gap: yes.** In the authors' setup MM- and EM-SplitCP are 1.02–1.62 times as long as LOO-StabCP for us (1.02–1.63 in the files) and slower. **C7 is only partially reproduced:** under the text setup on real-data SGD, LOO is longer (Boston 2.284 vs MM 2.155 / EM 1.926; Diabetes 2.924 vs 2.776 / 2.612). Its speed advantage persists in these comparisons.

## D11. Neural networks (§5 Fig. 3, App. A.2 Fig. 6): code in the supplement only; see D17–D20

The GitHub repository has no NN code. The supplement has `real_NN.py` and `result/results_nn.csv`. Under our literal
z-scoring the heuristic bounds (Eq. 8, ∝ R η ‖X_i‖‖X_{n+j}‖ with R = 30) are large, so RO and LOO are conservative and
longer than SplitCP. With X/√d (D2) they shrink by a factor d. The supplement adds four more differences (D17–D20).
With all of them (`authors`), the (10, 5) run matches `results_nn.csv`:

| (10, 5), mean cov / mean length | text | D2–D7, our network (`a_oursnet`) | + supplement network (`a_sknet`) | + constant bound (`authors`) | `results_nn.csv` |
|---|---|---|---|---|---|
| Boston SplitCP | 0.908 / 2.873 | 0.890 / 3.071 | 0.894 / 3.141 | 0.894 / 3.141 | 0.889 / 3.119 |
| Boston RO-StabCP | 0.994 / 5.825 | 0.923 / 3.281 | 0.927 / 3.309 | 0.916 / 3.275 | 0.915 / 3.273 |
| Boston LOO-StabCP | 0.961 / 4.101 | 0.911 / 3.153 | 0.917 / 3.168 | 0.906 / 3.151 | 0.906 / 3.151 |
| Diabetes SplitCP | 0.907 / 3.070 | 0.894 / 3.126 | 0.887 / 2.922 | 0.887 / 2.922 | 0.892 / 3.007 |
| Diabetes RO-StabCP | 1.000 / 5.266 | 0.929 / 3.371 | 0.930 / 3.166 | 0.940 / 3.176 | 0.913 / 3.119 |
| Diabetes LOO-StabCP | 0.980 / 4.064 | 0.911 / 3.254 | 0.910 / 3.050 | 0.914 / 3.056 | 0.904 / 3.059 |

One hidden layer (Fig. 3, no raw numbers): our `authors` medians are within 0.10 of the digitised medians
(Boston Split 2.461 vs 2.558, RO 2.469 vs 2.481, LOO 2.342 vs 2.358; Diabetes 2.725 vs 2.773, 2.962 vs 2.881,
2.839 vs 2.819). **Explains the gap: yes.** The network itself (D17, D18) explains the Diabetes residual that we could
not diagnose from the GitHub code (LOO 3.254 → 3.050); the bound (D19) changes lengths by at most 0.034, because with
‖X_i‖ ≈ 1 the constant Rη and Eq. (8) are of the same size.

## D12. Screening (§6): test fraction 0.3 and only 10 distinct splits

Our text implementation (`experiments/screen.py`, variant `text`) was written and run from the paper before we read
`recruit.py` / `funcs/CP_screening.py`. The author states that this state is the private tag `pre-diagnosis-screening`, which is not in this public repository. Disclosure: during the earlier diagnosis
of §4–§5 we had already seen that `recruit.py` drops `salary` and uses `get_dummies(..., drop_first=True)`;
our encoding choice (ASSUMPTION in `src/loostab/screening.py`) is the same.

* `recruit.py:33` uses `train_test_split(..., test_size=0.3)`; the paper says 20% test.
* That line runs only when `t % 100 == 0` (`recruit.py:31-33`), so the 1000 repetitions use 10 distinct
  train/test splits; only the cfBH calibration split and the SGD shuffles change between repetitions.

Effect (variant `a_split` vs `text`; `authors_resplit` vs `authors`; `results/table4_screening.md`):
the means move by at most a few hundredths (e.g. LOO-cfBH power at q = 0.1: 0.185 → 0.168 under the text setup;
0.654 with fresh splits → 0.608 with 10 splits under the authors' setup), which is within the real
Monte-Carlo error of a 10-split design. The reported sds are not comparable to a 1000-split design, and the standard
error of a mean is understated by about 10×: for LOO-cfBH power the cluster (per-split) SE is 0.035 / 0.011 / 0.002
for q = 0.1 / 0.2 / 0.3, against a naive sd/√1000 of 0.0034 / 0.0010 / 0.0002. **Matters for uncertainty, not for
the qualitative conclusions.**

## D13. Screening features scaled by 1/√(p+1), dummies standardised, intercept column added

`recruit.py:22-24` z-scores every column (dummies included), divides by √(p+1) and prepends a constant column
1/√(p+1), so ‖X_i‖ ≈ 1. The paper says only that the §5 robust regression is "imported". We z-scored the five
continuous columns, kept the 0/1 dummies and used no intercept (as in §4–§5), so ‖X_i‖ ≈ 3–5. The bounds
τ ∝ ‖X_i‖‖X_{n+j}‖ are then 10–20× larger relative to predictions in [0, 1].
This is the screening analogue of D2 and is the **main cause of the gap**: variant `a_xscale` alone raises
LOO-cfBH power at q = 0.1 from 0.185 to 0.602 and RO-cfBH power from 0.000 to 0.473.

## D14. Screening LOO-cfBH bound for training points lacks the factor R (code bug)

`funcs/CP_screening.py:122` sets `tau = lr*nu*rho_test[j]`, i.e. η ε ‖X_i‖‖X_{n+j}‖. The App. G.1 SGD bound is
τ^LOO_{i,j} = R η ε ‖X_i‖‖X_{n+j}‖ (R = 15). The test-point bound (line 123) and the regression code
(`funcs/CP.py:185`) both include R, as does RO-cfBH (`funcs/CP_screening.py:70`). The training-point bounds used for
LOO-cfBH in Table 4 are therefore 15× too small, so the p-values are not the Eq. (7) p-values that Thm 6 covers.
Effect: with everything else as the authors had it, restoring R (`authors_fixtau` vs `authors`) lowers LOO-cfBH power
from 0.608 / 0.965 / 0.998 to 0.483 / 0.896 / 0.998 and FDP from 0.048 / 0.195 / 0.289 to 0.035 / 0.158 / 0.274.
Paper Table 4 has LOO-cfBH power 0.674 / 0.943 / 0.992. The paper's statement that LOO-cfBH is *more* powerful than
cfBH at q = 0.1 and 0.2 depends on this bug. With the correct bound, LOO-cfBH is valid but less powerful than cfBH
at q = 0.1 (0.483 vs 0.628) and q = 0.2 (0.896 vs 0.938). (The mean FDP of LOO-cfBH and RO-cfBH was below q in every variant we ran.)

## D15. cfBH uses a 50/50 train/calibration split

`funcs/CP_screening.py:11` uses `n_train = int(0.5*n)`; §6 says 70/30. Effect is small (`a_cal50`: cfBH power
0.660 → 0.679 at q = 0.1, ≤ 0.02 elsewhere).

## D16. Minor screening differences

* BH rejects p_j ≤ q k*/m (standard BH, `funcs/utils.py:41-52`). The §6 text says "<"; we follow the text in
  `text` and use "≤" in `authors`.
* RO-cfBH uses ỹ = 0 (`funcs/CP_screening.py:49`); ours uses mean(y) (ASSUMPTION A7, as in §4).
* One set of R shuffles per repetition is shared by all fits (`recruit.py:36`), as in D3.
* Each method is re-run for each q, so cfBH draws a new calibration split per q. Ours computes the p-values once
  per repetition, since only BH depends on q.
These are included in variant `authors`; we did not isolate them. Variant `authors` reproduces Table 4 closely
(e.g. LOO-cfBH power 0.608 / 0.965 / 0.998 vs paper 0.674 / 0.943 / 0.992; RO-cfBH 0.286 / 0.628 / 0.980 vs
0.304 / 0.652 / 0.963; cfBH 0.628 / 0.938 / 0.997 vs 0.632 / 0.928 / 0.992). The remaining gap is about the size of
the 10-split Monte-Carlo error (D12).

## D17. Neural networks: ReLU activation, not sigmoid (supplement)

§5 and App. A.2 describe sigmoid hidden units. The supplement calls scikit-learn's `MLPRegressor(activation='relu')`
(`funcs/CP.py:98, 190, 236`). `real_NN.py:26-27` puts `'activation': 'logistic'` in the parameter dictionary, but
`funcs/CP.py` never reads that key. Our text setup uses sigmoid units; `a_sknet` and `authors` use ReLU. Not isolated
from D18 (switched together as "the supplement network").

## D18. Neural networks: training loop and initialisation (supplement)

The paper's heuristic bound (Eq. 8) is motivated by per-sample SGD with R epochs and step η (as in Alg. 9) and a
Lipschitz loss. The supplement trains `MLPRegressor(solver='sgd', learning_rate='constant', learning_rate_init=0.001,
max_iter=30, shuffle=True, tol=1e-4, random_state=42)` (`funcs/CP.py:98-100`), i.e. with scikit-learn's defaults for
everything else: **squared-error loss** (not Huber), **mini-batches of min(200, n)** (2–3 updates per epoch, not n),
**Nesterov momentum 0.9**, an **L2 penalty 1e-4**, early stopping of the epoch loop when the training loss improves by
less than 1e-4 for 10 epochs, and the **same initialisation and batch order (random_state = 42) for every fit in every
repetition**. Our text network: Huber loss, per-sample SGD with reshuffling, Glorot-uniform initialisation drawn once
per repetition. Effect (D17 + D18, `a_oursnet` → `a_sknet`): LOO length (10, 5) Diabetes 3.254 → 3.050, Boston 3.153 →
3.168; (20) Boston 2.210 → 2.358, Diabetes 2.778 → 2.825; SplitCP (20) Boston 2.344 → 2.521. **Explains the remaining
NN gap: yes.** The bound of Eq. (8) is not derived for this training procedure (momentum, mini-batches, squared loss);
the paper presents it as a heuristic.

## D19. Neural networks: constant stability bound instead of Eq. (8) (supplement)

Eq. (8): τ^LOO_{i,j} ≈ Rηγ‖X_i‖‖X_{n+j}‖, and twice that for RO. The supplement uses `tau = lr * epochs` for every
point (`funcs/CP.py:263`, LOO) and `2 * lr * epochs` (`funcs/CP.py:197`, RO), i.e. τ = Rη = 0.03 and 0.06 with no
norms. With X/√d (D2) the norms are ≈ 1, so the two are close. Effect (`a_sknet` → `authors`): at most 0.034 in length.
Under the text's scaling, the constant bound would be d times smaller than Eq. (8).

## D20. Neural-network result file: (10, 5) configuration; no raw numbers for Fig. 3 (supplement)

`real_NN.py:26-27` is set to one hidden layer of 20 units, with the (10, 5) configuration commented out (lines 28-29).
`result/results_nn.csv` (600 rows: 2 data sets × 3 methods × 100 repetitions, no architecture column) matches the
(10, 5) figure (Fig. 6): its medians agree with our digitised Fig. 6 medians to within 0.006, and not with Fig. 3
(differences 0.24–0.80). So the file is the Fig. 6 run, and the one-layer run of Fig. 3 has no published raw numbers.
We therefore compare Fig. 6 with the raw file and Fig. 3 with our digitised medians.

## D21. Kernels: RBF bandwidth (supplement)

App. A.1: k_RBF(x, x') = exp(−‖x − x'‖² / (2σ²)) with σ = 0.1, i.e. γ = 1/(2σ²) = 50. The supplement uses
`kernel_matrix(..., params_RBF={'gamma': 0.1})` (`kernel.py:35-36`) with k = exp(−γ‖x − x'‖²) (`funcs/utils.py:44-47`),
i.e. γ = 0.1 (σ ≈ 2.24). Under the §4 design ‖X_i − X_j‖² ≈ 2, so γ = 50 gives off-diagonal kernel values ≈ e^−100:
the kernel map is the identity on the training points and ≈ 0 on test points, so the features carry no information
about a test point. With
γ = 0.1, k ≈ e^−0.2 ≈ 0.82 for every pair, a near-constant feature. Effect: see D22 (not isolated from it).

## D22. Kernels: step size, algorithm and feature map (supplement)

* `kernel.py:44` uses **η = 1e-5** for SGD with a kernel (η = 1e-3 without); App. A.1 gives no step size, and we had
  assumed the §4 value 1e-3.
* Only **SGD** is run (`kernel.py`), with the kernel rows as features: D = (K(X, X), Y), D_test = (K(X_test, X), Y_test)
  (`kernel.py:37, 41`), i.e. the empirical kernel map with the n training points as centres, and the plain SGD bound
  (App. G.1) on these features. App. A.1 describes kernel RLM with penalty θ'Kθ, for which `funcs/CP.py:181-182,
  254-255` divide the RLM bound by λ_min(K), but no script calls it. Fig. 5 does not say which algorithm it shows.
* Effect of D21 + D22 together (`kernel` → `kernel_a_kparams`, text DGP): polynomial kernel, linear setting, LOO
  coverage / length 1.000 / 11.575 → 0.900 / 6.541 (the η = 1e-3 bounds on features of norm ≈ 10 dominate the
  interval); RBF almost unchanged. With the authors' DGP as well (`kernel_authors`), every kernel-study mean length is
  within 0.102 of `results_kernel.csv` and every coverage within 0.013.

## D23. Kernels: the length reduction comes from an implicit intercept (finding, not a code difference)

With the supplement's parameters, kernels shorten the nonlinear LOO intervals (ours 3.859 → 3.475 RBF, 3.464 poly;
file 3.849 → 3.487, 3.413) but not the linear ones (3.327 → 3.378, 3.347). Both kernel maps contain a large
near-constant component (RBF entries ≈ 0.82; the +1 of the polynomial kernel), which acts as an intercept and absorbs
the offset Σβ_j ≈ 0.55 of the nonlinear design (D1). Centring the response at its training mean (`kernel_authors_centered`)
removes the advantage: nonlinear LOO 3.367 without a kernel, 3.358 RBF, 3.405 polynomial. So App. A.1's "shorter
intervals in the nonlinear setting" is reproduced, but it reflects the missing intercept of the no-kernel model, not a
better fit of the nonlinearity.
Also noted (not quantified): a training point used as a calibration point in SplitCP is one of the kernel centres, so its
feature vector contains k(x_i, x_i), which a test point's does not; under the text parameters with the polynomial
kernel SplitCP under-covers (0.784 nonlinear, 0.883 linear), which we attribute to this asymmetry but did not
investigate further.

## Summary

| ID | Difference | Explains a gap? |
|---|---|---|
| D1 | synthetic ‖β‖² = 1/d vs d (supplement: AR(1) design as in the text; GitHub: iid) | **yes**: all Table 2 lengths; supplement file = Table 2 exactly |
| D2 | real X divided by √d | **yes**: real-data lengths, SGD/NN conservativeness |
| D3 | shared SGD permutations | no (third decimal) |
| D4–D7 | ỹ = 0, quantile, FullCP grid/interval, ⌊0.7n⌋ | small; D6 explains FullCP under-coverage and the near-identical FullCP rows |
| D8 | cvxpy vs Newton | absolute runtimes only |
| D9 | λ = 2 | none (same as ours) |
| D10 | MM/EM code in supplement only: D5 at α/2; K = 50 on real data | yes, with D1/D2: within MC error of the supplement files |
| D11 | NN code in supplement only | yes, with D2 and D17–D19: (10, 5) matches `results_nn.csv` |
| D12 | screening: 30% test, only 10 distinct splits | means: no (within MC error); understates SEs ~10× |
| D13 | screening X scaled by 1/√(p+1) + intercept | **yes**: main cause of the LOO/RO-cfBH power gap |
| D14 | screening LOO training bound missing R (bug) | **yes**: LOO-cfBH beating cfBH in power depends on it |
| D15 | cfBH 50/50 split | small |
| D16 | BH ≤, ỹ = 0, shared shuffles, per-q re-run | small (not isolated) |
| D17 | NN: ReLU, not sigmoid | with D18: the Diabetes residual |
| D18 | NN: scikit-learn MLP (squared loss, mini-batch, momentum, L2, fixed seed 42) | with D17: yes (Diabetes LOO 3.254 → 3.050) |
| D19 | NN: constant bound Rη / 2Rη instead of Eq. (8) | small (≤ 0.034) once ‖X_i‖ ≈ 1 |
| D20 | NN result file is the (10, 5) run; none for Fig. 3 | what can be compared |
| D21 | kernel: RBF γ = 0.1 (σ ≈ 2.24) vs σ = 0.1 | with D22: yes (text σ gives a degenerate kernel) |
| D22 | kernel: η = 1e-5, SGD only, empirical kernel map | with D21: yes; within 0.102 of `results_kernel.csv` |
| D23 | kernel gain = implicit intercept (finding) | the C6 length gain vanishes with a centred response |
