@echo off
echo ========================================
echo   20-20-20 Eye Guard - Remove Startup
echo ========================================
echo.

set "SHORTCUT=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\EyeGuard.bat"

if not exist "%SHORTCUT%" (
    echo Eye Guard is not set to run on startup.
    pause
    exit /b 0
)

set /p confirm="Remove Eye Guard from startup? (y/n): "
if /i not "%confirm%"=="y" (
    echo Cancelled.
    pause
    exit /b 0
)

del "%SHORTCUT%"

echo.
echo Done! Eye Guard will no longer start automatically.
echo.
pause
