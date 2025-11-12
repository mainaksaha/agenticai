"""
Test Google ADK Implementation
Tests ADK agents, A2A protocol, and LangGraph orchestration
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from orchestrator_adk.orchestrator import ADKReconciliationOrchestrator


def test_adk_orchestrator():
    """Test the complete ADK orchestrator"""
    print("\n" + "="*80)
    print("TEST: Google ADK Orchestrator")
    print("="*80)
    
    # Initialize orchestrator
    orchestrator = ADKReconciliationOrchestrator()
    
    # Test 1: Process a break
    print("\n[Test 1] Processing break with ADK + A2A + LangGraph")
    print("-"*80)
    
    result = orchestrator.process_break(break_id="BRK-001")
    
    print("\n[Test 1] Results:")
    print(f"  Success: {result['success']}")
    print(f"  Break ID: {result['break_id']}")
    print(f"  Execution Path: {' → '.join(result['execution_path'])}")
    print(f"  Decision: {result['decision'].get('action', 'N/A')}")
    print(f"  A2A Context: {result['a2a_context']}")
    print(f"  A2A Messages: {len(result['a2a_messages'])} messages")
    print(f"  Duration: {result['duration_ms']:.0f}ms")
    
    if result['errors']:
        print(f"  Errors: {result['errors']}")
    
    # Test 2: Agent information
    print("\n[Test 2] Agent Information")
    print("-"*80)
    
    agents_info = orchestrator.get_agent_info()
    for name, info in agents_info.items():
        print(f"\nAgent: {info['name']}")
        print(f"  Description: {info['description']}")
        print(f"  Model: {info['model']}")
        print(f"  Tools: {', '.join(info['tools'])}")
    
    print("\n" + "="*80)
    print("✅ Tests complete!")
    print("="*80)


if __name__ == "__main__":
    test_adk_orchestrator()
