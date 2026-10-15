@echo off
where py >nul 2>nul
if %errorlevel% equ 0 (py -3 -B "%~dp0desk.py" %*) else (python -B "%~dp0desk.py" %*)
if errorlevel 1 pause
