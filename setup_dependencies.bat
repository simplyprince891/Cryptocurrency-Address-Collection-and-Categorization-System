@echo off
echo ===================================================
echo   Installing CyberProject Dependencies
echo ===================================================

echo.
echo [1/2] Installing Backend Dependencies (Python)...
cd backend
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install Python dependencies. Please check if Python/Pip is installed.
    pause
    exit /b %errorlevel%
)
echo [SUCCESS] Backend dependencies installed.

echo.
echo [2/2] Installing Frontend Dependencies (Node.js/React)...
cd ../frontend
call npm install
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install Node.js dependencies. Please check if Node.js/npm is installed.
    pause
    exit /b %errorlevel%
)
echo [SUCCESS] Frontend dependencies installed.

echo.
echo ===================================================
echo   All dependencies installed successfully!
echo   You can now run 'start_project.bat'
echo ===================================================
pause
