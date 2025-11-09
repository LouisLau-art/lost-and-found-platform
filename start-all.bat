@echo off
echo Starting Lost ^& Found Platform...
echo.
echo Starting Backend...
start "Backend" cmd /k "cd backend && call venv\Scripts\activate.bat && python start.py"
timeout /t 3 /nobreak > nul
echo.
echo Starting Frontend...
start "Frontend" cmd /k "cd frontend\frontend && npm run dev"
echo.
echo Both services are starting...
echo Backend will be available at: http://localhost:8000
echo Frontend will be available at: http://localhost:5173
echo.

