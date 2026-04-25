#!/usr/bin/env bash
# phase-01.5 开发运行脚本
# 作用：运行最小闭环编排链路，生成消息预览、状态文件和待审核结果。

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
  echo "未找到 Python。请先参考 docs/install.md 手动准备 Python 环境。" >&2
  exit 1
fi

"$PYTHON_BIN" ./services/orchestrator/src/main.py --topic "lobster-farm phase-04 demo topic"
