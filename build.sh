#!/usr/bin/env bash
set -o errexit

# Install system dependencies (Debian-based)
apt-get update && apt-get install -y \
    build-essential \
    graphviz-dev \
    libpq-dev \
    python3-dev \
    pkg-config \
    git

# Install Python build tools
pip install --upgrade pip setuptools wheel Cython

# Install Python dependencies
pip install -r requirements.txt
