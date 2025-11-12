"""
Agent 5: Pattern & Root-Cause Intelligence Agent
Learns from history to infer probable causes
"""
from agents.base_agent import BaseReconAgent
from mcp.tools.pattern_tools import PATTERN_TOOLS
from typing import Dict, Any


class PatternIntelligenceAgent(BaseReconAgent):
    """Agent responsible for pattern analysis and root cause prediction"""
    
    def __init__(self, message_bus=None):
        super().__init__(
            agent_name="pattern_intelligence",
            agent_description="Learns from historical patterns to infer probable root causes and suggest fixes",
            tools=PATTERN_TOOLS,
            message_bus=message_bus
        )
    
    def analyze_patterns(
        self,
        break_data: Dict[str, Any],
        rules_evaluation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze patterns and predict root cause
        
        Args:
            break_data: Break data
            rules_evaluation: Rules evaluation
        
        Returns:
            Pattern analysis with root cause and fix suggestion
        """
        # Get historical patterns
        get_patterns_func = self.tools["get_historical_patterns"]["function"]
        patterns = get_patterns_func(
            break_type=break_data.get("break_type"),
            limit=20
        )
        
        # Predict root cause
        predict_func = self.tools["predict_root_cause"]["function"]
        prediction = predict_func(break_data, rules_evaluation, patterns)
        
        # Suggest fix
        suggest_func = self.tools["suggest_fix"]["function"]
        fix_suggestion = suggest_func(
            prediction.get("probable_root_cause"),
            break_data
        )
        
        return {
            "break_id": break_data.get("break_id"),
            "ml_insights": prediction,
            "fix_suggestion": fix_suggestion,
            "historical_patterns_count": len(patterns) if isinstance(patterns, list) else 0,
            "status": "ANALYZED"
        }
