# Dynamic Orchestration Design (v2)

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     INCOMING BREAK                               │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│               BREAK CLASSIFIER                                   │
│   Analyzes: type, amount, asset class, risk tier               │
│   Output: Break Profile                                         │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│              POLICY ENGINE                                       │
│   Looks up routing policy for break profile                    │
│   Output: Execution Plan (DAG)                                  │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│           DYNAMIC DAG EXECUTOR                                   │
│   - Executes nodes in parallel where possible                  │
│   - Respects dependencies                                       │
│   - Can early-exit on decision                                  │
│   - Can expand graph if needed                                  │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│              DECISION EVALUATOR                                  │
│   - Can decide at any point if confidence is sufficient        │
│   - Triggers more agents if needed                             │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                 FINAL DECISION                                   │
│   AUTO_RESOLVE / HIL_REVIEW / ESCALATE                          │
└─────────────────────────────────────────────────────────────────┘
```

---

## Component Design

### 1. Break Classifier

**Purpose**: Analyze incoming break and create a profile

**Input**: Raw break data
**Output**: Break profile

```python
class BreakProfile:
    break_id: str
    break_type: str  # TRADE_OMS_MISMATCH, CASH_BREAK, etc.
    asset_class: str  # EQUITY, FX, FIXED_INCOME, DERIVATIVE
    exposure: float
    risk_tier: str  # LOW, MEDIUM, HIGH, CRITICAL
    source_systems: List[str]
    materiality: str  # LOW, MEDIUM, HIGH
    urgency: str  # NORMAL, HIGH, CRITICAL
    requires_enrichment: bool
    requires_matching: bool
    requires_pattern_analysis: bool
```

**Logic**:
```python
def classify_break(break_data: Dict) -> BreakProfile:
    # Amount-based risk
    amount = abs(break_data.get('amount_diff', 0))
    if amount < 5000:
        risk_tier = "LOW"
    elif amount < 100000:
        risk_tier = "MEDIUM"
    else:
        risk_tier = "HIGH"
    
    # Type-based routing
    break_type = break_data.get('break_type')
    
    # Determine required agents
    requires_enrichment = True  # Almost always
    requires_matching = break_type in ['TRADE_OMS_MISMATCH', 'BROKER_VS_INTERNAL']
    requires_pattern = risk_tier in ['MEDIUM', 'HIGH']
    
    return BreakProfile(...)
```

---

### 2. Policy Engine

**Purpose**: Given a break profile, determine which agents to run and in what order

**Input**: Break profile
**Output**: Execution plan (DAG)

```python
class AgentNode:
    agent_id: str
    agent_name: str
    depends_on: List[str]  # List of node IDs
    can_run_parallel: bool
    is_mandatory: bool
    skip_conditions: List[str]

class ExecutionPlan:
    plan_id: str
    break_profile: BreakProfile
    nodes: List[AgentNode]
    decision_checkpoints: List[str]  # After which nodes to check if we can decide
    max_parallel: int  # Max concurrent agents
    early_exit_enabled: bool
```

**Policy Definition** (YAML):
```yaml
policies:
  TRADE_OMS_MISMATCH:
    LOW_RISK:
      mandatory_agents:
        - BREAK_INGESTION
        - DATA_ENRICHMENT
        - RULES_TOLERANCE
      optional_agents:
        - MATCHING_CORRELATION  # Only if initial rules fail
        - PATTERN_INTELLIGENCE  # Only if repeated issue
      parallel_groups:
        - [DATA_ENRICHMENT]
        - [MATCHING_CORRELATION, RULES_TOLERANCE]
      decision_checkpoints:
        - after: RULES_TOLERANCE
          condition: "within_tolerance and confidence > 0.9"
          action: "AUTO_RESOLVE"
    
    HIGH_RISK:
      mandatory_agents:
        - BREAK_INGESTION
        - DATA_ENRICHMENT
        - MATCHING_CORRELATION
        - RULES_TOLERANCE
        - PATTERN_INTELLIGENCE
        - DECISIONING
      parallel_groups:
        - [DATA_ENRICHMENT]
        - [MATCHING_CORRELATION, RULES_TOLERANCE, PATTERN_INTELLIGENCE]
        - [DECISIONING]
      decision_checkpoints:
        - after: DECISIONING
          condition: "always"
          action: "FOLLOW_DECISION"
