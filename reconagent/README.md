# Reconciliation Agent System

AI Agent-based Reconciliation System using A2A Protocol, OpenAI GPT-4.1, and MCP Tools.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              Orchestration Layer                             │
│           (Manages Agent Lifecycle & A2A Comm)               │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
   ┌────▼────┐         ┌────▼────┐        ┌────▼────┐
   │ Agent 1 │◄────────┤ Agent 2 │◄───────┤ Agent 3 │
   │(Break   │  A2A    │(Data    │  A2A   │(Matching│
   │Ingestion│Protocol │Enrichmt)│Protocol│Correlat)│
   └────┬────┘         └────┬────┘        └────┬────┘
        │                   │                   │
   ┌────▼────────────┬──────▼────────────┬──────▼─────┐
   │   MCP Tool 1    │   MCP Tool 2      │  MCP Tool 3│
   │  (Break API)    │  (OMS API)        │(Reference) │
   └────┬────────────┴──────┬────────────┴──────┬─────┘
        │                   │                   │
   ┌────▼────────────┬──────▼────────────┬──────▼─────┐
   │  Mock API 1     │  Mock API 2       │ Mock API 3 │
   │(Breaks Service) │(OMS Service)      │(Ref Data)  │
   └─────────────────┴───────────────────┴────────────┘
```

## 7 Agents

1. **Break Ingestion Agent** - Normalizes incoming breaks
2. **Data Enrichment Agent** - Gathers data from multiple sources
3. **Matching & Correlation Agent** - Finds candidate matches
4. **Rules & Tolerance Agent** - Applies business rules
5. **Pattern Intelligence Agent** - Predicts root causes
6. **Decisioning Agent** - Makes final decision
7. **Workflow & Feedback Agent** - Creates tickets and logs feedback

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create `.env` file:
```bash
cp .env.example .env
```

3. Add your Google API Key to `.env`:
```
GOOGLE_API_KEY=your_api_key_here
```

## Running the System

### Option 1: Run Mock API Server (Terminal 1)
```bash
python main.py mock-api
```

### Option 2: Run Example Workflow (Terminal 2)
```bash
python main.py
```

Or in a single terminal with mock API running in background:
```bash
# Windows PowerShell
Start-Job -ScriptBlock { python main.py mock-api }
Start-Sleep -Seconds 2
python main.py
```

## Workflow

The system processes breaks through 7 stages:

```
Incoming Break 
  → [1] Break Ingestion 
  → [2] Data Enrichment 
  → [3] Matching & Correlation
  → [4] Rules & Tolerance
  → [5] Pattern & Root-Cause
  → [6] Decisioning
  → [7] Workflow & Feedback
  → (Auto-Resolve | HIL Review | Escalate)
```

## A2A Protocol

Agents communicate using A2A (Agent-to-Agent) protocol:

- **Request**: Agent requests action from another agent
- **Response**: Agent responds with result
- **Notification**: Agent notifies others of events
- **Error**: Agent reports error

All messages include:
- `message_id`: Unique identifier
- `conversation_id`: Groups related messages
- `from_agent` / `to_agent`: Source and destination
- `payload`: Message data
- `timestamp`: Message timestamp

## MCP Tools

Each agent has domain-specific MCP tools:

- **Break Tools**: `get_breaks`, `normalize_break`, `validate_break`
- **Enrichment Tools**: `get_oms_data`, `get_trade_capture`, `get_settlement`
- **Matching Tools**: `find_match_candidates`, `calculate_similarity`
- **Rules Tools**: `check_tolerance`, `apply_business_rules`
- **Pattern Tools**: `get_historical_patterns`, `predict_root_cause`
- **Decision Tools**: `calculate_risk_score`, `evaluate_decision`
- **Workflow Tools**: `create_ticket`, `log_feedback`, `get_audit_trail`

## Mock APIs

The system includes mock APIs for all data sources:

- `GET /api/breaks` - Get breaks
- `GET /api/oms/orders/{order_id}` - Get OMS data
- `GET /api/trade-capture/trades/{trade_id}` - Get trade data
- `GET /api/settlement/positions/{account}` - Get settlement data
- `GET /api/custodian/holdings/{account}` - Get custodian data
- `GET /api/reference-data/instrument/{symbol}` - Get reference data
- `GET /api/broker/confirms/{trade_id}` - Get broker confirms
- `GET /api/historical/patterns` - Get historical patterns

## Configuration

Edit `shared/config.py` or `.env` file to adjust:

- Tolerance thresholds (amount, quantity, FX)
- Auto-resolve thresholds (confidence, amount)
- Escalation thresholds (amount, risk score)
- API endpoints and timeouts

## Decision Logic

The Decisioning Agent uses the following logic:

**Auto-Resolve** if:
- Within tolerance
- High ML confidence (>90%)
- Low amount (<$10,000)
- Low risk score (<0.3)

**Escalate** if:
- High risk score (>0.75)
- Large amount (>$100,000)
- System error or data entry error

**HIL Review** otherwise

## Project Structure

```
reconagent/
├── agents/                    # 7 Agents
│   ├── base_agent.py
│   ├── break_ingestion_agent.py
│   ├── data_enrichment_agent.py
│   ├── matching_correlation_agent.py
│   ├── rules_tolerance_agent.py
│   ├── pattern_intelligence_agent.py
│   ├── decisioning_agent.py
│   └── workflow_feedback_agent.py
├── mcp/tools/                 # MCP Tools
│   ├── break_tools.py
│   ├── enrichment_tools.py
│   ├── matching_tools.py
│   ├── rules_tools.py
│   ├── pattern_tools.py
│   ├── decision_tools.py
│   └── workflow_tools.py
├── mock_apis/                 # Mock Data APIs
│   └── main.py
├── shared/                    # Common utilities
│   ├── schemas.py
│   ├── a2a_protocol.py
│   └── config.py
├── orchestrator/              # Workflow orchestration
│   └── workflow.py
├── main.py                    # Entry point
└── requirements.txt
```

## Human-in-the-Loop (HIL) UI

The system includes a **Streamlit web interface** for human review of cases:

### Starting the UI

```bash
# Terminal 1: Start Mock API
python main.py mock-api

# Terminal 2: Start Streamlit UI
streamlit run frontend/streamlit_app.py
```

The UI will open at: **http://localhost:8501**

### UI Features

- **📊 Dashboard** - Overview of all cases with metrics
- **📝 Review Queue** - Detailed review interface for HIL cases
  - View raw vs enriched data side-by-side
  - See complete 7-stage agent analysis
  - Review risk assessment
  - Take action: Approve, Override, or Escalate
- **📈 Analytics** - System performance and feedback stats
- **⚙️ Settings** - Configuration viewer

See **UI_GUIDE.md** for complete UI documentation.

## Next Steps

1. ✅ HIL UI (Complete - Streamlit)
2. Replace mock APIs with real connectors
3. Integrate with production databases
4. Add authentication and authorization
5. Implement monitoring and alerting
6. Add more sophisticated ML models
7. Implement feedback learning loop

## License

MIT
