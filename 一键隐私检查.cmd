@echo off
REM Scan GitHub upload candidates and Git history without printing secret values.

setlocal
chcp 65001 >nul
set "PYTHONUTF8=1"
cd /d "%~dp0"

set "AUDIT_PYTHON="
if exist ".venv\Scripts\python.exe" set "AUDIT_PYTHON=.venv\Scripts\python.exe"
if not defined AUDIT_PYTHON (
  where python >nul 2>nul
  if not errorlevel 1 set "AUDIT_PYTHON=python"
)
if not defined AUDIT_PYTHON (
  where py >nul 2>nul
  if not errorlevel 1 set "AUDIT_PYTHON=py"
)
if not defined AUDIT_PYTHON (
  echo [ERROR] Python was not found.
  if /i not "%~1"=="--no-pause" pause
  exit /b 1
)

"%AUDIT_PYTHON%" ".\scripts\privacy-audit.py"
set "AUDIT_EXIT_CODE=%ERRORLEVEL%"

echo.
if "%AUDIT_EXIT_CODE%"=="0" (
  echo [OK] Privacy audit completed without blocking findings.
) else (
  echo [ERROR] Privacy audit found a blocking issue.
)

if /i not "%~1"=="--no-pause" pause
exit /b %AUDIT_EXIT_CODE%
