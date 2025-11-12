#!/bin/bash

echo "========================================"
echo "Starting ADK Orchestrator UI"
echo "========================================"
echo ""

echo "Checking Python..."
python3 --version
if [ $? -ne 0 ]; then
    echo "ERROR: Python not found!"
    exit 1
fi

echo ""
echo "Checking Streamlit..."
python3 -c "import streamlit" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "ERROR: Streamlit not installed!"
    echo "Run: pip install streamlit"
    exit 1
fi

echo ""
echo "========================================"
echo "Starting ADK UI..."
echo "========================================"
echo ""
echo "URL: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop"
echo "========================================"
echo ""

streamlit run frontend/streamlit_app_adk.py
