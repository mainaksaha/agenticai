"""
Test for end-to-end workflow
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from orchestrator.workflow import ReconciliationOrchestrator


def test_single_break():
    """Test processing a single break"""
    print("\n[Test] Testing single break processing...")
    
    orchestrator = ReconciliationOrchestrator()
    
    # Create a sample break
    sample_break = {
        "break_id": "TEST-BRK-001",
        "break_type": "TRADE_OMS_MISMATCH",
        "status": "NEW",
        "system_a": {
            "system_name": "OMS",
            "quantity": 1000.0,
            "amount": 150000.0,
            "price": 150.0,
            "currency": "USD"
        },
        "system_b": {
            "system_name": "Trade Capture",
            "quantity": 1000.0,
            "amount": 150005.0,
            "price": 150.005,
            "currency": "USD"
        },
        "entities": {
            "instrument": "AAPL",
            "account": "ACC-12345",
            "broker": "XYZ Broker",
            "trade_ids": ["T123456"],
            "order_ids": ["O987654"]
        },
        "date": "2025-11-09T00:00:00",
        "source": "Test"
    }
    
    result = orchestrator.process_break(raw_break=sample_break)
    
    assert result is not None
    assert "case" in result
    assert "decision" in result["case"]
    assert result["case"]["decision"]["action"] in ["AUTO_RESOLVE", "HIL_REVIEW", "ESCALATE"]
    
    print(f"✓ Test passed!")
    print(f"  Decision: {result['case']['decision']['action']}")
    print(f"  Risk Score: {result['case']['decision']['risk_score']:.2f}")
    
    return result


if __name__ == "__main__":
    test_single_break()
    print("\n[Test] All tests passed! ✓")
