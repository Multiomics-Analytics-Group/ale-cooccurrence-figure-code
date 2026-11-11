#!/usr/bin/env bash
# Rebuild every figure from the pipeline outputs in data/ and the precomputed values in cache/.
# Needs the two conda environments defined in environments/ (see README.md).
set -euo pipefail
cd "$(dirname "$0")"

ENV_A=ale-paper-a    # Figures 1, 3, 5 and S2
ENV_B=ale-paper-b    # Figures 4, 6 and S1

# Each notebook must run in the Python of the environment named for it: prefer the environment's
# own Jupyter kernel over a user-level kernel called python3, and ignore packages in the user's
# site-packages folder. The last setting silences a notice about frozen modules that the
# debugger of the Python 3.12 kernel prints at start.
export JUPYTER_PREFER_ENV_PATH=1 PYTHONNOUSERSITE=1 PYDEVD_DISABLE_FILE_VALIDATION=1

run_notebook() {    # environment, notebook in code/
  echo "== $2 ($1)"
  conda run -n "$1" --no-capture-output python -m nbconvert --to notebook --execute --inplace \
    --ExecutePreprocessor.timeout=1800 --ExecutePreprocessor.record_timing=False "code/$2"
}

run_notebook "$ENV_A" Figure_1.ipynb
run_notebook "$ENV_A" Figure_3.ipynb
run_notebook "$ENV_B" Figure_4.ipynb
run_notebook "$ENV_A" Figure_5.ipynb

echo "== Figure_6.py ($ENV_B)"
conda run -n "$ENV_B" --no-capture-output python code/Figure_6.py figures/Figure_6
conda run -n "$ENV_B" --no-capture-output python code/svg_for_illustrator.py \
  figures/Figure_6/Figure_6_raw.svg figures/Figure_6/Figure_6.svg "Build binary|unit matrix" ""
rm figures/Figure_6/Figure_6_raw.svg

run_notebook "$ENV_B" Figure_S1.ipynb
run_notebook "$ENV_A" Figure_S2.ipynb
echo "All figures written to figures/"
