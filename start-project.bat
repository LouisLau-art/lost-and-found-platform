@echo off

:: Startup Script - Lost and Found Platform
:: Provides options to start different services

:menu
cls
echo =======================================
echo      Lost and Found Platform
echo         Startup Tool
echo =======================================
echo 1. Start Full Platform (Frontend + Backend)
echo 2. Start Backend Only
echo 3. Start Frontend Only
echo 4. Check Environment
echo 0. Exit
echo =======================================

set /p choice="Please select an option (0-4): "

if "%choice%"=="0" goto exit
if "%choice%"=="1" goto start_all
if "%choice%"=="2" goto start_backend
if "%choice%"=="3" goto start_frontend
if "%choice%"=="4" goto check_environment

echo Invalid choice, please try again.
pause
goto menu

:check_environment
echo Checking runtime environment...
echo.

:: Check Python environment
echo Checking Python...
python --version >nul 2>nul
if %errorlevel% neq 0 (
    echo Error: Python not found. Please install Python first.
) else (
    for /f "tokens=2" %%i in ('python --version') do set python_version=%%i
    echo Python version: %python_version%
)

echo.
:: Check Node.js environment
echo Checking Node.js...
npm --version >nul 2>nul
if %errorlevel% neq 0 (
    echo Error: Node.js not found. Please install Node.js and npm.
) else (
    for /f %%i in ('npm --version') do set npm_version=%%i
    echo npm version: %npm_version%
)

echo.
:: Check backend environment
echo Checking backend environment...
if exist "backend\venv" (
    echo Python virtual environment exists
) else (
    echo Warning: Backend virtual environment does not exist. You may need to initialize the project first.
)

echo.
:: Check frontend dependencies
echo Checking frontend environment...
if exist "frontend\frontend\node_modules" (
    echo Frontend dependencies are installed
) else (
    echo Warning: Frontend dependencies not installed. They will be installed automatically on first run.
)

echo.
echo Environment check completed.
pause
goto menu

:start_all
echo Starting full platform...

:: Start backend service
start "Backend Service" cmd /k "cd backend && if exist venv\Scripts\activate.bat (call venv\Scripts\activate.bat && python start.py) else (echo Error: Virtual environment does not exist, creating... && python -m venv venv && call venv\Scripts\activate.bat && pip install -r requirements.txt && python start.py)"

:: Wait for backend to start
echo Waiting for backend service to initialize...
timeout /t 5 /nobreak > nul

:: Start frontend service
start "Frontend Service" cmd /k "cd frontend\frontend && if exist node_modules (npm run dev) else (echo Error: Dependencies not installed, installing... && npm install && npm run dev)"

echo.
echo Service startup information:
echo ---------------------------------------
echo Backend service is starting, please wait...
echo Backend address: http://localhost:8000
echo Frontend service is starting, please wait...
echo Frontend address: http://localhost:5173
echo ---------------------------------------
echo Tip: Please wait for services to fully start before accessing

echo.
echo Opening browser...
pause
goto menu

:start_backend
echo Starting backend service...
start "Backend Service" cmd /k "cd backend && if exist venv\Scripts\activate.bat (call venv\Scripts\activate.bat && python start.py) else (echo Error: Virtual environment does not exist, creating... && python -m venv venv && call venv\Scripts\activate.bat && pip install -r requirements.txt && python start.py)"

echo.
echo Backend service is starting, please wait...
echo Backend address: http://localhost:8000
echo Tip: Please wait for service to fully start before accessing

pause
goto menu

:start_frontend
echo Starting frontend service...
start "Frontend Service" cmd /k "cd frontend\frontend && if exist node_modules (npm run dev) else (echo Error: Dependencies not installed, installing... && npm install && npm run dev)"

echo.
echo Frontend service is starting, please wait...
echo Frontend address: http://localhost:5173
echo Tip: Please wait for service to fully start before accessing

pause
goto menu

:exit
echo Thank you for using the Lost and Found Platform startup tool, goodbye!
