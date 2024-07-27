@echo off

:: check if python is installed
python --version > nul 2>&1

if %errorlevel% neq 0 (
    echo "Python is not installed. Please install Python and try again."
    exit /b 1
)

:: run the program
python src/main.py