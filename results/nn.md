# Neural networks (§5 Fig. 3: one hidden layer of 20; App. A.2 Fig. 6: hidden layers (10, 5))

The paper reports these only as box plots (no table), so this table has no paper column.

| Data | Hidden | Method | Coverage | Length | Time s | LOO train R^2 |
|---|---|---|---|---|---|---|
| boston | (10, 5) | SplitCP | 0.908 (0.040) | 2.873 (0.559) | 0.0275 |  |
| boston | (10, 5) | RO-StabCP | 0.994 (0.008) | 5.825 (0.343) | 3.9368 |  |
| boston | (10, 5) | LOO-StabCP | 0.961 (0.019) | 4.101 (0.303) | 0.0402 | 0.279 (0.108) |
| boston | (20,) | SplitCP | 0.902 (0.041) | 1.798 (0.354) | 0.0598 |  |
| boston | (20,) | RO-StabCP | 0.996 (0.006) | 4.923 (0.174) | 2.9003 |  |
| boston | (20,) | LOO-StabCP | 0.984 (0.012) | 3.213 (0.111) | 0.0299 | 0.688 (0.025) |
| diabetes | (10, 5) | SplitCP | 0.907 (0.042) | 3.070 (0.246) | 0.0234 |  |
| diabetes | (10, 5) | RO-StabCP | 1.000 (0.000) | 5.266 (0.203) | 3.3029 |  |
| diabetes | (10, 5) | LOO-StabCP | 0.980 (0.015) | 4.064 (0.178) | 0.0336 | 0.166 (0.078) |
| diabetes | (20,) | SplitCP | 0.902 (0.044) | 2.452 (0.158) | 0.0170 |  |
| diabetes | (20,) | RO-StabCP | 0.998 (0.004) | 4.639 (0.100) | 2.4073 |  |
| diabetes | (20,) | LOO-StabCP | 0.985 (0.012) | 3.485 (0.065) | 0.0249 | 0.497 (0.020) |
