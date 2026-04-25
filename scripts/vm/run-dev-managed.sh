#!/usr/bin/env bash
# run-dev 常驻执行统一入口。
# 作用：
# 1. 显式加载项目根目录 .env。
# 2. 通过 flock 防止重入。
# 3. 记录最近成功/失败信息。
# 4. 在连续失败达到阈值时调用预留告警脚本。

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
RUNTIME_DIR="${PROJECT_ROOT}/data/runtime/run-dev"
LOCK_FILE="${RUNTIME_DIR}/run-dev.lock"
LAST_FAILURE_LOG="${RUNTIME_DIR}/last_failure.log"
LAST_SUCCESS_LOG="${RUNTIME_DIR}/last_success.log"
STATUS_FILE="${RUNTIME_DIR}/status.env"
FAILURE_THRESHOLD="${LOBSTER_FAILURE_ALERT_THRESHOLD:-3}"
SANITIZED_ENV_FILE="${RUNTIME_DIR}/systemd.env"

mkdir -p "${RUNTIME_DIR}"
cd "${PROJECT_ROOT}"

if [[ -f "${SANITIZED_ENV_FILE}" ]]; then
  # 优先加载经过清洗的环境变量文件，规避 BOM 与 CRLF 对 bash/systemd 的影响。
  set -a
  # shellcheck disable=SC1091
  source "${SANITIZED_ENV_FILE}"
  set +a
fi

exec 9>"${LOCK_FILE}"
if ! flock -n 9; then
  echo "$(date '+%Y-%m-%d %H:%M:%S') [run-dev-managed] 检测到上一次任务仍在运行，本轮跳过。"
  exit 0
fi

echo "$(date '+%Y-%m-%d %H:%M:%S') [run-dev-managed] 开始执行 run-dev.sh"

TMP_LOG="$(mktemp)"
RUN_STATUS="success"
EXIT_CODE=0

if bash ./scripts/run-dev.sh >"${TMP_LOG}" 2>&1; then
  RUN_STATUS="success"
else
  RUN_STATUS="failed"
  EXIT_CODE=$?
fi

cat "${TMP_LOG}"

PREVIOUS_FAILURE_COUNT=0
if [[ -f "${STATUS_FILE}" ]]; then
  PREVIOUS_FAILURE_COUNT="$(grep '^FAILURE_COUNT=' "${STATUS_FILE}" | tail -n 1 | cut -d'=' -f2 | tr -d '"' || true)"
  if [[ -z "${PREVIOUS_FAILURE_COUNT}" ]]; then
    PREVIOUS_FAILURE_COUNT=0
  fi
fi

TIMESTAMP="$(date '+%Y-%m-%d %H:%M:%S')"

if [[ "${RUN_STATUS}" = "success" ]]; then
  cp "${TMP_LOG}" "${LAST_SUCCESS_LOG}"
  cat > "${STATUS_FILE}" <<EOF
LAST_RUN_AT="${TIMESTAMP}"
LAST_RUN_STATUS=success
LAST_EXIT_CODE=0
FAILURE_COUNT=0
EOF
  echo "${TIMESTAMP} [run-dev-managed] run-dev.sh 执行成功。"
else
  CURRENT_FAILURE_COUNT=$((PREVIOUS_FAILURE_COUNT + 1))
  cp "${TMP_LOG}" "${LAST_FAILURE_LOG}"
  cat > "${STATUS_FILE}" <<EOF
LAST_RUN_AT="${TIMESTAMP}"
LAST_RUN_STATUS=failed
LAST_EXIT_CODE=${EXIT_CODE}
FAILURE_COUNT=${CURRENT_FAILURE_COUNT}
EOF
  echo "${TIMESTAMP} [run-dev-managed] run-dev.sh 执行失败，exit_code=${EXIT_CODE}，连续失败=${CURRENT_FAILURE_COUNT}。"
  if (( CURRENT_FAILURE_COUNT >= FAILURE_THRESHOLD )); then
    bash ./scripts/vm/notify-failure.sh "${CURRENT_FAILURE_COUNT}" "${EXIT_CODE}" "${LAST_FAILURE_LOG}" || true
  fi
fi

rm -f "${TMP_LOG}"
exit "${EXIT_CODE}"
