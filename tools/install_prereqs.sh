#!/bin/bash
set -e  # Exit on error
OS_TYPE="$(uname)"
if [ "$OS_TYPE" = "Darwin" ]; then
    echo "Detected macOS."
    brew install pipx bazel python3
    # python3 -m pip install --user pip-tools
    # python3 -m piptools compile requirements.in --output-file=requirements.txt
elif [ "$OS_TYPE" = "Linux" ]; then
    echo "Detected linux."
    pip install pip-tools
    # pip-compile requirements.in --output-file=requirements.txt
else
    echo "Unsupported OS: $OS_TYPE"
    exit 1
fi
# Install the requirements