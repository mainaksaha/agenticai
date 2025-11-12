"""
Agent 1: Break Ingestion Agent
Normalizes incoming reconciliation breaks
"""
from agents.base_agent import BaseReconAgent
from mcp.tools.break_tools import BREAK_TOOLS
from typing import Dict, Any


class BreakIngestionAgent(BaseReconAgent):
    """Agent responsible for ingesting and normalizing breaks"""
    
    def __init__(self, message_bus=None):
        super().__init__(
            agent_name="break_ingestion",
            agent_description="Normalizes incoming reconciliation breaks and validates data completeness",
            tools=BREAK_TOOLS,
            message_bus=message_bus
        )
    
    def ingest_break(self, break_id: str = None, raw_break: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Main entry point for break ingestion
        
        Args:
            break_id: Break ID to fetch, or
            raw_break: Raw break data to normalize
        
        Returns:
            Normalized and validated break
        """
        # Fetch break if ID provided
        if break_id:
            get_break_func = self.tools["get_break_by_id"]["function"]
            raw_break = get_break_func(break_id)
        
        if not raw_break:
            return {"error": "No break data provided"}
        
        # Check for API errors
        if "error" in raw_break:
            return raw_break
        
        # Normalize break
        normalize_func = self.tools["normalize_break"]["function"]
        normalized = normalize_func(raw_break)
        
        if "error" in normalized:
            return normalized
        
        # Validate break
        validate_func = self.tools["validate_break"]["function"]
        validation = validate_func(normalized)
        
        return {
            "break_data": normalized,
            "validation": validation,
            "status": "INGESTED" if validation.get("is_valid") else "VALIDATION_FAILED"
        }
    
    def ingest_multiple_breaks(self, limit: int = 10, break_type: str = None) -> Dict[str, Any]:
        """
        Ingest multiple breaks
        
        Args:
            limit: Number of breaks to ingest
            break_type: Optional filter
        
        Returns:
            Ingestion results
        """
        get_breaks_func = self.tools["get_breaks"]["function"]
        breaks = get_breaks_func(limit=limit, break_type=break_type)
        
        if "error" in breaks:
            return breaks
        
        results = []
        for raw_break in breaks:
            result = self.ingest_break(raw_break=raw_break)
            results.append(result)
        
        return {
            "total": len(results),
            "successful": sum(1 for r in results if r.get("status") == "INGESTED"),
            "failed": sum(1 for r in results if r.get("status") == "VALIDATION_FAILED"),
            "results": results
        }
