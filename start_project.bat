@echo off
chcp 65001 > nul
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
echo 🚀 Starting Traffic Analysis NLP Project...
echo.
echo [1/3] Activating virtual environment...
call venv\Scripts\activate.bat

echo [2/3] Installing dependencies...
pip install -r requirements.txt

echo [3/3] Starting Flask server...
python app.py

echo.
echo 📊 Traffic Analysis Dashboard running on http://localhost:5000
echo Press Ctrl+C to stop
pause
