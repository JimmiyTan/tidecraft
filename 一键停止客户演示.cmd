@echo off
REM Stop only the lobster-farm customer demo process listening on port 8765.

setlocal
chcp 65001 >nul
cd /d "%~dp0"

echo Stopping lobster-farm customer demo...
where pwsh.exe >nul 2>nul
if not errorlevel 1 (
  pwsh.exe -NoProfile -File ".\scripts\stop-customer-demo.ps1" -Port 8765
) else (
  powershell.exe -NoProfile -Command "$s=[IO.File]::ReadAllText((Resolve-Path '.\scripts\stop-customer-demo.ps1'),[Text.Encoding]::UTF8); & ([ScriptBlock]::Create($s)) -Port 8765"
)
set "DEMO_EXIT_CODE=%ERRORLEVEL%"

echo.
if "%DEMO_EXIT_CODE%"=="0" (
  echo [OK] Customer demo stop check completed.
) else (
  echo [ERROR] Customer demo was not stopped. Review the message above.
)

if /i not "%~1"=="--no-pause" pause
exit /b %DEMO_EXIT_CODE%
