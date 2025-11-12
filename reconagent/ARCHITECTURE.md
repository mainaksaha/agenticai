# System Architecture

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Reconciliation Orchestrator                       │
│                 (Coordinates Agent Workflow via A2A)                 │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                    ┌───────────▼───────────┐
                    │  A2A Message Bus      │
                    │  (Agent Communication)│
                    └───────────┬───────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
┌───────▼────────┐    ┌────────▼────────┐    ┌────────▼────────┐
│   Agent 1      │    │   Agent 2       │    │   Agent 3       │
│   Break        │    │   Data          │    │   Matching &    │
│   Ingestion    │    │   Enrichment    │    │   Correlation   │
└───────┬────────┘    └────────┬────────┘    └────────┬────────┘
        │                      │                      │
┌───────▼────────┐    ┌────────▼────────┐    ┌────────▼────────┐
│   Agent 4      │    │   Agent 5       │    │   Agent 6       │
│   Rules &      │    │   Pattern &     │    │   Decisioning   │
│   Tolerance    │    │   Intelligence  │    │                 │
└───────┬────────┘    └────────┬────────┘    └────────┬────────┘
        │                      │                      │
        └───────────────────┬──┴──────────────────────┘
                            │
                    ┌───────▼────────┐
                    │   Agent 7      │
                    │   Workflow &   │
                    │   Feedback     │
                    └───────┬────────┘
                            │
                ┌───────────┴───────────┐
                │                       │
        ┌───────▼────────┐    ┌────────▼────────┐
        │  Ticket System │    │  Audit Trail    │
        │  (In-memory)   │    │  (In-memory)    │
        └────────────────┘    └─────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                         MCP Tools Layer                              │
