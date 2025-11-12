# Reconciliation Agent Blueprint — Dynamic Orchestration Version (v2.0)

This version models a **non-linear, policy-driven orchestration**: agents are **not forced to run sequentially**. 
The Orchestrator decides, per break, **which subset of agents to invoke, in what order, and in parallel where possible**.

---

## 1️⃣ Design Principles

1. **Dynamic Routing**  
   - For each break, decide which agents are required based on:
     - Break type
     - Source systems
     - Product / asset class
     - Materiality (amount at risk)
     - Historical patterns

2. **Parallelism by Default**  
   - Independent checks (e.g., data enrichment from multiple systems, FX/tolerance checks, lifecycle checks) run **in parallel** to reduce latency.

3. **Selective Invocation**  
   - No “all agents every time”.  
   - Only the **minimal set of agents** are invoked to reach a confident, policy-compliant decision.

4. **Policy- & Risk-Aware**  
   - Orchestrator behavior is driven by **configurable policies** (YAML/DB):
     - Routing rules
     - Escalation rules
     - Which agents are mandatory for which break types.

5. **Auditable Graph Execution**  
   - Every run produces an **execution graph**: nodes (agents), edges (data deps), decisions, and skipped branches.

---

## 2️⃣ Key Components

### 2.1 Orchestrator

A central **Decision & Routing Engine** that:

- Classifies incoming break into a **Break Profile**:
  ```json
  {
    "break_id": "BRK-2025-11-01001",
    "type": "TRADE_OMS_MISMATCH",
    "asset_class": "EQUITY",
    "exposure": 1500.00,
    "source_systems": ["OMS", "TRADING", "CONFIRMATION"],
    "risk_tier": "LOW"
  }
  ```
- Looks up **Routing Policy** for that profile.
- Builds an **execution plan**: which agents, in which structure (parallel/series), with dependencies.

Example policy snippet (pseudo-YAML):

```yaml
routes:
  TRADE_OMS_MISMATCH:
    low_risk:
      parallel:
        - DATA_ENRICHMENT
        - MATCHING
      next:
        - RULES_TOLERANCE
      decision_from:
        - RULES_TOLERANCE
    high_risk:
      parallel:
        - DATA_ENRICHMENT
        - MATCHING
        - PATTERN_ROOT_CAUSE
      next:
        - RULES_TOLERANCE
        - COMPLIANCE_SCREEN
      decision_from:
        - DECISIONING
```

### 2.2 Agent Catalog (Same functional roles as v1)

- **DATA_ENRICHMENT**
- **MATCHING_CORRELATION**
- **RULES_TOLERANCE**
- **PATTERN_ROOT_CAUSE**
- **DECISIONING**
- **WORKFLOW_FEEDBACK**
- (Optional domain-specific: **PNL_ANALYZER**, **LIFECYCLE_CHECKER**, **REG_REPORT_CHECKER**, etc.)

Each agent:
- Has a clear **contract**: input schema, output schema, preconditions.
- Is **stateless** in execution; state is persisted in the Case Store.

---

## 3️⃣ Execution Model (Dynamic Graph)

Instead of a fixed pipeline, treat orchestration as a **conditional DAG**.

### 3.1 High-Level Flow

```text
[Incoming Break]
   -> Orchestrator classifies & reads policy
   -> Orchestrator builds execution graph (nodes=agents)
   -> Execute independent nodes in parallel
   -> Gather outputs, evaluate policies
   -> If sufficient confidence & rules satisfied -> Decision
   -> Else -> Extend graph (invoke more agents) -> Re-evaluate
   -> Emit final decision + execution graph for audit
```

### 3.2 Example: Minimal Path for Simple Break

Break: Small **cash FX rounding** mismatch, low risk.

Plan:
- Orchestrator only invokes:
  - DATA_ENRICHMENT (bank stmt + internal)
  - RULES_TOLERANCE
- If within configured rounding rule → DECISIONING → AUTO_RESOLVE.
- No PATTERN_ROOT_CAUSE, no MATCHING_CORRELATION, no escalation.

### 3.3 Example: Expanded Path for Complex Break

Break: Large PnL discrepancy on exotic derivative, high exposure.

