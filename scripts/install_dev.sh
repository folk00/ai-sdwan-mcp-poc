#!/usr/bin/env bash
set -euo pipefail

PYTHON_BIN="${PYTHON_BIN:-python3}"

if [ ! -d ".venv" ]; then
  "$PYTHON_BIN" -m venv .venv
fi

. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m py_compile \
  backend/app.py \
  backend/automation_engine.py \
  mcp_server/sdwan_tools_example.py \
  mcp_server/tool_catalog.py \
  scripts/print_tool_catalog.py

echo "Development environment ready."
echo "Run tests with: python -m unittest discover -s tests -t . -v"
