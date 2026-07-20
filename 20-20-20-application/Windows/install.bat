@echo off
setlocal EnableExtensions

title Eye Guard Setup

echo ========================================
echo         Eye Guard - Setup
echo ========================================
echo.

set "PYTHON_CMD="

:: ------------------------------------------------------------
:: Check for an existing Python installation
:: ------------------------------------------------------------

py -3.11 --version >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_CMD=py -3.11"
    goto :python_found
)

python --version >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_CMD=python"
    goto :python_found
)

py --version >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_CMD=py"
    goto :python_found
)

:: ------------------------------------------------------------
:: Python is missing — attempt automatic installation
:: ------------------------------------------------------------

echo Python was not found.
echo Attempting to install Python 3.11 automatically...
echo.

winget --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Windows Package Manager ^(winget^) is not available.
    echo.
    echo Python could not be installed automatically.
    echo Please install Python 3.11 or later and run this file again.
    echo.
    pause
    exit /b 1
)

winget install ^
    --id Python.Python.3.11 ^
    --exact ^
    --silent ^
    --accept-package-agreements ^
    --accept-source-agreements

if errorlevel 1 (
    echo.
    echo [ERROR] Python installation failed or was blocked.
    echo Your organisation may restrict software installation.
    echo.
    pause
    exit /b 1
)

echo.
echo Python installation completed.
echo Detecting the new installation...
echo.

:: Check standard installation locations because the current
:: Command Prompt may not receive the updated PATH immediately.

if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
    set "PYTHON_CMD="%LOCALAPPDATA%\Programs\Python\Python311\python.exe""
    goto :python_found
)

if exist "%ProgramFiles%\Python311\python.exe" (
    set "PYTHON_CMD="%ProgramFiles%\Python311\python.exe""
    goto :python_found
)

if exist "%ProgramFiles(x86)%\Python311\python.exe" (
    set "PYTHON_CMD="%ProgramFiles(x86)%\Python311\python.exe""
    goto :python_found
)

py -3.11 --version >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_CMD=py -3.11"
    goto :python_found
)

python --version >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_CMD=python"
    goto :python_found
)

echo [ERROR] Python was installed but could not be located.
echo Restart Windows, then run install.bat again.
echo.
pause
exit /b 1

:: ------------------------------------------------------------
:: Install Eye Guard dependencies
:: ------------------------------------------------------------

:python_found

echo Python detected:
%PYTHON_CMD% --version
echo.

echo Preparing pip...
%PYTHON_CMD% -m ensurepip --upgrade >nul 2>&1

echo Updating pip...
%PYTHON_CMD% -m pip install --upgrade pip

if errorlevel 1 (
    echo.
    echo [ERROR] pip could not be updated.
    pause
    exit /b 1
)

echo.
echo Installing Eye Guard dependencies...
%PYTHON_CMD% -m pip install --upgrade pywin32 pystray pillow

if errorlevel 1 (
    echo.
    echo [ERROR] Dependencies could not be installed.
    echo Check your internet connection or organisation restrictions.
    echo.
    pause
    exit /b 1
)

:: ------------------------------------------------------------
:: Verify installation
:: ------------------------------------------------------------

echo.
echo Verifying dependencies...

%PYTHON_CMD% -c "import win32api, pystray, PIL" >nul 2>&1

if errorlevel 1 (
    echo.
    echo [ERROR] Dependency verification failed.
    echo Please run install.bat again.
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo          Setup complete
echo ========================================
echo.
echo Python and all required packages are ready.
echo.
echo Double-click eye_guard_2020.pyw
echo to launch Eye Guard.
echo.
pause

endlocal
exit /b 0
