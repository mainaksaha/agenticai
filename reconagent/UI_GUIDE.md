# Streamlit UI Guide - Human-in-the-Loop Interface

## 🎯 Overview

The Streamlit UI provides a web-based interface for humans to review reconciliation breaks that agents cannot automatically resolve. It includes:

- **Dashboard** - Overview of all cases with metrics
- **Review Queue** - Detailed review interface for HIL cases
- **Analytics** - Statistics and feedback insights
- **Settings** - System configuration viewer

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd C:\Work\reconagent
pip install -r requirements.txt
```

This will install Streamlit and all other dependencies.

### 2. Start Mock API Server (Terminal 1)

```bash
python main.py mock-api
```

Keep this running in the background.

### 3. Start Streamlit UI (Terminal 2)

```bash
streamlit run frontend/streamlit_app.py
```

The UI will automatically open in your browser at: **http://localhost:8501**

---

## 📱 UI Features

### 📊 Dashboard

**Purpose**: High-level overview of all processed cases

**Features**:
- Total cases processed
- Auto-resolved count and percentage
- Pending HIL review count
- Escalated cases count
- Recent cases table with key details

**How to Use**:
1. Use sidebar to process new breaks
2. View summary metrics at top
3. Browse recent cases in the table
4. Click on different pages in sidebar

### 📝 Review Queue

**Purpose**: Detailed interface for reviewing cases that require human decision

**Features**:

#### Tab 1: Overview
- Break ID, type, instrument, account
- Agent recommendation summary
- Risk score and confidence
- Explanation of agent decision

#### Tab 2: Data Comparison
- Side-by-side comparison of System A vs System B
- Quantity, amount, price differences
- Visual metrics showing discrepancies

#### Tab 3: Agent Analysis
- Complete 7-stage pipeline details
- Break ingestion validation
- Data enrichment sources
- Match candidates found
- Rules evaluation results
- Pattern analysis and root cause
- Decision reasoning

#### Tab 4: Risk Assessment
- Visual risk gauge (Low/Medium/High)
- Risk score breakdown
- List of risk factors identified
- Color-coded alerts

#### Tab 5: Take Action
Three action buttons:

**✅ Approve & Resolve**
- Agrees with agent recommendation
- Resolves the break
- Logs feedback for learning
- Removes from review queue

**🔄 Override Decision**
- Allows changing agent decision
- Requires explanation notes
- Options: AUTO_RESOLVE, ESCALATE, REJECTED
- Logs override with reasoning

**🚨 Escalate to Senior**
- Sends to senior team
- Logs escalation reason
- Removes from your queue

### 📈 Analytics

**Purpose**: System performance and feedback metrics

**Features**:
- Total cases processed
- Auto-resolve rate
- Average risk score
- Feedback statistics
- Agent-human agreement rate
- Break type distribution chart
- Decision distribution breakdown

### ⚙️ Settings

**Purpose**: View and understand system configuration

**Features**:
- Tolerance settings (amount, quantity, FX)
- Auto-resolve thresholds
- Escalation thresholds
- System information
- Clear all data button (for testing)

---

## 🔄 Typical Workflow

### For Reviewers

1. **Start with Dashboard**
   - Check how many cases need review
   - View recent activity

2. **Go to Review Queue**
   - See list of pending HIL cases
   - Select a case to review

3. **Review Case Details**
   - Check Overview for basic info
   - Compare data in Data Comparison tab
   - Review all 7 agent stages in Agent Analysis
   - Assess risk in Risk Assessment tab

4. **Make Decision**
   - Go to Take Action tab
   - Choose: Approve, Override, or Escalate
   - Add notes if overriding
   - Submit decision

5. **Check Analytics**
   - Monitor your agreement rate with agents
   - Track overall system performance

### For Testing

1. **Process Breaks**
   - Use sidebar to process 5-10 breaks
   - Wait for processing to complete

2. **View Results**
   - Check dashboard for distribution
   - Auto-resolved cases won't appear in review queue
   - Only HIL_REVIEW cases need human action

3. **Review Cases**
   - Test approve, override, and escalate actions
   - Verify feedback is logged

4. **Check Analytics**
   - Verify feedback statistics update
   - Check agreement rates

---

## 🎨 UI Components Explained

### Status Badges

- **🟢 AUTO_RESOLVE** - Green badge, low risk, auto-resolved
- **🟡 HIL_REVIEW** - Yellow badge, needs human review
- **🔴 ESCALATE** - Red badge, high risk, escalated

### Risk Gauge

- **🟢 Low Risk (0.0 - 0.3)** - Safe to approve
- **🟡 Medium Risk (0.3 - 0.75)** - Review carefully
- **🔴 High Risk (0.75 - 1.0)** - Consider escalation

### Metrics

- **Green Delta** - Positive indicator
- **Red Delta** - Needs attention
- **Numbers** - Absolute values

---

## 💡 Tips & Best Practices

### For Efficient Review

1. **Start with Overview Tab**
   - Get quick context before diving deep
   - Check agent explanation first

2. **Trust High Confidence**
   - Agent decisions with >90% confidence are usually correct
   - Focus review time on lower confidence cases

3. **Check Data Comparison**
   - Verify the actual differences
   - Understand magnitude of discrepancy

4. **Review Agent Pipeline**
   - See what data was enriched
   - Check which rules passed/failed
   - Understand root cause prediction

5. **Consider Risk Score**
   - Low risk (<0.3) - Usually safe to approve
   - High risk (>0.75) - Consider escalation

### For Learning

1. **Add Detailed Notes When Overriding**
   - Helps improve agent learning
   - Documents decision rationale

2. **Track Agreement Rate**
   - High agreement = agents learning well
   - Low agreement = may need tuning

3. **Review Analytics Regularly**
   - Identify patterns in escalations
   - Monitor auto-resolve rate

---

## 🔧 Troubleshooting

### UI Won't Start

**Error**: Module not found
**Solution**: 
```bash
pip install -r requirements.txt
```

### No Cases in Review Queue

**Cause**: No HIL cases processed yet
**Solution**: 
1. Process more breaks using sidebar
2. Most breaks might be auto-resolved (check dashboard)
3. Try processing 10-20 breaks to get HIL cases

### Changes Not Reflecting

**Solution**: 
- Streamlit auto-reloads, but you can click "Rerun" in top-right
- Or press 'R' key to force refresh

### Mock API Not Running

**Error**: Connection refused
**Solution**:
```bash
# Terminal 1
python main.py mock-api
```

---

## 📊 Understanding the Data

### Break Types

- **TRADE_OMS_MISMATCH** - Trading system vs OMS
- **BROKER_VS_INTERNAL** - External broker vs internal
- **FO_VS_BO** - Front office vs back office
- **CUSTODIAN_MISMATCH** - Custodian holdings mismatch
- **CASH_RECONCILIATION** - Cash position differences
- **PNL_RECONCILIATION** - P&L differences
- **LIFECYCLE_EVENT** - Corporate actions, dividends
- **REGULATORY_DATA** - Regulatory reporting mismatches

### Decision Actions

- **AUTO_RESOLVE** - Agent resolved automatically
- **HIL_REVIEW** - Needs human review (YOU!)
- **ESCALATE** - Sent to senior team
- **REJECTED** - Marked as false positive

### Agent Stages

1. **Break Ingestion** - Validates and normalizes
2. **Data Enrichment** - Gathers from 6+ sources
3. **Matching** - Finds similar records
4. **Rules** - Checks business rules
5. **Pattern** - Predicts root cause
6. **Decision** - Makes recommendation
7. **Workflow** - Creates tickets

---

## 🎓 Example Review Session

### Scenario: $5,000 Trade Mismatch

1. **Overview Tab Shows**:
   - Break Type: TRADE_OMS_MISMATCH
   - Instrument: AAPL
   - Agent Recommendation: HIL_REVIEW
   - Confidence: 75%
   - Risk Score: 0.45

2. **Data Comparison Shows**:
   - System A: $150,000 (1000 shares @ $150)
   - System B: $155,000 (1000 shares @ $155)
   - Difference: $5,000 (price difference)

3. **Agent Analysis Shows**:
   - Enrichment: Found broker confirm
   - Rules: Failed amount tolerance (10 bps vs 0.5 bps limit)
   - Pattern: Probable cause = "timing_lag" (75% confidence)
   - Decision: HIL_REVIEW due to tolerance failure

4. **Risk Assessment Shows**:
   - Medium Risk (0.45)
   - Factor: "Failed 1 business rule"
   - Amount within auto-resolve limit

5. **Your Decision**:
   - Review broker confirm in enriched data
   - If broker shows $155, approve System B
   - If broker shows $150, escalate for investigation
   - Add notes explaining reasoning

---

## 🚀 Advanced Features

### Batch Operations (Future Enhancement)

Currently reviews one case at a time. Could add:
- Multi-select for bulk approve
- Filter by break type
- Search by instrument/account

### Real-time Updates (Future Enhancement)

Could add WebSocket for live updates when new HIL cases arrive.

### Custom Rules (Future Enhancement)

Could allow setting custom tolerances per instrument or desk.

---

## 📞 Support

For issues:
1. Check QUICKSTART.md for setup
2. Check README.md for system overview
3. Check ARCHITECTURE.md for technical details
4. Verify mock API is running
5. Check console for error messages

---

## ✨ Summary

The Streamlit UI provides a complete Human-in-the-Loop interface for:
- ✅ Reviewing agent decisions
- ✅ Approving, overriding, or escalating cases
- ✅ Viewing complete agent analysis
- ✅ Tracking system performance
- ✅ Logging feedback for learning

**Start the UI**: `streamlit run frontend/streamlit_app.py`

Enjoy reviewing reconciliation breaks! 🎉
