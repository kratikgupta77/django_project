#!/usr/bin/env bash
set -o errexit

# Required system packages for pygraphviz and other builds
apt-get update && apt-get install -y \
    graphviz \
    graphviz-dev \
    libgraphviz-dev \
    pkg-config \
    python3-dev \
    build-essential

# Upgrade pip and build tools
pip install --upgrade pip setuptools wheel Cython

# Install requirements
pip install -r requirements.txt
