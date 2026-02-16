@echo off
echo ========================================
echo Cricket Auction Platform - Starting Server
echo ========================================
echo.

REM Activate virtual environment and start server
call venv\Scripts\activate.bat

echo Starting server on http://localhost:8000
echo.
echo Press Ctrl+C to stop the server
echo.
echo Available URLs:
echo - Main App: http://localhost:8000
echo - Admin: http://localhost:8000/admin
echo - API Docs: http://localhost:8000/docs
echo - Health Check: http://localhost:8000/health
echo.

uvicorn main_new:app --reload --host 0.0.0.0 --port 8000
