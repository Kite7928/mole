@echo off
cd /d "%~dp0"

echo ==========================================
echo    AI Assistant - Startup Script
echo ==========================================
echo.

echo [1/6] Check directory...
if not exist "backend\app\main.py" (
    echo [ERROR] Backend file not found
    pause
    exit /b 1
)
if not exist "frontend\package.json" (
    echo [ERROR] Frontend file not found
    pause
    exit /b 1
)
echo [OK] Directory check passed
echo.

echo [2/6] Check Python...
py --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found
    pause
    exit /b 1
)
py --version
echo.

echo [3/6] Check Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js not found
    pause
    exit /b 1
)
node --version
echo.

echo [4/6] Check ports...
netstat -ano | findstr ":8000" | findstr "LISTENING" >nul
if %errorlevel% == 0 (
    echo [WARNING] Port 8000 is busy, releasing...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000" ^| findstr "LISTENING"') do (
        taskkill /F /PID %%a >nul 2>&1
    )
    timeout /t 2 /nobreak >nul
)
echo [OK] Port 8000 available

netstat -ano | findstr ":3000" | findstr "LISTENING" >nul
if %errorlevel% == 0 (
    echo [WARNING] Port 3000 is busy, releasing...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":3000" ^| findstr "LISTENING"') do (
        taskkill /F /PID %%a >nul 2>&1
    )
    timeout /t 2 /nobreak >nul
)
echo [OK] Port 3000 available
echo.

echo [5/6] Starting services...
echo.

echo [Backend] Starting backend service (port 8000)...
cd backend
start "Backend-8000" cmd /k "cd /d %CD% && echo [Backend] Working directory: %CD% && py -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
cd ..
echo [OK] Backend started
echo.

timeout /t 5 /nobreak >nul

echo [Frontend] Starting frontend service (port 3000)...
cd frontend
start "Frontend-3000" cmd /k "cd /d %CD% && echo [Frontend] Working directory: %CD% && npm run dev"
cd ..
echo [OK] Frontend started
echo.

echo [6/6] Done!
echo.
echo ==========================================
echo    Services Started Successfully
echo ==========================================
echo.
echo Please check new windows:
echo   - Window 1: Backend service (wait for Ready)
echo   - Window 2: Frontend service (wait for Compiled)
echo.
echo Access URLs:
echo   - Frontend: http://localhost:3000
echo   - Backend API: http://localhost:8000
echo   - API Docs: http://localhost:8000/docs
echo.
echo Press any key to close all services...
pause >nul

echo.
echo Closing services...
taskkill /FI "WINDOWTITLE eq Backend-8000*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Frontend-3000*" /F >nul 2>&1
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM node.exe >nul 2>&1

echo [OK] All services closed
timeout /t 2 /nobreak >nul