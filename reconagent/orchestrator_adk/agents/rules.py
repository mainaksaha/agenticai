"""
Rules Agent - Google ADK Implementation
Applies business rules and tolerance checks
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from typing import Dict, Any
from orchestrator_adk.agent_base import ADKAgent, ADKAgentConfig, ADKTool
from mcp.tools import rules_tools


class RulesAgent(ADKAgent):
    """ADK Agent for rules and tolerance checking"""
    
    def __init__(self):
        tools = [
            ADKTool(
                name="check_tolerance",
                description="Check if break is within tolerance limits",  
                function=rules_tools.apply_business_rules,  # Use apply_business_rules which accepts break_data and enriched_data
                parameters={
                    "break_data": {"type": "object", "description": "Break data"},
                    "enriched_data": {"type": "object", "description": "Enriched data"}
                }
            ),
            ADKTool(
                name="apply_business_rules",
                description="Apply business rules to break",
                function=rules_tools.apply_business_rules,
                parameters={
                    "break_data": {"type": "object", "description": "Break data"},
                    "enriched_data": {"type": "object", "description": "Enriched data"}
                }
            ),
            ADKTool(
                name="validate_rules",
                description="Validate critical business rules",
                function=rules_tools.validate_rules,
                parameters={
                    "break_data": {"type": "object", "description": "Break data"},
                    "rules_evaluation": {"type": "object", "description": "Rules evaluation"}
                }
            )
        ]
        
        config = ADKAgentConfig(
            name="rules_tolerance",
            description="Applies business rules and tolerance checks",
            model="gemini-2.0-flash-exp",
            tools=tools,
            instructions="""You are the Rules & Tolerance Agent.
Your responsibilities:
1. Check tolerance limits (amount, quantity, FX)
2. Apply business rules (timing, status, lifecycle)
3. Validate critical compliance rules
4. Determine if break can be auto-resolved

Be strict with compliance rules but flexible with operational tolerances."""
        )
        
        super().__init__(config)
    
    async def evaluate_rules(self, break_data: Dict[str, Any], enriched_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate rules and tolerances
        
        Args:
            break_data: Break data
            enriched_data: Enriched contextual data
        
        Returns:
            Rules evaluation results
        """
        # Check tolerance
        tolerance_task = {
            'action': 'check_tolerance',
            'parameters': {
                'break_data': break_data,
                'enriched_data': enriched_data
            }
        }
        
        tolerance_result = await self.process(tolerance_task)
        
        if not tolerance_result['success']:
            return tolerance_result
        
        # Apply business rules
        rules_task = {
            'action': 'apply_business_rules',
            'parameters': {
                'break_data': break_data,
                'enriched_data': enriched_data
            }
        }
        
        rules_result = await self.process(rules_task)
        
        if rules_result['success']:
            rules_eval = rules_result['result'].get('rules_evaluation', {})
            
            # Validate critical rules
            validate_task = {
                'action': 'validate_rules',
                'parameters': {
                    'break_data': break_data,
                    'rules_evaluation': rules_eval
                }
            }
            
            validate_result = await self.process(validate_task)
            
            # Handle result - might be dict or bool
            if validate_result.get('success'):
                result_data = validate_result.get('result', {})
                if isinstance(result_data, dict):
                    all_critical_passed = result_data.get('all_critical_passed', False)
                else:
                    # If result is boolean, use it directly
                    all_critical_passed = bool(result_data)
            else:
                all_critical_passed = False
            
            return {
                'success': True,
                'rules_evaluation': rules_eval,
                'all_critical_rules_passed': all_critical_passed
            }
        else:
            return rules_result
