# 第一阶段引导脚本
# 作用：检查关键目录是否存在，不做联网安装。

$requiredDirs = @(
  "config",
  "docs",
  "apps/openclaw",
  "workers/hermes",
  "services/feishu-bridge",
  "services/video-gateway",
  "services/orchestrator",
  "tests/smoke"
)

foreach ($dir in $requiredDirs) {
  if (-not (Test-Path -LiteralPath $dir)) {
    Write-Error "缺少目录：$dir"
    exit 1
  }
}

Write-Output "bootstrap 完成：目录骨架已存在。"
