"""
Data Enrichment Agent - Google ADK Implementation
Gathers contextual data from multiple sources
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from typing import Dict, Any
from orchestrator_adk.agent_base import ADKAgent, ADKAgentConfig, ADKTool
from mcp.tools import enrichment_tools


class DataEnrichmentAgent(ADKAgent):
    """ADK Agent for data enrichment"""
    
    def __init__(self):
        tools = [
            ADKTool(
                name="get_oms_data",
                description="Fetch OMS order data",
                function=enrichment_tools.get_oms_data,
                parameters={
                    "order_id": {"type": "string", "description": "Order ID"}
                }
            ),
            ADKTool(
                name="get_trade_capture",
                description="Fetch trade capture data",
                function=enrichment_tools.get_trade_capture,
                parameters={
                    "trade_id": {"type": "string", "description": "Trade ID"}
                }
            ),
            ADKTool(
                name="get_settlement",
                description="Fetch settlement data",
                function=enrichment_tools.get_settlement,
                parameters={
                    "account": {"type": "string", "description": "Account ID"}
                }
            ),
            ADKTool(
                name="get_custodian_data",
                description="Fetch custodian holdings",
                function=enrichment_tools.get_custodian_data,
                parameters={
                    "account": {"type": "string", "description": "Account ID"}
                }
            ),
            ADKTool(
                name="get_reference_data",
                description="Fetch instrument reference data",
                function=enrichment_tools.get_reference_data,
                parameters={
                    "symbol": {"type": "string", "description": "Instrument symbol"}
                }
            ),
            ADKTool(
                name="get_broker_confirm",
                description="Fetch broker confirmation",
                function=enrichment_tools.get_broker_confirm,
                parameters={
                    "trade_id": {"type": "string", "description": "Trade ID"}
                }
            ),
            ADKTool(
                name="enrich_case",
                description="Enrich break with all relevant data",
                function=enrichment_tools.enrich_case,
                parameters={
                    "break_data": {"type": "object", "description": "Break data"}
                }
            )
        ]
        
        config = ADKAgentConfig(
            name="data_enrichment",
            description="Gathers contextual data from multiple sources",
            model="gemini-2.0-flash-exp",
            tools=tools,
            instructions="""You are the Data Enrichment Agent.
Your responsibilities:
1. Fetch OMS order data
2. Fetch trade capture data
3. Fetch settlement positions
4. Fetch custodian holdings
5. Fetch reference data
6. Fetch broker confirmations
7. Build complete context for reconciliation

Gather data from all relevant sources to build a complete picture."""
        )
        
        super().__init__(config)
    
    async def enrich_break(self, break_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich break with contextual data
        
        Args:
            break_data: Normalized break data
        
        Returns:
            Enriched break data with context
        """
        task = {
            'action': 'enrich_case',
            'parameters': {'break_data': break_data}
        }
        
        result = await self.process(task)
        
        if result['success']:
            return {
                'success': True,
                'enriched_data': result['result'].get('enriched_data', {}),
                'sources_successful': result['result'].get('sources_successful', 0)
            }
        else:
            return result
