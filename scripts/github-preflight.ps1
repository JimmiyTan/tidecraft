# GitHub 上传前总检查
# 执行隐私审计、项目验证、差异检查和忽略规则确认；不暂存、不提交、不推送。

$pythonCommand = Get-Command ".\.venv\Scripts\python.exe" -ErrorAction SilentlyContinue
if (-not $pythonCommand) {
  $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
}
if (-not $pythonCommand) {
  $pythonCommand = Get-Command py -ErrorAction SilentlyContinue
}
if (-not $pythonCommand) {
  Write-Error "未找到 Python。"
  exit 1
}

Write-Output "检查 1/4：隐私与密钥审计"
& $pythonCommand.Source ".\scripts\privacy-audit.py"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Output "检查 2/4：完整项目验证"
$verifySource = [System.IO.File]::ReadAllText(
  (Resolve-Path ".\scripts\verify.ps1"),
  [System.Text.Encoding]::UTF8
)
& ([ScriptBlock]::Create($verifySource))
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Output "检查 3/4：Git 差异格式"
git diff --check
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Output "检查 4/4：敏感与运行目录忽略状态"
$ignoreProbes = @(".env", "data/.audit-probe", "exports/.audit-probe", "logs/.audit-probe")
foreach ($probe in $ignoreProbes) {
  git check-ignore --quiet --no-index -- $probe
  if ($LASTEXITCODE -ne 0) {
    Write-Error "忽略规则未覆盖：$probe"
    exit 1
  }
}

Write-Output "GitHub 上传前总检查通过。"
Write-Output "注意：本脚本不会执行 git add、commit 或 push。"
git status --short --branch
