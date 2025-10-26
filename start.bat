@echo off
echo ========================================
echo   Blueprint - Hackathon Idea Generator
echo ========================================
echo.

REM Kill any existing servers first
echo Stopping any running servers...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5173 ^| findstr LISTENING') do taskkill /F /PID %%a 2>nul
timeout /t 2 /nobreak > nul
echo.

REM Activate virtual environment
call .venv\Scripts\activate

REM Set Python path to include the Blueprint directory
set PYTHONPATH=%CD%;%PYTHONPATH%

echo Starting Frontend in background...
cd frontend
start /MIN "Blueprint Frontend" cmd /c "npm run dev"
cd ..
echo.

echo ========================================
echo   Starting Backend API Server
echo   Backend logs will appear below
echo ========================================
echo.
echo Frontend: http://localhost:5173
echo Backend API: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the backend server
echo ========================================
echo.

REM Run backend in this terminal to see all debug logs
python api\server.py
