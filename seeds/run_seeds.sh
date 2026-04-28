#!/bin/bash
# Run all seeds or a specific one
# Usage:
#   bash seeds/run_seeds.sh              -> runs all in order
#   bash seeds/run_seeds.sh 02_products  -> runs only that script

cd seeds

if [ -n "$1" ]; then
    echo "Running $1.py ..."
    python3 "$1.py"
else
    for f in $(ls [0-9]*.py | sort); do
        echo "==> Running $f ..."
        python3 "$f"
        echo ""
    done
fi
