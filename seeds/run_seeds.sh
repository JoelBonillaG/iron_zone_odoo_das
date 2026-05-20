#!/usr/bin/env bash
set -euo pipefail

# Run all seeds or a specific one
# Usage:
#   bash seeds/run_seeds.sh              -> runs all in order
#   bash seeds/run_seeds.sh 03_products  -> runs only that script

cd "$(dirname "$0")"

# Detect Python executable
if command -v py >/dev/null 2>&1; then
    PYTHON_BIN="py"
elif command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_BIN="python"
else
    echo "Python not found. Install Python 3 and ensure it is in PATH."
    exit 1
fi

# Run a specific seed
if [ -n "${1:-}" ]; then
    echo "Running $1.py ..."
    "$PYTHON_BIN" "$1.py"

# Run all seeds
else
    echo "==> Running 00_company_config.py ..."
    "$PYTHON_BIN" 00_company_config.py
    echo ""

    echo "==> Running 00_smtp_config.py ..."
    "$PYTHON_BIN" 00_smtp_config.py
    echo ""

    echo "==> Running 01_email_templates_sync.py ..."
    "$PYTHON_BIN" 01_email_templates_sync.py
    echo ""

    for f in [0-9]*.py; do
        if [ "$f" = "00_company_config.py" ] || [ "$f" = "00_smtp_config.py" ] || [ "$f" = "01_email_templates_sync.py" ]; then
            continue
        fi

        echo "==> Running $f ..."
        "$PYTHON_BIN" "$f"
        echo ""
    done
fi