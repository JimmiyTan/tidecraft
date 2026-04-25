# Video Gateway runner
# Purpose: generate a mock pending-review output file.

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

& $pythonCommand.Source .\services\video-gateway\src\main.py --topic "video gateway demo topic" --review-items-json "[{""title"":""demo title"",""script_text"":""demo script""}]"
