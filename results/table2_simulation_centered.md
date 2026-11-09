# Simulation (§4), variant 'centered' (Y centred by training mean)

Ours: mean (sd) over 100 repetitions. Paper: [App. G.2, Table 2] of arXiv:2504.12189v1. Time is wall-clock seconds per repetition (all m=100 test points).

## linear / RLM

| Method | Coverage (ours) | Coverage (paper) | Length (ours) | Length (paper) | Time s (ours) | Time s (paper) |
|---|---|---|---|---|---|---|
| OracleCP | 0.901 (0.042) | 0.903 (0.040) | 6.257 (0.492) | 3.272 (0.250) | 0.0170 | 3.201 |
| FullCP | 0.901 (0.041) | 0.896 (0.043) | 6.452 (0.538) | 3.300 (0.257) | 0.4859 | 176.783 |
| SplitCP | 0.908 (0.054) | 0.903 (0.060) | 6.770 (1.045) | 3.455 (0.514) | 0.0003 | 0.017 |
| RO-StabCP | 0.904 (0.040) | 0.910 (0.039) | 6.521 (0.535) | 3.442 (0.257) | 0.0173 | 3.190 |
| LOO-StabCP | 0.904 (0.040) | 0.910 (0.039) | 6.520 (0.535) | 3.442 (0.257) | 0.0007 | 0.035 |
| MM-SplitCP | 0.973 (0.025) | fig. 7 only | 8.943 (1.242) | fig. 7 only | 0.0082 | fig. 7 only |
| EM-SplitCP | 0.947 (0.040) | fig. 7 only | 7.837 (1.171) | fig. 7 only | 0.0093 | fig. 7 only |

lambda = 1 sensitivity (same fits, RLM bound with lambda=1 instead of 2):

- RO-StabCP: coverage 0.908 (0.040), length 6.601 (0.535)
- LOO-StabCP: coverage 0.908 (0.040), length 6.600 (0.535)

Diagnostic: training R^2 of the single LOO-StabCP fit = 0.012 (0.002)

## linear / SGD

| Method | Coverage (ours) | Coverage (paper) | Length (ours) | Length (paper) | Time s (ours) | Time s (paper) |
|---|---|---|---|---|---|---|
| OracleCP | 0.900 (0.042) | 0.903 | 6.180 (0.542) | 3.252 | 0.0247 | 0.720 |
| FullCP | 0.901 (0.042) | 0.896 | 6.441 (0.573) | 3.300 | 0.6120 | 19.320 |
| SplitCP | 0.904 (0.056) | 0.900 | 6.653 (1.043) | 3.420 (0.557) | 0.0002 | 0.005 |
| RO-StabCP | 0.905 (0.042) | 0.911 | 6.487 (0.573) | 3.464 | 0.0168 | 0.720 |
| LOO-StabCP | 0.902 (0.042) | 0.906 | 6.427 (0.572) | 3.405 | 0.0005 | 0.009 |
| MM-SplitCP | 0.969 (0.020) | fig. 7 only | 8.756 (0.892) | fig. 7 only | 0.0066 | fig. 7 only |
| EM-SplitCP | 0.950 (0.036) | fig. 7 only | 7.922 (1.080) | fig. 7 only | 0.0078 | fig. 7 only |

Diagnostic: training R^2 of the single LOO-StabCP fit = 0.035 (0.004)

## nonlinear / RLM

| Method | Coverage (ours) | Coverage (paper) | Length (ours) | Length (paper) | Time s (ours) | Time s (paper) |
|---|---|---|---|---|---|---|
| OracleCP | 0.892 (0.048) | 0.892 | 3.227 (0.266) | 3.659 | 0.0171 | 3.289 |
| FullCP | 0.892 (0.048) | 0.886 | 3.321 (0.290) | 3.690 | 0.6521 | 163.101 |
| SplitCP | 0.894 (0.066) | 0.893 | 3.438 (0.549) | 3.812 (0.554) | 0.0003 | 0.017 |
| RO-StabCP | 0.902 (0.047) | 0.897 | 3.393 (0.288) | 3.828 | 0.0173 | 3.275 |
| LOO-StabCP | 0.902 (0.047) | 0.897 | 3.393 (0.288) | 3.827 | 0.0007 | 0.038 |
| MM-SplitCP | 0.970 (0.025) | fig. 7 only | 4.600 (0.544) | fig. 7 only | 0.0082 | fig. 7 only |
| EM-SplitCP | 0.949 (0.038) | fig. 7 only | 4.146 (0.562) | fig. 7 only | 0.0093 | fig. 7 only |

lambda = 1 sensitivity (same fits, RLM bound with lambda=1 instead of 2):

- RO-StabCP: coverage 0.908 (0.045), length 3.472 (0.288)
- LOO-StabCP: coverage 0.908 (0.045), length 3.472 (0.288)

Diagnostic: training R^2 of the single LOO-StabCP fit = 0.007 (0.001)

## nonlinear / SGD

| Method | Coverage (ours) | Coverage (paper) | Length (ours) | Length (paper) | Time s (ours) | Time s (paper) |
|---|---|---|---|---|---|---|
| OracleCP | 0.896 (0.053) | 0.892 | 3.248 (0.310) | 3.641 | 0.0159 | 0.732 |
| FullCP | 0.895 (0.054) | 0.886 | 3.376 (0.330) | 3.690 | 0.5786 | 17.425 |
| SplitCP | 0.888 (0.066) | 0.895 | 3.402 (0.547) | 3.855 (0.612) | 0.0002 | 0.005 |
| RO-StabCP | 0.904 (0.050) | 0.900 | 3.459 (0.324) | 3.849 | 0.0158 | 0.746 |
| LOO-StabCP | 0.898 (0.051) | 0.894 | 3.400 (0.324) | 3.789 | 0.0005 | 0.009 |
| MM-SplitCP | 0.977 (0.017) | fig. 7 only | 4.710 (0.535) | fig. 7 only | 0.0063 | fig. 7 only |
| EM-SplitCP | 0.949 (0.041) | fig. 7 only | 4.115 (0.582) | fig. 7 only | 0.0075 | fig. 7 only |

Diagnostic: training R^2 of the single LOO-StabCP fit = 0.021 (0.004)

