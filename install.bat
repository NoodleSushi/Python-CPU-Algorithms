@echo off

where python >nul 2>&1
if %errorlevel% neq 0 (
  echo Python is not installed or not in the system path. Please install Python and make sure it's part of the system variables.
  goto :eof
)

echo initializing virtual environment
call python -m venv .venv

echo activating virtual environment
call .venv\Scripts\activate.bat

echo installing requirements
call pip install -r requirements.txt || (echo ERROR: Failed to install requirements && exit /b 1)
