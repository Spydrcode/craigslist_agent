@echo off
echo ================================================================================
echo FORECASTA LEAD ANALYSIS DASHBOARD
echo ================================================================================
echo.

cd /d "%~dp0"
set PYTHONPATH=%CD%

echo Checking Flask installation...
python -c "import flask" 2>nul
if errorlevel 1 (
    echo Flask not found. Installing...
    pip install flask
)

echo.
echo Starting dashboard server...
echo.
echo Dashboard URL: http://localhost:3000
echo.
echo Press Ctrl+C to stop the server
echo.
echo ================================================================================
echo.

python dashboard\leads_app.py

pause
