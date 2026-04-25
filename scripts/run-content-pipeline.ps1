# content pipeline runner
# Purpose: run trend radar, viral analysis, original rewrite, distribution package, and Feishu review.

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

$topic = "AI$([char]0x5206)$([char]0x8EAB)$([char]0x5185)$([char]0x5BB9)$([char]0x589E)$([char]0x957F)"
& $pythonCommand.Source .\src\lobster_farm\content_pipeline\app.py --topic $topic
