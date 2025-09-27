#!/usr/bin/env bash
# Simple setup script for macOS / zsh
set -euo pipefail
python -m venv .venv
echo "Activating virtualenv: source .venv/bin/activate"
# Install required packages
. .venv/bin/activate
pip install -r requirements.txt
# Install Playwright browsers (non-interactive)
playwright install

echo "Setup complete. Activate with: source .venv/bin/activate"
