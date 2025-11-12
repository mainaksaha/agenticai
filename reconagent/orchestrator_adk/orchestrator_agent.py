"""
Orchestrator Agent - The Intelligence Layer
This agent analyzes the break and decides which agents to invoke and in what order
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from typing import Dict, Any, List
from orchestrator_adk.agent_base import ADKAgent, ADKAgentConfig
import json


class OrchestratorAgent(ADKAgent):
    """
    Meta-agent that analyzes breaks and decides which agents to invoke
    
    This is the intelligence layer that makes the system dynamic:
    - Analyzes break type and complexity
    - Determines which agents are needed
    - Decides execution order
    - Manages conditional logic
    """
    
    def __init__(self):
        config = ADKAgentConfig(
            name="orchestrator",
            description="Intelligent orchestrator that analyzes breaks and decides which agents to invoke",
            model="gpt-4-turbo",
            tools=[],  # Orchestrator uses LLM reasoning, not tools
            instructions="""You are the Orchestrator Agent - the intelligent decision-maker in a reconciliation system.

Your responsibilities:
1. Analyze the break to understand its type, complexity, and requirements
2. Determine which specialist agents need to be invoked
3. Decide the optimal execution order
4. Apply conditional logic (some agents optional based on break characteristics)

Available specialist agents:
- break_ingestion: Normalizes and validates breaks (ALWAYS needed)
- data_enrichment: Gathers contextual data from multiple sources (ALWAYS needed)
- matching_correlation: Finds and correlates matches (needed for trade mismatches)
- rules_tolerance: Applies business rules and tolerance checks (ALWAYS needed)
- pattern_intelligence: ML-based root cause analysis (needed for complex/recurring breaks)
- decisioning: Makes final decision on action (ALWAYS needed)
- workflow_feedback: Creates tickets and captures feedback (needed if HIL_REVIEW or ESCALATE)

Decision rules:
1. ALWAYS invoke: ingestion, enrichment, rules, decision
2. CONDITIONAL - matching: Only for breaks involving trade correlation (TRADE_OMS_MISMATCH, BROKER_VS_INTERNAL, FO_VS_BO)
3. CONDITIONAL - pattern: Skip if rules pass with high confidence (>0.9), otherwise invoke for root cause
4. CONDITIONAL - workflow: Invoke if decision is HIL_REVIEW or ESCALATE

Output format (JSON):
{
    "agents_to_invoke": ["agent1", "agent2", ...],
    "execution_plan": {
        "stage1": ["agent1"],
        "stage2": ["agent2", "agent3"],
        ...
    },
    "reasoning": "Explanation of why these agents and this order",
    "skip_reasons": {
        "agent_name": "reason for skipping"
    }
}"""
        )
        
        super().__init__(config)
    
    async def analyze_and_plan(self, break_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze break and create execution plan
        
        Args:
            break_data: Break information
        
        Returns:
            Execution plan with agents to invoke
        """
        # Build analysis prompt
        prompt = f"""Analyze this reconciliation break and determine which agents to invoke:

Break Data:
{json.dumps(break_data, indent=2)}

Break Type: {break_data.get('break_type', 'UNKNOWN')}
Amount: {break_data.get('system_a', {}).get('amount', 0)} vs {break_data.get('system_b', {}).get('amount', 0)}
Status: {break_data.get('status', 'UNKNOWN')}

Analyze:
1. What type of break is this?
2. Does it need matching/correlation? (only if trade mismatch)
3. Is it complex enough to need pattern analysis?
4. What's the optimal agent sequence?

Provide your analysis and execution plan in the specified JSON format."""
        
        # Call LLM for intelligent analysis
        if self.client:
            try:
                response = await self._call_llm(prompt)
                
                # Parse LLM response
                # Try to extract JSON from response
                import re
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    plan = json.loads(json_match.group())
                else:
                    # Fallback: use default plan
                    plan = self._get_default_plan(break_data)
                
                return {
                    'success': True,
                    'plan': plan,
                    'llm_response': response
                }
            except Exception as e:
                print(f"LLM analysis failed: {e}, using default plan")
                return {
                    'success': True,
                    'plan': self._get_default_plan(break_data),
                    'error': str(e)
                }
        else:
            # No LLM available, use rule-based plan
            return {
                'success': True,
                'plan': self._get_default_plan(break_data),
                'mode': 'rule_based'
            }
    
    def _get_default_plan(self, break_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fallback rule-based execution plan
        Used when LLM is not available or fails
        """
        break_type = break_data.get('break_type', '')
        
        # Determine which agents are needed
        agents_to_invoke = ['ingestion', 'enrichment']
        skip_reasons = {}
        
        # Matching: needed for trade correlation
        if break_type in ['TRADE_OMS_MISMATCH', 'BROKER_VS_INTERNAL', 'FO_VS_BO']:
            agents_to_invoke.append('matching')
        else:
            skip_reasons['matching'] = f'Not needed for {break_type} - no trade correlation required'
        
        # Rules: always needed
        agents_to_invoke.append('rules')
        
        # Pattern: needed for complex breaks
        # Skip if it's a simple tolerance issue
        if break_type in ['SETTLEMENT_DISCREPANCY', 'FX_RATE_DIFF']:
            skip_reasons['pattern'] = 'Simple tolerance issue - rules check sufficient'
        else:
            agents_to_invoke.append('pattern')
        
        # Decision: always needed
        agents_to_invoke.append('decision')
        
        # Workflow: always add (will be conditionally executed based on decision)
        agents_to_invoke.append('workflow')
        
        return {
            'agents_to_invoke': agents_to_invoke,
            'execution_plan': {
                'stage1_ingestion': ['ingestion'],
                'stage2_enrichment': ['enrichment'],
                'stage3_matching': ['matching'] if 'matching' in agents_to_invoke else [],
                'stage4_analysis': ['rules', 'pattern'] if 'pattern' in agents_to_invoke else ['rules'],
                'stage5_decision': ['decision'],
                'stage6_workflow': ['workflow']
            },
            'reasoning': f'Rule-based plan for {break_type}: Standard flow with conditional matching and pattern analysis',
            'skip_reasons': skip_reasons
        }


def create_orchestrator_agent() -> OrchestratorAgent:
    """Factory function to create orchestrator agent"""
    return OrchestratorAgent()
