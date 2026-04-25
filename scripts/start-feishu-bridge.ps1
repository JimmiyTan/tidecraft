# Feishu Bridge runner
# Purpose: generate a dry-run review message.

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

& $pythonCommand.Source .\services\feishu-bridge\src\main.py --topic "feishu bridge demo topic"
