#!/usr/bin/env bash
# VM 生产健康检查脚本。
# 作用：
# 1. 检查项目目录、.venv、.env、运行状态文件是否存在。
# 2. 检查 verify.sh 是否通过。
# 3. 检查 systemd timer 是否 active。
# 4. 输出最近一次运行状态。

set -euo pipefail

PROJECT_ROOT="/opt/lobster-farm"
STATUS_FILE="${PROJECT_ROOT}/data/runtime/run-dev/status.env"
VERIFY_SCRIPT="${PROJECT_ROOT}/scripts/verify.sh"
TIMER_NAME="lobster-farm-run-dev.timer"

print_ok() {
  echo "[通过] $1"
}

print_fail() {
  echo "[失败] $1"
}

print_info() {
  echo "[信息] $1"
}

overall_ok=0

if [[ -d "${PROJECT_ROOT}" ]]; then
  print_ok "项目目录存在：${PROJECT_ROOT}"
else
  print_fail "项目目录不存在：${PROJECT_ROOT}"
  overall_ok=1
fi

if [[ -d "${PROJECT_ROOT}/.venv" ]]; then
  print_ok ".venv 存在"
else
  print_fail ".venv 不存在"
  overall_ok=1
fi

if [[ -f "${PROJECT_ROOT}/.env" ]]; then
  print_ok ".env 存在"
else
  print_fail ".env 不存在"
  overall_ok=1
fi

if [[ -f "${STATUS_FILE}" ]]; then
  print_ok "运行状态文件存在：${STATUS_FILE}"
  # shellcheck disable=SC1090
  source "${STATUS_FILE}"
  print_info "最近一次运行时间：${LAST_RUN_AT:-未知}"
  print_info "最近一次运行状态：${LAST_RUN_STATUS:-未知}"
  print_info "最近一次退出码：${LAST_EXIT_CODE:-未知}"
  print_info "连续失败次数：${FAILURE_COUNT:-未知}"
else
  print_fail "运行状态文件不存在：${STATUS_FILE}"
  overall_ok=1
fi

if systemctl is-active --quiet "${TIMER_NAME}"; then
  print_ok "systemd timer 处于 active 状态：${TIMER_NAME}"
else
  print_fail "systemd timer 不在 active 状态：${TIMER_NAME}"
  overall_ok=1
fi

cd "${PROJECT_ROOT}"

if [[ -x "${VERIFY_SCRIPT}" || -f "${VERIFY_SCRIPT}" ]]; then
  print_info "开始执行 verify.sh ..."
  if bash "${VERIFY_SCRIPT}" >/tmp/lobster-farm-health-verify.log 2>&1; then
    print_ok "verify.sh 检查通过"
  else
    print_fail "verify.sh 检查失败，详情见：/tmp/lobster-farm-health-verify.log"
    overall_ok=1
  fi
else
  print_fail "verify.sh 不存在：${VERIFY_SCRIPT}"
  overall_ok=1
fi

exit "${overall_ok}"
