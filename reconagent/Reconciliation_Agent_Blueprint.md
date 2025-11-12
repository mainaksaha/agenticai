# Reconciliation Agent Blueprint

## 1️⃣ Goals & Constraints

**Primary Goals**
- Reduce manual effort on reconciliation break investigation and classification.
- Auto-resolve “safe” breaks under transparent rules.
- Provide explainable decisions that mimic human reconcilers.

**Constraints**
- Must be fully auditable (inputs + rules + rationale).
- Deterministic for tolerance-based logic, probabilistic for pattern detection.
- Human-in-the-loop (HIL) required for high-impact or regulatory cases.

---

## 2️⃣ Core Architecture

### Agents

1. **Break Ingestion Agent**
   - Normalizes incoming reconciliation breaks.
   - Schema: `BreakID, Type, SystemA, SystemB, Instrument, Qty, Amount, Date, Party, Source, RawFields...`

2. **Data Enrichment Agent**
   - Gathers details from OMS, trade capture, settlement, custodian, reference data, etc.
   - Builds a unified case context.

3. **Matching & Correlation Agent**
   - Identifies candidate matches (partial fills, aggregated trades, cross-system ID mapping).

4. **Rules & Tolerance Agent**
   - Applies business rules: rounding, FX, known lags, standard ranges.
   - Outputs tolerance check results and break categorization.

5. **Pattern & Root-Cause Intelligence Agent**
   - Learns from history to infer probable causes and suggest fixes.

6. **Decisioning Agent**
   - Combines rule outcomes, ML/LLM insights, and firm policies.
   - Decides: Auto-Resolve | Recommend (HIL) | Escalate.

7. **Workflow & Feedback Agent**
   - Integrates with ticketing systems and captures final decisions.
   - Feeds learning back to improve logic and prompts.

---

## 3️⃣ End-to-End Flow

```text
Incoming Break 
  -> Break Ingestion Agent 
  -> Data Enrichment Agent 
  -> Matching & Correlation Agent
  -> Rules & Tolerance Agent
  -> Pattern & Root-Cause Agent
  -> Decisioning Agent
  -> (Auto-Resolve | HIL Review | Escalate)
  -> Workflow & Feedback Agent
```

---

## 4️⃣ Reconciliation Use Case Mapping

| Use Case | Key Inputs | Break Causes | Agent Logic | Action |
|-----------|-------------|--------------|--------------|--------|
| **1. Trade vs OMS** | OMS orders, trade capture | Price/Qty mismatch | Matching + Rules | Auto if within tolerance |
| **2. Broker vs Internal** | Broker confirms, trade book | Fee, price diff | Enrich + Pattern | Auto or Escalate |
| **3. FO vs BO** | Blotter, settlement | Status mismatch | Rules | Timing lag or Escalate |
| **4. Internal vs Custodian** | Holdings | Corp action, FX diff | Enrich + Rules | Auto / Escalate |
| **5. Cash Reconciliation** | Ledgers, bank stmts | Timing / FX lag | Rules + Pattern | Auto / Review |
| **6. PnL Reconciliation** | FO vs Finance PnL | Pricing source diff | Enrich + Pattern | Recommend correction |
| **7. Lifecycle Events** | Event schedules | Missing/duplicate event | Enrich + Rules | Recommend / Escalate |
| **8. Regulatory Data** | Internal vs Regulatory | LEI/ISIN mismatch | Rules + Pattern | Escalate |

---

## 5️⃣ Case Schema Example

```json
{
  "break_id": "BRK-2025-11-00123",
  "break_type": "TRADE_OMS_MISMATCH",
  "entities": {
    "instrument": "AAPL",
    "account": "12345",
    "broker": "XYZ",
    "trade_ids": ["T123"],
    "order_ids": ["O999"]
  },
  "rules_evaluation": {
    "within_tolerance": true,
    "violated_rules": []
  },
  "ml_insights": {
    "probable_root_cause": "timing_lag",
    "confidence": 0.91
  },
  "decision": {
    "action": "AUTO_RESOLVE",
    "labels": ["TimingLag", "NoFinancialImpact"],
    "explanation": "Broker confirm received T+1; amounts match within 0.5 bps tolerance."
  }
}
```

---

## 6️⃣ Control Levers & UX Design

**Configurable Controls**
- Tolerances per asset/desk.
- Auto-resolve policies by exposure threshold.
- Escalation matrix by product type.
- Model guardrails: LLMs only assist, not execute.

**Human Interface**
- Display raw vs enriched data.
- Show agent recommendations & rationale.
- Enable one-click Apply / Override / Escalate.
- Log every action for audit & retraining.

---

## 7️⃣ Implementation Notes

- Represent as LangGraph / DAG for orchestration.
- Each agent logs intermediate results to a case DB.
- Use LLMs only for explanation generation and classification (not book adjustments).
- Measure: precision, coverage, resolution time improvement.

---

© 2025 Reconciliation Agent Blueprint — Draft v1.0
