@echo off
REM Open the local Chinese user manual with the default Markdown application.

setlocal
cd /d "%~dp0"

if not exist ".\使用说明书.md" (
  echo [ERROR] User manual was not found.
  if /i not "%~1"=="--no-pause" pause
  exit /b 1
)

start "" ".\使用说明书.md"
exit /b 0
