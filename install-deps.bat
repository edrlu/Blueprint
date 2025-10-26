@echo off
echo ========================================
echo   Blueprint - Install Dependencies
echo ========================================
echo.

echo [1/2] Installing Python dependencies...
call .venv\Scripts\activate
pip install -r requirements.txt
echo.

echo [2/2] Installing Frontend dependencies...
cd frontend
npm install
cd ..
echo.

echo ========================================
echo   Dependencies installed!
echo ========================================
pause
