# ADK Orchestrator - Fresh Installation Guide

## 🚀 Complete Setup from Scratch

Follow these steps to set up a fresh environment for the ADK orchestrator.

---

## Step 1: Create Conda Environment

```bash
# Create new environment with Python 3.11
conda create -n py311_gadk python=3.11

# Activate the environment
conda activate py311_gadk

# Verify Python version
python --version
# Should show: Python 3.11.x
```

---

## Step 2: Install Core Dependencies

```bash
# Navigate to ADK folder
cd orchestrator_adk

# Install all requirements
pip install -r requirements.txt

# This will install:
# - OpenAI SDK
# - LangGraph + LangChain
# - Streamlit
# - FastAPI
# - Pydantic
# - And more...
```

---

## Step 3: Install Google ADK SDKs (Optional - Preview)

```bash
# These are preview/beta SDKs from Google
# Install when you're ready to use official Google libraries

pip install google-adk        # Google Agent Development Kit
pip install a2a-python        # Official A2A Protocol SDK
```

**Note:** The code works WITHOUT these SDKs! It's designed to be SDK-compatible, so it will use the official libraries once installed, but has fallback implementations for testing.

---

## Step 4: Set Up Environment Variables

```bash
# Navigate back to project root
cd ..

# Copy example env file
cp .env.example .env

# Edit .env and add your API keys
# For ADK with OpenAI:
OPENAI_API_KEY=your_openai_key_here
OPENAI_MODEL=gpt-4-turbo-preview

# Or if using Google Gemini:
GOOGLE_API_KEY=your_google_key_here
```

---

## Step 5: Verify Installation

```bash
# Test core imports
python -c "import langgraph; print('✅ LangGraph:', langgraph.__version__)"
python -c "import openai; print('✅ OpenAI:', openai.__version__)"
python -c "import streamlit; print('✅ Streamlit:', streamlit.__version__)"
python -c "import fastapi; print('✅ FastAPI:', fastapi.__version__)"
python -c "import pydantic; print('✅ Pydantic:', pydantic.__version__)"

# Test optional SDKs (if installed)
python -c "import google.adk; print('✅ Google ADK installed')" 2>/dev/null || echo "⚠️  Google ADK not installed (optional)"
python -c "import a2a; print('✅ A2A Protocol installed')" 2>/dev/null || echo "⚠️  A2A SDK not installed (optional)"
```

---

## Step 6: Test ADK Backend

```bash
# Navigate to ADK folder
cd orchestrator_adk

# Run test suite
python test_adk.py

# Expected output:
# ================================================================================
# TEST: Google ADK Orchestrator
# ================================================================================
# Initializing ADK Reconciliation Orchestrator
# ...
# ✅ Tests complete!
```

---

## Step 7: Start Mock API (Required)

```bash
# Navigate back to project root
cd ..

# Start mock API server (keep this running)
python main.py mock-api

# Expected output:
# Mock API server starting...
# Running on http://localhost:8000
```

**Keep this terminal open!**

---

## Step 8: Launch ADK UI

Open a **NEW terminal**:

```bash
# Activate environment
conda activate py311_gadk

# Navigate to project root
cd C:\Work\reconagent

# Start Streamlit UI
streamlit run frontend/streamlit_app_adk.py

# Expected output:
# You can now view your Streamlit app in your browser.
# Local URL: http://localhost:8501
```

---

## Step 9: Access the UI

Open your browser and go to:
```
http://localhost:8501
```

You should see the **Google ADK Orchestrator** UI with 7 pages!

---

## 🎯 Quick Test

### Test 1: Process a Break
1. In UI, go to "🤖 Process Break"
2. Enter break ID: `BRK-001`
3. Click "🚀 Process with ADK"
4. See results!

### Test 2: View A2A Messages
1. Go to "📨 A2A Messages"
2. Select the break you just processed
3. See all A2A protocol messages

### Test 3: Check LangGraph Flow
1. Go to "🔄 LangGraph Flow"
2. See execution path
3. Check which agents were executed/skipped

