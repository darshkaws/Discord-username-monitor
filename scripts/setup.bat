@echo off
REM Discord Username Monitor - Setup Script for Windows
REM This script sets up the environment and dependencies

echo ===================================================
echo Discord Username Monitor v2.0 - Setup Script
echo ===================================================
echo.

REM Check Python installation
echo Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] Python %PYTHON_VERSION% detected

REM Check Chrome installation
echo Checking Google Chrome installation...
where chrome >nul 2>&1
if %errorlevel% neq 0 (
    where "C:\Program Files\Google\Chrome\Application\chrome.exe" >nul 2>&1
    if %errorlevel% neq 0 (
        where "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" >nul 2>&1
        if %errorlevel% neq 0 (
            echo [WARNING] Chrome not detected. Installing Chrome is recommended.
            echo You can install it manually or continue without it.
            set /p continue="Continue anyway? (y/n): "
            if /i not "%continue%"=="y" exit /b 1
        ) else (
            echo [OK] Chrome detected
        )
    ) else (
        echo [OK] Chrome detected
    )
) else (
    echo [OK] Chrome detected
)

REM Create virtual environment
echo Setting up virtual environment...
if not exist "venv" (
    python -m venv venv
    echo [OK] Virtual environment created
) else (
    echo [OK] Virtual environment already exists
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo Installing Python dependencies...
if exist "requirements.txt" (
    pip install -r requirements.txt
    echo [OK] Dependencies installed
) else (
    echo [ERROR] requirements.txt not found
    pause
    exit /b 1
)

REM Create directory structure
echo Setting up directory structure...
mkdir logs 2>nul
mkdir results 2>nul
mkdir data 2>nul
mkdir config 2>nul
mkdir accounts 2>nul
mkdir usernames 2>nul
mkdir proxies 2>nul
echo [OK] Directories created

REM Create example files
echo Creating example configuration files...

REM Create example tokens file
if not exist "accounts\tokens.txt" (
    (
        echo # Discord Username Monitor - Account Tokens
        echo # 
        echo # Supported formats:
        echo # 1. email:password:token
        echo # 2. email:token  
        echo # 3. token ^(token only^)
        echo #
        echo # Example entries:
        echo # user@example.com:mypassword:MTAxNTExNjQyNzc4MzUyNjQxMA...
        echo # user@example.com:MTAxNTExNjQyNzc4MzUyNjQxMA...
        echo # MTAxNTExNjQyNzc4MzUyNjQxMA...
        echo.
        echo # Add your tokens below:
        echo.
    ) > accounts\tokens.txt.example
    echo [OK] Example tokens file created
)

REM Create example username list
if not exist "usernames\example_list.txt" (
    (
        echo cool
        echo epic
        echo user
        echo name
        echo fire
        echo star
        echo moon
        echo test
        echo demo
        echo example
    ) > usernames\example_list.txt
    echo [OK] Example username list created
)

REM Create gitkeep files
echo. > logs\.gitkeep
echo. > results\.gitkeep
echo. > data\.gitkeep

echo.
echo ===================================================
echo [OK] Setup completed successfully!
echo ===================================================
echo.
echo Next steps:
echo 1. Add your Discord tokens to accounts\tokens.txt
echo 2. Run the monitor: python src\main.py
echo 3. Follow the interactive configuration
echo.
echo For help:
echo - Check the README.md file
echo - Visit the documentation in docs\
echo - Report issues on GitHub
echo.
echo Happy monitoring!
echo.
pause
