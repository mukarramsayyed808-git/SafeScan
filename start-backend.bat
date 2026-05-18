@echo off
REM SafeScan Backend Startup Script (Windows)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies if needed
pip install -q -r backend/requirements.txt

REM Start the server
echo Starting SafeScan backend server...
echo.
echo Backend: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo Frontend: http://localhost:8000
echo.

cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

pause
