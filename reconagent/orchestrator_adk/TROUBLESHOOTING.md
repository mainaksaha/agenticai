# ADK Orchestrator - Troubleshooting Guide

## Common Issues and Solutions

---

## 1. TypeError: function() got an unexpected keyword argument

### Symptom
```
TypeError: check_tolerance() got an unexpected keyword argument 'break_data'
```

### Cause
Parameter mismatch between ADK agent tool definitions and actual MCP tool functions.

### Solution
✅ **FIXED in latest version!**

The `agent_base.py` now intelligently filters parameters to match function signatures.

### Verification
```bash
streamlit run frontend/streamlit_app_adk.py
# Go to "Process Break" → Enter BRK-001 → Click "Process"
# Should work without errors
```

### Details
See [BUGFIX_PARAMETER_MISMATCH.md](BUGFIX_PARAMETER_MISMATCH.md)

---

## 2. Mock API Not Running

### Symptom
```
Connection refused on localhost:8000
Failed to fetch breaks
```

### Cause
Mock API server not started.

### Solution
```bash
# Terminal 1: Start mock API
python main.py mock-api

# Keep this running!
```

### Verification
Open browser: http://localhost:8000/breaks
Should see JSON data.

---

## 3. ADK Orchestrator Failed to Initialize

### Symptom
UI shows warning: "⚠️ ADK Orchestrator Failed to Initialize"

### Cause
One of several issues:
1. Mock API not running
2. Missing dependencies
3. Import errors

### Solution

**Step 1: Check Mock API**
```bash
# Make sure this is running
python main.py mock-api
```

**Step 2: Check Dependencies**
```bash
conda activate py311_gadk
pip list | findstr "streamlit langgraph openai"
```

**Step 3: Check Imports**
```bash
python -c "from orchestrator_adk.orchestrator import ADKReconciliationOrchestrator; print('OK')"
```

**Step 4: View Error**
Check UI - the error message will show the actual problem.

---

## 4. Module Import Errors

### Symptom
```
ModuleNotFoundError: No module named 'langgraph'
ModuleNotFoundError: No module named 'orchestrator_adk'
```

### Cause
Missing dependencies or wrong directory.

### Solution

**For missing packages:**
```bash
conda activate py311_gadk
cd orchestrator_adk
pip install -r requirements.txt
```

**For wrong directory:**
```bash
# Make sure you're in project root
cd C:\Work\reconagent

# Then run UI
streamlit run frontend/streamlit_app_adk.py
```

---

## 5. UI Won't Start

### Symptom
```
streamlit: command not found
```

### Cause
Streamlit not installed or environment not activated.

### Solution
```bash
# Activate environment
conda activate py311_gadk

# Install streamlit
pip install streamlit

# Verify
streamlit --version
```

---

## 6. Break Processing Hangs

### Symptom
UI shows "Processing..." forever

### Cause
One of the agents is stuck or erroring silently.

### Solution

**Check terminal output:**
Look for error messages in the Streamlit terminal.

**Restart UI:**
```bash
# Ctrl+C to stop
# Then restart
streamlit run frontend/streamlit_app_adk.py
```

**Check mock API:**
```bash
# Make sure it's responding
curl http://localhost:8000/breaks
```

---

## 7. Google API Key Errors

### Symptom
```
Error calling LLM: API key not found
```

### Cause
GOOGLE_API_KEY or OPENAI_API_KEY not set in .env

### Solution

**Option 1: Use OpenAI (Recommended for ADK)**
```bash
# Edit .env file
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4-turbo-preview
```

**Option 2: Use Google Gemini**
```bash
# Edit .env file
GOOGLE_API_KEY=your_key_here
```

**Restart UI after updating .env**

---

## 8. A2A Messages Not Showing

### Symptom
A2A Messages page shows empty or "No messages found"

### Cause
Break hasn't been processed yet, or execution didn't create A2A messages.

### Solution
1. Go to "Process Break" page
2. Process a break first
3. Then check "A2A Messages" page
4. Select the break from dropdown

### Note
A2A messages are created during break processing.

---

## 9. Comparison Not Working

### Symptom
"ADK vs Custom" page shows v2 orchestrator error

### Cause
Custom v2 orchestrator failed to initialize (this is OK).

