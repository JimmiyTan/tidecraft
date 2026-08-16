# phase-07 一键功能演示脚本
# 作用：使用固定 dry-run/mock 配置演示完整人工审核与发布回执闭环。

param(
  [string]$Topic = "AI 如何帮助本地商家提升短视频内容效率",
  [string]$Operator = "demo-operator",
  [switch]$Guided
)

$pythonCommand = Get-Command ".\.venv\Scripts\python.exe" -ErrorAction SilentlyContinue
if (-not $pythonCommand) {
  $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
}
if (-not $pythonCommand) {
  $pythonCommand = Get-Command py -ErrorAction SilentlyContinue
}
if (-not $pythonCommand) {
  Write-Error "未找到 Python。请先参考 docs/install.md 准备 Python 环境。"
  exit 1
}

$demoArgs = @(
  ".\services\orchestrator\src\demo.py",
  "--topic",
  $Topic,
  "--operator",
  $Operator
)
if ($Guided) {
  $demoArgs += "--guided"
}

& $pythonCommand.Source @demoArgs
exit $LASTEXITCODE
