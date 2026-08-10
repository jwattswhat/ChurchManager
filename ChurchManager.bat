@echo off
setlocal
set "LEGACY_LAUNCHER=C:\Users\Pastor\Documents\ChurchManager-Legacy\ChurchManager\ChurchManager-Legacy.bat"
if not exist "%LEGACY_LAUNCHER%" goto legacy_missing
call "%LEGACY_LAUNCHER%"
exit /b %errorlevel%

:legacy_missing
echo The frozen ChurchManager Legacy installation was not found.
echo Expected: %LEGACY_LAUNCHER%
echo Production ChurchDB will not be opened from the development workspace.
pause
exit /b 1
