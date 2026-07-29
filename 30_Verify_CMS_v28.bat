@echo off
setlocal EnableExtensions
title Verify Aastha CMS v28
cd /d "%~dp0"

set "PYTHON_LAUNCHER="
where py >nul 2>nul
if not errorlevel 1 set "PYTHON_LAUNCHER=py -3"
if not defined PYTHON_LAUNCHER (
  where python >nul 2>nul
  if not errorlevel 1 set "PYTHON_LAUNCHER=python"
)
if not defined PYTHON_LAUNCHER (
  echo.
  echo ERROR: Python 3 was not found.
  echo Install a current stable Python 3.12 or 3.13 and enable Add Python to PATH.
  goto FAIL
)

if not exist ".cms-venv\Scripts\python.exe" (
  echo Creating an isolated CMS verification environment...
  %PYTHON_LAUNCHER% -m venv .cms-venv || goto FAIL
)

".cms-venv\Scripts\python.exe" -c "import sys" >nul 2>nul
if errorlevel 1 (
  echo.
  echo ERROR: .cms-venv is broken. Rename or remove only that folder, then retry.
  goto FAIL
)

echo Installing the pinned CMS dependencies...
".cms-venv\Scripts\python.exe" -m pip install -r requirements.txt || goto FAIL

set "VERIFY_DB=%CD%\cms_verify.sqlite3"
if exist "%VERIFY_DB%" del /q "%VERIFY_DB%"
set "DATABASE_URL=sqlite:///cms_verify.sqlite3"
set "DJANGO_SETTINGS_MODULE=aastha_cms.settings.dev"

echo.
echo Building and checking a clean temporary CMS...
".cms-venv\Scripts\python.exe" manage.py migrate --noinput || goto FAIL
".cms-venv\Scripts\python.exe" manage.py initialize_cms || goto FAIL
".cms-venv\Scripts\python.exe" manage.py makemigrations --check --dry-run || goto FAIL
".cms-venv\Scripts\python.exe" manage.py check || goto FAIL
".cms-venv\Scripts\python.exe" manage.py qa_cms_release || goto FAIL
".cms-venv\Scripts\python.exe" manage.py test || goto FAIL

if exist "%VERIFY_DB%" del /q "%VERIFY_DB%"
echo.
echo SUCCESS: Aastha CMS v28 passed import, public-site, admin, link, token and test checks.
echo Run 31_Preview_CMS_v28.bat to preview it.
pause
exit /b 0

:FAIL
echo.
echo ERROR: CMS verification stopped. Do not deploy until the reported issue is fixed.
pause
exit /b 1
