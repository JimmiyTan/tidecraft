@echo off
REM Run every local GitHub preflight check. This does not add, commit, or push.

setlocal
chcp 65001 >nul
set "PYTHONUTF8=1"
cd /d "%~dp0"

echo Running GitHub upload preflight checks...
where pwsh.exe >nul 2>nul
if not errorlevel 1 (
  pwsh.exe -NoProfile -File ".\scripts\github-preflight.ps1"
) else (
  powershell.exe -NoProfile -Command "[Console]::OutputEncoding=[Text.UTF8Encoding]::new(); $OutputEncoding=[Console]::OutputEncoding; $s=[IO.File]::ReadAllText((Resolve-Path '.\scripts\github-preflight.ps1'),[Text.Encoding]::UTF8); & ([ScriptBlock]::Create($s))"
)
set "PREFLIGHT_EXIT_CODE=%ERRORLEVEL%"

echo.
if "%PREFLIGHT_EXIT_CODE%"=="0" (
  echo [OK] Local GitHub upload preflight passed.
  echo No files were staged, committed, or pushed.
) else (
  echo [ERROR] Upload preflight failed. Review the message above.
)

if /i not "%~1"=="--no-pause" pause
exit /b %PREFLIGHT_EXIT_CODE%
