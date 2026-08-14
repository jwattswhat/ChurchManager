@echo off
cd /d C:\Users\Pastor\Documents\ChurchManager
if not exist ".runtime-venv\Scripts\python.exe" goto runtime_missing
".runtime-venv\Scripts\python.exe" -c "import wx, mariadb, JSForm; from development_boundary import assert_development_isolation; assert_development_isolation(JSForm)" >nul 2>&1
if errorlevel 1 goto runtime_missing
".runtime-venv\Scripts\python.exe" cm.py --server 127.0.0.1 --user church --test
exit /b %errorlevel%

:runtime_missing
echo ChurchManager's Python runtime is missing or incomplete.
echo Repair .runtime-venv and verify the independent development JSForm before starting ChurchManager TEST MODE.
pause
exit /b 1
