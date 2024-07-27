@echo off

:: check if pip is installed
pip --version > nul 2>&1
if %errorlevel% neq 0 (
    echo pip3 is not installed. Please install pip3 and try again.
    exit /b 1
)

:: Install dependencies.
pip3 install -r requirements.txt