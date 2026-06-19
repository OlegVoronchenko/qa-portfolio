#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

echo "=== Installing Node dependencies ==="
npm install

echo "=== Building Vite app ==="
npm run build

echo "=== Installing Python dependencies ==="
pip3 install -r requirements.txt -q

echo "=== Installing Chromium ==="
playwright install chromium

echo "=== Running tests ==="
pytest tests/ -v

echo "=== Generating report ==="
python3 scripts/generate_report.py

echo "=== Done ==="
