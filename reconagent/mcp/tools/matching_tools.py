"""
MCP Tools for Matching & Correlation Agent
"""
from typing import List, Dict, Any
from shared.schemas import MatchCandidate


def calculate_similarity(data_a: Dict[str, Any], data_b: Dict[str, Any]) -> float:
    """
    Calculate similarity score between two data records
    
    Args:
        data_a: First record
        data_b: Second record
    
    Returns:
        Similarity score (0.0 to 1.0)
    """
    score = 0.0
    total_fields = 0
    
    comparable_fields = ["instrument", "quantity", "amount", "price", "currency"]
    
    for field in comparable_fields:
        if field in data_a and field in data_b:
            total_fields += 1
            
            if field in ["instrument", "currency"]:
                # Exact match for strings
                if data_a[field] == data_b[field]:
                    score += 1.0
            else:
                # Tolerance-based match for numbers
                try:
                    val_a = float(data_a[field])
                    val_b = float(data_b[field])
                    
                    if val_a == 0 and val_b == 0:
                        score += 1.0
                    elif val_a == 0 or val_b == 0:
                        score += 0.0
                    else:
                        diff_pct = abs(val_a - val_b) / max(abs(val_a), abs(val_b))
                        if diff_pct < 0.01:  # Within 1%
                            score += 1.0
                        elif diff_pct < 0.05:  # Within 5%
                            score += 0.7
                        elif diff_pct < 0.10:  # Within 10%
                            score += 0.4
                except (ValueError, TypeError):
                    pass
    
    return score / total_fields if total_fields > 0 else 0.0


def find_match_candidates(
    break_data: Dict[str, Any],
    enriched_data: Dict[str, Any],
    threshold: float = 0.7
) -> List[Dict[str, Any]]:
    """
    Find potential matching records
    
    Args:
        break_data: Break data
        enriched_data: Enriched data from various sources
        threshold: Minimum similarity threshold
    
    Returns:
        List of match candidates
    """
    candidates = []
    system_a = break_data.get("system_a", {})
    system_b = break_data.get("system_b", {})
    
    # Check OMS data
    oms_data = enriched_data.get("oms_data", {})
    if oms_data and not oms_data.get("error"):
        sim_score = calculate_similarity(system_a, oms_data)
        if sim_score >= threshold:
            candidates.append({
                "candidate_id": oms_data.get("order_id", "OMS-UNKNOWN"),
                "source": "OMS",
                "match_type": "ORDER_MATCH",
                "similarity_score": sim_score,
                "matched_fields": ["instrument", "quantity", "price"],
                "data": oms_data
            })
    
    # Check trade capture
    trade_data = enriched_data.get("trade_capture_data", {})
    if trade_data and not trade_data.get("error"):
        sim_score = calculate_similarity(system_b, trade_data)
        if sim_score >= threshold:
            candidates.append({
                "candidate_id": trade_data.get("trade_id", "TRADE-UNKNOWN"),
                "source": "TRADE_CAPTURE",
                "match_type": "TRADE_MATCH",
                "similarity_score": sim_score,
                "matched_fields": ["instrument", "quantity", "amount"],
                "data": trade_data
            })
    
    # Check broker confirm
    broker_data = enriched_data.get("broker_confirm_data", {})
    if broker_data and not broker_data.get("error"):
        sim_score = calculate_similarity(system_b, broker_data)
        if sim_score >= threshold:
            candidates.append({
                "candidate_id": broker_data.get("confirm_id", "BROKER-UNKNOWN"),
                "source": "BROKER",
                "match_type": "BROKER_CONFIRM",
                "similarity_score": sim_score,
                "matched_fields": ["instrument", "quantity", "amount"],
                "data": broker_data
            })
    
    return sorted(candidates, key=lambda x: x["similarity_score"], reverse=True)


def correlate_trades(candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Correlate multiple candidate matches to identify relationships
    
    Args:
        candidates: List of match candidates
    
    Returns:
        Correlation analysis
    """
    if not candidates:
        return {"has_correlation": False, "reason": "No candidates found"}
    
    if len(candidates) == 1:
        return {
            "has_correlation": True,
            "correlation_type": "SINGLE_MATCH",
            "primary_candidate": candidates[0]["candidate_id"],
            "confidence": candidates[0]["similarity_score"]
        }
    
    # Multiple candidates - check for partial fills or aggregations
    total_qty = sum(c.get("data", {}).get("quantity", 0) for c in candidates)
    avg_score = sum(c["similarity_score"] for c in candidates) / len(candidates)
    
    return {
        "has_correlation": True,
        "correlation_type": "MULTIPLE_MATCHES",
        "num_candidates": len(candidates),
        "average_similarity": avg_score,
        "total_quantity": total_qty,
        "possible_explanation": "Partial fills or aggregated trades"
    }


MATCHING_TOOLS = {
    "calculate_similarity": {
        "function": calculate_similarity,
        "description": "Calculate similarity between two records",
        "parameters": {
            "data_a": {"type": "object"},
            "data_b": {"type": "object"}
        }
    },
    "find_match_candidates": {
        "function": find_match_candidates,
        "description": "Find potential matching records",
        "parameters": {
            "break_data": {"type": "object"},
            "enriched_data": {"type": "object"},
            "threshold": {"type": "number"}
        }
    },
    "correlate_trades": {
        "function": correlate_trades,
        "description": "Correlate multiple match candidates",
        "parameters": {
            "candidates": {"type": "array"}
        }
    }
}
