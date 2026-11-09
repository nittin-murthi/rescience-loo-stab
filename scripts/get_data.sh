#!/usr/bin/env bash
# Downloads Boston Housing (Diabetes ships with scikit-learn). Paper: arXiv:2504.12189v1 §5.
set -euo pipefail
cd "$(dirname "$0")/../data"
[ -f BostonHousing.csv ] || curl -sL -o BostonHousing.csv https://raw.githubusercontent.com/selva86/datasets/master/BostonHousing.csv
echo "ab16ba38fbbbbcc69fe930aab1293104f1442c8279c130d9eba03dd864bef675  BostonHousing.csv" | sha256sum -c -
# Diagnosis only (DISCREPANCIES.md): the authors' own published result files at a pinned commit.
# These are result tables (data), not code; they are summarised in results/authors_repo_summary.md.
C=3b376827c77369dd3079c14734c6282c16901890
mkdir -p authors_results
for f in results_synthetic.csv results_real.csv results_recruit.csv; do
  [ -f authors_results/$f ] || curl -sfL -o authors_results/$f https://raw.githubusercontent.com/KiljaeL/LOO-StabCP/$C/result/$f
done
( cd authors_results && sha256sum -c - <<'SUMS'
d8d70a5e873c1bebd64d926a440ec1e30e50599614ebbcaf7cb5035fa4491181  results_synthetic.csv
503806e7ef585658cf0c7dfd861ada2cc4745ef377b183ae9c41f3e9b4b3884f  results_real.csv
33ed44e2716f06ff157f0e16899c2b52b91c691904875f655111fc4859aeae8c  results_recruit.csv
SUMS
)

# Diagnosis only: the authors' ICLR 2025 supplementary material (code_final/), listed as "Supplemental" on the
# ICLR proceedings page of the paper. It contains the kernel (App. A.1), neural-network (App. A.2) and
# derandomisation (App. B) scripts and result files that the GitHub repository lacks. Not redistributed here.
SUPP_URL=https://proceedings.iclr.cc/paper_files/paper/2025/file/297fe652867e4897e9f1fe1cd715de19-Supplemental-Conference.zip
mkdir -p authors_supplement
[ -f authors_supplement/supplement.zip ] || curl -sfL -o authors_supplement/supplement.zip "$SUPP_URL"
echo "7f39cd75fda4e126ebdf5f545b34c3dbe2208f6216086e4137f23ef82a765e53  authors_supplement/supplement.zip" | sha256sum -c -
[ -d authors_supplement/code_final ] || python3 -c "import zipfile; zipfile.ZipFile('authors_supplement/supplement.zip').extractall('authors_supplement')"
( cd authors_supplement/code_final && sha256sum -c - <<'SUMS'
355abfc895aef7a93dbd61363a81505793a59f36d766dbe23482c9b8b10d4aab  real_NN.py
cd0a1146f15de7b246e3e77ac576467cbfeca7404385221010bce5157bc93700  kernel.py
a91ba896a45f53b66785297be42e17e303475ca60ce418d29e8e47c3d35ccc1e  synthetic_derandom.py
62f32e625e05769a3e822ea82dd03340060ba2d57478cc49c83ac36f153f1a45  real_derandom.py
ae377385226e68e99d41e98be0cbcb01b3995e5fbf528f8d6be38f7a1f1fedff  simul.py
b9c35467f4a8133e7fbdf9d4e106e85c40cf85534c5a2204115555a8dd41e412  funcs/CP.py
495424e9d340f55285e2c98455777996b0c6ec273834abbef2c8e08fcfca1e1e  funcs/utils.py
a8340b7e21484831031b13a710bedde0a5d4719402fbeaaa0cfbe235bf33afde  result/results_nn.csv
272692fb4b6c0b7adfc72818443a055072eb62ca975dd755d67a3b433b51cd18  result/results_kernel.csv
b8d84696fca05fab9b26aa7a76dc49c70818a4aa51bd553908313432a5c2bf1a  result/results_synthetic_derandom.csv
789c0d3e0dbe8c010ad1def393fdc2cfecc1d89d8ac3315b823d93595a40360b  result/results_real_derandom.csv
7f4c97d64597f8bffa0ee8d192dad1c9489c74111aeeca7ac8c2857c3f6091d4  result/results_synthetic_ar1_05.csv
f4f6ad9e13313a7edd12a71d88adfcec3e5153bf45469199c44e6d47c5de4bd3  data/recruit.csv
SUMS
)

# Screening data (§6): Kaggle "Campus Recruitment" / "Factors affecting campus placement" by Ben Roshan.
# Kaggle lists it as CC0: Public Domain; it is still kept out of git here (data/screening/ is git-ignored). Download it yourself
# (a free Kaggle login is needed) from https://www.kaggle.com/datasets/benroshan/factors-affecting-campus-placement
# and place Placement_Data_Full_Class.csv (215 rows, 15 columns) in data/screening/.
# The supplement ships the same file as code_final/data/recruit.csv (identical sha256 to our Kaggle copy), so we
# take it from there when it is missing. The Kaggle page lists the data as CC0: Public Domain.
if [ ! -f screening/Placement_Data_Full_Class.csv ] && [ -f authors_supplement/code_final/data/recruit.csv ]; then
  mkdir -p screening && cp authors_supplement/code_final/data/recruit.csv screening/Placement_Data_Full_Class.csv
fi
if [ -f screening/Placement_Data_Full_Class.csv ]; then
  echo "f4f6ad9e13313a7edd12a71d88adfcec3e5153bf45469199c44e6d47c5de4bd3  screening/Placement_Data_Full_Class.csv" | sha256sum -c -
  echo "screening data present"
else
  echo "NOTE: data/screening/Placement_Data_Full_Class.csv missing; download it from Kaggle (see comment above)" >&2
fi

# Optional, for scripts/digitize_nn_figures.py only: the arXiv source of the original paper (its box-plot PNGs).
if [ ! -f ../paper/src/plots/rev_figure_nn_1layer.png ]; then
  mkdir -p ../paper/src && curl -sfL -o ../paper/src.tar.gz https://arxiv.org/e-print/2504.12189v1 \
    && echo "d2690b91e41a1158aa3b71789b400e3ab4f17d9891dd1329189420aa059a6cec  ../paper/src.tar.gz" | sha256sum -c - \
    && tar -xzf ../paper/src.tar.gz -C ../paper/src || echo "NOTE: could not fetch arXiv source (only needed for digitize_nn_figures.py)" >&2
fi
