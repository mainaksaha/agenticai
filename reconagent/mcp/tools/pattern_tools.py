"""
MCP Tools for Pattern & Root-Cause Intelligence Agent
"""
import requests
from typing import Dict, Any, List
from shared.config import settings


def get_historical_patterns(break_type: str = None, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Fetch historical break patterns from mock API
    
    Args:
        break_type: Optional filter by break type
        limit: Number of patterns to fetch
    
    Returns:
        List of historical patterns
    """
    params = {"limit": limit}
    if break_type:
        params["break_type"] = break_type
    
    try:
        response = requests.get(
            f"{settings.mock_api_base_url}/api/historical/patterns",
            params=params,
            timeout=settings.agent_timeout_seconds
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": f"Failed to fetch patterns: {str(e)}"}


def predict_root_cause(
    break_data: Dict[str, Any],
    rules_evaluation: Dict[str, Any],
    historical_patterns: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Predict probable root cause based on patterns
    
    Args:
        break_data: Break data
        rules_evaluation: Rules evaluation results
        historical_patterns: Historical patterns
    
    Returns:
        Root cause prediction with confidence
    """
    system_a = break_data.get("system_a", {})
    system_b = break_data.get("system_b", {})
    
    # Analyze difference characteristics
    amt_diff = abs(system_a.get("amount", 0) - system_b.get("amount", 0))
    qty_diff = abs(system_a.get("quantity", 0) - system_b.get("quantity", 0))
    
    tolerance_checks = rules_evaluation.get("tolerance_checks", {})
    amt_within_tol = tolerance_checks.get("amount", {}).get("within_tolerance", False)
    qty_within_tol = tolerance_checks.get("quantity", {}).get("within_tolerance", False)
    
    # Rule-based prediction
    probable_cause = "unknown"
    confidence = 0.5
    explanation = []
    
    if amt_within_tol and qty_within_tol:
        probable_cause = "timing_lag"
        confidence = 0.85
        explanation.append("Differences within tolerance suggest timing lag")
    elif qty_diff == 0 and amt_diff > 0:
        probable_cause = "fee_mismatch"
        confidence = 0.80
        explanation.append("Quantity matches but amount differs - likely fees or commissions")
    elif amt_diff < 10:
        probable_cause = "rounding_difference"
        confidence = 0.75
        explanation.append("Small difference suggests rounding")
    elif qty_diff > 0 and amt_diff > 1000:
        probable_cause = "partial_fill"
        confidence = 0.70
        explanation.append("Quantity and amount differ significantly - possible partial fill")
    else:
        probable_cause = "data_entry_error"
        confidence = 0.60
        explanation.append("No clear pattern - possible data entry error")
    
    # Enhance with historical patterns
    if isinstance(historical_patterns, list) and historical_patterns:
        matching_patterns = [
            p for p in historical_patterns
            if p.get("break_type") == break_data.get("break_type")
        ]
        
        if matching_patterns:
            most_common = max(matching_patterns, key=lambda x: x.get("frequency", 0))
            if most_common.get("frequency", 0) > 10:
                probable_cause = most_common.get("root_cause", probable_cause)
                confidence = min(0.95, confidence + 0.1)
                explanation.append(f"Historical data supports this cause (seen {most_common['frequency']} times)")
    
    return {
        "probable_root_cause": probable_cause,
        "confidence": confidence,
        "explanation": " | ".join(explanation),
        "alternative_causes": ["system_error", "timing_lag", "manual_adjustment"],
        "historical_support": len([p for p in (historical_patterns if isinstance(historical_patterns, list) else []) 
                                   if p.get("root_cause") == probable_cause])
    }


def suggest_fix(root_cause: str, break_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Suggest fix based on root cause
    
    Args:
        root_cause: Identified root cause
        break_data: Break data
    
    Returns:
        Suggested fix with actions
    """
    fix_suggestions = {
        "timing_lag": {
            "action": "WAIT_AND_RECHECK",
            "description": "Wait for T+1 settlement and recheck",
            "auto_resolvable": True,
            "steps": ["Wait 24 hours", "Recheck both systems", "Auto-resolve if matched"]
        },
        "fee_mismatch": {
            "action": "ADJUST_FOR_FEES",
            "description": "Adjust for broker fees and commissions",
            "auto_resolvable": True,
            "steps": ["Calculate net amount", "Verify fee schedule", "Apply adjustment"]
        },
        "rounding_difference": {
            "action": "AUTO_RESOLVE",
            "description": "Acceptable rounding difference",
            "auto_resolvable": True,
            "steps": ["Verify within tolerance", "Document reason", "Auto-resolve"]
        },
        "partial_fill": {
            "action": "CORRELATE_TRADES",
            "description": "Find and correlate related partial fills",
            "auto_resolvable": False,
            "steps": ["Find all related trades", "Aggregate quantities", "Manual review"]
        },
        "data_entry_error": {
            "action": "MANUAL_REVIEW",
            "description": "Requires manual investigation",
            "auto_resolvable": False,
            "steps": ["Review source documents", "Identify error", "Manual correction"]
        },
        "system_error": {
            "action": "ESCALATE",
            "description": "Escalate to technical team",
            "auto_resolvable": False,
            "steps": ["Document error", "Create incident ticket", "Escalate to IT"]
        }
    }
    
    return fix_suggestions.get(root_cause, {
        "action": "MANUAL_REVIEW",
        "description": "Unknown root cause - requires manual review",
        "auto_resolvable": False,
        "steps": ["Investigate manually"]
    })


PATTERN_TOOLS = {
    "get_historical_patterns": {
        "function": get_historical_patterns,
        "description": "Fetch historical break patterns",
        "parameters": {
            "break_type": {"type": "string"},
            "limit": {"type": "integer"}
        }
    },
    "predict_root_cause": {
        "function": predict_root_cause,
        "description": "Predict probable root cause",
        "parameters": {
            "break_data": {"type": "object"},
            "rules_evaluation": {"type": "object"},
            "historical_patterns": {"type": "array"}
        }
    },
    "suggest_fix": {
        "function": suggest_fix,
        "description": "Suggest fix based on root cause",
        "parameters": {
            "root_cause": {"type": "string"},
            "break_data": {"type": "object"}
        }
    }
}
