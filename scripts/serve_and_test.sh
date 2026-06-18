#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

echo "=== Installing dependencies ==="
pip3 install -r requirements.txt --break-system-packages -q

echo "=== Installing Chromium ==="
playwright install chromium

echo "=== Running tests ==="
pytest tests/ -v

echo "=== Generating report ==="
python3 scripts/generate_report.py

echo "=== Done ==="
