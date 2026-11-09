# Our runs vs the result files of the authors' ICLR 2025 supplementary material

Supplement: https://proceedings.iclr.cc/paper_files/paper/2025/file/297fe652867e4897e9f1fe1cd715de19-Supplemental-Conference.zip
(sha256 7f39cd75fda4e126ebdf5f545b34c3dbe2208f6216086e4137f23ef82a765e53), fetched by `scripts/get_data.sh`.
The supplement's numbers are computed by us from its `code_final/result/*.csv`; they are diagnosis references, not paper numbers.

## Simulation (§4): supplement result file vs Table 2

`results_synthetic_ar1_05.csv` is the supplement's output of `simul.py` (AR(1) design). Max |file − Table 2| over all coverage, length and time cells:

- max abs difference after rounding to 3 decimals: 0.0000 over 60 cells

| Setting | Method | Ours text | Ours authors' (supplement DGP) | Ours authors' (GitHub DGP) | Supplement file | Table 2 |
|---|---|---|---|---|---|---|
| linear RLM | OracleCP | 0.902 / 6.255 | 0.900 / 3.221 | 0.900 / 3.221 | 0.903 / 3.272 | 0.903 / 3.272 |
| linear RLM | FullCP | 0.901 / 6.449 | 0.892 / 3.227 | 0.892 / 3.228 | 0.896 / 3.300 | 0.896 / 3.300 |
| linear RLM | SplitCP | 0.910 / 6.808 | 0.901 / 3.373 | 0.901 / 3.372 | 0.903 / 3.455 | 0.903 / 3.455 |
| linear RLM | RO-StabCP | 0.905 / 6.515 | 0.907 / 3.371 | 0.906 / 3.373 | 0.910 / 3.442 | 0.910 / 3.442 |
| linear RLM | LOO-StabCP | 0.905 / 6.515 | 0.907 / 3.371 | 0.906 / 3.372 | 0.910 / 3.442 | 0.910 / 3.442 |
| linear SGD | OracleCP | 0.907 / 6.233 | 0.901 / 3.245 | 0.901 / 3.245 | 0.903 / 3.252 | 0.903 / 3.252 |
| linear SGD | FullCP | 0.907 / 6.499 | 0.894 / 3.291 | 0.894 / 3.289 | 0.896 / 3.300 | 0.896 / 3.300 |
| linear SGD | SplitCP | 0.906 / 6.670 | 0.908 / 3.488 | 0.908 / 3.488 | 0.900 / 3.420 | 0.900 / 3.420 |
| linear SGD | RO-StabCP | 0.911 / 6.534 | 0.911 / 3.451 | 0.911 / 3.449 | 0.911 / 3.464 | 0.911 / 3.464 |
| linear SGD | LOO-StabCP | 0.908 / 6.475 | 0.905 / 3.391 | 0.905 / 3.389 | 0.906 / 3.405 | 0.906 / 3.405 |
| nonlinear RLM | OracleCP | 0.897 / 112.773 | 0.894 / 3.653 | 0.894 / 3.653 | 0.892 / 3.659 | 0.892 / 3.659 |
| nonlinear RLM | FullCP | 0.897 / 5.129 | 0.887 / 3.667 | 0.887 / 3.667 | 0.885 / 3.690 | 0.886 / 3.690 |
| nonlinear RLM | SplitCP | 0.893 / 112.906 | 0.892 / 3.764 | 0.892 / 3.765 | 0.893 / 3.812 | 0.893 / 3.812 |
| nonlinear RLM | RO-StabCP | 0.905 / 112.970 | 0.901 / 3.805 | 0.902 / 3.806 | 0.897 / 3.828 | 0.897 / 3.828 |
| nonlinear RLM | LOO-StabCP | 0.904 / 112.970 | 0.901 / 3.805 | 0.902 / 3.806 | 0.897 / 3.827 | 0.897 / 3.827 |
| nonlinear SGD | OracleCP | 0.902 / 112.806 | 0.901 / 3.663 | 0.902 / 3.663 | 0.892 / 3.641 | 0.892 / 3.641 |
| nonlinear SGD | FullCP | 0.900 / 5.137 | 0.895 / 3.725 | 0.895 / 3.726 | 0.885 / 3.690 | 0.886 / 3.690 |
| nonlinear SGD | SplitCP | 0.901 / 113.031 | 0.903 / 3.887 | 0.903 / 3.885 | 0.895 / 3.855 | 0.895 / 3.855 |
| nonlinear SGD | RO-StabCP | 0.909 / 113.028 | 0.910 / 3.889 | 0.910 / 3.890 | 0.900 / 3.849 | 0.900 / 3.849 |
| nonlinear SGD | LOO-StabCP | 0.904 / 112.968 | 0.903 / 3.829 | 0.904 / 3.830 | 0.894 / 3.789 | 0.894 / 3.789 |