```

---

### 3. Dynamic DAG Executor

**Purpose**: Execute agents according to the plan, with parallel execution and early exit

```python
class DynamicDAGExecutor:
    def __init__(self, execution_plan: ExecutionPlan, agents: Dict[str, BaseReconAgent]):
        self.plan = execution_plan
        self.agents = agents
        self.results = {}
        self.execution_graph = []
    
    async def execute(self, break_data: Dict) -> Dict[str, Any]:
        """
        Execute the DAG plan with parallelism and early exit
        """
        # Track completed nodes
        completed = set()
        
        # While there are uncompleted nodes
        while len(completed) < len(self.plan.nodes):
            # Find nodes ready to execute (dependencies met)
            ready_nodes = self._get_ready_nodes(completed)
            
            if not ready_nodes:
                break
            
            # Execute ready nodes in parallel
            results = await self._execute_parallel(ready_nodes, break_data)
            
            # Update results
            for node_id, result in results.items():
                self.results[node_id] = result
                completed.add(node_id)
                self.execution_graph.append({
                    "node_id": node_id,
                    "status": "COMPLETED",
                    "timestamp": datetime.now()
                })
            
            # Check if we can make decision early
            if self._can_decide_early(completed):
                decision = self._make_decision()
                if decision:
                    # Early exit - skip remaining agents
                    skipped = set(self.plan.nodes) - completed
                    for node in skipped:
                        self.execution_graph.append({
                            "node_id": node.agent_id,
                            "status": "SKIPPED",
                            "reason": "Early decision reached"
                        })
                    break
        
        return {
            "results": self.results,
            "execution_graph": self.execution_graph,
            "decision": self._make_final_decision()
        }
    
    def _get_ready_nodes(self, completed: Set[str]) -> List[AgentNode]:
        """Get nodes whose dependencies are all completed"""
        ready = []
        for node in self.plan.nodes:
            if node.agent_id in completed:
                continue
            # Check if all dependencies are met
            deps_met = all(dep in completed for dep in node.depends_on)
            if deps_met:
                ready.append(node)
        return ready
    
    async def _execute_parallel(self, nodes: List[AgentNode], break_data: Dict) -> Dict[str, Any]:
        """Execute multiple nodes in parallel using asyncio"""
        tasks = []
        for node in nodes:
            agent = self.agents[node.agent_name]
            task = self._execute_agent(agent, node, break_data)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        return {node.agent_id: result for node, result in zip(nodes, results)}
```

---

### 4. Routing Policy Examples

#### Example 1: Small Cash Break (Minimal Path)
```yaml
profile:
  type: CASH_RECONCILIATION
  risk_tier: LOW
  exposure: 1200

routing:
  agents:
    - id: N1
      name: BREAK_INGESTION
      depends_on: []
    - id: N2
      name: DATA_ENRICHMENT
      depends_on: [N1]
    - id: N3
      name: RULES_TOLERANCE
      depends_on: [N2]
  
  decision_checkpoint:
    - after: N3
      condition: "within_rounding_tolerance"
      action: AUTO_RESOLVE

execution_path: N1 → N2 → N3 → Decision
agents_invoked: 3 out of 7
parallel_steps: None (linear for simple case)
```

#### Example 2: Large Derivative Break (Full Path)
```yaml
profile:
  type: TRADE_OMS_MISMATCH
  risk_tier: HIGH
  exposure: 250000
  asset_class: DERIVATIVE

routing:
  agents:
    - id: N1
      name: BREAK_INGESTION
      depends_on: []
    - id: N2
      name: DATA_ENRICHMENT
      depends_on: [N1]
    - id: N3
      name: MATCHING_CORRELATION
      depends_on: [N2]
    - id: N4
      name: RULES_TOLERANCE
      depends_on: [N2]
    - id: N5
      name: PATTERN_INTELLIGENCE
      depends_on: [N2]
    - id: N6
      name: DECISIONING
      depends_on: [N3, N4, N5]
    - id: N7
      name: WORKFLOW_FEEDBACK
      depends_on: [N6]

  parallel_stages:
    - [N2]  # Enrichment alone
    - [N3, N4, N5]  # These three can run in parallel
    - [N6]  # Decision
    - [N7]  # Workflow

execution_path:
  N1 → N2 → [N3 || N4 || N5] → N6 → N7
agents_invoked: 7 out of 7
parallel_steps: 3 agents in stage 3
```

#### Example 3: Medium Risk with Conditional Expansion
```yaml
profile:
  type: BROKER_VS_INTERNAL
  risk_tier: MEDIUM
  exposure: 45000

routing:
  phase_1:
    - BREAK_INGESTION
    - DATA_ENRICHMENT
    - RULES_TOLERANCE
  
  decision_checkpoint_1:
    condition: "within_tolerance and confidence > 0.85"
    action: AUTO_RESOLVE
  
  phase_2_conditional:
    trigger: "rules_failed or confidence < 0.85"
    additional_agents:
      - MATCHING_CORRELATION
      - PATTERN_INTELLIGENCE
  
  decision_checkpoint_2:
    condition: "after_phase_2"
    action: DECISIONING_AGENT

