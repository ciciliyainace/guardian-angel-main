@echo off
echo ========================================================
echo Starting SentinelAI Backend Server (FastAPI + Uvicorn)
echo ========================================================

REM Activate virtual environment if present
if exist "..\.venv\Scripts\activate.bat" (
    call ..\.venv\Scripts\activate.bat
) else if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

REM Run database initialization
python scripts\initialize_database.py

REM Start uvicorn server on port 8000
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
pause