Max relative length gap, authors' setup vs Table 2: 2.36%


## Derandomised split conformal (App. B, Figs. 7-8) vs the supplement result files

Mean coverage / mean length (time in ms) over 100 repetitions. Ours: m = 100. Supplement: `results_synthetic_derandom.csv` (K = 30) and `results_real_derandom.csv` (K = 50).

| Setting | Source | LOO-StabCP | MM-SplitCP | EM-SplitCP | SplitCP |
|---|---|---|---|---|---|
| Linear, RLM | text | 0.905 / 6.515 (0.7) | 0.976 / 9.050 (8.2) | 0.951 / 7.920 (9.5) | 0.910 / 6.808 (0.3) |
| Linear, RLM | authors | 0.907 / 3.371 (1.6) | 0.942 / 3.851 (8.8) | 0.910 / 3.430 (9.9) | 0.901 / 3.373 (0.3) |
| Linear, RLM | file | 0.909 / 3.399 (25.3) | 0.944 / 3.906 (467.1) | 0.913 / 3.489 (1293.2) | 0.903 / 3.415 (13.4) |
| Linear, SGD | text | 0.908 / 6.475 (0.5) | 0.973 / 8.865 (7.0) | 0.951 / 7.934 (8.2) | 0.906 / 6.670 (0.2) |
| Linear, SGD | authors | 0.905 / 3.391 (1.3) | 0.946 / 3.894 (5.7) | 0.913 / 3.510 (6.8) | 0.908 / 3.488 (0.2) |
| Linear, SGD | file | 0.906 / 3.361 (7.1) | 0.940 / 3.865 (159.3) | 0.910 / 3.481 (981.7) | 0.905 / 3.449 (3.1) |
| Nonlinear, RLM | text | 0.904 / 112.970 (0.7) | 0.977 / 114.374 (7.8) | 0.952 / 113.776 (9.0) | 0.893 / 112.906 (0.3) |
| Nonlinear, RLM | authors | 0.901 / 3.805 (1.8) | 0.941 / 4.326 (9.1) | 0.904 / 3.892 (10.1) | 0.892 / 3.764 (0.3) |
| Nonlinear, RLM | file | 0.911 / 3.920 (28.6) | 0.945 / 4.433 (523.8) | 0.915 / 4.003 (1359.7) | 0.903 / 3.988 (16.0) |
| Nonlinear, SGD | text | 0.904 / 112.968 (0.5) | 0.980 / 114.523 (5.7) | 0.948 / 113.866 (6.9) | 0.901 / 113.031 (0.2) |
| Nonlinear, SGD | authors | 0.903 / 3.829 (1.3) | 0.942 / 4.416 (5.9) | 0.909 / 3.972 (7.0) | 0.903 / 3.887 (0.2) |
| Nonlinear, SGD | file | 0.908 / 3.882 (8.5) | 0.946 / 4.447 (174.3) | 0.914 / 3.998 (1019.5) | 0.907 / 4.028 (3.6) |
| Boston, RLM | text | 0.920 / 2.183 (0.9) | 0.953 / 3.331 (8.0) | 0.936 / 2.768 (9.3) | 0.902 / 2.017 (0.3) |
| Boston, RLM | authors | 0.900 / 2.869 (1.8) | 0.945 / 4.127 (12.8) | 0.928 / 3.438 (15.1) | 0.895 / 2.861 (0.3) |
| Boston, RLM | file | 0.902 / 2.872 (15.4) | 0.944 / 4.121 (556.7) | 0.929 / 3.519 (2692.8) | 0.892 / 2.825 (10.1) |
| Boston, SGD | text | 0.961 / 2.284 (0.7) | 0.950 / 2.155 (7.5) | 0.931 / 1.926 (8.6) | 0.897 / 1.567 (0.2) |
| Boston, SGD | authors | 0.897 / 1.815 (1.4) | 0.938 / 2.945 (8.7) | 0.922 / 2.443 (10.8) | 0.884 / 1.883 (0.2) |
| Boston, SGD | file | 0.905 / 1.839 (15.1) | 0.945 / 3.002 (526.6) | 0.930 / 2.480 (2664.2) | 0.900 / 1.931 (8.8) |
| Diabetes, RLM | text | 0.936 / 2.726 (0.8) | 0.954 / 2.883 (7.7) | 0.936 / 2.745 (8.8) | 0.902 / 2.540 (0.2) |
| Diabetes, RLM | authors | 0.901 / 2.888 (1.6) | 0.944 / 3.282 (11.7) | 0.927 / 3.119 (13.7) | 0.889 / 2.852 (0.2) |
| Diabetes, RLM | file | 0.902 / 2.891 (13.4) | 0.941 / 3.271 (483.8) | 0.925 / 3.101 (2630.6) | 0.897 / 2.885 (8.5) |
| Diabetes, SGD | text | 0.958 / 2.924 (0.6) | 0.959 / 2.776 (6.7) | 0.939 / 2.612 (7.8) | 0.908 / 2.433 (0.2) |
| Diabetes, SGD | authors | 0.909 / 2.464 (1.3) | 0.946 / 2.801 (8.1) | 0.928 / 2.669 (10.0) | 0.900 / 2.494 (0.2) |
| Diabetes, SGD | file | 0.906 / 2.461 (13.3) | 0.944 / 2.794 (470.5) | 0.929 / 2.669 (2613.4) | 0.897 / 2.484 (7.8) |

