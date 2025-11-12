# ADK Orchestrator UI Guide

## 🚀 Quick Start

### 1. Install Dependencies
```bash
# Core dependencies (already should be installed)
pip install streamlit

# Google ADK dependencies (when ready)
pip install google-adk a2a-python langgraph
```

### 2. Start Mock API (Required)
```bash
# In terminal 1
python main.py mock-api
```

### 3. Launch ADK UI
```bash
# In terminal 2
streamlit run frontend/streamlit_app_adk.py
```

### 4. Access UI
Open browser to: http://localhost:8501

---

## 📱 UI Features

### 🏠 Dashboard
- **Metrics Overview** - Total breaks processed, success rate, avg duration
- **Recent Executions** - Last 10 executions with details
- **Agent Status** - All 7 ADK agents with their status
- **Quick Stats** - Real-time performance metrics

**What you see:**
- Breaks processed count
- Success/failure ratio
- Average execution time
- Average agents used per execution
- All registered ADK agents

### 🤖 Process Break
- **Input Interface** - Enter break ID to process
- **Real-time Processing** - Watch ADK orchestrator work
- **Execution Results** - See full results immediately

**Features:**
- Process any break ID
- View LangGraph execution path
- See final decision (AUTO_RESOLVE/HIL_REVIEW/ESCALATE)
- Check A2A context and messages
- View any errors

**Example:**
1. Enter break ID: `BRK-001`
2. Click "🚀 Process with ADK"
3. See results in real-time

### 📨 A2A Messages
- **Message Viewer** - All A2A protocol messages
- **Context Threading** - See conversation flow
- **Message Details** - Full content and metadata

**What you see:**
- Message ID and type (REQUEST/RESPONSE/NOTIFICATION)
- From/To agent information
- Timestamps
- Message content (JSON)
- Context ID for threading
- Reply-to relationships

**Useful for:**
- Debugging agent communication
- Understanding message flow
- Verifying A2A protocol compliance
- Analyzing conversation threading

### 🔄 LangGraph Flow
- **Execution Path** - Visual execution sequence
- **Conditional Routing** - See which agents were skipped and why
- **Flow Diagram** - Clear visualization of the path
- **Performance** - Execution metrics

**Shows:**
- ✅ Agents that were executed
- ⊘ Agents that were skipped
- Conditional routing decisions:
  - Why matching was executed/skipped
  - Why pattern analysis was executed/skipped
  - Why workflow was executed/skipped
- Total duration and agent counts

**Example flow:**
```
INGESTION → ENRICHMENT → RULES → DECISION → WORKFLOW
(matching skipped: break type didn't require it)
(pattern skipped: high confidence from rules)
```

### 🛠️ Agent Tools
- **Tool Registry** - All tools for each agent
- **Tool Details** - Name, description, parameters
- **Usage Tracking** - Which tools were used

**For each agent:**
- Agent name and description
- Model being used (gemini-2.0-flash-exp)
- All available tools (🔧 badge for each)
- Whether agent was used in latest execution

**7 ADK Agents:**
1. **Break Ingestion** - get_breaks, normalize_break, validate_break
2. **Data Enrichment** - get_oms_data, get_trade_capture, enrich_case
3. **Matching** - calculate_similarity, find_match_candidates
4. **Rules** - check_tolerance, apply_business_rules
5. **Pattern** - get_historical_patterns, predict_root_cause
6. **Decision** - calculate_risk_score, determine_action
7. **Workflow** - create_ticket, log_feedback

### 🆚 ADK vs Custom
- **Side-by-Side Comparison** - Run both implementations
- **Performance Metrics** - Compare speed and efficiency
- **Decision Comparison** - Same or different decisions?
- **Architecture Comparison** - Visual architecture differences

**Features:**
1. Run both ADK and Custom v2 on same break
2. Compare results side-by-side
3. See performance differences
4. Compare agent usage
5. Check decision agreement
6. View architecture differences

**Metrics compared:**
- Execution duration (which is faster?)
- Number of agents used
- Execution path
- Final decision
- Success/failure status

### 📊 Performance
- **Overall Statistics** - Total processed, success rate
- **Performance Breakdown** - Duration, agents, messages
- **Common Paths** - Most frequent execution paths
- **Decision Distribution** - AUTO_RESOLVE vs HIL_REVIEW vs ESCALATE
- **Recent History** - Last 10 executions with details

**Analytics:**
- Average/min/max duration
- Average/min/max agents used
- Average/min/max A2A messages
- Most common execution paths (with percentages)
- Decision breakdown with percentages

---

## 🎨 UI Design

### Color Scheme
- **Blue** (`#4285f4`) - ADK/A2A elements
- **Green** (`#4caf50`) - Success/executed
- **Orange** (`#ff9800`) - Tools/warnings
- **Red** (`#ea4335`) - Errors/escalations
- **Gray** (`#f8f9fa`) - Skipped/disabled