---

## 📦 What Gets Installed

### Core (Always)
- **OpenAI SDK** - LLM calls
- **LangGraph** - Orchestration
- **LangChain** - Base framework
- **Streamlit** - UI
- **FastAPI** - Mock APIs
- **Pydantic** - Data validation

### Optional (When Available)
- **google-adk** - Official Google ADK
- **a2a-python** - Official A2A Protocol

---

## 🔍 Troubleshooting

### Issue: `pip install -r requirements.txt` fails

**Solution 1:** Install in stages
```bash
# Core dependencies
pip install pydantic python-dotenv openai

# LangGraph
pip install langgraph langchain langchain-core

# Web frameworks
pip install streamlit fastapi uvicorn

# Data processing
pip install pandas numpy requests
```

**Solution 2:** Update pip
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Issue: Mock API won't start

**Check if port 8000 is in use:**
```bash
# Windows
netstat -ano | findstr :8000

# Linux/Mac
lsof -i :8000
```

**Use different port:**
```bash
python main.py mock-api --port 8001
```

### Issue: UI shows "ADK Orchestrator Failed to Initialize"

**This is NORMAL without Google SDKs!**

The UI will show a warning but the structure is still visible.

**To fix (when ready):**
```bash
pip install google-adk a2a-python
```

### Issue: Import errors

**Make sure you're in the right directory:**
```bash
# Should be in project root
pwd
# Should show: .../reconagent

# And environment is activated
conda info --envs
# Should show * next to py311_gadk
```

---

## 📋 Complete Command Sequence

Here's everything in one place:

```bash
# 1. Create environment
conda create -n py311_gadk python=3.11
conda activate py311_gadk

# 2. Install dependencies
cd C:\Work\reconagent\orchestrator_adk
pip install -r requirements.txt

# 3. Install Google SDKs (optional)
pip install google-adk a2a-python

# 4. Verify
python -c "import langgraph, openai, streamlit; print('✅ All core packages installed')"

# 5. Test backend
python test_adk.py

# 6. Start mock API (Terminal 1)
cd ..
python main.py mock-api

# 7. Start UI (Terminal 2 - new terminal)
conda activate py311_gadk
cd C:\Work\reconagent
streamlit run frontend/streamlit_app_adk.py

# 8. Open browser
# http://localhost:8501
```

---

## 🎓 Next Steps After Installation

### Learn the System
1. Read: `UI_GUIDE.md` - How to use the UI
2. Read: `README.md` - Architecture overview
3. Explore all 7 UI pages

### Customize
1. Modify agents in `agents/` folder
2. Add new tools to agents
3. Adjust LangGraph routing in `langgraph_orchestrator.py`

### Deploy
1. Replace mock APIs with real data sources
2. Set up production environment variables
3. Configure database persistence
4. Deploy UI and backend

---

## 📞 Need Help?

### Documentation
- **Installation:** This file
- **UI Guide:** `UI_GUIDE.md`
- **Architecture:** `README.md`
- **Quick Start:** `../ADK_QUICKSTART.md`

### Check Installation
```bash
# Environment
conda info --envs

# Packages
pip list | grep -E "langgraph|openai|streamlit|google-adk"

# Python version
python --version
```

---

## ✅ Installation Checklist

- [ ] Conda environment created (`py311_gadk`)
- [ ] Environment activated
- [ ] Core dependencies installed (`pip install -r requirements.txt`)
- [ ] Google ADK SDKs installed (optional)
- [ ] Installation verified (imports work)
- [ ] Backend test passed (`python test_adk.py`)
- [ ] Mock API started (`python main.py mock-api`)
- [ ] UI launched (`streamlit run frontend/streamlit_app_adk.py`)
- [ ] Browser opened (`http://localhost:8501`)
- [ ] Processed first break successfully

---

**🎉 You're all set!** Enjoy exploring the Google ADK Orchestrator!

---

**Created:** 2025-11-09  
**For:** Fresh py311_gadk environment  
**Platform:** Windows/Linux/Mac