## Neural networks (§5 Fig. 3, App. A.2 Fig. 6) vs `results_nn.csv`

`results_nn.csv` holds 100 repetitions per data set and method, without a column for the architecture. Its medians agree with our digitised Fig. 6 (hidden layers (10, 5)) to within the values below, so we treat it as the Fig. 6 run, although the shipped `real_NN.py` is set to one hidden layer of 20.

| Data | Method | file median | digitised Fig. 6 median | |diff| | digitised Fig. 3 median |
|---|---|---|---|---|---|
| boston | SplitCP | 3.156 | 3.159 | 0.003 | 2.558 |
| boston | RO-StabCP | 3.281 | 3.287 | 0.006 | 2.481 |
| boston | LOO-StabCP | 3.154 | 3.159 | 0.005 | 2.358 |
| diabetes | SplitCP | 3.009 | 3.009 | 0.000 | 2.773 |
| diabetes | RO-StabCP | 3.131 | 3.137 | 0.006 | 2.881 |
| diabetes | LOO-StabCP | 3.072 | 3.076 | 0.004 | 2.819 |

Max |file median − digitised Fig. 6 median| = 0.0061

Mean coverage / mean length (median length) over 100 repetitions:

| Hidden | Data | Method | text | D2-D7, our network | + authors' network, Eq. (8) bound | authors' setup (+ constant bound) | supplement file |
|---|---|---|---|---|---|---|---|
| (20,) | boston | SplitCP | 0.902 / 1.798 (1.714) | 0.894 / 2.344 (2.302) | 0.891 / 2.521 (2.461) | 0.891 / 2.521 (2.461) | digitised median 2.558 |
| (20,) | boston | RO-StabCP | 0.996 / 4.923 (4.921) | 0.914 / 2.335 (2.327) | 0.917 / 2.484 (2.482) | 0.914 / 2.474 (2.469) | digitised median 2.481 |
| (20,) | boston | LOO-StabCP | 0.984 / 3.213 (3.219) | 0.908 / 2.210 (2.202) | 0.906 / 2.358 (2.357) | 0.904 / 2.352 (2.342) | digitised median 2.358 |
| (20,) | diabetes | SplitCP | 0.902 / 2.452 (2.459) | 0.893 / 2.827 (2.797) | 0.895 / 2.759 (2.725) | 0.895 / 2.759 (2.725) | digitised median 2.773 |
| (20,) | diabetes | RO-StabCP | 0.998 / 4.639 (4.634) | 0.927 / 2.893 (2.883) | 0.916 / 2.935 (2.945) | 0.923 / 2.955 (2.962) | digitised median 2.881 |
| (20,) | diabetes | LOO-StabCP | 0.985 / 3.485 (3.480) | 0.908 / 2.778 (2.769) | 0.905 / 2.825 (2.830) | 0.909 / 2.835 (2.839) | digitised median 2.819 |
| (10, 5) | boston | SplitCP | 0.908 / 2.873 (2.753) | 0.890 / 3.071 (3.054) | 0.894 / 3.141 (3.125) | 0.894 / 3.141 (3.125) | 0.889 / 3.119 (3.156) |
| (10, 5) | boston | RO-StabCP | 0.994 / 5.825 (5.865) | 0.923 / 3.281 (3.284) | 0.927 / 3.309 (3.332) | 0.916 / 3.275 (3.294) | 0.915 / 3.273 (3.281) |
| (10, 5) | boston | LOO-StabCP | 0.961 / 4.101 (4.108) | 0.911 / 3.153 (3.153) | 0.917 / 3.168 (3.175) | 0.906 / 3.151 (3.158) | 0.906 / 3.151 (3.154) |
| (10, 5) | diabetes | SplitCP | 0.907 / 3.070 (3.080) | 0.894 / 3.126 (3.084) | 0.887 / 2.922 (2.905) | 0.887 / 2.922 (2.905) | 0.892 / 3.007 (3.009) |
| (10, 5) | diabetes | RO-StabCP | 1.000 / 5.266 (5.266) | 0.929 / 3.371 (3.365) | 0.930 / 3.166 (3.165) | 0.940 / 3.176 (3.173) | 0.913 / 3.119 (3.131) |
| (10, 5) | diabetes | LOO-StabCP | 0.980 / 4.064 (4.066) | 0.911 / 3.254 (3.255) | 0.910 / 3.050 (3.048) | 0.914 / 3.056 (3.051) | 0.904 / 3.059 (3.072) |

