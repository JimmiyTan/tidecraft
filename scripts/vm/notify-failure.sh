#!/usr/bin/env bash
# run-dev 连续失败告警预留脚本。
# 当前行为：
# 1. 将失败信息写入标准输出，供 journald 收集。
# 2. 预留后续飞书告警接入点，但默认不主动发送。

set -euo pipefail

FAILURE_COUNT="${1:-0}"
EXIT_CODE="${2:-1}"
FAILURE_LOG_PATH="${3:-}"

echo "$(date '+%Y-%m-%d %H:%M:%S') [notify-failure] 连续失败达到阈值，failure_count=${FAILURE_COUNT}，exit_code=${EXIT_CODE}。"
if [[ -n "${FAILURE_LOG_PATH}" ]]; then
  echo "$(date '+%Y-%m-%d %H:%M:%S') [notify-failure] 最近失败日志：${FAILURE_LOG_PATH}"
fi
echo "$(date '+%Y-%m-%d %H:%M:%S') [notify-failure] 预留飞书告警接口：后续可在此处接入飞书发送逻辑。"
