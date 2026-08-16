#!/usr/bin/env bash
# phase-07 final verification script
# Purpose: check Python, workflow, provider, review, publishing, exports, and tests.

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
  echo "Python was not found. Please prepare Python manually by following docs/install.md." >&2
  exit 1
fi

# 验证阶段使用项目内临时 dry-run 配置，避免误触真实飞书或真实视频服务。
mkdir -p data/temp
cat > data/temp/verify.env <<'EOF'
APP_ENV=dev
APP_NAME=lobster-farm
APP_TIMEZONE=Asia/Shanghai
RUN_MODE=dry-run
WORKSPACE_ROOT=./
DATA_DIR=./data
LOG_DIR=./logs
EXPORT_DIR=./exports
ASSET_DIR=./assets
FEISHU_ENABLED=true
FEISHU_ADAPTER=dry-run
FEISHU_API_BASE_URL=https://open.feishu.cn
FEISHU_APP_ID=
FEISHU_APP_SECRET=
FEISHU_BOT_NAME=lobster-bot
FEISHU_DEFAULT_CHAT_ID=
FEISHU_REQUEST_TIMEOUT_SECONDS=10
FEISHU_MAX_RETRIES=2
VIDEO_PROVIDER=mock
VIDEO_API_KEY=
VIDEO_PROVIDER_BASE_URL=
VIDEO_SUBMIT_PATH=/submit
VIDEO_STATUS_PATH=/status/{remote_task_id}
VIDEO_OUTPUT_DIR=./exports/pending_review
VIDEO_REQUEST_TIMEOUT_SECONDS=30
VIDEO_MAX_RETRIES=2
VIDEO_POLL_INTERVAL_SECONDS=1
VIDEO_MAX_POLL_ATTEMPTS=2
ORCHESTRATOR_STATE_FILE=./data/state/workflow_state.json
ORCHESTRATOR_QUEUE_DIR=./data/queue
ORCHESTRATOR_TASK_STATE_DIR=./data/state/tasks
ORCHESTRATOR_TASK_INDEX_FILE=./data/state/task_index.json
ORCHESTRATOR_MAX_RETRIES=1
LOG_LEVEL=INFO
EOF
export LOBSTER_ENV_FILE="data/temp/verify.env"

required_dirs=(
  "config"
  "docs"
  "src"
  "services/feishu-bridge/src"
  "services/video-gateway/src"
  "services/orchestrator/src"
  "exports/pending_review"
  "data/state"
)

for dir in "${required_dirs[@]}"; do
  if [[ ! -d "$dir" ]]; then
    echo "Missing required directory: $dir" >&2
    exit 1
  fi
done

"$PYTHON_BIN" ./services/orchestrator/src/main.py --topic "phase-07 final verify topic"

if [[ ! -f ./data/state/workflow_state.json ]]; then
  echo "data/state/workflow_state.json was not generated." >&2
  exit 1
fi

if [[ ! -f ./data/state/task_index.json ]]; then
  echo "data/state/task_index.json was not generated." >&2
  exit 1
fi

"$PYTHON_BIN" ./tests/smoke/smoke_feishu.py
"$PYTHON_BIN" ./tests/smoke/smoke_video_gateway.py
"$PYTHON_BIN" ./tests/smoke/smoke_workflow.py
"$PYTHON_BIN" ./tests/smoke/smoke_content_pipeline.py
"$PYTHON_BIN" ./tests/smoke/smoke_failure_branch.py
"$PYTHON_BIN" ./tests/smoke/smoke_feishu_real_config.py
"$PYTHON_BIN" ./tests/smoke/smoke_video_api_config.py
"$PYTHON_BIN" -m unittest ./services/feishu-bridge/tests/test_formatter.py
"$PYTHON_BIN" -m unittest ./services/feishu-bridge/tests/test_real_adapter.py
"$PYTHON_BIN" -m unittest ./services/video-gateway/tests/test_mock_provider.py
"$PYTHON_BIN" -m unittest ./services/video-gateway/tests/test_api_provider.py
"$PYTHON_BIN" -m unittest ./services/orchestrator/tests/test_workflow.py
"$PYTHON_BIN" -m unittest ./services/orchestrator/tests/test_review_workflow.py
"$PYTHON_BIN" -m unittest ./services/orchestrator/tests/test_publishing_workflow.py
"$PYTHON_BIN" -m unittest ./services/orchestrator/tests/test_demo.py
"$PYTHON_BIN" -m unittest ./services/orchestrator/tests/test_customer_demo_web.py
"$PYTHON_BIN" ./scripts/privacy-audit.py

echo "verify completed: workflow, provider, review, publishing, demo, customer web, privacy audit, task exports, and tests passed."
