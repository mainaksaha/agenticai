"""
Main entry point for Reconciliation Agent System
"""
import asyncio
import uvicorn
from orchestrator.workflow import ReconciliationOrchestrator
from shared.config import settings


def run_example_workflow():
    """Run example reconciliation workflow"""
    print("\n" + "="*80)
    print(" Reconciliation Agent System - Example Workflow")
    print("="*80 + "\n")
    
    # Initialize orchestrator
    orchestrator = ReconciliationOrchestrator()
    
    # Example 1: Process a single break
    print("\n[Example 1] Processing a single break...")
    result = orchestrator.process_break(break_id="BRK-2025-11-12345")
    
    print(f"\nResult Summary:")
    print(f"  Break ID: {result.get('break_id')}")
    print(f"  Final Status: {result.get('final_status')}")
    print(f"  Requires HIL: {result.get('requires_hil')}")
    print(f"  Ticket ID: {result.get('ticket', {}).get('ticket_id')}")
    
    # Example 2: Process multiple breaks
    print("\n" + "="*80)
    print("\n[Example 2] Processing multiple breaks...")
    batch_result = orchestrator.process_multiple_breaks(limit=3)
    
    return batch_result


def start_mock_api_server():
    """Start the mock API server"""
    from mock_apis.main import app
    
    print(f"\nStarting Mock API Server on {settings.mock_api_host}:{settings.mock_api_port}...")
    uvicorn.run(
        app,
        host=settings.mock_api_host,
        port=settings.mock_api_port,
        log_level="info"
    )


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "mock-api":
        # Start mock API server
        start_mock_api_server()
    else:
        # Run example workflow
        run_example_workflow()
