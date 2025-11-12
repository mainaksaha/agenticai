@echo off
echo ========================================
echo Starting ADK Orchestrator UI
echo ========================================
echo.

echo Checking Python...
python --version
if errorlevel 1 (
    echo ERROR: Python not found!
    pause
    exit /b 1
)

echo.
echo Checking Streamlit...
python -c "import streamlit" 2>nul
if errorlevel 1 (
    echo ERROR: Streamlit not installed!
    echo Run: pip install streamlit
    pause
    exit /b 1
)

echo.
echo ========================================
echo Starting ADK UI...
echo ========================================
echo.
echo URL: http://localhost:8501
echo.
echo Press Ctrl+C to stop
echo ========================================
echo.

streamlit run frontend/streamlit_app_adk.py
