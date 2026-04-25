#!/usr/bin/env bash
# 兼容旧 service 方案的循环包装脚本。
# 说明：
# 1. 新的生产默认方案是 systemd timer。
# 2. 此脚本保留给需要 while+sleep 模式的场景。

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
INTERVAL_SECONDS="${LOBSTER_RUN_INTERVAL_SECONDS:-300}"

cd "${PROJECT_ROOT}"

while true; do
  if ! bash ./scripts/vm/run-dev-managed.sh; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') [run-dev-service] 检测到执行失败，将在等待后重试。"
  fi
  sleep "${INTERVAL_SECONDS}"
done
