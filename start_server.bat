@echo off
title AlHafiz Islamic Quran Academy - Live Server
echo ===================================================================
echo     AlHafiz Islamic Quran Academy - Online & Home Quran Portal
echo ===================================================================
echo.
echo [1/2] Opening Web Application in your Default Browser...
start "" "http://localhost:5000"
timeout /t 2 >nul

echo [2/2] Starting High-Performance Web Server on port 5000...
echo.
where python >nul 2>nul
if %errorlevel% equ 0 (
    echo Python detected. Launching Flask/Python Server...
    python "%~dp0app.py"
) else (
    echo Launching Native Windows PowerShell Web Server...
    powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0server.ps1"
)
pause
