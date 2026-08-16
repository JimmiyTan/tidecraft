@echo off
REM lobster-farm customer demo one-click launcher.
REM Starts a localhost-only server and opens the customer presentation page.

setlocal
chcp 65001 >nul
set "PYTHONUTF8=1"
cd /d "%~dp0"

set "DEMO_PYTHON="
if exist ".venv\Scripts\python.exe" set "DEMO_PYTHON=.venv\Scripts\python.exe"

if not defined DEMO_PYTHON (
  where python >nul 2>nul
  if not errorlevel 1 set "DEMO_PYTHON=python"
)

if not defined DEMO_PYTHON (
  where py >nul 2>nul
  if not errorlevel 1 set "DEMO_PYTHON=py"
)

if not defined DEMO_PYTHON (
  echo [ERROR] Python was not found. See docs\install.md.
  pause
  exit /b 1
)

echo ============================================================
echo lobster-farm customer presentation
echo Local URL: http://127.0.0.1:8765
echo Press Ctrl+C to stop the demo server.
echo ============================================================
echo.

set "DEMO_OPEN=--open"
set "DEMO_PAUSE=1"
if /i "%~1"=="--no-open" set "DEMO_OPEN="
if /i "%~1"=="--no-pause" set "DEMO_PAUSE=0"
if /i "%~2"=="--no-pause" set "DEMO_PAUSE=0"

"%DEMO_PYTHON%" ".\services\orchestrator\src\customer_demo_server.py" --port 8765 %DEMO_OPEN%
set "DEMO_EXIT_CODE=%ERRORLEVEL%"

echo.
echo Customer demo server stopped with exit code %DEMO_EXIT_CODE%.
if "%DEMO_PAUSE%"=="1" pause
exit /b %DEMO_EXIT_CODE%
