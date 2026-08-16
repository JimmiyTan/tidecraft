@echo off
REM lobster-farm Phase 07 one-click demo launcher.
REM This launcher always uses the safe dry-run/mock demo entry.

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
  set "DEMO_EXIT_CODE=1"
  goto :finish
)

echo ============================================================
echo lobster-farm Phase 07 one-click demo
echo Safe mode: dry-run / Feishu dry-run / Video mock
echo ============================================================
echo.

"%DEMO_PYTHON%" ".\services\orchestrator\src\demo.py"
set "DEMO_EXIT_CODE=%ERRORLEVEL%"

echo.
if "%DEMO_EXIT_CODE%"=="0" (
  echo [OK] Demo completed. Review the summary above.
) else (
  echo [ERROR] Demo failed with exit code %DEMO_EXIT_CODE%.
)

:finish
if /i not "%~1"=="--no-pause" pause
exit /b %DEMO_EXIT_CODE%
