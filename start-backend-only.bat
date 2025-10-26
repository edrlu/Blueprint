@echo off
echo ========================================
echo   Blueprint - Backend Only
echo ========================================
echo.

REM Kill any existing backend server
echo Stopping any running backend...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do taskkill /F /PID %%a 2>nul
timeout /t 1 /nobreak > nul
echo.

REM Activate virtual environment
call .venv\Scripts\activate

REM Set Python path to include the Blueprint directory
set PYTHONPATH=%CD%;%PYTHONPATH%

echo Backend API: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

REM Run backend with debug logs visible
python api\server.py
