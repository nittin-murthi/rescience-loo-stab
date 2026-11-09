# Neural-network results digitised from the original paper's box plots

Source: arXiv source of the paper, `plots/rev_figure_nn_1layer.png` (paper Fig. 3, one hidden layer of 20)
and `plots/rev_figure_nn_2layer.png` (paper App. A.2 Fig. 6, hidden layers (10, 5)). Values are box-plot
MEDIANS and quartiles converted from pixel rows by `scripts/digitize_nn_figures.py`; resolution ~ one line
width (column `res`). The authors did not publish the underlying numbers.

| Figure | Panel | Data | Method | Q1 | Median | Q3 | res |
|---|---|---|---|---|---|---|---|
| rev_figure_nn_1layer.png | Length | Boston | SplitCP | 2.350 | 2.558 | 2.712 | 0.015 |
| rev_figure_nn_1layer.png | Length | Boston | RO-StabCP | 2.396 | 2.481 | 2.542 | 0.015 |
| rev_figure_nn_1layer.png | Length | Boston | LOO-StabCP | 2.288 | 2.358 | 2.412 | 0.015 |
| rev_figure_nn_1layer.png | Length | Diabetes | SplitCP | 2.635 | 2.773 | 2.904 | 0.015 |
| rev_figure_nn_1layer.png | Length | Diabetes | RO-StabCP | 2.865 | 2.881 | 2.912 | 0.015 |
| rev_figure_nn_1layer.png | Length | Diabetes | LOO-StabCP | 2.804 | 2.819 | 2.858 | 0.015 |
| rev_figure_nn_2layer.png | Length | Boston | SplitCP | 2.888 | 3.159 | 3.347 | 0.015 |
| rev_figure_nn_2layer.png | Length | Boston | RO-StabCP | 3.227 | 3.287 | 3.340 | 0.015 |
| rev_figure_nn_2layer.png | Length | Boston | LOO-StabCP | 3.114 | 3.159 | 3.212 | 0.015 |
| rev_figure_nn_2layer.png | Length | Diabetes | SplitCP | 2.926 | 3.009 | 3.076 | 0.015 |
| rev_figure_nn_2layer.png | Length | Diabetes | RO-StabCP | 3.107 | 3.137 | 3.152 | 0.015 |
| rev_figure_nn_2layer.png | Length | Diabetes | LOO-StabCP | 3.039 | 3.076 | 3.091 | 0.015 |

## Comparison with our medians (100 repetitions each; results/raw/nn*.csv)

Median interval length. Text setup = `nn`; X/sqrt(d) only = `nn_a_scale`; authors' setup (GitHub + supplement choices, scikit-learn network) = `nn_authors`. For the (10, 5) run the supplement's raw `results_nn.csv` supersedes these digitised values; see results/supplement_comparison.md (max |difference of medians| 0.006).

| Hidden | Data | Method | Original (digitised) | Ours, text setup | Ours, X/sqrt(d) only | Ours, authors' setup |
|---|---|---|---|---|---|---|
| (20,) | Boston | SplitCP | 2.558 | 1.714 | 2.418 | 2.461 |
| (20,) | Boston | RO-StabCP | 2.481 | 4.921 | 2.342 | 2.469 |
| (20,) | Boston | LOO-StabCP | 2.358 | 3.219 | 2.238 | 2.342 |
| (20,) | Diabetes | SplitCP | 2.773 | 2.459 | 2.873 | 2.725 |
| (20,) | Diabetes | RO-StabCP | 2.881 | 4.634 | 2.889 | 2.962 |
| (20,) | Diabetes | LOO-StabCP | 2.819 | 3.480 | 2.771 | 2.839 |
| (10, 5) | Boston | SplitCP | 3.159 | 2.753 | 3.161 | 3.125 |
| (10, 5) | Boston | RO-StabCP | 3.287 | 5.865 | 3.310 | 3.294 |
| (10, 5) | Boston | LOO-StabCP | 3.159 | 4.108 | 3.185 | 3.158 |
| (10, 5) | Diabetes | SplitCP | 3.009 | 3.080 | 3.261 | 2.905 |
| (10, 5) | Diabetes | RO-StabCP | 3.137 | 5.266 | 3.408 | 3.173 |
| (10, 5) | Diabetes | LOO-StabCP | 3.076 | 4.066 | 3.289 | 3.051 |
