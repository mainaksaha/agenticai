"""
Matching Agent - Google ADK Implementation  
Identifies candidate matches and correlates trades
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from typing import Dict, Any
from orchestrator_adk.agent_base import ADKAgent, ADKAgentConfig, ADKTool
from mcp.tools import matching_tools


class MatchingAgent(ADKAgent):
    """ADK Agent for matching and correlation"""
    
    def __init__(self):
        tools = [
            ADKTool(
                name="calculate_similarity",
                description="Calculate similarity score between two records",
                function=matching_tools.calculate_similarity,
                parameters={
                    "record1": {"type": "object", "description": "First record"},
                    "record2": {"type": "object", "description": "Second record"}
                }
            ),
            ADKTool(
                name="find_match_candidates",
                description="Find matching candidates for a break",
                function=matching_tools.find_match_candidates,
                parameters={
                    "break_data": {"type": "object", "description": "Break data"},
                    "enriched_data": {"type": "object", "description": "Enriched data"}
                }
            ),
            ADKTool(
                name="correlate_trades",
                description="Correlate trades across systems",
                function=matching_tools.correlate_trades,
                parameters={
                    "break_data": {"type": "object", "description": "Break data"},
                    "candidates": {"type": "array", "description": "Match candidates"}
                }
            )
        ]
        
        config = ADKAgentConfig(
            name="matching_correlation",
            description="Identifies candidate matches and correlates trades",
            model="gemini-2.0-flash-exp",
            tools=tools,
            instructions="""You are the Matching & Correlation Agent.
Your responsibilities:
1. Calculate similarity scores between records
2. Find matching candidates from enriched data
3. Correlate trades across different systems
4. Identify relationships (1:1, 1:N, N:1, N:M)

Use fuzzy matching and similarity algorithms to find matches."""
        )
        
        super().__init__(config)
    
    async def find_matches(self, break_data: Dict[str, Any], enriched_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Find matching candidates
        
        Args:
            break_data: Break data
            enriched_data: Enriched contextual data
        
        Returns:
            Match candidates with similarity scores
        """
        task = {
            'action': 'find_match_candidates',
            'parameters': {
                'break_data': break_data,
                'enriched_data': enriched_data
            }
        }
        
        result = await self.process(task)
        
        if result['success']:
            candidates = result['result'].get('match_candidates', [])
            
            # Correlate trades
            correlate_task = {
                'action': 'correlate_trades',
                'parameters': {
                    'break_data': break_data,
                    'candidates': candidates
                }
            }
            
            correlate_result = await self.process(correlate_task)
            
            return {
                'success': True,
                'match_candidates': candidates,
                'correlation': correlate_result.get('result', {})
            }
        else:
            return result
