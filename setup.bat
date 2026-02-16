@echo off
REM Cricket Auction Platform - Windows Setup Script

echo ========================================
echo Cricket Auction Platform - Setup Script
echo ========================================
echo.

REM Check Python
echo Checking Python version...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python 3.11+
    pause
    exit /b 1
)
python --version
echo [OK] Python found
echo.

REM Create virtual environment
echo Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo [OK] Virtual environment created
) else (
    echo [WARNING] Virtual environment already exists
)
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo [OK] Virtual environment activated
echo.

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip >nul 2>&1
echo [OK] pip upgraded
echo.

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
echo [OK] Dependencies installed
echo.

REM Create .env file
echo Setting up environment variables...
if not exist ".env" (
    copy .env.example .env
    echo [OK] .env file created
    echo [WARNING] Please update .env file with your settings
) else (
    echo [WARNING] .env file already exists
)
echo.

REM Create directories
echo Creating directories...
if not exist "logs" mkdir logs
if not exist "uploads" mkdir uploads
echo [OK] Directories created
echo.

REM Summary
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next Steps:
echo.
echo 1. Review and update .env file:
echo    notepad .env
echo.
echo 2. Start MongoDB (if not running)
echo.
echo 3. Run the development server:
echo    venv\Scripts\activate
echo    uvicorn main_new:app --reload
echo.
echo 4. Access the application:
echo    http://localhost:8000
echo.
echo 5. View API documentation:
echo    http://localhost:8000/docs
echo.
echo Docker Alternative:
echo    docker-compose up -d
echo.
echo Happy coding!
echo.
pause
