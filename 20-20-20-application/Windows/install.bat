@echo off
setlocal
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0install.ps1"
set "RC=%ERRORLEVEL%"
if not "%RC%"=="0" echo EyeGuard setup failed with code %RC%.
pause
exit /b %RC%
