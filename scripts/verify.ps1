# phase-04 verify script
# Purpose: check Python, workflow, content pipeline, provider files, and tests.

$pythonCommand = Get-Command ".\.venv\Scripts\python.exe" -ErrorAction SilentlyContinue
if (-not $pythonCommand) {
  $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
}
if (-not $pythonCommand) {
  $pythonCommand = Get-Command py -ErrorAction SilentlyContinue
}
if (-not $pythonCommand) {
  Write-Error "Python was not found. Please prepare Python manually by following docs/install.md."
  exit 1
}

function Invoke-VerifyStep {
  param(
    [string]$Name,
    [string[]]$CommandArgs
  )
  Write-Output "verify step: $Name"
  & $pythonCommand.Source @CommandArgs
  if ($LASTEXITCODE -ne 0) {
    Write-Error "Command failed: $($CommandArgs -join ' ')"
    exit 1
  }
}

# 验证阶段使用项目内临时 dry-run 配置，避免误触真实飞书或真实视频服务。
New-Item -ItemType Directory -Force -Path "data/temp" | Out-Null
@"
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
"@ | Set-Content -LiteralPath "data/temp/verify.env" -Encoding UTF8
$env:LOBSTER_ENV_FILE = "data/temp/verify.env"

$requiredDirs = @(
  "config",
  "docs",
  "src",
  "services/feishu-bridge/src",
  "services/video-gateway/src",
  "services/orchestrator/src",
  "exports/pending_review",
  "data/state"
)

foreach ($dir in $requiredDirs) {
  if (-not (Test-Path -LiteralPath $dir)) {
    Write-Error "Missing required directory: $dir"
    exit 1
  }
}

Invoke-VerifyStep "orchestrator minimal workflow" @(".\services\orchestrator\src\main.py", "--topic", "phase-04 verify topic")

if (-not (Test-Path -LiteralPath ".\data\state\workflow_state.json")) {
  Write-Error "data/state/workflow_state.json was not generated."
  exit 1
}

if (-not (Test-Path -LiteralPath ".\data\state\task_index.json")) {
  Write-Error "data/state/task_index.json was not generated."
  exit 1
}

$state = Get-Content -LiteralPath ".\data\state\workflow_state.json" -Raw -Encoding UTF8 | ConvertFrom-Json
if ($state.status -ne "completed") {
  Write-Error "latest workflow status is not completed."
  exit 1
}

$taskDir = $state.task_dir
foreach ($fileName in @("topic_list.json", "scripts.json", "review_message.json", "video_result.json", "summary.txt", "provider_request.json", "provider_response.json")) {
  $filePath = Join-Path $taskDir $fileName
  if (-not (Test-Path -LiteralPath $filePath)) {
    Write-Error "Missing task export file: $filePath"
    exit 1
  }
}

Invoke-VerifyStep "smoke feishu dry-run" @(".\tests\smoke\smoke_feishu.py")
Invoke-VerifyStep "smoke video gateway mock" @(".\tests\smoke\smoke_video_gateway.py")
Invoke-VerifyStep "smoke workflow" @(".\tests\smoke\smoke_workflow.py")
Invoke-VerifyStep "smoke content pipeline" @(".\tests\smoke\smoke_content_pipeline.py")
Invoke-VerifyStep "smoke failure branch" @(".\tests\smoke\smoke_failure_branch.py")
Invoke-VerifyStep "smoke feishu real config" @(".\tests\smoke\smoke_feishu_real_config.py")
Invoke-VerifyStep "smoke video api config" @(".\tests\smoke\smoke_video_api_config.py")
Invoke-VerifyStep "unittest feishu formatter" @("-m", "unittest", ".\services\feishu-bridge\tests\test_formatter.py")
Invoke-VerifyStep "unittest feishu real adapter" @("-m", "unittest", ".\services\feishu-bridge\tests\test_real_adapter.py")
Invoke-VerifyStep "unittest video mock provider" @("-m", "unittest", ".\services\video-gateway\tests\test_mock_provider.py")
Invoke-VerifyStep "unittest video api provider" @("-m", "unittest", ".\services\video-gateway\tests\test_api_provider.py")
Invoke-VerifyStep "unittest orchestrator workflow" @("-m", "unittest", ".\services\orchestrator\tests\test_workflow.py")

Write-Output "verify completed: content pipeline, workflow, provider tests, task exports, and tests passed."
