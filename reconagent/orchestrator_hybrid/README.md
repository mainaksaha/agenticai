# Option C: Hybrid Approach - ADK Wrapper Layer

## Overview

This is a **hybrid implementation** that wraps existing agents with Google ADK:
- ✅ **Existing agents** continue to work
- ✅ **ADK wrapper layer** provides official interfaces
- ✅ **Gradual migration** path
- ✅ **Both systems** can coexist

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│               Google ADK Interface Layer                     │
│          (Exposes existing agents via ADK)                   │
└───────────────────────────┬─────────────────────────────────┘
                            │
                    ┌───────▼───────┐
                    │  ADK Wrapper  │
                    │  (Adapter)    │
                    └───────┬───────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
┌───────▼────────┐  ┌───────▼────────┐  ┌──────▼─────────┐
│  Wrapped       │  │  Wrapped       │  │  Wrapped       │
│  Agent 1       │  │  Agent 2       │  │  Agent 3       │
│  (ADK compat)  │  │  (ADK compat)  │  │  (ADK compat)  │
└───────┬────────┘  └───────┬────────┘  └───────┬────────┘
        │                   │                   │
┌───────▼────────┐  ┌───────▼────────┐  ┌──────▼─────────┐
│  Original      │  │  Original      │  │  Original      │
│  Custom Agent  │  │  Custom Agent  │  │  Custom Agent  │
│  (v2)          │  │  (v2)          │  │  (v2)          │
└────────────────┘  └────────────────┘  └────────────────┘
```

---

## Installation

```bash
# Install both custom and ADK requirements
pip install -r requirements_adk.txt
```

---

## Components

### 1. ADK Wrapper (`adk_wrapper.py`)
- Wraps existing `BaseReconAgent`
- Converts to ADK-compatible interface
- Handles message translation

### 2. A2A Adapter (`a2a_adapter.py`)
- Converts custom A2A to official A2A
- Message format translation
- Backward compatibility

### 3. Hybrid Orchestrator (`orchestrator.py`)
- Can use both custom and ADK agents
- Supports both orchestration modes
- Gradual migration support

### 4. Existing Agents (Reused)
- No changes to existing agents!
- Work as-is
- Wrapped when needed

---

## Key Files

```
orchestrator_hybrid/
├── README.md                    # This file
├── adk_wrapper.py               # Wraps custom agents for ADK
├── a2a_adapter.py               # Converts A2A messages
├── orchestrator.py              # Hybrid orchestrator
├── agent_registry.py            # Manages both types
└── test_hybrid.py               # Tests
```

---

## Usage

### Using Custom Agents (As-Is)
```python
from orchestrator.v2 import DynamicReconciliationOrchestrator

# Works exactly as before
orchestrator = DynamicReconciliationOrchestrator()
result = orchestrator.process_break(break_id="BRK-001")
```

### Using ADK-Wrapped Agents
```python
from orchestrator_hybrid import HybridOrchestrator

# Uses ADK interfaces
orchestrator = HybridOrchestrator(mode="adk")
result = await orchestrator.process_break(break_id="BRK-001")
```

### Mixing Both
```python
from orchestrator_hybrid import HybridOrchestrator

# Some agents custom, some ADK
orchestrator = HybridOrchestrator(mode="hybrid")
result = await orchestrator.process_break(break_id="BRK-001")
```

---

## Features

### ✅ No Breaking Changes
- Existing agents work unchanged
- Custom v2 orchestrator still works
- Gradual migration possible

### ✅ ADK Compatibility
- Agents exposed via ADK interface
- Official A2A protocol support
- Can interact with external ADK agents

### ✅ Flexible
- Choose custom or ADK per agent
- Mix and match
- Test both approaches

---

## Migration Path

### Phase 1: Wrap Existing (Current)
```python
# Wrap existing agents
wrapped_agent = ADKWrapper(existing_agent)

# Use with ADK interface
result = await wrapped_agent.process_adk(task)
```

### Phase 2: Selective Migration
```python
# Migrate one agent at a time
class NewADKAgent(google.adk.Agent):
    # Pure ADK implementation
    ...

# Mix with wrapped agents
orchestrator.register(new_adk_agent)
orchestrator.register(wrapped_custom_agent)
```

### Phase 3: Complete Migration
```python
# Eventually all agents are pure ADK
# Remove wrapper layer
# Keep only ADK implementation
```

---

## Wrapper Implementation

### ADK Wrapper
```python
class ADKWrapper(google.adk.Agent):
    def __init__(self, custom_agent: BaseReconAgent):
        self.custom_agent = custom_agent
    
    async def process(self, task: Task) -> TaskResult:
        # Convert ADK task to custom format
        custom_input = self._convert_task(task)
        
        # Call custom agent
        result = self.custom_agent.execute_action(
            custom_input['action'],
            custom_input['parameters']
        )
        
        # Convert back to ADK format
        return self._convert_result(result)
```

### A2A Adapter
```python
class A2AAdapter:
    def custom_to_official(self, custom_msg):
        # Convert custom A2A to official format
        return A2AMessage(
            from_agent=custom_msg.from_agent,
            to_agent=custom_msg.to_agent,
            content=self._convert_payload(custom_msg.payload)
        )
    
    def official_to_custom(self, official_msg):
        # Convert official A2A to custom format
        return CustomA2AMessage(...)
```

---

## Differences from Pure Implementations

| Aspect | Custom (v2) | Hybrid (Option C) | Pure ADK (Option A) |
|--------|-------------|-------------------|---------------------|
| **Agents** | Custom | Wrapped + Custom | Pure ADK |
| **A2A** | Custom | Adapted | Official |
| **Orchestrator** | Custom DAG | Hybrid | LangGraph |
| **Migration** | N/A | Gradual | Complete |
| **Complexity** | Low | Medium | Medium |

---

## Advantages

### ✅ Gradual Migration
- No big-bang rewrite
- Test ADK gradually
- Keep working system

### ✅ Flexibility
- Choose approach per agent
- Test both side-by-side
- Easy rollback

### ✅ Learning Curve
- Learn ADK incrementally
- Not all-or-nothing
- Lower risk

---

## Disadvantages

### ⚠️ Complexity
- Two systems to maintain
- Wrapper overhead
- More code

### ⚠️ Performance
- Wrapper translation cost
- Not as clean as pure ADK
- More memory usage

---

## Next Steps

1. Test wrapper: `pytest test_hybrid.py`
2. Run in hybrid mode
3. Migrate one agent at a time
4. Eventually move to pure ADK

---

**Status:** ✅ Hybrid Implementation
**Approach:** Gradual migration with wrapper layer
