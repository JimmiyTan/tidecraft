#!/usr/bin/env bash
# phase-07 客户前端演示启动脚本
# 作用：仅在 127.0.0.1 启动本地客户演示页面。

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
  echo "未找到 Python。请先参考 docs/install.md 准备 Python 环境。" >&2
  exit 1
fi

"$PYTHON_BIN" ./services/orchestrator/src/customer_demo_server.py --open "$@"
