@echo off
setlocal EnableExtensions
title Preview Aastha CMS v28
cd /d "%~dp0"

if not exist ".cms-venv\Scripts\python.exe" (
  echo Run 30_Verify_CMS_v28.bat first.
  pause
  exit /b 1
)

set "DJANGO_SETTINGS_MODULE=aastha_cms.settings.dev"
".cms-venv\Scripts\python.exe" manage.py migrate --noinput || goto FAIL
".cms-venv\Scripts\python.exe" manage.py initialize_cms || goto FAIL

start "" http://localhost:8000
echo.
echo Public preview: http://localhost:8000
echo Admin login:   http://localhost:8000/admin/
echo Press Ctrl+C to stop the preview.
".cms-venv\Scripts\python.exe" manage.py runserver 127.0.0.1:8000
exit /b 0

:FAIL
echo Preview setup failed. Run 30_Verify_CMS_v28.bat and review the error.
pause
exit /b 1
