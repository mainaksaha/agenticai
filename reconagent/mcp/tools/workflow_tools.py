"""
MCP Tools for Workflow & Feedback Agent
"""
from datetime import datetime
from typing import Dict, Any, List
import uuid


# In-memory storage for demo (would be database in production)
TICKETS = {}
AUDIT_LOGS = {}
FEEDBACK_LOG = []


def create_ticket(
    break_id: str,
    decision: Dict[str, Any],
    case_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Create workflow ticket for break
    
    Args:
        break_id: Break identifier
        decision: Decision data
        case_data: Full case data
    
    Returns:
        Created ticket
    """
    ticket_id = f"TKT-{uuid.uuid4().hex[:8].upper()}"
    
    ticket = {
        "ticket_id": ticket_id,
        "break_id": break_id,
        "status": "OPEN" if decision.get("requires_hil") else "RESOLVED",
        "action": decision.get("action"),
        "priority": "HIGH" if decision.get("risk_score", 0) > 0.7 else "MEDIUM",
        "assigned_to": "AUTO" if decision.get("auto_resolvable") else "ANALYST_QUEUE",
        "created_at": datetime.now().isoformat(),
        "resolved_at": None if decision.get("requires_hil") else datetime.now().isoformat(),
        "resolution": decision.get("explanation") if not decision.get("requires_hil") else None,
        "case_summary": {
            "break_type": case_data.get("break", {}).get("break_type"),
            "amount_diff": abs(
                case_data.get("break", {}).get("system_a", {}).get("amount", 0) -
                case_data.get("break", {}).get("system_b", {}).get("amount", 0)
            ),
            "instrument": case_data.get("break", {}).get("entities", {}).get("instrument"),
            "root_cause": case_data.get("ml_insights", {}).get("probable_root_cause")
        }
    }
    
    TICKETS[ticket_id] = ticket
    return ticket


def update_ticket(ticket_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update existing ticket
    
    Args:
        ticket_id: Ticket identifier
        updates: Fields to update
    
    Returns:
        Updated ticket
    """
    if ticket_id not in TICKETS:
        return {"error": f"Ticket {ticket_id} not found"}
    
    ticket = TICKETS[ticket_id]
    ticket.update(updates)
    ticket["updated_at"] = datetime.now().isoformat()
    
    return ticket


def log_feedback(
    break_id: str,
    decision: Dict[str, Any],
    human_action: str = None,
    human_notes: str = None
) -> Dict[str, Any]:
    """
    Log feedback for learning and improvement
    
    Args:
        break_id: Break identifier
        decision: Agent decision
        human_action: Human action taken (if any)
        human_notes: Human notes
    
    Returns:
        Feedback record
    """
    feedback = {
        "feedback_id": f"FB-{uuid.uuid4().hex[:8].upper()}",
        "break_id": break_id,
        "agent_decision": decision.get("action"),
        "agent_confidence": decision.get("confidence"),
        "human_action": human_action,
        "human_notes": human_notes,
        "agreement": human_action == decision.get("action") if human_action else None,
        "timestamp": datetime.now().isoformat()
    }
    
    FEEDBACK_LOG.append(feedback)
    return feedback


def get_audit_trail(break_id: str) -> List[Dict[str, Any]]:
    """
    Get audit trail for a break
    
    Args:
        break_id: Break identifier
    
    Returns:
        List of audit events
    """
    if break_id not in AUDIT_LOGS:
        return []
    
    return AUDIT_LOGS[break_id]


def add_audit_event(
    break_id: str,
    event_type: str,
    agent_name: str,
    details: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Add audit event
    
    Args:
        break_id: Break identifier
        event_type: Type of event
        agent_name: Agent that generated event
        details: Event details
    
    Returns:
        Audit event
    """
    if break_id not in AUDIT_LOGS:
        AUDIT_LOGS[break_id] = []
    
    event = {
        "event_id": f"AUD-{uuid.uuid4().hex[:8].upper()}",
        "break_id": break_id,
        "event_type": event_type,
        "agent_name": agent_name,
        "details": details,
        "timestamp": datetime.now().isoformat()
    }
    
    AUDIT_LOGS[break_id].append(event)
    return event


def get_feedback_stats() -> Dict[str, Any]:
    """
    Get feedback statistics for model improvement
    
    Returns:
        Feedback statistics
    """
    if not FEEDBACK_LOG:
        return {
            "total_feedback": 0,
            "agreement_rate": 0.0,
            "avg_confidence": 0.0
        }
    
    agreements = sum(1 for f in FEEDBACK_LOG if f.get("agreement") is True)
    total_with_human = sum(1 for f in FEEDBACK_LOG if f.get("human_action") is not None)
    
    return {
        "total_feedback": len(FEEDBACK_LOG),
        "total_with_human_action": total_with_human,
        "agreements": agreements,
        "agreement_rate": agreements / total_with_human if total_with_human > 0 else 0.0,
        "avg_confidence": sum(f.get("agent_confidence", 0) for f in FEEDBACK_LOG) / len(FEEDBACK_LOG)
    }


WORKFLOW_TOOLS = {
    "create_ticket": {
        "function": create_ticket,
        "description": "Create workflow ticket",
        "parameters": {
            "break_id": {"type": "string"},
            "decision": {"type": "object"},
            "case_data": {"type": "object"}
        }
    },
    "update_ticket": {
        "function": update_ticket,
        "description": "Update existing ticket",
        "parameters": {
            "ticket_id": {"type": "string"},
            "updates": {"type": "object"}
        }
    },
    "log_feedback": {
        "function": log_feedback,
        "description": "Log feedback for learning",
        "parameters": {
            "break_id": {"type": "string"},
            "decision": {"type": "object"},
            "human_action": {"type": "string"},
            "human_notes": {"type": "string"}
        }
    },
    "get_audit_trail": {
        "function": get_audit_trail,
        "description": "Get audit trail for break",
        "parameters": {
            "break_id": {"type": "string"}
        }
    },
    "add_audit_event": {
        "function": add_audit_event,
        "description": "Add audit event",
        "parameters": {
            "break_id": {"type": "string"},
            "event_type": {"type": "string"},
            "agent_name": {"type": "string"},
            "details": {"type": "object"}
        }
    },
    "get_feedback_stats": {
        "function": get_feedback_stats,
        "description": "Get feedback statistics",
        "parameters": {}
    }
}
