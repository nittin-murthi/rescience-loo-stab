# Real data (§5): Table 3 coverage and Fig. 2 length

Ours: mean (sd) over 100 repetitions. Paper coverage: [App. G.3, Table 3]. Paper lengths are not tabulated; Fig. 2 values below are approximate, read by eye from the figure.

## boston, m=1, RLM

| Method | Coverage (ours) | Coverage (paper) | Length (ours) | Time s (ours) |
|---|---|---|---|---|
| OracleCP | 0.890 (0.314) | 0.920 | 1.896 (0.000) | 0.0004 |
| FullCP | 0.890 (0.314) | 0.910 | 1.912 (0.032) | 0.0052 |
| SplitCP | 0.880 (0.327) | 0.910 | 1.980 (0.280) | 0.0002 |
| RO-StabCP | 0.910 (0.288) | 0.920 | 2.129 (0.098) | 0.0003 |
| LOO-StabCP | 0.910 (0.288) | 0.920 | 2.129 (0.065) | 0.0002 |

Paper Fig. 2 length (approx., read from figure): all methods approx. 2.8-2.9

- lambda=1 sensitivity, RO-StabCP: coverage 0.930 (0.256), length 2.328 (0.188)
- lambda=1 sensitivity, LOO-StabCP: coverage 0.930 (0.256), length 2.318 (0.120)

## boston, m=1, SGD

| Method | Coverage (ours) | Coverage (paper) | Length (ours) | Time s (ours) |
|---|---|---|---|---|
| OracleCP | 0.910 (0.288) | 0.900 | 1.457 (0.019) | 0.0077 |
| FullCP | 0.910 (0.288) | 0.920 | 1.535 (0.056) | 0.0086 |
| SplitCP | 0.910 (0.288) | 0.910 | 1.557 (0.146) | 0.0002 |
| RO-StabCP | 0.990 (0.100) | 0.900 | 3.291 (1.071) | 0.0003 |
| LOO-StabCP | 0.960 (0.197) | 0.900 | 2.360 (0.537) | 0.0003 |

Paper Fig. 2 length (approx., read from figure): Oracle ~1.7, Full ~2.05 (m=1) / ~2.2 (m=100), Split ~1.8, RO ~1.83, LOO ~1.77

## boston, m=100, RLM

| Method | Coverage (ours) | Coverage (paper) | Length (ours) | Time s (ours) |
|---|---|---|---|---|
| OracleCP | 0.899 (0.036) | 0.906 | 1.907 (0.058) | 0.0095 |
| FullCP | 0.898 (0.035) | 0.897 | 1.944 (0.061) | 0.4504 |
| SplitCP | 0.902 (0.042) | 0.898 | 2.017 (0.317) | 0.0003 |
| RO-StabCP | 0.920 (0.029) | 0.905 | 2.195 (0.059) | 0.0104 |
| LOO-StabCP | 0.920 (0.029) | 0.905 | 2.183 (0.058) | 0.0009 |
| MM-SplitCP | 0.953 (0.024) | fig. 8 only | 3.331 (0.225) | 0.0080 |
| EM-SplitCP | 0.936 (0.032) | fig. 8 only | 2.768 (0.503) | 0.0093 |

Paper Fig. 2 length (approx., read from figure): all methods approx. 2.8-2.9

- lambda=1 sensitivity, RO-StabCP: coverage 0.933 (0.024), length 2.464 (0.067)
- lambda=1 sensitivity, LOO-StabCP: coverage 0.933 (0.024), length 2.444 (0.064)

## boston, m=100, SGD

| Method | Coverage (ours) | Coverage (paper) | Length (ours) | Time s (ours) |
|---|---|---|---|---|
| OracleCP | 0.893 (0.031) | 0.905 | 1.448 (0.034) | 0.0203 |
| FullCP | 0.893 (0.032) | 0.901 | 1.537 (0.045) | 0.7361 |
| SplitCP | 0.897 (0.035) | 0.901 | 1.567 (0.187) | 0.0002 |
| RO-StabCP | 0.990 (0.009) | 0.910 | 3.136 (0.075) | 0.0203 |
| LOO-StabCP | 0.961 (0.018) | 0.906 | 2.284 (0.054) | 0.0007 |
| MM-SplitCP | 0.950 (0.022) | fig. 8 only | 2.155 (0.085) | 0.0075 |
| EM-SplitCP | 0.931 (0.028) | fig. 8 only | 1.926 (0.181) | 0.0086 |

