"""
Test Dynamic Orchestrator v2
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from orchestrator.v2.dynamic_orchestrator import DynamicReconciliationOrchestrator


def test_single_break():
    """Test processing a single break with dynamic orchestration"""
    print("\n" + "="*80)
    print("TEST: Single Break Processing with Dynamic Orchestrator v2")
    print("="*80 + "\n")
    
    # Initialize orchestrator
    orchestrator = DynamicReconciliationOrchestrator()
    
    # Process a break
    result = orchestrator.process_break(break_id="BRK-001")
    
    # Print results
    print("\n" + "="*80)
    print("RESULT SUMMARY")
    print("="*80)
    print(f"Break ID: {result.get('break_id')}")
    print(f"Break Type: {result['break_profile']['break_type']}")
    print(f"Risk Tier: {result['break_profile']['risk_tier']}")
    print(f"Exposure: ${result['break_profile']['exposure']:,.2f}")
    print(f"\nExecution:")
    print(f"  Agents Planned: {result['execution_plan']['agents_planned']}")
    print(f"  Agents Invoked: {result['execution_plan']['agents_invoked']}")
    print(f"  Agents Skipped: {result['execution_plan']['agents_skipped']}")
    print(f"  Efficiency: {result['performance']['efficiency']}")
    print(f"  Early Exit: {result['performance']['early_exit']}")
    print(f"  Duration: {result['performance']['total_duration_ms']:.0f}ms")
    print(f"\nDecision:")
    print(f"  Action: {result['decision']['action']}")
    print(f"  Explanation: {result['decision'].get('explanation', 'N/A')}")
    print("="*80 + "\n")
    
    return result


def test_multiple_breaks():
    """Test processing multiple breaks"""
    print("\n" + "="*80)
    print("TEST: Multiple Breaks Processing with Dynamic Orchestrator v2")
    print("="*80 + "\n")
    
    # Initialize orchestrator
    orchestrator = DynamicReconciliationOrchestrator()
    
    # Process multiple breaks
    results = orchestrator.process_multiple_breaks(limit=5)
    
    # Summary already printed by orchestrator
    return results


def test_policy_info():
    """Test policy information retrieval"""
    print("\n" + "="*80)
    print("TEST: Policy Information")
    print("="*80 + "\n")
    
    orchestrator = DynamicReconciliationOrchestrator()
    
    policy_info = orchestrator.get_policy_info()
    
    print("Loaded Policies:")
    print(f"  Break Types: {len(policy_info['break_types'])}")
    for break_type, risk_tiers in policy_info['policies'].items():
        print(f"    - {break_type}: {', '.join(risk_tiers)}")
    print("\n" + "="*80 + "\n")


def compare_v1_vs_v2():
    """Compare v1 (sequential) vs v2 (dynamic) orchestrators"""
    print("\n" + "="*80)
    print("COMPARISON: v1 (Sequential) vs v2 (Dynamic)")
    print("="*80 + "\n")
    
    # Test v1
    print("[Testing v1 - Sequential Orchestrator]")
    from orchestrator.workflow import ReconciliationOrchestrator
    orch_v1 = ReconciliationOrchestrator()
    
    import time
    start = time.time()
    result_v1 = orch_v1.process_break(break_id="BRK-001")
    v1_time = (time.time() - start) * 1000
    
    print(f"  ✓ v1 completed in {v1_time:.0f}ms")
    print(f"  ✓ Agents: 7 (all sequential)")
    
    # Test v2
    print("\n[Testing v2 - Dynamic Orchestrator]")
    orch_v2 = DynamicReconciliationOrchestrator()
    
    start = time.time()
    result_v2 = orch_v2.process_break(break_id="BRK-001")
    v2_time = (time.time() - start) * 1000
    
    print(f"  ✓ v2 completed in {v2_time:.0f}ms")
    print(f"  ✓ Agents: {result_v2['execution_plan']['agents_invoked']} invoked, "
          f"{result_v2['execution_plan']['agents_skipped']} skipped")
    
    # Comparison
    print("\n" + "="*80)
    print("COMPARISON RESULTS")
    print("="*80)
    print(f"v1 Time: {v1_time:.0f}ms")
    print(f"v2 Time: {v2_time:.0f}ms")
    
    if v2_time < v1_time:
        improvement = ((v1_time - v2_time) / v1_time) * 100
        print(f"v2 is {improvement:.1f}% faster")
    
    print(f"\nv1 Agents: 7 (sequential)")
    print(f"v2 Agents: {result_v2['execution_plan']['agents_invoked']} "
          f"({result_v2['performance']['efficiency']} efficiency)")
    
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    # Run tests
    test_policy_info()
    test_single_break()
    test_multiple_breaks()
    compare_v1_vs_v2()
    
    print("\n✅ All tests completed!")
