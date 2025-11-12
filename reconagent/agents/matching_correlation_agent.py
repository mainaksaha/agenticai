"""
Agent 3: Matching & Correlation Agent
Identifies candidate matches and correlations
"""
from agents.base_agent import BaseReconAgent
from mcp.tools.matching_tools import MATCHING_TOOLS
from typing import Dict, Any, List


class MatchingCorrelationAgent(BaseReconAgent):
    """Agent responsible for finding and correlating matches"""
    
    def __init__(self, message_bus=None):
        super().__init__(
            agent_name="matching_correlation",
            agent_description="Identifies candidate matches through partial fills, aggregated trades, and cross-system ID mapping",
            tools=MATCHING_TOOLS,
            message_bus=message_bus
        )
    
    def find_matches(
        self,
        break_data: Dict[str, Any],
        enriched_data: Dict[str, Any],
        threshold: float = 0.7
    ) -> Dict[str, Any]:
        """
        Find matching candidates
        
        Args:
            break_data: Break data
            enriched_data: Enriched data
            threshold: Similarity threshold
        
        Returns:
            Match candidates and correlation
        """
        find_func = self.tools["find_match_candidates"]["function"]
        candidates = find_func(break_data, enriched_data, threshold)
        
        correlate_func = self.tools["correlate_trades"]["function"]
        correlation = correlate_func(candidates)
        
        return {
            "break_id": break_data.get("break_id"),
            "match_candidates": candidates,
            "num_candidates": len(candidates),
            "correlation": correlation,
            "status": "MATCHED" if candidates else "NO_MATCHES"
        }
