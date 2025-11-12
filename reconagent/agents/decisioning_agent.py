"""
Agent 6: Decisioning Agent
Combines insights and makes final decision
"""
from agents.base_agent import BaseReconAgent
from mcp.tools.decision_tools import DECISION_TOOLS
from typing import Dict, Any


class DecisioningAgent(BaseReconAgent):
    """Agent responsible for final decision making"""
    
    def __init__(self, message_bus=None):
        super().__init__(
            agent_name="decisioning",
            agent_description="Combines rule outcomes, ML insights, and firm policies to decide: Auto-Resolve, HIL Review, or Escalate",
            tools=DECISION_TOOLS,
            message_bus=message_bus
        )
    
    def make_decision(
        self,
        break_data: Dict[str, Any],
        rules_evaluation: Dict[str, Any],
        ml_insights: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Make final decision on break resolution
        
        Args:
            break_data: Break data
            rules_evaluation: Rules evaluation
            ml_insights: ML insights
        
        Returns:
            Final decision with action and explanation
        """
        # Calculate risk score
        calc_risk_func = self.tools["calculate_risk_score"]["function"]
        risk_score = calc_risk_func(break_data, rules_evaluation, ml_insights)
        
        # Evaluate decision
        evaluate_func = self.tools["evaluate_decision"]["function"]
        decision = evaluate_func(break_data, rules_evaluation, ml_insights, risk_score)
        
        # Determine action
        action_func = self.tools["determine_action"]["function"]
        action_description = action_func(decision)
        
        return {
            "break_id": break_data.get("break_id"),
            "decision": decision,
            "action_description": action_description,
            "status": "DECIDED"
        }
