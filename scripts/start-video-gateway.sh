#!/usr/bin/env bash
# Video Gateway 启动脚本
# 作用：生成待审核 mock 结果文件。

set -euo pipefail

if command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="python3"
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN="python"
else
  echo "未找到 Python。请先参考 docs/install.md 手动准备 Python 环境。" >&2
  exit 1
fi

"$PYTHON_BIN" ./services/video-gateway/src/main.py --topic "视频网关演示主题" --review-items-json '[{"title":"示例选题","script_text":"这是一个脚本占位结果。"}]'
