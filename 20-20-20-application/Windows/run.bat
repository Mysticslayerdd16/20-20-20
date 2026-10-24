@echo off
set "PY=%~dp0.venv\Scripts\pythonw.exe"
if not exist "%PY%" (echo Run install.bat first. & pause & exit /b 1)
start "" "%PY%" "%~dp0eye_guard_2020.pyw"
