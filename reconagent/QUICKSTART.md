# Quick Start Guide

## Prerequisites

- Python 3.9 or higher
- Google API Key (for Google GenAI)

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file in the root directory:

```bash
# Copy the example file
cp .env.example .env
```

Edit `.env` and add your OpenAI API Key:
```
OPENAI_API_KEY=your_actual_api_key_here
```

To get an OpenAI API Key:
1. Go to https://platform.openai.com/api-keys
2. Create a new API key
3. Copy and paste it into your `.env` file

## Running the System

### Option 1: Quick Test (Without Mock API Server)

Run the test workflow directly (doesn't require mock API server):

```bash
python tests/test_workflow.py
```

This will process a sample break through all 7 agents.

### Option 2: Full System with Mock APIs

#### Terminal 1 - Start Mock API Server:
```bash
python main.py mock-api
```

Keep this running. You should see:
```
INFO:     Started server process
INFO:     Uvicorn running on http://127.0.0.1:8000
```

#### Terminal 2 - Run Example Workflow:
```bash
python main.py
```

This will:
1. Process a single break through all agents
2. Process a batch of 3 breaks
3. Show detailed output for each stage

### Option 3: PowerShell Single Command

```powershell
# Start mock API in background, wait, then run workflow
Start-Job -ScriptBlock { cd C:\Work\reconagent; python main.py mock-api }
Start-Sleep -Seconds 3
python main.py
```

### Option 4: Run with Streamlit UI (Recommended)

```bash
# Terminal 1 - Start Mock API Server:
python main.py mock-api

# Terminal 2 - Start Streamlit UI:
streamlit run frontend/streamlit_app.py
```

Then open your browser to **http://localhost:8501**

The UI provides:
- Dashboard with metrics
- Review queue for HIL cases
- Complete agent analysis
- Approve/Override/Escalate actions
- Analytics and feedback stats

See **UI_GUIDE.md** for complete UI documentation.

## What to Expect

### Example Output:

```
================================================================================
 Reconciliation Agent System - Example Workflow
================================================================================

[Orchestrator] All agents initialized

============================================================
[Orchestrator] Starting workflow - Conversation ID: abc123...
============================================================

[Stage 1] Break Ingestion...
✓ Break ingested: BRK-2025-11-12345

[Stage 2] Data Enrichment...
✓ Enriched with 6 sources

[Stage 3] Matching & Correlation...
✓ Found 2 match candidates

[Stage 4] Rules & Tolerance Check...
✓ Rules evaluation: PASSED

[Stage 5] Pattern Intelligence...
✓ Root cause: timing_lag (confidence: 85.00%)

[Stage 6] Decision Making...
✓ Decision: AUTO_RESOLVE (risk score: 0.15)
  Explanation: Within tolerance | High confidence | Low amount

[Stage 7] Workflow Creation...
✓ Ticket created: TKT-ABC12345 - Status: RESOLVED

============================================================
[Orchestrator] Workflow completed successfully
============================================================
```

## Verify Installation

Check that all components are installed:

```bash
# Check Python version
python --version

# Check installed packages
pip list | findstr "pydantic fastapi uvicorn google-genai"

# Test imports
python -c "from orchestrator.workflow import ReconciliationOrchestrator; print('✓ All imports successful')"
```

## Project Structure Verification

```
C:\Work\reconagent\
├── agents/                    ✓ 7 agent files + base_agent.py
├── mcp/tools/                 ✓ 7 tool files
├── mock_apis/                 ✓ FastAPI server
├── shared/                    ✓ Schemas, A2A protocol, config
├── orchestrator/              ✓ Workflow orchestration
├── tests/                     ✓ Test files
├── main.py                    ✓ Entry point
├── requirements.txt           ✓ Dependencies
├── .env.example               ✓ Config template
└── README.md                  ✓ Documentation
```

## Troubleshooting

### Issue: "Module not found" errors

**Solution**: Make sure you're in the project root directory:
```bash
cd C:\Work\reconagent
python main.py
```

### Issue: "OPENAI_API_KEY not set"

**Solution**: 
1. Create `.env` file from `.env.example`
2. Add your OpenAI API key
3. Restart the application

### Issue: "Connection refused" when running workflow

**Solution**: Make sure Mock API server is running first:
```bash
# Terminal 1
python main.py mock-api
```

### Issue: Port 8000 already in use

**Solution**: Either:
1. Stop other services using port 8000
2. Or change port in `.env`:
   ```
   MOCK_API_PORT=8001
   MOCK_API_BASE_URL=http://127.0.0.1:8001
   ```

## API Documentation

Once the mock API server is running, view API docs at:
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## Test Endpoints

Test the mock APIs directly:

```bash
# Get breaks
curl http://127.0.0.1:8000/api/breaks?limit=5

# Get OMS order
curl http://127.0.0.1:8000/api/oms/orders/O123456

# Get reference data
curl http://127.0.0.1:8000/api/reference-data/instrument/AAPL
```

## Next Steps

1. Review the workflow output to understand agent interactions
2. Check the A2A protocol messages in the console
3. Explore the code in `agents/` and `mcp/tools/`
4. Modify tolerances in `shared/config.py` or `.env`
5. Add custom business rules in `mcp/tools/rules_tools.py`
6. Implement HIL UI (see README.md for next steps)

## Support

For issues or questions:
1. Check the full README.md
2. Review the blueprint: Reconciliation_Agent_Blueprint.md
3. Check agent logs for detailed error messages
