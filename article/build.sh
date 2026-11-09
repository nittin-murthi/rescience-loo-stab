#!/usr/bin/env bash
# Replication of arXiv:2504.12189v1 (Lee & Zhang, ICLR 2025); article for ReScience C.
# Builds article.pdf from metadata.yaml + content.tex with tectonic (XeTeX engine) and biber 2.17.
# The template's yaml-to-latex.py forces locale en_US.UTF-8; we map it to C.UTF-8 when that locale is missing.
set -euo pipefail
cd "$(dirname "$0")"
PY=${PY:-../.venv/bin/python}
$PY -W ignore -c "
import locale, runpy, sys
_s = locale.setlocale
def _set(c, l=None):
    try: return _s(c, l)
    except locale.Error: return _s(c, 'C.UTF-8')
locale.setlocale = _set
sys.path.insert(0, '.'); sys.argv = ['yaml-to-latex.py', '-i', 'metadata.yaml', '-o', 'metadata.tex']
runpy.run_path('yaml-to-latex.py', run_name='__main__')"
PATH="$HOME/bin:/home/box/bin:$PATH" tectonic article.tex
