@echo off
echo ========================================
echo   Killing Blueprint Servers
echo ========================================
echo.

echo Killing Python backend (port 8000)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do taskkill /F /PID %%a 2>nul
echo.

echo Killing Frontend dev server (port 5173)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5173 ^| findstr LISTENING') do taskkill /F /PID %%a 2>nul
echo.

echo ========================================
echo   All servers stopped!
echo ========================================
echo.
pause
