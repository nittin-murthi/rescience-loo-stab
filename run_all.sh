#!/usr/bin/env bash
# Reproduces every number and figure of this replication of arXiv:2504.12189v1.
# Usage: PY=.venv/bin/python bash run_all.sh   (about 30 min on 4 CPU cores; see results/runtimes.md)
set -euo pipefail
cd "$(dirname "$0")"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
PY=${PY:-python}
W=${WORKERS:-4}
bash scripts/get_data.sh
$PY experiments/run.py sim  --workers "$W" 2>&1 | tee logs/sim.log
$PY experiments/run.py sim  --workers "$W" --variant centered 2>&1 | tee logs/sim_centered.log
$PY experiments/run.py real --workers "$W" 2>&1 | tee logs/real.log
$PY experiments/run.py nn   --workers "$W" 2>&1 | tee logs/nn.log
# ---- diagnosis variants (added after consulting the authors' code; see DISCREPANCIES.md) ----
# "authors" uses every choice found in the GitHub code and the ICLR supplementary material; "*_github" are the
# earlier variants built from the GitHub repository alone (kept for the record).
for v in a_dgp a_dgp_github authors authors_github; do $PY experiments/run.py sim --workers "$W" --variant $v 2>&1 | tee logs/sim_$v.log; done
for v in a_scale a_coupled a_cpdetails authors authors_github; do $PY experiments/run.py real --workers "$W" --variant $v 2>&1 | tee logs/real_$v.log; done
for v in a_scale a_oursnet a_sknet authors; do $PY experiments/run.py nn --workers "$W" --variant $v 2>&1 | tee logs/nn_$v.log; done
# ---- kernel study, claim C6 (App. A.1); written after reading the supplementary material ----
$PY experiments/run.py kernel --workers "$W" 2>&1 | tee logs/kernel_text.log
for v in a_kparams authors authors_centered; do $PY experiments/run.py kernel --workers "$W" --variant $v 2>&1 | tee logs/kernel_$v.log; done
$PY scripts/make_tables.py
$PY scripts/make_figures.py
[ -f paper/src/plots/rev_figure_nn_1layer.png ] && $PY scripts/digitize_nn_figures.py
$PY tools/traceability.py
# ---- screening, claim C8 (§6); needs data/screening/Placement_Data_Full_Class.csv from Kaggle (see data/README.md) ----
if [ -f data/screening/Placement_Data_Full_Class.csv ]; then
  $PY experiments/screen.py --workers "$W" 2>&1 | tee logs/screen.log
  for v in a_split a_xscale a_tau a_cal50 authors authors_resplit authors_fixtau; do
    $PY experiments/screen.py --workers "$W" --variant $v 2>&1 | tee logs/screen_$v.log
  done
  $PY scripts/make_screening.py
  $PY tools/traceability.py
fi
# ---- comparison with the result files of the supplementary material (needs data/authors_supplement/) ----
[ -d data/authors_supplement/code_final ] && $PY scripts/compare_supplement.py
# ---- article figures (figures/article_*.pdf); need the screening results and data/authors_results/ (see data/README.md) ----
[ -f results/raw/screen.csv ] && [ -d data/authors_results ] && $PY scripts/make_article_figures.py
