@echo off
echo Stopping Python processes...
taskkill /F /IM python.exe 2>nul
timeout /t 2 /nobreak >nul

echo Running database migration...
cd backend
python quick_migrate.py

echo.
echo Migration complete! Now restart backend with: python app.py
pause
