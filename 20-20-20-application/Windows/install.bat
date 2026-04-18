@echo off
echo ========================================
echo   20-20-20 Eye Guard - Installer
echo ========================================
echo.

:: Check Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found.
    echo Please install Python from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during install.
    echo.
    pause
    exit /b 1
)

echo [OK] Python found.
echo.
echo Installing dependencies...
echo.

pip install pywin32 pystray Pillow

if errorlevel 1 (
    echo.
    echo [ERROR] Installation failed. Try running this script as Administrator.
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Installation complete!
echo   Double-click eye_guard_2020.pyw to run.
echo ========================================
echo.
pause
