@echo off
echo ========================================
echo ADK Orchestrator - Fresh Environment Setup
echo ========================================
echo.

echo Step 1: Creating conda environment 'py311_gadk'
echo.
conda create -n py311_gadk python=3.11 -y
if errorlevel 1 (
    echo ERROR: Failed to create conda environment
    pause
    exit /b 1
)

echo.
echo Step 2: Activating environment
echo.
call conda activate py311_gadk
if errorlevel 1 (
    echo ERROR: Failed to activate environment
    pause
    exit /b 1
)

echo.
echo Step 3: Installing dependencies from requirements.txt
echo.
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Step 4: Verifying installation
echo.
python -c "import langgraph; print('✅ LangGraph installed')"
python -c "import openai; print('✅ OpenAI installed')"
python -c "import streamlit; print('✅ Streamlit installed')"
python -c "import fastapi; print('✅ FastAPI installed')"

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo Next steps:
echo   1. Set up .env file with API keys
echo   2. Start mock API: python main.py mock-api
echo   3. Start UI: streamlit run frontend/streamlit_app_adk.py
echo.
echo To activate this environment later:
echo   conda activate py311_gadk
echo.
echo Optional - Install Google ADK SDKs:
echo   pip install google-adk a2a-python
echo.
pause
