#!/usr/bin/env bash
set -o errexit

# Update and install required system packages
apt-get update && apt-get install -y \
    graphviz \
    graphviz-dev \
    libgraphviz-dev \
    pkg-config \
    python3-dev \
    build-essential \
    curl

# Upgrade pip & build tools
python3 -m pip install --upgrade pip setuptools wheel Cython

# Avoid source builds for problematic packages (like PyYAML)
# by using binary-only installs where possible
python3 -m pip install --only-binary=:all: PyYAML

# Then install your project requirements
python3 -m pip install -r requirements.txt
