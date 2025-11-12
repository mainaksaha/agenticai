# How to Run the UI

## Two Versions Available

### Version 1 (v1) - Sequential Orchestrator
**Original implementation with all 7 agents running sequentially**

### Version 2 (v2) - Dynamic Orchestrator  
**New implementation with parallel execution, early exit, and policy-driven routing**

---

## Option 1: Run Both UIs Simultaneously

### Terminal 1 - Mock API Server
```bash
cd C:\Work\reconagent
python main.py mock-api
```
**Keep this running!**

### Terminal 2 - v1 UI (Port 8501)
```bash
cd C:\Work\reconagent
streamlit run frontend/streamlit_app.py
```
**Access at:** http://localhost:8501

### Terminal 3 - v2 UI (Port 8502)
```bash
cd C:\Work\reconagent
streamlit run frontend/streamlit_app_v2.py --server.port 8502
```
**Access at:** http://localhost:8502

---

## Option 2: Run Just v1 (Original)

### Terminal 1 - Mock API
```bash
python main.py mock-api
```

### Terminal 2 - v1 UI
```bash
streamlit run frontend/streamlit_app.py
```
**Access at:** http://localhost:8501

---

## Option 3: Run Just v2 (Dynamic)

### Terminal 1 - Mock API
```bash
python main.py mock-api
```

### Terminal 2 - v2 UI
```bash
streamlit run frontend/streamlit_app_v2.py
```
**Access at:** http://localhost:8501

---

## UI Features Comparison

### v1 UI Features
- ✅ Dashboard with metrics
- ✅ Review queue for HIL cases
- ✅ Case detail with 5 tabs
- ✅ Data comparison view
- ✅ Agent analysis
- ✅ Risk assessment
- ✅ Action buttons (Approve/Override/Escalate)
- ✅ Analytics

### v2 UI Features (NEW!)
- ✅ Dashboard with v2 metrics
- ✅ Single break analysis with execution graph
- ✅ Batch processing with efficiency stats
- ✅ **v1 vs v2 performance comparison** ⭐
- ✅ **Execution graph visualization** ⭐
- ✅ **Policy viewer** ⭐
- ✅ Efficiency metrics
- ✅ Early exit tracking
- ✅ Agent invocation tracking

---

## v2 UI Pages

### 1. 🏠 Dashboard
- Overview of processed breaks
- Efficiency metrics
- Early exit statistics
- Recent results

### 2. 🔬 Single Break Analysis
- Process individual breaks
- View execution graph
- See which agents ran/skipped
- Detailed timing per agent
- Break profile classification

### 3. 📊 Batch Processing
- Process multiple breaks
- Aggregate statistics
- Decision distribution
- Risk tier distribution
- Overall efficiency

### 4. ⚖️ v1 vs v2 Comparison
- **Side-by-side comparison** ⭐
- Performance metrics
- Time savings
- Agent efficiency
- Visual charts

### 5. 📖 Policy Viewer
- View routing policies
- See which agents run per break type
- Understand decision checkpoints
- Explore parallel execution groups

---

## Quick Start Guide

### For First Time Users:

1. **Start Mock API:**
   ```bash
   python main.py mock-api
   ```

2. **Start v2 UI:**
   ```bash
   streamlit run frontend/streamlit_app_v2.py
   ```

3. **Open browser:** http://localhost:8501

4. **Try it out:**
   - Go to "Single Break Analysis"
   - Click "Process Break"
   - Watch the execution graph
   - See efficiency metrics

5. **Compare v1 vs v2:**
   - Go to "v1 vs v2 Comparison"
   - Click "Run Comparison"
   - See performance difference!

---

## Troubleshooting

### Issue: Port already in use

**Solution:** Specify different port
```bash
streamlit run frontend/streamlit_app_v2.py --server.port 8503
```

### Issue: Mock API not running

**Solution:** Start mock API first
```bash
python main.py mock-api
```

### Issue: Import errors

**Solution:** Make sure you're in project root
```bash
cd C:\Work\reconagent
```

---

## Screenshots Expected

### v2 Dashboard
- Metrics: Breaks Processed, Avg Efficiency, Avg Time, Early Exits
- Recent breaks list
- Quick stats

### Execution Graph
```
✅ BREAK_INGESTION (150ms)
✅ DATA_ENRICHMENT (300ms)
✅ RULES_TOLERANCE (200ms)
⊘ MATCHING_CORRELATION (Skipped: Early decision reached)
⊘ PATTERN_INTELLIGENCE (Skipped: Early decision reached)
⊘ DECISIONING (Skipped: Early decision reached)
⊘ WORKFLOW_FEEDBACK (Skipped: Early decision reached)

🚪 Early Exit: Decision checkpoint met
```

### v1 vs v2 Comparison
```
⏱️ Time Comparison
━━━━━━━━━━━━━━━━━━
v1: 2500ms
v2: 800ms
Improvement: 68% faster

🤖 Agent Invocation
━━━━━━━━━━━━━━━━━━
v1: 7 agents (all)
v2: 3 agents (43% efficiency)

🏆 Winner: v2 is 68% faster with 4 fewer agents!
```

---

## Recommended Workflow

### For Testing v2:
1. Start with "Single Break Analysis"
2. Process a few breaks
3. Check "Batch Processing" for aggregate stats
4. Use "v1 vs v2 Comparison" to see improvements
5. Review "Policy Viewer" to understand routing

### For Production Use:
- Use v1 UI for **human review** of pending cases
- Use v2 UI for **performance monitoring** and analysis
- Compare both to validate v2 results

---

## Performance Tips

- v2 processes breaks 30-70% faster
- Use batch processing for multiple breaks
- Early exits save 40-60% of processing time
- Check execution graphs to optimize policies

---

## Next Steps

1. **Test v2 UI** with sample breaks
2. **Compare with v1** to see improvements
3. **Customize policies** in `orchestrator/v2/policies/routing_policies.yaml`
4. **Monitor efficiency** metrics over time

---

**Enjoy the new Dynamic Orchestrator v2 UI! ⚡**
