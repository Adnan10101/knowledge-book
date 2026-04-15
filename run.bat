@echo off
REM Quick Start Script for Book RAG System

echo.
echo ======================================
echo   Book RAG System - Quick Start
echo ======================================
echo.

REM Check if virtual environment exists
if exist "env\" (
    echo Activating virtual environment...
    call env\Scripts\activate.bat
) else (
    echo Creating virtual environment...
    python -m venv env
    call env\Scripts\activate.bat
    
    echo Installing dependencies...
    pip install -r requirements.txt
)

echo.
echo Starting Streamlit application...
echo Opening in browser at http://localhost:8501
echo.
echo Press Ctrl+C to stop the server
echo.

cd data-preprocess
streamlit run app.py