Paper Fig. 2 length (approx., read from figure): Oracle ~1.7, Full ~2.05 (m=1) / ~2.2 (m=100), Split ~1.8, RO ~1.83, LOO ~1.77

## diabetes, m=1, RLM

| Method | Coverage (ours) | Coverage (paper) | Length (ours) | Time s (ours) |
|---|---|---|---|---|
| OracleCP | 0.940 (0.239) | 0.910 | 2.503 (0.000) | 0.0004 |
| FullCP | 0.940 (0.239) | 0.900 | 2.516 (0.028) | 0.0050 |
| SplitCP | 0.920 (0.273) | 0.890 | 2.522 (0.117) | 0.0002 |
| RO-StabCP | 0.960 (0.197) | 0.910 | 2.696 (0.084) | 0.0003 |
| LOO-StabCP | 0.960 (0.197) | 0.910 | 2.685 (0.054) | 0.0002 |

Paper Fig. 2 length (approx., read from figure): all methods approx. 2.8-2.9

- lambda=1 sensitivity, RO-StabCP: coverage 0.990 (0.100), length 2.888 (0.165)
- lambda=1 sensitivity, LOO-StabCP: coverage 0.990 (0.100), length 2.869 (0.108)

## diabetes, m=1, SGD

| Method | Coverage (ours) | Coverage (paper) | Length (ours) | Time s (ours) |
|---|---|---|---|---|
| OracleCP | 0.910 (0.288) | 0.920 | 2.345 (0.008) | 0.0003 |
| FullCP | 0.910 (0.288) | 0.910 | 2.381 (0.033) | 0.0078 |
| SplitCP | 0.910 (0.288) | 0.920 | 2.429 (0.127) | 0.0002 |
| RO-StabCP | 0.980 (0.141) | 0.930 | 3.458 (0.464) | 0.0003 |
| LOO-StabCP | 0.950 (0.219) | 0.920 | 2.907 (0.228) | 0.0002 |

Paper Fig. 2 length (approx., read from figure): Oracle ~2.35, Full ~2.6, Split ~2.45, RO ~2.45, LOO ~2.38

## diabetes, m=100, RLM

| Method | Coverage (ours) | Coverage (paper) | Length (ours) | Time s (ours) |
|---|---|---|---|---|
| OracleCP | 0.900 (0.036) | 0.900 | 2.502 (0.036) | 0.0090 |
| FullCP | 0.899 (0.035) | 0.889 | 2.530 (0.037) | 0.4398 |
| SplitCP | 0.902 (0.041) | 0.894 | 2.540 (0.131) | 0.0002 |
| RO-StabCP | 0.935 (0.028) | 0.900 | 2.732 (0.038) | 0.0095 |
| LOO-StabCP | 0.936 (0.027) | 0.900 | 2.726 (0.037) | 0.0008 |
| MM-SplitCP | 0.954 (0.024) | fig. 8 only | 2.883 (0.059) | 0.0077 |
| EM-SplitCP | 0.936 (0.032) | fig. 8 only | 2.745 (0.121) | 0.0088 |

Paper Fig. 2 length (approx., read from figure): all methods approx. 2.8-2.9

- lambda=1 sensitivity, RO-StabCP: coverage 0.956 (0.021), length 2.950 (0.041)
- lambda=1 sensitivity, LOO-StabCP: coverage 0.959 (0.020), length 2.940 (0.038)

## diabetes, m=100, SGD

| Method | Coverage (ours) | Coverage (paper) | Length (ours) | Time s (ours) |
|---|---|---|---|---|
| OracleCP | 0.907 (0.035) | 0.902 | 2.326 (0.048) | 0.0174 |
| FullCP | 0.909 (0.034) | 0.890 | 2.400 (0.050) | 0.6343 |
| SplitCP | 0.908 (0.036) | 0.902 | 2.433 (0.145) | 0.0002 |
| RO-StabCP | 0.979 (0.013) | 0.914 | 3.501 (0.059) | 0.0174 |
| LOO-StabCP | 0.958 (0.020) | 0.906 | 2.924 (0.054) | 0.0006 |
| MM-SplitCP | 0.959 (0.022) | fig. 8 only | 2.776 (0.070) | 0.0067 |
| EM-SplitCP | 0.939 (0.030) | fig. 8 only | 2.612 (0.100) | 0.0078 |

Paper Fig. 2 length (approx., read from figure): Oracle ~2.35, Full ~2.6, Split ~2.45, RO ~2.45, LOO ~2.38

