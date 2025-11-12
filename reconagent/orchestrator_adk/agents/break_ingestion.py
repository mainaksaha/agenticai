"""
Break Ingestion Agent - Google ADK Implementation
Normalizes and validates incoming reconciliation breaks
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from typing import Dict, Any
from orchestrator_adk.agent_base import ADKAgent, ADKAgentConfig, ADKTool
from mcp.tools import break_tools


class BreakIngestionAgent(ADKAgent):
    """
    ADK Agent for break ingestion
    
    Official ADK Pattern:
    class MyAgent(google.adk.Agent):
        name = "agent_name"
        description = "..."
        tools = [...]
    """
    
    def __init__(self):
        # Define tools following ADK pattern
        tools = [
            ADKTool(
                name="get_breaks",
                description="Fetch breaks from the API",
                function=break_tools.get_breaks,
                parameters={
                    "limit": {"type": "integer", "description": "Number of breaks to fetch"}
                }
            ),
            ADKTool(
                name="get_break_by_id",
                description="Fetch a specific break by ID",
                function=break_tools.get_break_by_id,
                parameters={
                    "break_id": {"type": "string", "description": "Break ID to fetch"}
                }
            ),
            ADKTool(
                name="normalize_break",
                description="Normalize break data to standard format",
                function=break_tools.normalize_break,
                parameters={
                    "raw_break": {"type": "object", "description": "Raw break data"}
                }
            ),
            ADKTool(
                name="validate_break",
                description="Validate break data completeness",
                function=break_tools.validate_break,
                parameters={
                    "break_data": {"type": "object", "description": "Break data to validate"}
                }
            )
        ]
        
        config = ADKAgentConfig(
            name="break_ingestion",
            description="Normalizes and validates incoming reconciliation breaks",
            model="gemini-2.0-flash-exp",
            tools=tools,
            instructions="""You are the Break Ingestion Agent in a reconciliation system.
Your responsibilities:
1. Fetch breaks from the API
2. Normalize break data to standard format
3. Validate break data completeness
4. Ensure all required fields are present

Always validate breaks before passing to next agent."""
        )
        
        super().__init__(config)
    
    async def ingest_break(self, break_id: str = None, raw_break: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        High-level method to ingest a break
        
        Args:
            break_id: Break ID to fetch, or
            raw_break: Raw break data
        
        Returns:
            Normalized and validated break data
        """
        # Fetch break if only ID provided
        if break_id and not raw_break:
            task = {
                'action': 'get_break_by_id',
                'parameters': {'break_id': break_id}
            }
            fetch_result = await self.process(task)
            if not fetch_result['success']:
                return fetch_result
            raw_break = fetch_result['result']
        
        # Normalize break
        task = {
            'action': 'normalize_break',
            'parameters': {'raw_break': raw_break}
        }
        normalize_result = await self.process(task)
        if not normalize_result['success']:
            return normalize_result
        
        break_data = normalize_result['result']
        
        # Validate break
        task = {
            'action': 'validate_break',
            'parameters': {'break_data': break_data}
        }
        validate_result = await self.process(task)
        
        if validate_result['success'] and validate_result['result'].get('valid'):
            return {
                'success': True,
                'break_data': break_data,
                'validation': validate_result['result']
            }
        else:
            return {
                'success': False,
                'error': 'Break validation failed',
                'details': validate_result
            }
