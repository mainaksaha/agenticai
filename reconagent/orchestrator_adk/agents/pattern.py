"""
Pattern Intelligence Agent - Google ADK Implementation
Learns from history to infer probable causes
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from typing import Dict, Any
from orchestrator_adk.agent_base import ADKAgent, ADKAgentConfig, ADKTool
from mcp.tools import pattern_tools


class PatternAgent(ADKAgent):
    """ADK Agent for pattern intelligence and root cause analysis"""
    
    def __init__(self):
        tools = [
            ADKTool(
                name="get_historical_patterns",
                description="Get historical pattern data for similar breaks",
                function=pattern_tools.get_historical_patterns,
                parameters={
                    "break_type": {"type": "string", "description": "Break type"},
                    "instrument": {"type": "string", "description": "Instrument symbol"}
                }
            ),
            ADKTool(
                name="predict_root_cause",
                description="Predict root cause using ML/patterns",
                function=pattern_tools.predict_root_cause,
                parameters={
                    "break_data": {"type": "object", "description": "Break data"},
                    "historical_patterns": {"type": "array", "description": "Historical patterns"}
                }
            ),
            ADKTool(
                name="suggest_fix",
                description="Suggest fix based on patterns",
                function=pattern_tools.suggest_fix,
                parameters={
                    "break_data": {"type": "object", "description": "Break data"},
                    "root_cause": {"type": "string", "description": "Predicted root cause"}
                }
            )
        ]
        
        config = ADKAgentConfig(
            name="pattern_intelligence",
            description="Learns from history to infer probable causes using ML",
            model="gemini-2.0-flash-exp",
            tools=tools,
            instructions="""You are the Pattern & Root-Cause Intelligence Agent.
Your responsibilities:
1. Analyze historical patterns for similar breaks
2. Use ML to predict root cause
3. Suggest fixes based on past resolutions
4. Provide confidence scores

Learn from history to identify recurring patterns and root causes."""
        )
        
        super().__init__(config)
    
    async def analyze_patterns(self, break_data: Dict[str, Any], rules_evaluation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze patterns and predict root cause
        
        Args:
            break_data: Break data
            rules_evaluation: Rules evaluation results
        
        Returns:
            ML insights with root cause prediction
        """
        # Get historical patterns
        patterns_task = {
            'action': 'get_historical_patterns',
            'parameters': {
                'break_type': break_data.get('break_type'),
                'instrument': break_data.get('entities', {}).get('instrument', '')
            }
        }
        
        patterns_result = await self.process(patterns_task)
        
        if not patterns_result['success']:
            return patterns_result
        
        historical_patterns = patterns_result['result'].get('patterns', [])
        
        # Predict root cause
        predict_task = {
            'action': 'predict_root_cause',
            'parameters': {
                'break_data': break_data,
                'historical_patterns': historical_patterns
            }
        }
        
        predict_result = await self.process(predict_task)
        
        if not predict_result['success']:
            return predict_result
        
        root_cause = predict_result['result'].get('root_cause', 'unknown')
        confidence = predict_result['result'].get('confidence', 0.5)
        
        # Suggest fix
        fix_task = {
            'action': 'suggest_fix',
            'parameters': {
                'break_data': break_data,
                'root_cause': root_cause
            }
        }
        
        fix_result = await self.process(fix_task)
        
        return {
            'success': True,
            'ml_insights': {
                'root_cause': root_cause,
                'confidence': confidence,
                'suggested_fix': fix_result['result'].get('suggested_fix', ''),
                'historical_support': len(historical_patterns)
            }
        }
