# Data
- `BostonHousing.csv` is **not** in this public snapshot. Harrison & Rubinfeld (1978) Boston Housing, 506 x 14, is fetched by `scripts/get_data.sh` from
  https://raw.githubusercontent.com/selva86/datasets/master/BostonHousing.csv,
  sha256 `ab16ba38fbbbbcc69fe930aab1293104f1442c8279c130d9eba03dd864bef675`.
  That GitHub mirror has no license file, so the downloaded CSV is not redistributed here. `src/loostab/data.py` writes `boston.csv` (the same table with upper-case column names) after the download. Both paths are gitignored.
  **Ethics note:** the `B` variable, 1000(Bk − 0.63)², encodes the proportion of Black residents of each town and was built on a racist assumption. That is why the dataset was removed from scikit-learn. We use it only to replicate the paper (arXiv:2504.12189v1 §5) and do not endorse its use.
- `diabetes.csv`: included. The Efron et al. (2004) diabetes data (442 x 10, unscaled), exported from `sklearn.datasets.load_diabetes(scaled=False)`. scikit-learn is BSD-3-Clause. If the file is absent, `src/loostab/data.py` exports it again from scikit-learn.

## Authors' result files (diagnosis only)
`scripts/get_data.sh` also downloads `result/results_synthetic.csv` and `result/results_real.csv` from
github.com/KiljaeL/LOO-StabCP at commit 3b37682 (sha256-checked) into `data/authors_results/`. They are used only to
build `results/diagnosis.md` and `results/authors_repo_summary.md`. That repository has no licence file, so these
files are not redistributed here (git-ignored).

## Authors' ICLR 2025 supplementary material (diagnosis only)
`scripts/get_data.sh` downloads the "Supplemental" zip of the ICLR 2025 paper,
https://proceedings.iclr.cc/paper_files/paper/2025/file/297fe652867e4897e9f1fe1cd715de19-Supplemental-Conference.zip
(1,101,625 bytes, sha256 `7f39cd75fda4e126ebdf5f545b34c3dbe2208f6216086e4137f23ef82a765e53`), into
`data/authors_supplement/supplement.zip`, extracts it to `data/authors_supplement/code_final/` and checks the sha256 of
every file used. Contents: `README.md`, `requirements.txt`, `simul.py`, `real.py`, `real_NN.py`, `kernel.py`,
`synthetic_derandom.py`, `real_derandom.py`, `recruit.py`, `funcs/{CP,CP_screening,utils,post}.py`, `data/recruit.csv`,
`result/` (7 CSV files: results_synthetic_ar1_05, results_real, results_nn, results_kernel, results_synthetic_derandom,
results_real_derandom, results_recruit) and `figure/` (8 PNG files). It is used only by
`scripts/compare_supplement.py` and `scripts/make_article_figures.py`. It has no licence file, so it is not
redistributed (git-ignored and excluded from the release zip).

## Screening data (§6, claim C8)

`data/screening/Placement_Data_Full_Class.csv` (215 rows, 15 columns) is the Kaggle dataset
"Campus Recruitment" (URL slug factors-affecting-campus-placement) by Ben Roshan D (data provided by Dr. Dhimant Ganatara, Jain University):
https://www.kaggle.com/datasets/benroshan/factors-affecting-campus-placement . Downloading needs a free Kaggle
login. The Kaggle page lists its licence as CC0: Public Domain (checked 24 Oct 2026). The file is kept **out of** the git repository
(`data/screening/` is in `.gitignore`). Download it yourself and place it at that path before running
`experiments/screen.py`. The copy we used had sha256
`f4f6ad9e13313a7edd12a71d88adfcec3e5153bf45469199c44e6d47c5de4bd3`.

`scripts/get_data.sh` also fetches the authors' published screening results (`result/results_recruit.csv` at
commit 3b37682) for diagnosis only; their means/sds equal the paper's Table 4.
