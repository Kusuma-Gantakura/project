@echo off
setlocal

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in your PATH.
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

:: Check for virtual environment
if not exist "venv" (
    echo [INFO] Creating virtual environment...
    python -m venv venv
)

:: Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate

:: Upgrade pip within venv (fixes some connection/version issues)
echo [INFO] Upgrading pip...
python -m pip install --upgrade pip --timeout 100

:: Install dependencies with longer timeout and retries for network issues
echo [INFO] Installing dependencies (this may take a moment)...
python -m pip install -r requirements.txt --timeout 100 --retries 10

:: Verify installation
python -c "import flask" >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Flask was not installed correctly. Please check your internet connection and try again.
    pause
    exit /b 1
)

:: Run the application
echo [INFO] Starting the AI Study Buddy application...
echo [INFO] The browser will open automatically in a few seconds.

:: Start a background process to open the browser after a short delay
start /b cmd /c "timeout /t 5 >nul && start http://127.0.0.1:5000"

python app.py

:: Keep window open if app crashes
if %errorlevel% neq 0 (
    echo [ERROR] Application crashed.
    pause
)

endlocal
