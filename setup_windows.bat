@echo off
title GPT Course Knowledge Extractor Setup
cd /d "%~dp0"

echo ==============================================
echo GPT Course Knowledge Extractor - Setup
echo ==============================================
echo.

if not exist ".venv\Scripts\activate.bat" (
    echo Creating virtual environment...
    python -m venv .venv
) else (
    echo Virtual environment already exists.
)

call ".venv\Scripts\activate.bat"

echo.
echo Upgrading pip...
python -m pip install --upgrade pip

echo.
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Setup completed.
echo You can now run run_app.bat
pause