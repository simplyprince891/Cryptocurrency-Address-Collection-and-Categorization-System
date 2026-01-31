@echo off
echo ===================================================
echo   Starting CyberProject...
echo ===================================================

echo [1/2] Starting Backend Server...
start "CyberProject Backend" cmd /k "cd backend && python app.py"

echo [2/2] Starting Frontend Dashboard...
start "CyberProject Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo System is launching! 
echo Backend will run on http://127.0.0.1:5000
echo Frontend will run on http://localhost:5173
echo.
echo You can close this window now.
pause
