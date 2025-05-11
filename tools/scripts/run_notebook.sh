#!/usr/bin/env bash
set -euo pipefail

NOTEBOOK_FILE="${RUNFILES_DIR:-$(pwd)}/sandbox_notebook.ipynb"

# Check if file exists
if [ ! -f "$NOTEBOOK_FILE" ]; then
  echo "Notebook file not found: $NOTEBOOK_FILE"
  exit 1
fi

echo "Launching Jupyter on: $NOTEBOOK_FILE"

jupyter notebook "$NOTEBOOK_FILE" --ip=127.0.0.1 --port=8888 --no-browser