Plan:
- Parallel:
  - DATA_ENRICHMENT (all systems)
  - MATCHING_CORRELATION
  - PNL_ANALYZER
  - LIFECYCLE_CHECKER
- Once complete:
  - RULES_TOLERANCE (on exposures, pricing, lifecycle)
  - PATTERN_ROOT_CAUSE (historical similar breaks)
- If confidence < threshold or rules violated:
  - Invoke DECISIONING for recommendation + required escalation.
- Result:
  - Escalate + pre-filled explanation.

---

## 4️⃣ Use Case Matrix (Selective & Parallel Agent Invocation)

| Use Case | Orchestrator Behavior | Parallel Agents | Conditional Agents |
|---------|------------------------|-----------------|--------------------|
| Trade vs OMS | Route by risk + asset | Enrichment + Matching | Rules, then Pattern if mismatch persists |
| Broker vs Internal | Based on broker, product | Enrichment + Matching | Pattern for repeated broker issues |
| FO vs BO | By system + status | Enrichment + Matching | Rules; LifecycleChecker for complex products |
| Internal vs Custodian | By asset/corp action | Enrichment + LifecycleChecker | Pattern if same CSD issues recur |
| Cash / Nostro | By currency, size | Enrichment(bank+ledger) | Rules; Pattern for timing norms |
| PnL Reconciliation | By product/exposure | Enrichment + PNL_Analyzer | Pattern + Decisioning for root-cause |
| Lifecycle Events | By event type | Enrichment + LifecycleChecker | Rules; escalate if structural gap |
| Regulatory Data | By regime (MiFID/CAT/etc.) | Enrichment + Reg_Report_Checker | Pattern + Compliance flags |

---

## 5️⃣ Case & Execution Graph Schema

### 5.1 Case Record (Core State)

```json
{
  "break_id": "BRK-2025-11-01001",
  "profile": { "type": "CASH_BREAK", "risk_tier": "LOW" },
  "inputs": {...},
  "artifacts": {
    "DATA_ENRICHMENT": {...},
    "RULES_TOLERANCE": {...}
  },
  "decision": {
    "action": "AUTO_RESOLVE",
    "reason": "Within FX rounding tolerance per policy CASH_LOW_01",
    "confidence": 0.99
  }
}
```

### 5.2 Execution Graph Metadata

```json
{
  "break_id": "BRK-2025-11-01001",
  "nodes": [
    {"id": "N1", "agent": "DATA_ENRICHMENT", "status": "COMPLETED"},
    {"id": "N2", "agent": "RULES_TOLERANCE", "status": "COMPLETED", "depends_on": ["N1"]}
  ],
  "skipped_nodes": [
    "PATTERN_ROOT_CAUSE",
    "MATCHING_CORRELATION"
  ],
  "created_at": "2025-11-09T01:23:45Z",
  "orchestrator_policy_version": "2.0.0"
}
```

This makes the **how** of each decision fully reconstructable.

---

## 6️⃣ Policy & Configuration Examples

1. **Selective Invocation by Exposure**
   - If exposure `< $5,000` and break-type in `[ROUNDING, TIMING]`:
     - Only run: ENRICHMENT + RULES_TOLERANCE.
2. **Expanded Checks for High Risk**
   - If exposure `> $100,000` or product in `[DERIVATIVES, STRUCTURED]`:
     - Run: ENRICHMENT + MATCHING + RULES + PATTERN + PNL_ANALYZER in a DAG.
3. **Regime-Specific**
   - If trade is reportable under MiFID/CAT:
     - Always invoke: REG_REPORT_CHECKER before auto-resolve.

All policies are externalized so business/ops can adjust without code changes.

---

## 7️⃣ Implementation Notes

- Implement the Orchestrator using:
  - Workflow engine / LangGraph / Temporal / Step Functions / Airflow-like DAG runner.
- Agents as:
  - Microservices or functions with strict IO contracts.
- LLM Usage:
  - Assist in classification, explanation, anomaly narratives.
  - Never directly update books/records.
- KPIs:
  - % of breaks resolved with minimal agents.
  - Latency reduction via parallelism.
  - False auto-resolve rate vs human benchmark.

---

© 2025 Reconciliation Agent Blueprint — Dynamic Orchestration Version (v2.0)
