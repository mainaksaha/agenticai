"""
MCP Tools for Data Enrichment Agent
"""
import requests
from typing import Dict, Any, Optional
from shared.config import settings


def get_oms_data(order_id: str) -> Dict[str, Any]:
    """Fetch OMS order data"""
    try:
        response = requests.get(
            f"{settings.mock_api_base_url}/api/oms/orders/{order_id}",
            timeout=settings.agent_timeout_seconds
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": f"Failed to fetch OMS data: {str(e)}"}


def get_trade_capture(trade_id: str) -> Dict[str, Any]:
    """Fetch trade capture data"""
    try:
        response = requests.get(
            f"{settings.mock_api_base_url}/api/trade-capture/trades/{trade_id}",
            timeout=settings.agent_timeout_seconds
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": f"Failed to fetch trade capture data: {str(e)}"}


def get_settlement(account: str) -> Dict[str, Any]:
    """Fetch settlement data"""
    try:
        response = requests.get(
            f"{settings.mock_api_base_url}/api/settlement/positions/{account}",
            timeout=settings.agent_timeout_seconds
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": f"Failed to fetch settlement data: {str(e)}"}


def get_custodian_data(account: str) -> Dict[str, Any]:
    """Fetch custodian holdings"""
    try:
        response = requests.get(
            f"{settings.mock_api_base_url}/api/custodian/holdings/{account}",
            timeout=settings.agent_timeout_seconds
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": f"Failed to fetch custodian data: {str(e)}"}


def get_reference_data(symbol: str) -> Dict[str, Any]:
    """Fetch instrument reference data"""
    try:
        response = requests.get(
            f"{settings.mock_api_base_url}/api/reference-data/instrument/{symbol}",
            timeout=settings.agent_timeout_seconds
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": f"Failed to fetch reference data: {str(e)}"}


def get_broker_confirm(trade_id: str) -> Dict[str, Any]:
    """Fetch broker confirmation"""
    try:
        response = requests.get(
            f"{settings.mock_api_base_url}/api/broker/confirms/{trade_id}",
            timeout=settings.agent_timeout_seconds
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": f"Failed to fetch broker confirm: {str(e)}"}


def enrich_case(break_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enrich break with all relevant data sources
    
    Args:
        break_data: Break data to enrich
    
    Returns:
        Enriched data from all sources
    """
    enriched = {}
    entities = break_data.get("entities", {})
    
    # Fetch OMS data
    if entities.get("order_ids"):
        enriched["oms_data"] = get_oms_data(entities["order_ids"][0])
    
    # Fetch trade capture data
    if entities.get("trade_ids"):
        enriched["trade_capture_data"] = get_trade_capture(entities["trade_ids"][0])
        enriched["broker_confirm_data"] = get_broker_confirm(entities["trade_ids"][0])
    
    # Fetch settlement and custodian data
    if entities.get("account"):
        enriched["settlement_data"] = get_settlement(entities["account"])
        enriched["custodian_data"] = get_custodian_data(entities["account"])
    
    # Fetch reference data
    if entities.get("instrument"):
        enriched["reference_data"] = get_reference_data(entities["instrument"])
    
    return enriched


ENRICHMENT_TOOLS = {
    "get_oms_data": {
        "function": get_oms_data,
        "description": "Fetch OMS order data",
        "parameters": {"order_id": {"type": "string"}}
    },
    "get_trade_capture": {
        "function": get_trade_capture,
        "description": "Fetch trade capture data",
        "parameters": {"trade_id": {"type": "string"}}
    },
    "get_settlement": {
        "function": get_settlement,
        "description": "Fetch settlement data",
        "parameters": {"account": {"type": "string"}}
    },
    "get_custodian_data": {
        "function": get_custodian_data,
        "description": "Fetch custodian holdings",
        "parameters": {"account": {"type": "string"}}
    },
    "get_reference_data": {
        "function": get_reference_data,
        "description": "Fetch instrument reference data",
        "parameters": {"symbol": {"type": "string"}}
    },
    "get_broker_confirm": {
        "function": get_broker_confirm,
        "description": "Fetch broker confirmation",
        "parameters": {"trade_id": {"type": "string"}}
    },
    "enrich_case": {
        "function": enrich_case,
        "description": "Enrich break with all relevant data",
        "parameters": {"break_data": {"type": "object"}}
    }
}
