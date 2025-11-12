"""
MCP Tools for Rules & Tolerance Agent
"""
from typing import Dict, Any, List
from shared.config import settings


def check_tolerance(
    value_a: float,
    value_b: float,
    tolerance_bps: float = None,
    tolerance_abs: float = None
) -> Dict[str, Any]:
    """
    Check if values are within tolerance
    
    Args:
        value_a: First value
        value_b: Second value
        tolerance_bps: Tolerance in basis points (0.01% = 1 bps)
        tolerance_abs: Absolute tolerance
    
    Returns:
        Tolerance check result
    """
    if tolerance_bps is None:
        tolerance_bps = settings.default_amount_tolerance_bps
    
    diff = abs(value_a - value_b)
    diff_pct = (diff / max(abs(value_a), abs(value_b))) * 100 if max(abs(value_a), abs(value_b)) > 0 else 0
    diff_bps = diff_pct * 100
    
    within_tolerance = False
    reason = []
    
    if tolerance_abs is not None and diff <= tolerance_abs:
        within_tolerance = True
        reason.append(f"Within absolute tolerance: {diff:.2f} <= {tolerance_abs:.2f}")
    
    if tolerance_bps is not None and diff_bps <= tolerance_bps:
        within_tolerance = True
        reason.append(f"Within bps tolerance: {diff_bps:.2f} bps <= {tolerance_bps:.2f} bps")
    
    if not within_tolerance:
        reason.append(f"Exceeds tolerance: diff={diff:.2f}, diff_bps={diff_bps:.2f}")
    
    return {
        "within_tolerance": within_tolerance,
        "difference": diff,
        "difference_pct": diff_pct,
        "difference_bps": diff_bps,
        "tolerance_bps": tolerance_bps,
        "tolerance_abs": tolerance_abs,
        "reason": "; ".join(reason)
    }


def apply_business_rules(break_data: Dict[str, Any], enriched_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply business rules to evaluate break
    
    Args:
        break_data: Break data
        enriched_data: Enriched data
    
    Returns:
        Rules evaluation results
    """
    system_a = break_data.get("system_a", {})
    system_b = break_data.get("system_b", {})
    
    results = {
        "rules_applied": [],
        "passed_rules": [],
        "failed_rules": [],
        "within_tolerance": True,
        "tolerance_checks": {}
    }
    
    # Rule 1: Amount tolerance check
    if system_a.get("amount") and system_b.get("amount"):
        amt_check = check_tolerance(
            system_a["amount"],
            system_b["amount"],
            tolerance_bps=settings.default_amount_tolerance_bps
        )
        results["tolerance_checks"]["amount"] = amt_check
        results["rules_applied"].append("AMOUNT_TOLERANCE")
        
        if amt_check["within_tolerance"]:
            results["passed_rules"].append("AMOUNT_TOLERANCE")
        else:
            results["failed_rules"].append("AMOUNT_TOLERANCE")
            results["within_tolerance"] = False
    
    # Rule 2: Quantity tolerance check
    if system_a.get("quantity") and system_b.get("quantity"):
        qty_check = check_tolerance(
            system_a["quantity"],
            system_b["quantity"],
            tolerance_abs=settings.default_quantity_tolerance
        )
        results["tolerance_checks"]["quantity"] = qty_check
        results["rules_applied"].append("QUANTITY_TOLERANCE")
        
        if qty_check["within_tolerance"]:
            results["passed_rules"].append("QUANTITY_TOLERANCE")
        else:
            results["failed_rules"].append("QUANTITY_TOLERANCE")
            results["within_tolerance"] = False
    
    # Rule 3: Currency match
    if system_a.get("currency") and system_b.get("currency"):
        results["rules_applied"].append("CURRENCY_MATCH")
        if system_a["currency"] == system_b["currency"]:
            results["passed_rules"].append("CURRENCY_MATCH")
        else:
            results["failed_rules"].append("CURRENCY_MATCH")
            results["within_tolerance"] = False
    
    # Rule 4: Timing check (T+1 lag acceptable)
    results["rules_applied"].append("TIMING_LAG")
    results["passed_rules"].append("TIMING_LAG")  # Default pass for now
    
    return results


def validate_rules(rules_evaluation: Dict[str, Any]) -> bool:
    """
    Validate if all critical rules passed
    
    Args:
        rules_evaluation: Rules evaluation results
    
    Returns:
        True if all critical rules passed
    """
    critical_rules = ["AMOUNT_TOLERANCE", "CURRENCY_MATCH"]
    failed_critical = [r for r in rules_evaluation.get("failed_rules", []) if r in critical_rules]
    
    return len(failed_critical) == 0


RULES_TOOLS = {
    "check_tolerance": {
        "function": check_tolerance,
        "description": "Check if values are within tolerance",
        "parameters": {
            "value_a": {"type": "number"},
            "value_b": {"type": "number"},
            "tolerance_bps": {"type": "number"},
            "tolerance_abs": {"type": "number"}
        }
    },
    "apply_business_rules": {
        "function": apply_business_rules,
        "description": "Apply business rules to break",
        "parameters": {
            "break_data": {"type": "object"},
            "enriched_data": {"type": "object"}
        }
    },
    "validate_rules": {
        "function": validate_rules,
        "description": "Validate if critical rules passed",
        "parameters": {
            "rules_evaluation": {"type": "object"}
        }
    }
}
