"""
Agent 4: Rules & Tolerance Agent
Applies business rules and tolerance checks
"""
from agents.base_agent import BaseReconAgent
from mcp.tools.rules_tools import RULES_TOOLS
from typing import Dict, Any


class RulesToleranceAgent(BaseReconAgent):
    """Agent responsible for applying business rules and tolerances"""
    
    def __init__(self, message_bus=None):
        super().__init__(
            agent_name="rules_tolerance",
            agent_description="Applies business rules including rounding, FX, known lags, and standard tolerance ranges",
            tools=RULES_TOOLS,
            message_bus=message_bus
        )
    
    def evaluate_rules(
        self,
        break_data: Dict[str, Any],
        enriched_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Evaluate business rules and tolerances
        
        Args:
            break_data: Break data
            enriched_data: Enriched data
        
        Returns:
            Rules evaluation results
        """
        apply_func = self.tools["apply_business_rules"]["function"]
        evaluation = apply_func(break_data, enriched_data)
        
        validate_func = self.tools["validate_rules"]["function"]
        is_valid = validate_func(evaluation)
        
        return {
            "break_id": break_data.get("break_id"),
            "rules_evaluation": evaluation,
            "all_critical_rules_passed": is_valid,
            "status": "RULES_PASSED" if is_valid else "RULES_FAILED"
        }