### Solution
**This is expected!** The comparison will only work if both implementations are available.

For now, focus on ADK implementation. v2 comparison is optional.

---

## 10. Performance Page Empty

### Symptom
Performance page shows "No execution data yet"

### Cause
No breaks have been processed.

### Solution
1. Go to "Process Break" page
2. Process some breaks
3. Return to Performance page
4. Metrics will now show

---

## Verification Commands

### Check Environment
```bash
# List environments
conda info --envs

# Should see: py311_gadk (with *)

# Activate if needed
conda activate py311_gadk
```

### Check Installation
```bash
# Core packages
python -c "import streamlit; print('Streamlit:', streamlit.__version__)"
python -c "import langgraph; print('LangGraph:', langgraph.__version__)"
python -c "import openai; print('OpenAI:', openai.__version__)"

# ADK components
python -c "from orchestrator_adk import ADKReconciliationOrchestrator; print('ADK: OK')"
```

### Check Mock API
```bash
# Start API
python main.py mock-api

# In another terminal, test:
curl http://localhost:8000/breaks
# Should return JSON
```

### Check UI
```bash
# Start UI
streamlit run frontend/streamlit_app_adk.py

# Open browser
http://localhost:8501
```

---

## Debug Mode

### Enable Detailed Logging

**Edit `frontend/streamlit_app_adk.py`:**
Add at top:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

**View logs in terminal where Streamlit is running.**

---

## Quick Fixes Summary

| Issue | Quick Fix |
|-------|-----------|
| TypeError | ✅ Fixed in latest code |
| Mock API | `python main.py mock-api` |
| Init failed | Check error message in UI |
| Import errors | `pip install -r requirements.txt` |
| UI won't start | `conda activate py311_gadk` |
| Processing hangs | Check terminal, restart UI |
| API key error | Update .env file |
| No messages | Process break first |
| Comparison fails | Expected (v2 optional) |
| Performance empty | Process breaks first |

---

## Getting Help

### Step 1: Check This Guide
Look for your error message above.

### Step 2: Check Documentation
- [INSTALLATION.md](INSTALLATION.md) - Setup issues
- [UI_GUIDE.md](UI_GUIDE.md) - UI issues  
- [BUGFIX_PARAMETER_MISMATCH.md](BUGFIX_PARAMETER_MISMATCH.md) - Parameter errors

### Step 3: Verify Installation
```bash
conda activate py311_gadk
cd orchestrator_adk
python -c "from orchestrator import ADKReconciliationOrchestrator; print('OK')"
```

### Step 4: Clean Reinstall
```bash
# Remove environment
conda env remove -n py311_gadk

# Recreate
conda create -n py311_gadk python=3.11
conda activate py311_gadk

# Reinstall
cd orchestrator_adk
pip install -r requirements.txt
```

---

## Still Having Issues?

### Collect Information
1. Error message (full text)
2. What you were doing
3. Which page in UI
4. Terminal output

### Check These Files
1. `frontend/streamlit_app_adk.py` - UI code
2. `orchestrator_adk/orchestrator.py` - Main entry
3. `orchestrator_adk/agent_base.py` - Agent base
4. `.env` - Environment variables

### Common Patterns

**Pattern 1: Environment Issues**
```bash
conda activate py311_gadk
python --version  # Should be 3.11.x
pip list  # Should show all packages
```

**Pattern 2: Path Issues**
```bash
# Always run from project root
cd C:\Work\reconagent
streamlit run frontend/streamlit_app_adk.py
```

**Pattern 3: API Issues**
```bash
# Mock API must be running
# Terminal 1:
python main.py mock-api

# Terminal 2:
streamlit run frontend/streamlit_app_adk.py
```

---

## Success Checklist

✅ Environment created and activated  
✅ Dependencies installed (`pip install -r requirements.txt`)  
✅ Mock API running (`python main.py mock-api`)  
✅ UI starts (`streamlit run frontend/streamlit_app_adk.py`)  
✅ Can access http://localhost:8501  
✅ No initialization errors  
✅ Can process break successfully  
✅ Results show in UI  

**If all checked, you're good to go! 🎉**

---

**Last Updated:** November 9, 2025  
**Status:** Active troubleshooting guide
