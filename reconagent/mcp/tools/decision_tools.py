"""
MCP Tools for Decisioning Agent
"""
from typing import Dict, Any
from shared.config import settings
from shared.schemas import ActionType


def calculate_risk_score(
    break_data: Dict[str, Any],
    rules_evaluation: Dict[str, Any],
    ml_insights: Dict[str, Any]
) -> float:
    """
    Calculate risk score for the break
    
    Args:
        break_data: Break data
        rules_evaluation: Rules evaluation
        ml_insights: ML insights
    
    Returns:
        Risk score (0.0 to 1.0, higher = more risky)
    """
    risk_score = 0.0
    
    # Factor 1: Amount magnitude (0-0.3)
    amount_diff = abs(
        break_data.get("system_a", {}).get("amount", 0) -
        break_data.get("system_b", {}).get("amount", 0)
    )
    
    if amount_diff > settings.escalation_amount_threshold:
        risk_score += 0.3
    elif amount_diff > settings.auto_resolve_max_amount:
        risk_score += 0.2
    elif amount_diff > 1000:
        risk_score += 0.1
    
    # Factor 2: Rules violations (0-0.3)
    failed_rules = len(rules_evaluation.get("failed_rules", []))
    if failed_rules >= 3:
        risk_score += 0.3
    elif failed_rules == 2:
        risk_score += 0.2
    elif failed_rules == 1:
        risk_score += 0.1
    
    # Factor 3: ML confidence (0-0.2)
    ml_confidence = ml_insights.get("confidence", 0.5)
    if ml_confidence < 0.5:
        risk_score += 0.2
    elif ml_confidence < 0.7:
        risk_score += 0.1
    
    # Factor 4: Break type (0-0.2)
    high_risk_types = ["REGULATORY_DATA", "CUSTODIAN_MISMATCH", "PNL_RECONCILIATION"]
    if break_data.get("break_type") in high_risk_types:
        risk_score += 0.2
    
    return min(1.0, risk_score)


def evaluate_decision(
    break_data: Dict[str, Any],
    rules_evaluation: Dict[str, Any],
    ml_insights: Dict[str, Any],
    risk_score: float
) -> Dict[str, Any]:
    """
    Make final decision on break resolution
    
    Args:
        break_data: Break data
        rules_evaluation: Rules evaluation
        ml_insights: ML insights
        risk_score: Calculated risk score
    
    Returns:
        Decision with action and explanation
    """
    amount_diff = abs(
        break_data.get("system_a", {}).get("amount", 0) -
        break_data.get("system_b", {}).get("amount", 0)
    )
    
    within_tolerance = rules_evaluation.get("within_tolerance", False)
    ml_confidence = ml_insights.get("confidence", 0.5)
    root_cause = ml_insights.get("probable_root_cause", "unknown")
    
    # Decision logic
    action = ActionType.HIL_REVIEW
    requires_hil = True
    auto_resolvable = False
    labels = []
    explanation_parts = []
    
    # Auto-resolve conditions
    if (within_tolerance and 
        ml_confidence >= settings.auto_resolve_confidence_threshold and
        amount_diff <= settings.auto_resolve_max_amount and
        risk_score < 0.3):
        
        action = ActionType.AUTO_RESOLVE
        requires_hil = False
        auto_resolvable = True
        labels = ["AutoResolved", "LowRisk", root_cause]
        explanation_parts = [
            f"Within tolerance ({rules_evaluation.get('tolerance_checks', {}).get('amount', {}).get('difference_bps', 0):.2f} bps)",
            f"High confidence ({ml_confidence:.2%})",
            f"Low amount (${amount_diff:,.2f})",
            f"Probable cause: {root_cause}"
        ]
    
    # Escalate conditions
    elif (risk_score >= settings.high_risk_score_threshold or
          amount_diff > settings.escalation_amount_threshold or
          root_cause in ["system_error", "data_entry_error"]):
        
        action = ActionType.ESCALATE
        requires_hil = True
        auto_resolvable = False
        labels = ["Escalated", "HighRisk", root_cause]
        explanation_parts = [
            f"High risk score ({risk_score:.2f})",
            f"Amount: ${amount_diff:,.2f}",
            f"Probable cause: {root_cause}",
            "Requires senior review"
        ]
    
    # HIL Review
    else:
        action = ActionType.HIL_REVIEW
        requires_hil = True
        auto_resolvable = False
        labels = ["PendingReview", "MediumRisk", root_cause]
        explanation_parts = [
            f"Risk score: {risk_score:.2f}",
            f"ML confidence: {ml_confidence:.2%}",
            f"Amount: ${amount_diff:,.2f}",
            f"Probable cause: {root_cause}",
            "Requires human review"
        ]
    
    return {
        "action": action,
        "requires_hil": requires_hil,
        "auto_resolvable": auto_resolvable,
        "labels": labels,
        "explanation": " | ".join(explanation_parts),
        "confidence": ml_confidence,
        "risk_score": risk_score
    }


def determine_action(decision: Dict[str, Any]) -> str:
    """
    Determine specific action to take
    
    Args:
        decision: Decision dict
    
    Returns:
        Action string
    """
    action_map = {
        ActionType.AUTO_RESOLVE: "Automatically resolve and close break",
        ActionType.HIL_REVIEW: "Send to human analyst for review",
        ActionType.ESCALATE: "Escalate to senior team or compliance",
        ActionType.REJECTED: "Reject as false positive"
    }
    
    return action_map.get(decision.get("action"), "Unknown action")


DECISION_TOOLS = {
    "calculate_risk_score": {
        "function": calculate_risk_score,
        "description": "Calculate risk score for break",
        "parameters": {
            "break_data": {"type": "object"},
            "rules_evaluation": {"type": "object"},
            "ml_insights": {"type": "object"}
        }
    },
    "evaluate_decision": {
        "function": evaluate_decision,
        "description": "Make final decision on resolution",
        "parameters": {
            "break_data": {"type": "object"},
            "rules_evaluation": {"type": "object"},
            "ml_insights": {"type": "object"},
            "risk_score": {"type": "number"}
        }
    },
    "determine_action": {
        "function": determine_action,
        "description": "Determine specific action to take",
        "parameters": {
            "decision": {"type": "object"}
        }
    }
}
