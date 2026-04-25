#!/usr/bin/env bash
# content pipeline runner
# Purpose: run trend radar, viral analysis, original rewrite, distribution package, and Feishu review.

set -euo pipefail

if [[ -x ./.venv/Scripts/python.exe ]]; then
  PYTHON_BIN="./.venv/Scripts/python.exe"
elif [[ -x ./.venv/bin/python ]]; then
  PYTHON_BIN="./.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="python3"
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN="python"
else
  echo "Python was not found. Please prepare Python manually by following docs/install.md." >&2
  exit 1
fi

"$PYTHON_BIN" ./src/lobster_farm/content_pipeline/app.py --topic "AI分身内容增长"
