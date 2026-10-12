@echo off
where py >nul 2>nul
if %errorlevel% equ 0 (py -3 "%~dp0desk.py") else (python "%~dp0desk.py")
if errorlevel 1 pause
