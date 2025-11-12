"""
Main ADK Orchestrator Entry Point
Combines A2A Protocol + LangGraph + ADK Agents
"""
import asyncio
from typing import Dict, Any
from orchestrator_adk.agents import (
    BreakIngestionAgent,
    DataEnrichmentAgent,
    MatchingAgent,
    RulesAgent,
    PatternAgent,
    DecisionAgent,
    WorkflowAgent
)
from orchestrator_adk.orchestrator_agent import OrchestratorAgent  # NEW: Intelligence layer
from orchestrator_adk.langgraph_orchestrator import LangGraphOrchestrator
from orchestrator_adk.a2a_protocol import a2a_protocol, A2AMessage, A2AMessageType


class ADKReconciliationOrchestrator:
    """
    Main orchestrator using Google ADK + A2A Protocol + LangGraph
    
    This is the production-ready orchestrator following official Google patterns
    """
    
    def __init__(self):
        print("\n" + "="*80)
        print("Initializing ADK Reconciliation Orchestrator")
        print("Google ADK + Official A2A Protocol + LangGraph")
        print("="*80)
        
        # Initialize A2A protocol handler
        self.a2a = a2a_protocol
        
        # Initialize all ADK agents
        print("\nInitializing ADK Agents...")
        self.agents = self._initialize_agents()
        
        # Initialize LangGraph orchestrator
        print("\nInitializing LangGraph Orchestrator...")
        self.langgraph = LangGraphOrchestrator(self.agents)
        
        print("\n✅ Orchestrator ready!")
        print("="*80 + "\n")
    
    def _initialize_agents(self) -> Dict[str, Any]:
        """Initialize all ADK agents including the orchestrator"""
        agents = {}
        
        try:
            # FIRST: Initialize the orchestrator agent (the intelligence layer)
            agents['orchestrator'] = OrchestratorAgent()
            print("  ✓ Orchestrator Agent (Intelligence Layer) - OpenAI Powered")
            
            # Then initialize specialist agents
            agents['break_ingestion'] = BreakIngestionAgent()
            print("  ✓ Break Ingestion Agent")
            
            agents['data_enrichment'] = DataEnrichmentAgent()
            print("  ✓ Data Enrichment Agent")
            
            agents['matching_correlation'] = MatchingAgent()
            print("  ✓ Matching & Correlation Agent")
            
            agents['rules_tolerance'] = RulesAgent()
            print("  ✓ Rules & Tolerance Agent")
            
            agents['pattern_intelligence'] = PatternAgent()
            print("  ✓ Pattern Intelligence Agent")
            
            agents['decisioning'] = DecisionAgent()
            print("  ✓ Decisioning Agent")
            
            agents['workflow_feedback'] = WorkflowAgent()
            print("  ✓ Workflow & Feedback Agent")
            
        except Exception as e:
            print(f"\n⚠️  Warning: Error initializing agents: {e}")
        
        return agents
    
    async def process_break_async(
        self, 
        break_id: str = None, 
        break_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Process a break using ADK + A2A + LangGraph
        
        Args:
            break_id: Break ID to fetch
            break_data: Or provide break data directly
        
        Returns:
            Complete result with A2A messages and LangGraph execution
        """
        # Create A2A context for this workflow
        context = self.a2a.create_context(
            metadata={
                'break_id': break_id or break_data.get('break_id', 'UNKNOWN'),
                'workflow': 'reconciliation',
                'orchestrator': 'adk'
            }
        )
        
        print(f"\n[ADK Orchestrator] Processing break: {break_id or 'from data'}")
        print(f"  A2A Context: {context.context_id}")
        
        # Send A2A message to start workflow
        start_message = self.a2a.create_message(
            from_agent="orchestrator",
            to_agent="langgraph_workflow",
            content={
                'action': 'process_break',
                'break_id': break_id,
                'break_data': break_data
            },
            message_type=A2AMessageType.REQUEST,
            context_id=context.context_id
        )
        
        # Execute LangGraph workflow
        result = await self.langgraph.process_break(break_id, break_data)
        
        # Send completion message via A2A
        complete_message = self.a2a.create_message(
            from_agent="langgraph_workflow",
            to_agent="orchestrator",
            content={
                'status': 'completed' if result['success'] else 'failed',
                'result': result
            },
            message_type=A2AMessageType.RESPONSE,
            context_id=context.context_id,
            reply_to=start_message.id
        )
        
        # Get all A2A messages in context
        a2a_messages = self.a2a.get_context_messages(context.context_id)
        
        return {
            'success': result['success'],
            'break_id': result['break_id'],
            'execution_path': result['execution_path'],
            'decision': result['decision'],
            'ticket': result['ticket'],
            'a2a_context': context.context_id,
            'a2a_messages': [msg.dict() for msg in a2a_messages],
            'duration_ms': result['duration_ms'],
            'errors': result['errors']
        }
    
    def process_break(
        self, 
        break_id: str = None, 
        break_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Synchronous wrapper"""
        return asyncio.run(self.process_break_async(break_id, break_data))
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about all registered agents"""
        agents_info = {}
        for name, agent in self.agents.items():
            agents_info[name] = {
                'name': agent.name,
                'description': agent.description,
                'model': agent.model,
                'tools': [tool.name for tool in agent.get_tools()]
            }
        return agents_info
