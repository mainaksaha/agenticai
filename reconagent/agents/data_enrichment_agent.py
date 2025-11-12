"""
Agent 2: Data Enrichment Agent
Gathers details from multiple data sources
"""
from agents.base_agent import BaseReconAgent
from mcp.tools.enrichment_tools import ENRICHMENT_TOOLS
from typing import Dict, Any


class DataEnrichmentAgent(BaseReconAgent):
    """Agent responsible for enriching breaks with contextual data"""
    
    def __init__(self, message_bus=None):
        super().__init__(
            agent_name="data_enrichment",
            agent_description="Gathers details from OMS, trade capture, settlement, custodian, and reference data sources",
            tools=ENRICHMENT_TOOLS,
            message_bus=message_bus
        )
    
    def enrich_break(self, break_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich break with all available data sources
        
        Args:
            break_data: Normalized break data
        
        Returns:
            Enriched data from all sources
        """
        enrich_func = self.tools["enrich_case"]["function"]
        enriched = enrich_func(break_data)
        
        # Count successful enrichments
        successful_sources = sum(
            1 for key, value in enriched.items()
            if isinstance(value, dict) and "error" not in value
        )
        
        return {
            "break_id": break_data.get("break_id"),
            "enriched_data": enriched,
            "sources_fetched": len(enriched),
            "sources_successful": successful_sources,
            "status": "ENRICHED" if successful_sources > 0 else "ENRICHMENT_FAILED"
        }
