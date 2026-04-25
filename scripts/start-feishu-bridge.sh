#!/usr/bin/env bash
# Feishu Bridge 启动脚本
# 作用：生成飞书 dry-run 消息内容。

set -euo pipefail

if command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="python3"
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN="python"
else
  echo "未找到 Python。请先参考 docs/install.md 手动准备 Python 环境。" >&2
  exit 1
fi

"$PYTHON_BIN" ./services/feishu-bridge/src/main.py --topic "飞书桥接演示主题"
