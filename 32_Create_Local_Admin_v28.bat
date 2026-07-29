@echo off
setlocal EnableExtensions
title Create local Aastha CMS administrator
cd /d "%~dp0"

if not exist ".cms-venv\Scripts\python.exe" (
  echo Run 30_Verify_CMS_v28.bat first.
  pause
  exit /b 1
)

set "DJANGO_SETTINGS_MODULE=aastha_cms.settings.dev"
".cms-venv\Scripts\python.exe" manage.py migrate --noinput || goto FAIL
".cms-venv\Scripts\python.exe" manage.py initialize_cms || goto FAIL
echo.
echo Choose a private username, email address and strong password.
".cms-venv\Scripts\python.exe" manage.py createsuperuser
if errorlevel 1 goto FAIL

echo.
echo Administrator ready. Open http://localhost:8000/admin/ while preview is running.
pause
exit /b 0

:FAIL
echo Administrator setup failed. Review the error above.
pause
exit /b 1
