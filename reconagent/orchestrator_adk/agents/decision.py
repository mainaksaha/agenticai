"""
Decision Agent - Google ADK Implementation
Combines insights and makes final decision
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from typing import Dict, Any
from orchestrator_adk.agent_base import ADKAgent, ADKAgentConfig, ADKTool
from mcp.tools import decision_tools


class DecisionAgent(ADKAgent):
    """ADK Agent for final decisioning"""
    
    def __init__(self):
        tools = [
            ADKTool(
                name="calculate_risk_score",
                description="Calculate risk score for break",
                function=decision_tools.calculate_risk_score,
                parameters={
                    "break_data": {"type": "object", "description": "Break data"},
                    "enriched_data": {"type": "object", "description": "Enriched data"},
                    "rules_evaluation": {"type": "object", "description": "Rules evaluation"},
                    "ml_insights": {"type": "object", "description": "ML insights"}
                }
            ),
            ADKTool(
                name="evaluate_decision",
                description="Evaluate decision based on all inputs",
                function=decision_tools.evaluate_decision,
                parameters={
                    "break_data": {"type": "object", "description": "Break data"},
                    "risk_score": {"type": "number", "description": "Risk score"},
                    "rules_evaluation": {"type": "object", "description": "Rules evaluation"},
                    "ml_insights": {"type": "object", "description": "ML insights"}
                }
            ),
            ADKTool(
                name="determine_action",
                description="Determine final action (AUTO_RESOLVE/HIL_REVIEW/ESCALATE)",
                function=decision_tools.determine_action,
                parameters={
                    "decision_evaluation": {"type": "object", "description": "Decision evaluation"}
                }
            )
        ]
        
        config = ADKAgentConfig(
            name="decisioning",
            description="Combines insights and makes final decision",
            model="gemini-2.0-flash-exp",
            tools=tools,
            instructions="""You are the Decisioning Agent.
Your responsibilities:
1. Calculate comprehensive risk score
2. Evaluate all inputs (rules, patterns, matches)
3. Determine final action (AUTO_RESOLVE, HIL_REVIEW, ESCALATE)
4. Provide clear explanation and confidence

Balance automation with safety - escalate when uncertain."""
        )
        
        super().__init__(config)
    
    async def make_decision(
        self,
        break_data: Dict[str, Any],
        enriched_data: Dict[str, Any],
        matching_result: Dict[str, Any],
        rules_result: Dict[str, Any],
        pattern_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Make final decision
        
        Args:
            break_data: Break data
            enriched_data: Enriched data
            matching_result: Matching results
            rules_result: Rules evaluation
            pattern_result: Pattern analysis
        
        Returns:
            Final decision with action
        """
        # Calculate risk score
        risk_task = {
            'action': 'calculate_risk_score',
            'parameters': {
                'break_data': break_data,
                'enriched_data': enriched_data,
                'rules_evaluation': rules_result.get('rules_evaluation', {}),
                'ml_insights': pattern_result.get('ml_insights', {})
            }
        }
        
        risk_result = await self.process(risk_task)
        
        if not risk_result['success']:
            return risk_result
        
        risk_score = risk_result['result'].get('risk_score', 0.5)
        
        # Evaluate decision
        eval_task = {
            'action': 'evaluate_decision',
            'parameters': {
                'break_data': break_data,
                'risk_score': risk_score,
                'rules_evaluation': rules_result.get('rules_evaluation', {}),
                'ml_insights': pattern_result.get('ml_insights', {})
            }
        }
        
        eval_result = await self.process(eval_task)
        
        if not eval_result['success']:
            return eval_result
        
        # Determine action
        action_task = {
            'action': 'determine_action',
            'parameters': {
                'decision_evaluation': eval_result['result']
            }
        }
        
        action_result = await self.process(action_task)
        
        if action_result['success']:
            return {
                'success': True,
                'decision': action_result['result'].get('decision', {}),
                'risk_score': risk_score
            }
        else:
            return action_result
