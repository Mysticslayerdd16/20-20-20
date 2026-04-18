@echo off
echo ========================================
echo   20-20-20 Eye Guard - Startup Setup
echo ========================================
echo.
echo This will make Eye Guard launch automatically
echo every time you log into Windows.
echo.
set /p confirm="Continue? (y/n): "
if /i not "%confirm%"=="y" (
    echo Cancelled.
    pause
    exit /b 0
)

:: Get the directory this script is running from
set "APP_DIR=%~dp0"
set "APP_FILE=%APP_DIR%eye_guard_2020.pyw"
set "STARTUP_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "SHORTCUT=%STARTUP_DIR%\EyeGuard.bat"

:: Check the .pyw file exists
if not exist "%APP_FILE%" (
    echo [ERROR] eye_guard_2020.pyw not found in the same folder as this script.
    echo Please make sure both files are in the same directory.
    pause
    exit /b 1
)

:: Write a small launcher into the startup folder
echo @echo off > "%SHORTCUT%"
echo start "" pythonw "%APP_FILE%" >> "%SHORTCUT%"

if errorlevel 1 (
    echo [ERROR] Could not write to startup folder.
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Done! Eye Guard will now start
echo   automatically when you log in.
echo.
echo   To remove it from startup, run:
echo   remove_startup.bat
echo ========================================
echo.
pause
