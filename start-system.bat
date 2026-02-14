@echo off
REM Startup script for NOVO-1 Drug Discovery System
REM This script starts both the Python API and Node.js backend

echo ============================================
echo NOVO-1 Drug Discovery System - Startup
echo ============================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    exit /b 1
)

REM Check if Node.js is available
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is not installed or not in PATH
    exit /b 1
)

echo [OK] Python and Node.js detected
echo.

REM Start Python API in new window
echo [1] Starting Python API (Port 5001)...
start "NOVO-1 Python API" cmd /k "cd /d %~dp0 && python api/novo1_api.py"

REM Wait for Python API to initialize
timeout /t 5 /nobreak >nul

REM Start Node.js backend in new window
echo [2] Starting Node.js Backend (Port 5000)...
start "NOVO-1 Node Backend" cmd /k "cd /d %~dp0\backend && npm run dev"

REM Wait for backend to start
timeout /t 3 /nobreak >nul

echo.
echo ============================================
echo All services started!
echo ============================================
echo.
echo API Endpoints:
echo   Python API: http://localhost:5001
echo   Node Backend: http://localhost:5000
echo   Frontend: http://localhost:5173
echo.
echo Test the integration:
echo   curl http://localhost:5000/api/drug-discovery/health
echo.
pause
