#!/usr/bin/env bash
# 第一阶段引导脚本
# 作用：检查关键目录是否存在，不做联网安装。

set -euo pipefail

required_dirs=(
  "config"
  "docs"
  "apps/openclaw"
  "workers/hermes"
  "services/feishu-bridge"
  "services/video-gateway"
  "services/orchestrator"
  "tests/smoke"
)

for dir in "${required_dirs[@]}"; do
  if [[ ! -d "$dir" ]]; then
    echo "缺少目录：$dir" >&2
    exit 1
  fi
done

echo "bootstrap 完成：目录骨架已存在。"
