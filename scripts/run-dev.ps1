# phase-07 final local runner
# Purpose: run the minimal workflow and generate review outputs.

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

& $pythonCommand.Source .\services\orchestrator\src\main.py --topic "lobster-farm phase-07 final demo topic"
