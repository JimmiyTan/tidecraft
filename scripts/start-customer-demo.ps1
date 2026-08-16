# phase-07 客户前端演示启动脚本
# 作用：仅在 127.0.0.1 启动本地客户演示页面，可选自动打开浏览器。

param(
  [int]$Port = 8765,
  [switch]$NoOpen
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

$customerDemoArgs = @(
  ".\services\orchestrator\src\customer_demo_server.py",
  "--port",
  $Port
)
if (-not $NoOpen) {
  $customerDemoArgs += "--open"
}

& $pythonCommand.Source @customerDemoArgs
exit $LASTEXITCODE
