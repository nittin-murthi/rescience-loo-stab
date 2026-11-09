# Simulation (§4), literal paper text: Table 2 / Fig. 1 / Fig. 7

Ours: mean (sd) over 100 repetitions. Paper: [App. G.2, Table 2] of arXiv:2504.12189v1. Time is wall-clock seconds per repetition (all m=100 test points).

## linear / RLM

| Method | Coverage (ours) | Coverage (paper) | Length (ours) | Length (paper) | Time s (ours) | Time s (paper) |
|---|---|---|---|---|---|---|
| OracleCP | 0.902 (0.041) | 0.903 (0.040) | 6.255 (0.500) | 3.272 (0.250) | 0.0178 | 3.201 |
| FullCP | 0.901 (0.040) | 0.896 (0.043) | 6.449 (0.548) | 3.300 (0.257) | 0.4935 | 176.783 |
| SplitCP | 0.910 (0.055) | 0.903 (0.060) | 6.808 (1.073) | 3.455 (0.514) | 0.0003 | 0.017 |
| RO-StabCP | 0.905 (0.040) | 0.910 (0.039) | 6.515 (0.548) | 3.442 (0.257) | 0.0178 | 3.190 |
| LOO-StabCP | 0.905 (0.040) | 0.910 (0.039) | 6.515 (0.548) | 3.442 (0.257) | 0.0007 | 0.035 |
| MM-SplitCP | 0.976 (0.022) | fig. 7 only | 9.050 (1.213) | fig. 7 only | 0.0082 | fig. 7 only |
| EM-SplitCP | 0.951 (0.039) | fig. 7 only | 7.920 (1.127) | fig. 7 only | 0.0095 | fig. 7 only |

lambda = 1 sensitivity (same fits, RLM bound with lambda=1 instead of 2):

- RO-StabCP: coverage 0.908 (0.039), length 6.595 (0.548)
- LOO-StabCP: coverage 0.908 (0.039), length 6.594 (0.548)

Diagnostic: training R^2 of the single LOO-StabCP fit = 0.001 (0.016)

## linear / SGD

| Method | Coverage (ours) | Coverage (paper) | Length (ours) | Length (paper) | Time s (ours) | Time s (paper) |
|---|---|---|---|---|---|---|
| OracleCP | 0.907 (0.039) | 0.903 | 6.233 (0.532) | 3.252 | 0.0254 | 0.720 |
| FullCP | 0.907 (0.039) | 0.896 | 6.499 (0.545) | 3.300 | 0.6282 | 19.320 |
| SplitCP | 0.906 (0.056) | 0.900 | 6.670 (1.085) | 3.420 (0.557) | 0.0002 | 0.005 |
| RO-StabCP | 0.911 (0.038) | 0.911 | 6.534 (0.537) | 3.464 | 0.0176 | 0.720 |
| LOO-StabCP | 0.908 (0.039) | 0.906 | 6.475 (0.537) | 3.405 | 0.0005 | 0.009 |
| MM-SplitCP | 0.973 (0.020) | fig. 7 only | 8.865 (0.882) | fig. 7 only | 0.0070 | fig. 7 only |
| EM-SplitCP | 0.951 (0.035) | fig. 7 only | 7.934 (1.122) | fig. 7 only | 0.0082 | fig. 7 only |

Diagnostic: training R^2 of the single LOO-StabCP fit = 0.025 (0.015)

## nonlinear / RLM

| Method | Coverage (ours) | Coverage (paper) | Length (ours) | Length (paper) | Time s (ours) | Time s (paper) |
|---|---|---|---|---|---|---|
| OracleCP | 0.897 (0.042) | 0.892 | 112.773 (0.321) | 3.659 | 0.0181 | 3.289 |
| FullCP | 0.897 (0.041) | 0.886 | 5.129 (0.564) | 3.690 | 0.2943 | 163.101 |
| SplitCP | 0.893 (0.060) | 0.893 | 112.906 (0.589) | 3.812 (0.554) | 0.0003 | 0.017 |
| RO-StabCP | 0.905 (0.040) | 0.897 | 112.970 (0.336) | 3.828 | 0.0187 | 3.275 |
| LOO-StabCP | 0.904 (0.039) | 0.897 | 112.970 (0.336) | 3.827 | 0.0007 | 0.038 |
| MM-SplitCP | 0.977 (0.023) | fig. 7 only | 114.374 (0.618) | fig. 7 only | 0.0078 | fig. 7 only |
| EM-SplitCP | 0.952 (0.040) | fig. 7 only | 113.776 (0.653) | fig. 7 only | 0.0090 | fig. 7 only |

lambda = 1 sensitivity (same fits, RLM bound with lambda=1 instead of 2):

- RO-StabCP: coverage 0.910 (0.038), length 113.049 (0.337)
- LOO-StabCP: coverage 0.910 (0.038), length 113.049 (0.336)

Diagnostic: training R^2 of the single LOO-StabCP fit = -3105.588 (423.503)

## nonlinear / SGD

| Method | Coverage (ours) | Coverage (paper) | Length (ours) | Length (paper) | Time s (ours) | Time s (paper) |
|---|---|---|---|---|---|---|
| OracleCP | 0.902 (0.041) | 0.892 | 112.806 (0.326) | 3.641 | 0.0129 | 0.732 |
| FullCP | 0.900 (0.043) | 0.886 | 5.137 (0.643) | 3.690 | 0.4684 | 17.425 |
| SplitCP | 0.901 (0.063) | 0.895 | 113.031 (0.681) | 3.855 (0.612) | 0.0002 | 0.005 |
| RO-StabCP | 0.909 (0.040) | 0.900 | 113.028 (0.342) | 3.849 | 0.0128 | 0.746 |
| LOO-StabCP | 0.904 (0.041) | 0.894 | 112.968 (0.342) | 3.789 | 0.0005 | 0.009 |
| MM-SplitCP | 0.980 (0.020) | fig. 7 only | 114.523 (0.578) | fig. 7 only | 0.0057 | fig. 7 only |
| EM-SplitCP | 0.948 (0.051) | fig. 7 only | 113.866 (0.823) | fig. 7 only | 0.0069 | fig. 7 only |

Diagnostic: training R^2 of the single LOO-StabCP fit = -3060.867 (437.242)