One hidden layer: our medians (authors' setup) vs digitised Fig. 3 medians:

| Data | Method | ours | digitised | diff |
|---|---|---|---|---|
| boston | SplitCP | 2.461 | 2.558 | -0.097 |
| boston | RO-StabCP | 2.469 | 2.481 | -0.012 |
| boston | LOO-StabCP | 2.342 | 2.358 | -0.016 |
| diabetes | SplitCP | 2.725 | 2.773 | -0.048 |
| diabetes | RO-StabCP | 2.962 | 2.881 | +0.081 |
| diabetes | LOO-StabCP | 2.839 | 2.819 | +0.020 |

Mean time per repetition (s), authors' setup vs file:

- boston (20,) SplitCP: ours 0.0331
- boston (10, 5) SplitCP: ours 0.0108, file 0.0060
- boston (20,) RO-StabCP: ours 1.2654
- boston (10, 5) RO-StabCP: ours 1.4451, file 0.8449
- boston (20,) LOO-StabCP: ours 0.0139
- boston (10, 5) LOO-StabCP: ours 0.0161, file 0.0110
- diabetes (20,) SplitCP: ours 0.0096
- diabetes (10, 5) SplitCP: ours 0.0106, file 0.0031
- diabetes (20,) RO-StabCP: ours 0.9729
- diabetes (10, 5) RO-StabCP: ours 1.0764, file 0.3289
- diabetes (20,) LOO-StabCP: ours 0.0114
- diabetes (10, 5) LOO-StabCP: ours 0.0122, file 0.0058

## Kernels (App. A.1, Fig. 5) vs `results_kernel.csv`

SGD; mean coverage / mean length (sd of length) over 100 repetitions. Text RLM rows are ours only.

| Setting | Kernel | Method | text | authors' kernel parameters only | authors' setup | authors' setup, centred Y | text, kernel RLM | supplement file |
|---|---|---|---|---|---|---|---|---|
| linear | none | SplitCP | 0.891 / 6.400 (1.111) | 0.891 / 6.400 (1.111) | 0.901 / 3.450 (0.549) | 0.901 / 3.430 (0.522) | 0.913 / 6.785 | 0.909 / 3.541 (0.623) |
| linear | none | RO-StabCP | 0.907 / 6.410 (0.514) | 0.907 / 6.410 (0.514) | 0.903 / 3.386 (0.312) | 0.903 / 3.373 (0.282) | 0.905 / 6.510 | 0.911 / 3.466 (0.302) |
| linear | none | LOO-StabCP | 0.904 / 6.350 (0.514) | 0.904 / 6.350 (0.514) | 0.898 / 3.327 (0.312) | 0.898 / 3.313 (0.282) | 0.905 / 6.510 | 0.906 / 3.406 (0.302) |
| linear | rbf | SplitCP | 0.901 / 6.709 (1.170) | 0.901 / 6.714 (1.175) | 0.905 / 3.473 (0.573) | 0.904 / 3.466 (0.577) | 0.910 / 6.733 | 0.902 / 3.456 (0.549) |
| linear | rbf | RO-StabCP | 0.905 / 6.559 (0.539) | 0.910 / 6.665 (0.550) | 0.908 / 3.418 (0.295) | 0.908 / 3.422 (0.288) | 0.906 / 6.512 | 0.909 / 3.447 (0.284) |
| linear | rbf | LOO-StabCP | 0.905 / 6.559 (0.539) | 0.908 / 6.625 (0.550) | 0.904 / 3.378 (0.295) | 0.905 / 3.381 (0.288) | 0.907 / 6.532 | 0.906 / 3.407 (0.284) |
| linear | poly | SplitCP | 0.883 / 5.716 (1.017) | 0.900 / 6.658 (1.121) | 0.893 / 3.379 (0.561) | 0.891 / 3.378 (0.554) | 0.906 / 6.686 | 0.906 / 3.480 (0.545) |
| linear | poly | RO-StabCP | 1.000 / 18.432 (0.402) | 0.904 / 6.609 (0.596) | 0.905 / 3.415 (0.310) | 0.906 / 3.420 (0.306) | 1.000 / 21.243 | 0.913 / 3.498 (0.281) |
| linear | poly | LOO-StabCP | 1.000 / 11.575 (0.401) | 0.900 / 6.541 (0.596) | 0.900 / 3.347 (0.310) | 0.899 / 3.351 (0.306) | 1.000 / 21.747 | 0.908 / 3.429 (0.281) |
| nonlinear | none | SplitCP | 0.903 / 113.111 (0.746) | 0.903 / 113.111 (0.746) | 0.907 / 3.968 (0.669) | 0.904 / 3.481 (0.602) | 0.903 / 113.118 | 0.905 / 3.881 (0.543) |
| nonlinear | none | RO-StabCP | 0.912 / 113.050 (0.384) | 0.912 / 113.050 (0.384) | 0.912 / 3.918 (0.369) | 0.909 / 3.427 (0.317) | 0.904 / 113.047 | 0.910 / 3.908 (0.351) |
| nonlinear | none | LOO-StabCP | 0.905 / 112.990 (0.383) | 0.905 / 112.990 (0.383) | 0.906 / 3.859 (0.369) | 0.905 / 3.367 (0.317) | 0.903 / 113.047 | 0.906 / 3.849 (0.352) |
| nonlinear | rbf | SplitCP | 0.904 / 113.099 (0.631) | 0.903 / 111.684 (0.630) | 0.898 / 3.610 (0.603) | 0.895 / 3.388 (0.552) | 0.897 / 112.962 | 0.896 / 3.555 (0.619) |
| nonlinear | rbf | RO-StabCP | 0.896 / 112.911 (0.351) | 0.904 / 110.974 (0.353) | 0.903 / 3.516 (0.304) | 0.902 / 3.398 (0.301) | 0.897 / 112.892 | 0.907 / 3.529 (0.322) |
| nonlinear | rbf | LOO-StabCP | 0.896 / 112.911 (0.351) | 0.901 / 110.954 (0.353) | 0.900 / 3.475 (0.304) | 0.897 / 3.358 (0.301) | 0.900 / 112.911 | 0.903 / 3.487 (0.322) |
| nonlinear | poly | SplitCP | 0.784 / 6.122 (1.279) | 0.897 / 110.734 (0.653) | 0.901 / 3.518 (0.499) | 0.902 / 3.450 (0.488) | 0.905 / 111.997 | 0.907 / 3.554 (0.506) |
| nonlinear | poly | RO-StabCP | 1.000 / 19.028 (0.646) | 0.906 / 109.793 (0.317) | 0.912 / 3.533 (0.288) | 0.909 / 3.473 (0.302) | 1.000 / 126.595 | 0.908 / 3.483 (0.313) |
| nonlinear | poly | LOO-StabCP | 0.996 / 12.181 (0.639) | 0.900 / 109.757 (0.317) | 0.907 / 3.464 (0.288) | 0.904 / 3.405 (0.303) | 1.000 / 127.098 | 0.902 / 3.413 (0.313) |

Mean time per repetition (s), authors' setup vs file:

- none SplitCP: ours 0.0037, file 0.0041
- none RO-StabCP: ours 0.0127, file 0.5330
- none LOO-StabCP: ours 0.0013, file 0.0087
- rbf SplitCP: ours 0.0001, file 0.0044
- rbf RO-StabCP: ours 0.0128, file 0.5285
- rbf LOO-StabCP: ours 0.0013, file 0.0084
- poly SplitCP: ours 0.0002, file 0.0041
- poly RO-StabCP: ours 0.0130, file 0.5361
- poly LOO-StabCP: ours 0.0013, file 0.0088
