@echo off
setlocal
if not exist "%~dp0.venv\Scripts\pythonw.exe" (echo Run install.bat first. & pause & exit /b 1)
set /p confirm="Start EyeGuard at login? [y/N]: "
if /i not "%confirm%"=="y" exit /b 0
set "TARGET=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\EyeGuard.bat"
> "%TARGET%" echo @echo off
>> "%TARGET%" echo start "" "%~dp0.venv\Scripts\pythonw.exe" "%~dp0eye_guard_2020.pyw"
echo Startup enabled.
pause