│  (Model Context Protocol - Agent's Interface to Data Sources)       │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
┌───────▼────────┐    ┌────────▼────────┐    ┌────────▼────────┐
│ Break Tools    │    │ Enrichment      │    │ Matching        │
│ - get_breaks   │    │ Tools           │    │ Tools           │
│ - normalize    │    │ - get_oms_data  │    │ - find_matches  │
│ - validate     │    │ - get_trades    │    │ - calculate_sim │
└───────┬────────┘    └────────┬────────┘    └────────┬────────┘
        │                      │                      │
┌───────▼────────┐    ┌────────▼────────┐    ┌────────▼────────┐
│ Rules Tools    │    │ Pattern Tools   │    │ Decision Tools  │
│ - check_tol    │    │ - get_patterns  │    │ - calc_risk     │
│ - apply_rules  │    │ - predict_cause │    │ - evaluate_dec  │
└───────┬────────┘    └────────┬────────┘    └────────┬────────┘
        │                      │                      │
        └───────────────────┬──┴──────────────────────┘
                            │
                    ┌───────▼────────┐
                    │ Workflow Tools │
                    │ - create_ticket│
                    │ - log_feedback │
                    └───────┬────────┘
                            │
┌─────────────────────────────────────────────────────────────────────┐
│                      Mock API Layer                                  │
│              (Simulates Real Data Sources)                           │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
┌───────▼────────┐    ┌────────▼────────┐    ┌────────▼────────┐
│ /api/breaks    │    │ /api/oms/       │    │ /api/trade-     │
│                │    │ orders          │    │ capture         │
└────────────────┘    └─────────────────┘    └─────────────────┘
        │                      │                      │
┌───────▼────────┐    ┌────────▼────────┐    ┌────────▼────────┐
│ /api/          │    │ /api/custodian/ │    │ /api/broker/    │
│ settlement     │    │ holdings        │    │ confirms        │
└────────────────┘    └─────────────────┘    └─────────────────┘
```

## Workflow Sequence

```
┌─────────────────────────────────────────────────────────────────────┐
│                      Break Processing Workflow                       │
└─────────────────────────────────────────────────────────────────────┘

1. INGESTION
   Break Data → Break Ingestion Agent
                ↓
                [Normalize & Validate]
                ↓
                Validated Break
                ↓
2. ENRICHMENT
   Validated Break → Data Enrichment Agent
                     ↓
                     [Fetch OMS, Trades, Settlement, Custodian, Ref Data]
                     ↓
                     Enriched Case
                     ↓
3. MATCHING
   Enriched Case → Matching Agent
                   ↓
                   [Find Candidates, Calculate Similarity, Correlate]
                   ↓
                   Match Candidates
                   ↓
4. RULES
   Break + Enriched Data → Rules Agent
                           ↓
                           [Check Tolerance, Apply Business Rules]
                           ↓
                           Rules Evaluation
                           ↓
5. PATTERN ANALYSIS
   Break + Rules → Pattern Agent
                   ↓
                   [Get Historical Patterns, Predict Root Cause]
                   ↓
                   ML Insights + Fix Suggestion
                   ↓
6. DECISION
   Break + Rules + ML Insights → Decisioning Agent
                                 ↓
                                 [Calculate Risk, Evaluate Decision]
                                 ↓
                                 Final Decision
                                 ↓
                         ┌───────┴───────┐
                         │               │
                   AUTO_RESOLVE    HIL_REVIEW    ESCALATE
                         │               │            │
7. WORKFLOW
   Decision → Workflow Agent
              ↓
              [Create Ticket, Log Audit, Capture Feedback]
              ↓
              Ticket Created
              ↓
        ┌─────┴─────┐
        │           │
   RESOLVED    PENDING_REVIEW
```

## A2A Protocol Message Flow

```
Agent A                    Message Bus                    Agent B
   │                            │                            │
   │  1. Create Request         │                            │
   ├──────────────────────────>│                            │
   │                            │  2. Route to Agent B       │
   │                            ├──────────────────────────>│
   │                            │                            │
   │                            │  3. Process Request        │
   │                            │<───────────────────────────┤
   │                            │                            │
   │  4. Receive Response       │                            │
   │<──────────────────────────┤                            │
   │                            │                            │

Message Structure:
{
  "message_id": "uuid",
  "conversation_id": "uuid",
  "message_type": "REQUEST | RESPONSE | NOTIFICATION | ERROR",
  "priority": "LOW | MEDIUM | HIGH | CRITICAL",
  "from_agent": "agent_name",
  "to_agent": "agent_name",
  "timestamp": "ISO-8601",
  "payload": {...},
  "metadata": {...}
}
```

## Agent Details

### Agent 1: Break Ingestion
**Purpose**: Entry point - normalizes and validates incoming breaks
**Tools**: 
- `get_breaks()` - Fetch from API
- `normalize_break()` - Standardize format
- `validate_break()` - Check completeness
**Output**: Validated break data

### Agent 2: Data Enrichment
**Purpose**: Gather contextual data from all sources
**Tools**:
- `get_oms_data()` - OMS orders
- `get_trade_capture()` - Trade details
- `get_settlement()` - Settlement positions
- `get_custodian_data()` - Custodian holdings
- `get_reference_data()` - Instrument info
- `get_broker_confirm()` - Broker confirmations
**Output**: Enriched case with all data

### Agent 3: Matching & Correlation
**Purpose**: Find and correlate potential matches
**Tools**:
- `find_match_candidates()` - Identify matches
- `calculate_similarity()` - Score similarity
- `correlate_trades()` - Find relationships
**Output**: Match candidates with scores

### Agent 4: Rules & Tolerance
**Purpose**: Apply business rules and tolerances
**Tools**:
- `check_tolerance()` - Verify within limits
- `apply_business_rules()` - Execute rules
- `validate_rules()` - Check critical rules
**Output**: Rules evaluation results

### Agent 5: Pattern Intelligence
**Purpose**: ML-based root cause analysis
**Tools**:
- `get_historical_patterns()` - Historical data
- `predict_root_cause()` - ML prediction
- `suggest_fix()` - Fix recommendation
**Output**: Root cause + fix suggestion

### Agent 6: Decisioning
**Purpose**: Final decision with risk assessment
**Tools**:
- `calculate_risk_score()` - Risk calculation
- `evaluate_decision()` - Decision logic
- `determine_action()` - Action mapping
**Output**: AUTO_RESOLVE | HIL_REVIEW | ESCALATE

### Agent 7: Workflow & Feedback
**Purpose**: Ticket management and learning
**Tools**:
- `create_ticket()` - Generate tickets
- `log_feedback()` - Capture human feedback
- `get_audit_trail()` - Audit history
- `add_audit_event()` - Log events
**Output**: Ticket + audit trail

## Decision Matrix

| Condition | Amount | Confidence | Risk | Tolerance | Action |
|-----------|--------|------------|------|-----------|--------|
| Low Risk  | <$10K  | >90%       | <0.3 | Within    | AUTO_RESOLVE |
| Medium    | $10K-$100K | 70-90% | 0.3-0.75 | Partial | HIL_REVIEW |
| High Risk | >$100K | <70%       | >0.75 | Outside  | ESCALATE |

## Technology Stack

- **Language**: Python 3.9+
- **AI Framework**: Google Gemini API (google-genai)
- **Agent Framework**: Google ADK (Agent Development Kit)
- **Protocol**: A2A (Agent-to-Agent) for communication
- **Tool Interface**: MCP (Model Context Protocol)
- **API Framework**: FastAPI
- **Schema Validation**: Pydantic v2
- **HTTP Client**: requests + httpx
- **Server**: Uvicorn (ASGI)

## Data Flow

```
External System → Mock API → MCP Tool → Agent → A2A Message → Next Agent
                                ↓
                         Pydantic Schema
                                ↓
                          Validation
                                ↓
                         Structured Data
```

## Extensibility Points

1. **Add New Agent**: Extend `BaseReconAgent`
2. **Add New Tool**: Create function + add to tool registry
3. **Add New Rule**: Update `rules_tools.py`
4. **Custom Decision Logic**: Modify `decision_tools.py`
5. **New Data Source**: Add API endpoint + MCP tool
6. **ML Model**: Replace `predict_root_cause()` implementation

## Security Considerations

- All A2A messages logged for audit
- Human approval required for high-risk/high-value
- Deterministic rules for compliance
- Immutable audit trail
- No direct database modifications by agents

## Scalability

- Stateless agents (can scale horizontally)
- Message bus can be replaced with Redis/Kafka
- Mock APIs can be replaced with real connectors
- Tools can call async APIs
- Batch processing supported

## Future Enhancements

1. Replace in-memory message bus with Redis/Kafka
2. Add persistent database (PostgreSQL)
3. Implement HIL UI (React/Streamlit)
4. Add real-time websockets for live updates
5. Integrate production data sources
6. Add authentication/authorization
7. Implement monitoring (Prometheus/Grafana)
8. Add distributed tracing (OpenTelemetry)
9. ML model training pipeline
10. Feedback learning loop
