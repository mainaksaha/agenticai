#!/bin/bash

echo "========================================"
echo "ADK Orchestrator - Fresh Environment Setup"
echo "========================================"
echo ""

echo "Step 1: Creating conda environment 'py311_gadk'"
echo ""
conda create -n py311_gadk python=3.11 -y
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create conda environment"
    exit 1
fi

echo ""
echo "Step 2: Activating environment"
echo ""
source $(conda info --base)/etc/profile.d/conda.sh
conda activate py311_gadk
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to activate environment"
    exit 1
fi

echo ""
echo "Step 3: Installing dependencies from requirements.txt"
echo ""
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

echo ""
echo "Step 4: Verifying installation"
echo ""
python -c "import langgraph; print('✅ LangGraph installed')"
python -c "import openai; print('✅ OpenAI installed')"
python -c "import streamlit; print('✅ Streamlit installed')"
python -c "import fastapi; print('✅ FastAPI installed')"

echo ""
echo "========================================"
echo "Installation Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "  1. Set up .env file with API keys"
echo "  2. Start mock API: python main.py mock-api"
echo "  3. Start UI: streamlit run frontend/streamlit_app_adk.py"
echo ""
echo "To activate this environment later:"
echo "  conda activate py311_gadk"
echo ""
echo "Optional - Install Google ADK SDKs:"
echo "  pip install google-adk a2a-python"
echo ""
