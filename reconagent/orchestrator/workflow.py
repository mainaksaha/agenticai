"""
Orchestrator for Reconciliation Agent Workflow
Coordinates all 7 agents using A2A protocol
"""
import uuid
from typing import Dict, Any, List
from shared.a2a_protocol import MessageBus, MessagePriority
from shared.schemas import Case
from agents.break_ingestion_agent import BreakIngestionAgent
from agents.data_enrichment_agent import DataEnrichmentAgent
from agents.matching_correlation_agent import MatchingCorrelationAgent
from agents.rules_tolerance_agent import RulesToleranceAgent
from agents.pattern_intelligence_agent import PatternIntelligenceAgent
from agents.decisioning_agent import DecisioningAgent
from agents.workflow_feedback_agent import WorkflowFeedbackAgent


class ReconciliationOrchestrator:
    """Orchestrates the reconciliation workflow across all agents"""
    
    def __init__(self):
        # Initialize message bus for A2A communication
        self.message_bus = MessageBus()
        
        # Initialize all 7 agents
        self.break_ingestion_agent = BreakIngestionAgent(self.message_bus)
        self.data_enrichment_agent = DataEnrichmentAgent(self.message_bus)
        self.matching_agent = MatchingCorrelationAgent(self.message_bus)
        self.rules_agent = RulesToleranceAgent(self.message_bus)
        self.pattern_agent = PatternIntelligenceAgent(self.message_bus)
        self.decision_agent = DecisioningAgent(self.message_bus)
        self.workflow_agent = WorkflowFeedbackAgent(self.message_bus)
        
        print("[Orchestrator] All agents initialized")
    
    def process_break(self, break_id: str = None, raw_break: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process a single break through the entire workflow
        
        Args:
            break_id: Break ID to fetch, or
            raw_break: Raw break data
        
        Returns:
            Complete case with all agent outputs
        """
        conversation_id = str(uuid.uuid4())
        print(f"\n{'='*60}")
        print(f"[Orchestrator] Starting workflow - Conversation ID: {conversation_id}")
        print(f"{'='*60}\n")
        
        # Stage 1: Break Ingestion
        print("[Stage 1] Break Ingestion...")
        ingestion_result = self.break_ingestion_agent.ingest_break(
            break_id=break_id,
            raw_break=raw_break
        )
        
        if ingestion_result.get("status") == "VALIDATION_FAILED":
            return {
                "error": "Break validation failed",
                "details": ingestion_result,
                "conversation_id": conversation_id
            }
        
        break_data = ingestion_result.get("break_data")
        print(f"✓ Break ingested: {break_data.get('break_id')}")
        
        # Stage 2: Data Enrichment
        print("\n[Stage 2] Data Enrichment...")
        enrichment_result = self.data_enrichment_agent.enrich_break(break_data)
        enriched_data = enrichment_result.get("enriched_data", {})
        print(f"✓ Enriched with {enrichment_result.get('sources_successful')} sources")
        
        # Stage 3: Matching & Correlation
        print("\n[Stage 3] Matching & Correlation...")
        matching_result = self.matching_agent.find_matches(break_data, enriched_data)
        match_candidates = matching_result.get("match_candidates", [])
        print(f"✓ Found {len(match_candidates)} match candidates")
        
        # Stage 4: Rules & Tolerance
        print("\n[Stage 4] Rules & Tolerance Check...")
        rules_result = self.rules_agent.evaluate_rules(break_data, enriched_data)
        rules_evaluation = rules_result.get("rules_evaluation", {})
        print(f"✓ Rules evaluation: {'PASSED' if rules_result.get('all_critical_rules_passed') else 'FAILED'}")
        
        # Stage 5: Pattern & Root-Cause Analysis
        print("\n[Stage 5] Pattern Intelligence...")
        pattern_result = self.pattern_agent.analyze_patterns(break_data, rules_evaluation)
        ml_insights = pattern_result.get("ml_insights", {})
        print(f"✓ Root cause: {ml_insights.get('probable_root_cause')} (confidence: {ml_insights.get('confidence', 0):.2%})")
        
        # Stage 6: Decisioning
        print("\n[Stage 6] Decision Making...")
        decision_result = self.decision_agent.make_decision(
            break_data,
            rules_evaluation,
            ml_insights
        )
        decision = decision_result.get("decision", {})
        print(f"✓ Decision: {decision.get('action')} (risk score: {decision.get('risk_score', 0):.2f})")
        print(f"  Explanation: {decision.get('explanation')}")
        
        # Stage 7: Workflow & Feedback
        print("\n[Stage 7] Workflow Creation...")
        
        # Build complete case
        case_data = {
            "break_data": break_data,
            "enriched_data": enriched_data,
            "match_candidates": match_candidates,
            "rules_evaluation": rules_evaluation,
            "ml_insights": ml_insights,
            "decision": decision
        }
        
        workflow_result = self.workflow_agent.create_workflow(
            break_data,
            decision,
            case_data
        )
        ticket = workflow_result.get("ticket", {})
        print(f"✓ Ticket created: {ticket.get('ticket_id')} - Status: {ticket.get('status')}")
        
        print(f"\n{'='*60}")
        print(f"[Orchestrator] Workflow completed successfully")
        print(f"{'='*60}\n")
        
        # Return complete case
        return {
            "conversation_id": conversation_id,
            "break_id": break_data.get("break_id"),
            "case": case_data,
            "ticket": ticket,
            "stages": {
                "ingestion": ingestion_result,
                "enrichment": enrichment_result,
                "matching": matching_result,
                "rules": rules_result,
                "pattern": pattern_result,
                "decision": decision_result,
                "workflow": workflow_result
            },
            "final_status": ticket.get("status"),
            "requires_hil": decision.get("requires_hil", False)
        }
    
    def process_multiple_breaks(self, limit: int = 5) -> Dict[str, Any]:
        """
        Process multiple breaks
        
        Args:
            limit: Number of breaks to process
        
        Returns:
            Summary of all processed breaks
        """
        print(f"\n[Orchestrator] Processing {limit} breaks...\n")
        
        # Fetch breaks
        ingestion_result = self.break_ingestion_agent.ingest_multiple_breaks(limit=limit)
        
        if "error" in ingestion_result:
            return ingestion_result
        
        results = []
        for break_result in ingestion_result.get("results", []):
            if break_result.get("status") == "INGESTED":
                break_data = break_result.get("break_data")
                case_result = self.process_break(raw_break=break_data)
                results.append(case_result)
        
        # Generate summary
        summary = {
            "total_processed": len(results),
            "auto_resolved": sum(1 for r in results if r.get("case", {}).get("decision", {}).get("action") == "AUTO_RESOLVE"),
            "hil_review": sum(1 for r in results if r.get("case", {}).get("decision", {}).get("action") == "HIL_REVIEW"),
            "escalated": sum(1 for r in results if r.get("case", {}).get("decision", {}).get("action") == "ESCALATE"),
            "results": results
        }
        
        print(f"\n{'='*60}")
        print(f"[Summary] Processed {summary['total_processed']} breaks")
        print(f"  - Auto-Resolved: {summary['auto_resolved']}")
        print(f"  - HIL Review: {summary['hil_review']}")
        print(f"  - Escalated: {summary['escalated']}")
        print(f"{'='*60}\n")
        
        return summary
    
    def get_message_history(self, conversation_id: str) -> List[Any]:
        """Get A2A message history for a conversation"""
        return self.message_bus.get_conversation_history(conversation_id)
