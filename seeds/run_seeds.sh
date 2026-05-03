#!/usr/bin/env bash
set -euo pipefail

# Run all seeds or a specific one
# Usage:
#   bash seeds/run_seeds.sh              -> runs all in order
#   bash seeds/run_seeds.sh 02_products  -> runs only that script

cd "$(dirname "$0")"

if [ -n "${1:-}" ]; then
    echo "Running $1.py ..."
    python3 "$1.py"
else
    for f in [0-9]*.py; do
        echo "==> Running $f ..."
        python3 "$f"
        echo ""
    done
fi
