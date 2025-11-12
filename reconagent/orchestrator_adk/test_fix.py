"""
Quick test to verify the parameter mismatch fix
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
from orchestrator_adk.agents.rules import RulesAgent

async def test_rules_agent():
    print("Testing RulesAgent with parameter handling fix...")
    
    agent = RulesAgent()
    print(f"✓ Agent created: {agent.name}")
    
    # Test data
    break_data = {
        "break_id": "TEST-001",
        "system_a": {"amount": 1000.0},
        "system_b": {"amount": 1001.0}
    }
    
    enriched_data = {
        "oms_data": {},
        "trade_capture": {}
    }
    
    # Call evaluate_rules
    print("\nCalling evaluate_rules...")
    try:
        result = await agent.evaluate_rules(break_data, enriched_data)
        print(f"✓ Success: {result.get('success')}")
        if result.get('rules_evaluation'):
            print(f"  Rules within tolerance: {result['rules_evaluation'].get('within_tolerance')}")
        if result.get('error'):
            print(f"  Error: {result['error']}")
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_rules_agent())
