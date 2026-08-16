#!/usr/bin/env bash
# phase-07 一键功能演示脚本
# 作用：使用固定 dry-run/mock 配置演示完整人工审核与发布回执闭环。

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

if [[ $# -eq 0 ]]; then
  set -- --topic "AI 如何帮助本地商家提升短视频内容效率"
fi

"$PYTHON_BIN" ./services/orchestrator/src/demo.py "$@"