### Badges
- 🤖 **ADK Badge** - Blue badge for ADK agents
- 🔧 **Tool Badge** - Orange badge for tools
- ✅ **Success** - Green checkmark for executed
- ⊘ **Skipped** - Gray for skipped agents

### Visual Elements
- **A2A Message Box** - Blue left border
- **Agent Node** - Green border with rounded corners
- **LangGraph Node** - Blue border for executed steps
- **Comparison Box** - Gray border for side-by-side

---

## 🔍 Use Cases

### 1. Testing ADK Implementation
```
1. Go to "Process Break"
2. Enter test break ID
3. Click process
4. Review execution path
5. Check A2A messages
```

### 2. Debugging Agent Flow
```
1. Go to "LangGraph Flow"
2. Select execution
3. See which agents ran
4. Check why agents were skipped
5. Review conditional routing decisions
```

### 3. Comparing Implementations
```
1. Go to "ADK vs Custom"
2. Enter break ID
3. Click "Run Both & Compare"
4. Review side-by-side results
5. Check performance differences
```

### 4. Monitoring Performance
```
1. Go to "Performance"
2. View overall statistics
3. Check average duration
4. See common execution paths
5. Review decision distribution
```

### 5. Analyzing A2A Protocol
```
1. Process a break
2. Go to "A2A Messages"
3. Select execution
4. Review all messages
5. Check context threading
```

---

## 🐛 Troubleshooting

### UI Won't Start
**Error:** `ADK Orchestrator Failed to Initialize`

**Solutions:**
1. Check mock API is running: `python main.py mock-api`
2. Install ADK SDKs: `pip install google-adk a2a-python langgraph`
3. Check Python version: `python --version` (need 3.8+)

### No Results Showing
**Issue:** Dashboard shows "No breaks processed yet"

**Solutions:**
1. Go to "Process Break" page
2. Enter a break ID (e.g., `BRK-001`)
3. Click "Process with ADK"
4. Return to Dashboard

### Comparison Not Working
**Issue:** v2 orchestrator not found

**Reason:** v2 orchestrator failed to initialize

**Solution:** This is okay - ADK will still work. Comparison just won't have v2 data.

### A2A Messages Empty
**Issue:** No A2A messages showing

**Reason:** Execution hasn't created A2A messages yet

**Solution:** Process a break first, then check A2A messages page

---

## 📚 Understanding the Output

### Execution Path
```
ingestion → enrichment → matching → rules → decision → workflow
```
- **ingestion** - Break normalized and validated
- **enrichment** - Data fetched from multiple sources
- **matching** - Candidates found and correlated
- **rules** - Tolerance and business rules checked
- **pattern** - ML analysis for root cause (optional)
- **decision** - Final decision made
- **workflow** - Ticket created (optional)

### Decision Actions
- **AUTO_RESOLVE** - System can resolve automatically
- **HIL_REVIEW** - Human-in-loop review needed
- **ESCALATE** - Escalation required

### A2A Message Types
- **REQUEST** - Agent requesting action from another agent
- **RESPONSE** - Agent responding to request
- **NOTIFICATION** - One-way notification
- **ERROR** - Error occurred during processing

---

## 🎯 Tips & Best Practices

### 1. Start Simple
- Process one break first
- Review all pages
- Understand the flow
- Then try comparisons

### 2. Use Filters
- Select specific executions in dropdowns
- Focus on one break at a time
- Use expanders to hide/show details

### 3. Monitor Performance
- Check "Performance" page regularly
- Look for patterns in execution paths
- Monitor success rates
- Identify slow executions

### 4. Compare Implementations
- Run same break ID in both
- Compare decisions
- Check performance differences
- Understand architecture differences

### 5. Debug with A2A Messages
- Always check A2A messages for errors
- Look at message flow
- Verify context threading
- Check timestamps

---

## 🚀 Advanced Features

### Session State
UI maintains session state for:
- All execution results
- Comparison results
- Orchestrator instances

**Refresh behavior:**
- Results persist across page changes
- Comparison cached until new comparison
- Metrics recalculated on dashboard

### Real-time Updates
- Process status updates live
- Metrics update after each execution
- Charts refresh automatically

### Data Export
Want to export results?
- View Full Result expanders show JSON
- Copy/paste JSON for analysis
- Use browser dev tools to access session state

---

## 📞 Support

### Questions?
1. Check this guide first
2. Review ADK documentation: `orchestrator_adk/README.md`
3. Check implementation docs: `orchestrator_adk/IMPLEMENTATION_COMPLETE.md`

### Issues?
1. Check mock API is running
2. Verify SDKs installed
3. Review error messages in UI
4. Check terminal for stack traces

---

**Happy Testing! 🎉**

The ADK Orchestrator UI provides complete visibility into your Google ADK implementation with A2A Protocol and LangGraph orchestration.
