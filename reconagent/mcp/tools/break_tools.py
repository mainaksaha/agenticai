"""
MCP Tools for Break Ingestion Agent
"""
import requests
from typing import List, Dict, Any
from shared.config import settings
from shared.schemas import Break, BreakType


def get_breaks(limit: int = 10, break_type: str = None) -> List[Dict[str, Any]]:
    """
    Fetch breaks from mock API
    
    Args:
        limit: Number of breaks to fetch
        break_type: Optional filter by break type
    
    Returns:
        List of break records
    """
    params = {"limit": limit}
    if break_type:
        params["break_type"] = break_type
    
    try:
        response = requests.get(
            f"{settings.mock_api_base_url}/api/breaks",
            params=params,
            timeout=settings.agent_timeout_seconds
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": f"Failed to fetch breaks: {str(e)}"}


def get_break_by_id(break_id: str) -> Dict[str, Any]:
    """
    Fetch specific break by ID
    
    Args:
        break_id: Break identifier
    
    Returns:
        Break record
    """
    try:
        response = requests.get(
            f"{settings.mock_api_base_url}/api/breaks/{break_id}",
            timeout=settings.agent_timeout_seconds
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": f"Failed to fetch break {break_id}: {str(e)}"}


def normalize_break(raw_break: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize raw break data to standard schema
    
    Args:
        raw_break: Raw break data
    
    Returns:
        Normalized break data
    """
    try:
        # Validate and normalize using Pydantic schema
        break_obj = Break(**raw_break)
        return break_obj.model_dump()
    except Exception as e:
        return {"error": f"Failed to normalize break: {str(e)}", "raw_data": raw_break}


def validate_break(break_data: Dict[str, Any]) -> Dict[str, bool]:
    """
    Validate break data completeness and correctness
    
    Args:
        break_data: Break data to validate
    
    Returns:
        Validation results
    """
    validations = {
        "has_break_id": bool(break_data.get("break_id")),
        "has_break_type": bool(break_data.get("break_type")),
        "has_system_a": bool(break_data.get("system_a")),
        "has_system_b": bool(break_data.get("system_b")),
        "has_entities": bool(break_data.get("entities")),
        "has_instrument": bool(break_data.get("entities", {}).get("instrument")),
        "system_a_has_amount": break_data.get("system_a", {}).get("amount") is not None,
        "system_b_has_amount": break_data.get("system_b", {}).get("amount") is not None,
    }
    
    validations["is_valid"] = all(validations.values())
    return validations


# MCP Tool Registry for Break Ingestion
BREAK_TOOLS = {
    "get_breaks": {
        "function": get_breaks,
        "description": "Fetch breaks from reconciliation system",
        "parameters": {
            "limit": {"type": "integer", "description": "Number of breaks to fetch"},
            "break_type": {"type": "string", "description": "Filter by break type"}
        }
    },
    "get_break_by_id": {
        "function": get_break_by_id,
        "description": "Fetch specific break by ID",
        "parameters": {
            "break_id": {"type": "string", "description": "Break identifier"}
        }
    },
    "normalize_break": {
        "function": normalize_break,
        "description": "Normalize raw break data to standard schema",
        "parameters": {
            "raw_break": {"type": "object", "description": "Raw break data"}
        }
    },
    "validate_break": {
        "function": validate_break,
        "description": "Validate break data completeness",
        "parameters": {
            "break_data": {"type": "object", "description": "Break data to validate"}
        }
    }
}
