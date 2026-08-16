@echo off
REM Run the complete lobster-farm verification suite.

setlocal
chcp 65001 >nul
cd /d "%~dp0"

echo Running complete project verification...
where pwsh.exe >nul 2>nul
if not errorlevel 1 (
  pwsh.exe -NoProfile -File ".\scripts\verify.ps1"
) else (
  powershell.exe -NoProfile -Command "[Console]::OutputEncoding=[Text.UTF8Encoding]::new(); $OutputEncoding=[Console]::OutputEncoding; $s=[IO.File]::ReadAllText((Resolve-Path '.\scripts\verify.ps1'),[Text.Encoding]::UTF8); & ([ScriptBlock]::Create($s))"
)
set "VERIFY_EXIT_CODE=%ERRORLEVEL%"

echo.
if "%VERIFY_EXIT_CODE%"=="0" (
  echo [OK] Complete verification passed.
) else (
  echo [ERROR] Verification failed. Review the message above.
)

if /i not "%~1"=="--no-pause" pause
exit /b %VERIFY_EXIT_CODE%