execution_path:
  Best case: N1 → N2 → N3 → Decision (3 agents)
  Expanded case: N1 → N2 → N3 → [N4 || N5] → N6 → Decision (6 agents)
agents_invoked: 3-6 out of 7 (conditional)
```

---

## Implementation Files Structure

```
orchestrator/
├── __init__.py
├── workflow.py                    # Current sequential orchestrator (keep for v1)
├── dynamic_orchestrator.py        # NEW: Dynamic orchestrator
├── break_classifier.py            # NEW: Break profiling
├── policy_engine.py               # NEW: Policy lookup and plan generation
├── dag_executor.py                # NEW: Parallel DAG execution
└── policies/                      # NEW: Policy definitions
    ├── __init__.py
    ├── routing_policies.yaml      # Routing rules
    ├── policy_loader.py           # Load and validate policies
    └── decision_rules.py          # Decision checkpoint logic

shared/
├── schemas.py                     # Extend with BreakProfile, ExecutionPlan, etc.
└── ...
```

---

## Key Implementation Details

### 1. Parallel Execution with asyncio

```python
import asyncio

async def execute_agent_async(agent, break_data):
    """Execute agent asynchronously"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, agent.process, break_data)

async def execute_parallel_agents(agents, break_data):
    """Execute multiple agents in parallel"""
    tasks = [execute_agent_async(agent, break_data) for agent in agents]
    results = await asyncio.gather(*tasks)
    return results
```

### 2. Early Exit Logic

```python
def can_decide_early(self, completed_agents: Set[str], results: Dict) -> bool:
    """Check if we have enough info to decide"""
    # Example: If rules passed with high confidence, we can decide
    if 'RULES_TOLERANCE' in completed_agents:
        rules_result = results['RULES_TOLERANCE']
        if rules_result['within_tolerance'] and rules_result['confidence'] > 0.9:
            return True
    return False
```

### 3. Conditional Agent Invocation

```python
def should_invoke_agent(self, agent_name: str, break_profile: BreakProfile, 
                       current_results: Dict) -> bool:
    """Decide if agent should be invoked"""
    # Example: Only invoke pattern analysis for repeated breaks
    if agent_name == 'PATTERN_INTELLIGENCE':
        if break_profile.risk_tier == 'LOW':
            return False  # Skip for low risk
        if 'RULES_TOLERANCE' in current_results:
            if current_results['RULES_TOLERANCE']['within_tolerance']:
                return False  # Skip if rules already passed
    return True
```

---

## Benefits of Dynamic Orchestration

### Performance Improvements

| Scenario | Sequential (v1) | Dynamic (v2) | Improvement |
|----------|----------------|--------------|-------------|
| Simple cash break | 7 agents, ~3s | 3 agents, ~1s | **67% faster** |
| Medium complexity | 7 agents, ~3s | 5 agents, ~2s (parallel) | **33% faster** |
| Complex derivative | 7 agents, ~3s | 7 agents, ~1.5s (parallel) | **50% faster** |

### Resource Optimization

- **Simple breaks**: 3-4 agents instead of 7 (60% reduction)
- **Medium breaks**: 5-6 agents instead of 7 (20% reduction)
- **Complex breaks**: All 7, but in parallel (50% time reduction)

### Cost Reduction

- Fewer OpenAI API calls (only invoke GPT-4.1 when needed)
- Reduced compute time
- Lower infrastructure costs

---

## Migration Path

### Phase 1: Add Dynamic Components (No Breaking Changes)
1. Create new orchestrator files
2. Implement break classifier
3. Implement policy engine
4. Implement DAG executor
5. Keep old orchestrator working

### Phase 2: Test Both Side-by-Side
1. Add mode flag to choose orchestrator
2. Run both in production
3. Compare results and performance
4. Tune policies

### Phase 3: Gradual Migration
1. Switch default to dynamic
2. Monitor for issues
3. Deprecate sequential orchestrator
4. Remove old code

---

## Recommended Next Steps

1. ✅ **Start with Break Classifier** - Simple component, no dependencies
2. ✅ **Implement Policy Engine** - Core routing logic
3. ✅ **Build DAG Executor** - Parallel execution capability
4. ✅ **Create Default Policies** - YAML configs for common break types
5. ✅ **Test with Simple Breaks** - Verify minimal path works
6. ✅ **Add Parallel Execution** - Async agent invocation
7. ✅ **Implement Early Exit** - Decision checkpoints
8. ✅ **Add Complex Scenarios** - Full DAG execution
9. ✅ **Performance Testing** - Compare v1 vs v2
10. ✅ **Production Rollout** - Gradual migration

---

**This design provides a clean path to implement dynamic orchestration while maintaining backward compatibility with the existing sequential system.**
