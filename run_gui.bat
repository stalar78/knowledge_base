@echo off
title GPT Course Knowledge Extractor GUI
cd /d "%~dp0"

echo ==============================================
echo GPT Course Knowledge Extractor - GUI
echo ==============================================
echo.

if exist ".venv\Scripts\activate.bat" (
    call ".venv\Scripts\activate.bat"
) else (
    echo WARNING: Virtual environment .venv not found.
    echo You may need to create it:
    echo   python -m venv .venv
    echo   .venv\Scripts\activate
    echo   pip install -r requirements.txt
    echo.
)

python -m src.gui_app

echo.
echo GUI closed.
pause