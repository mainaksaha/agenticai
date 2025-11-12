"""
LangGraph-based Dynamic Orchestrator
Uses official LangGraph StateGraph for conditional routing

LangGraph: https://langchain-ai.github.io/langgraph/
"""
import asyncio
from typing import Dict, Any, TypedDict, Annotated, Sequence, List
from datetime import datetime
import operator

# When langgraph is installed:
# from langgraph.graph import StateGraph, END
# from langgraph.prebuilt import ToolExecutor

# For now, we create LangGraph-compatible structure


class AgentState(TypedDict):
    """
    State that flows through the LangGraph
    
    Official LangGraph pattern:
    class State(TypedDict):
        messages: Annotated[Sequence[str], operator.add]
        data: Dict
    """
    # Input
    break_id: str
    break_data: Dict[str, Any]
    
    # Execution flow
    current_stage: str
    completed_stages: Annotated[list, operator.add]
    
    # Orchestrator planning
    orchestrator_plan: Dict[str, Any]
    agents_to_invoke: List[str]
    
    # Agent outputs
    ingestion_result: Dict[str, Any]
    enrichment_result: Dict[str, Any]
    matching_result: Dict[str, Any]
    rules_result: Dict[str, Any]
    pattern_result: Dict[str, Any]
    decision_result: Dict[str, Any]
    workflow_result: Dict[str, Any]
    
    # Metadata
    started_at: datetime
    execution_path: Annotated[list, operator.add]
    errors: Annotated[list, operator.add]


class LangGraphOrchestrator:
    """
    LangGraph-based orchestrator for dynamic agent execution
    
    Official LangGraph pattern:
    workflow = StateGraph(State)
    workflow.add_node("node1", node1_func)
    workflow.add_conditional_edges("node1", router_func, {...})
    app = workflow.compile()
    """
    
    def __init__(self, agents: Dict[str, Any]):
        """
        Initialize LangGraph orchestrator
        
        Args:
            agents: Dict of agent instances (name -> agent)
        """
        self.agents = agents
        self.graph = None
        self._build_graph()
    
    def _build_graph(self):
        """Build the LangGraph StateGraph"""
        # This will use actual LangGraph when installed:
        # from langgraph.graph import StateGraph
        # workflow = StateGraph(AgentState)
        
        # For now, we simulate the graph structure
        self.graph = {
            'nodes': {},
            'edges': {},
            'conditional_edges': {}
        }
        
        # Add orchestrator planning node FIRST
        self._add_node('orchestrator_plan', self._orchestrator_planning_node)
        
        # Add specialist agent nodes
        self._add_node('ingestion', self._ingestion_node)
        self._add_node('enrichment', self._enrichment_node)
        self._add_node('matching', self._matching_node)
        self._add_node('rules', self._rules_node)
        self._add_node('pattern', self._pattern_node)
        self._add_node('decision', self._decision_node)
        self._add_node('workflow', self._workflow_node)
        
        # Add edges (flow starts with orchestrator)
        self._add_edge('orchestrator_plan', 'ingestion')
        self._add_edge('ingestion', 'enrichment')
        
        # Add conditional edges (dynamic routing)
        self._add_conditional_edge(
            'enrichment',
            self._should_match,
            {
                'match': 'matching',
                'skip': 'rules'
            }
        )
        
        self._add_conditional_edge(
            'matching',
            lambda x: 'continue',
            {'continue': 'rules'}
        )
        
        self._add_conditional_edge(
            'rules',
            self._should_analyze_pattern,
            {
                'analyze': 'pattern',
                'skip': 'decision'
            }
        )
        
        self._add_conditional_edge(
            'pattern',
            lambda x: 'continue',
            {'continue': 'decision'}
        )
        
        self._add_conditional_edge(
            'decision',
            self._should_create_workflow,
            {
                'create': 'workflow',
                'skip': 'END'
            }
        )
        
        self._add_edge('workflow', 'END')
    
    def _add_node(self, name: str, func: callable):
        """Add node to graph"""
        self.graph['nodes'][name] = func
    
    def _add_edge(self, from_node: str, to_node: str):
        """Add edge to graph"""
        if from_node not in self.graph['edges']:
            self.graph['edges'][from_node] = []
        self.graph['edges'][from_node].append(to_node)
    
    def _add_conditional_edge(self, from_node: str, condition: callable, mapping: Dict):
        """Add conditional edge to graph"""
        self.graph['conditional_edges'][from_node] = {
            'condition': condition,
            'mapping': mapping
        }
    
    # Node functions (each calls an ADK agent)
    
    async def _orchestrator_planning_node(self, state: AgentState) -> AgentState:
        """
        Orchestrator planning node - THE INTELLIGENCE LAYER
        This agent analyzes the break and decides which agents to invoke
        """
        print(f"\n[Orchestrator Agent] Analyzing break and creating execution plan...")
        
        # Get orchestrator agent
        orchestrator = self.agents.get('orchestrator')
        if not orchestrator:
            print("  ⚠️  Orchestrator agent not found, using default plan")
            # Fallback: invoke all agents
            state['orchestrator_plan'] = {
                'agents_to_invoke': ['ingestion', 'enrichment', 'matching', 'rules', 'pattern', 'decision', 'workflow'],
                'reasoning': 'Default plan - orchestrator agent not available'
            }
            state['agents_to_invoke'] = state['orchestrator_plan']['agents_to_invoke']
            return state
        
        # Call orchestrator to analyze and plan
        result = await orchestrator.analyze_and_plan(state['break_data'])
        
        if result.get('success'):
            plan = result.get('plan', {})
            state['orchestrator_plan'] = plan
            state['agents_to_invoke'] = plan.get('agents_to_invoke', [])
            
            print(f"  ✓ Plan created:")
            print(f"    Agents to invoke: {state['agents_to_invoke']}")
            print(f"    Reasoning: {plan.get('reasoning', 'N/A')}")
            if plan.get('skip_reasons'):
                print(f"    Skip reasons: {plan.get('skip_reasons')}")
        else:
            print(f"  ⚠️  Planning failed, using default")
            state['orchestrator_plan'] = {
                'agents_to_invoke': ['ingestion', 'enrichment', 'rules', 'decision', 'workflow'],
                'reasoning': 'Fallback plan - orchestrator analysis failed'
            }
            state['agents_to_invoke'] = state['orchestrator_plan']['agents_to_invoke']
        
        state['execution_path'].append('orchestrator_plan')
        return state
    
    async def _ingestion_node(self, state: AgentState) -> AgentState:
        """Ingestion agent node"""
        agent = self.agents.get('break_ingestion')
        if not agent:
            state['errors'].append('Ingestion agent not found')
            return state
        
        result = await agent.ingest_break(
            break_id=state.get('break_id'),
            raw_break=state.get('break_data')
        )
        
        state['ingestion_result'] = result
        state['completed_stages'].append('ingestion')
        state['execution_path'].append('ingestion')
        
        if result.get('success'):
            state['break_data'] = result.get('break_data', state['break_data'])
        
        return state
    
    async def _enrichment_node(self, state: AgentState) -> AgentState:
        """Enrichment agent node"""
        agent = self.agents.get('data_enrichment')
        if not agent:
            state['errors'].append('Enrichment agent not found')
            return state
        
        result = await agent.enrich_break(state['break_data'])
        
        state['enrichment_result'] = result
        state['completed_stages'].append('enrichment')
        state['execution_path'].append('enrichment')
        
        return state
    
    async def _matching_node(self, state: AgentState) -> AgentState:
        """Matching agent node"""
        agent = self.agents.get('matching_correlation')
        if not agent:
            state['errors'].append('Matching agent not found')
            return state
        
        enriched_data = state['enrichment_result'].get('enriched_data', {})
        result = await agent.find_matches(state['break_data'], enriched_data)
        
        state['matching_result'] = result
        state['completed_stages'].append('matching')
        state['execution_path'].append('matching')
        
        return state
    
    async def _rules_node(self, state: AgentState) -> AgentState:
        """Rules agent node"""
        agent = self.agents.get('rules_tolerance')
        if not agent:
            state['errors'].append('Rules agent not found')
            return state
        
        enriched_data = state['enrichment_result'].get('enriched_data', {})
        result = await agent.evaluate_rules(state['break_data'], enriched_data)
        
        state['rules_result'] = result
        state['completed_stages'].append('rules')
        state['execution_path'].append('rules')
        
        return state
    
    async def _pattern_node(self, state: AgentState) -> AgentState:
        """Pattern agent node"""
        agent = self.agents.get('pattern_intelligence')
        if not agent:
            state['errors'].append('Pattern agent not found')
            return state
        
        rules_eval = state['rules_result'].get('rules_evaluation', {})
        result = await agent.analyze_patterns(state['break_data'], rules_eval)
        
        state['pattern_result'] = result
        state['completed_stages'].append('pattern')
        state['execution_path'].append('pattern')
        
        return state
    
    async def _decision_node(self, state: AgentState) -> AgentState:
        """Decision agent node"""
        agent = self.agents.get('decisioning')
        if not agent:
            state['errors'].append('Decision agent not found')
            return state
        
        result = await agent.make_decision(
            state['break_data'],
            state['enrichment_result'].get('enriched_data', {}),
            state.get('matching_result', {}),
            state['rules_result'],
            state.get('pattern_result', {})
        )
        
        state['decision_result'] = result
        state['completed_stages'].append('decision')
        state['execution_path'].append('decision')
        
        return state
    
    async def _workflow_node(self, state: AgentState) -> AgentState:
        """Workflow agent node"""
        agent = self.agents.get('workflow_feedback')
        if not agent:
            state['errors'].append('Workflow agent not found')
            return state
        
        decision = state['decision_result'].get('decision', {})
        case_data = {
            'break_data': state['break_data'],
            'enriched_data': state['enrichment_result'],
            'rules_evaluation': state['rules_result'],
            'ml_insights': state.get('pattern_result', {}).get('ml_insights'),
            'decision': decision
        }
        
        result = await agent.create_workflow(state['break_data'], decision, case_data)
        
        state['workflow_result'] = result
        state['completed_stages'].append('workflow')
        state['execution_path'].append('workflow')
        
        return state
    
    # Conditional routing functions
    
    def _should_match(self, state: AgentState) -> str:
        """Decide if matching is needed - USES ORCHESTRATOR PLAN"""
        agents_to_invoke = state.get('agents_to_invoke', [])
        
        if 'matching' in agents_to_invoke:
            print("  [Orchestrator Decision] ✓ Matching agent will be invoked")
            return 'match'
        else:
            skip_reason = state.get('orchestrator_plan', {}).get('skip_reasons', {}).get('matching', 'Not in orchestrator plan')
            print(f"  [Orchestrator Decision] ⊘ Matching agent skipped: {skip_reason}")
            return 'skip'
    
    def _should_analyze_pattern(self, state: AgentState) -> str:
        """Decide if pattern analysis is needed - USES ORCHESTRATOR PLAN"""
        agents_to_invoke = state.get('agents_to_invoke', [])
        
        if 'pattern' in agents_to_invoke:
            print("  [Orchestrator Decision] ✓ Pattern agent will be invoked")
            return 'analyze'
        else:
            skip_reason = state.get('orchestrator_plan', {}).get('skip_reasons', {}).get('pattern', 'Not in orchestrator plan')
            print(f"  [Orchestrator Decision] ⊘ Pattern agent skipped: {skip_reason}")
            return 'skip'
    
    def _should_create_workflow(self, state: AgentState) -> str:
        """Decide if workflow creation is needed - USES ORCHESTRATOR PLAN"""
        agents_to_invoke = state.get('agents_to_invoke', [])
        
        if 'workflow' in agents_to_invoke:
            print("  [Orchestrator Decision] ✓ Workflow agent will be invoked")
            return 'create'
        else:
            print("  [Orchestrator Decision] ⊘ Workflow agent skipped")
            return 'skip'
    
    async def execute(self, initial_state: AgentState) -> AgentState:
        """
        Execute the LangGraph workflow
        
        Official pattern:
        app = workflow.compile()
        result = await app.ainvoke(initial_state)
        """
        state = initial_state
        current_node = 'orchestrator_plan'  # START with orchestrator!
        
        print(f"\n[LangGraph] Starting execution with ORCHESTRATOR AGENT")
        print(f"  Initial node: {current_node}")
        
        while current_node != 'END':
            print(f"\n[LangGraph] Executing node: {current_node}")
            
            # Execute node
            if current_node in self.graph['nodes']:
                node_func = self.graph['nodes'][current_node]
                state = await node_func(state)
                state['current_stage'] = current_node
            
            # Determine next node
            if current_node in self.graph['conditional_edges']:
                # Conditional routing
                edge_config = self.graph['conditional_edges'][current_node]
                condition = edge_config['condition']
                mapping = edge_config['mapping']
                
                decision = condition(state)
                next_node = mapping.get(decision, 'END')
                
                print(f"  Conditional: {decision} → {next_node}")
            elif current_node in self.graph['edges']:
                # Direct edge
                next_node = self.graph['edges'][current_node][0]
                print(f"  Direct edge → {next_node}")
            else:
                # No edge, end
                next_node = 'END'
            
            current_node = next_node
        
        print(f"\n[LangGraph] Execution complete")
        print(f"  Path: {' → '.join(state['execution_path'])}")
        
        return state
    
    async def process_break(self, break_id: str = None, break_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process a break using LangGraph workflow
        
        Args:
            break_id: Break ID to fetch
            break_data: Or provide break data directly
        
        Returns:
            Complete execution result
        """
        # Initialize state
        initial_state: AgentState = {
            'break_id': break_id or break_data.get('break_id', 'UNKNOWN'),
            'break_data': break_data or {},
            'current_stage': '',
            'completed_stages': [],
            'orchestrator_plan': {},  # NEW: orchestrator's execution plan
            'agents_to_invoke': [],   # NEW: list of agents to invoke
            'ingestion_result': {},
            'enrichment_result': {},
            'matching_result': {},
            'rules_result': {},
            'pattern_result': {},
            'decision_result': {},
            'workflow_result': {},
            'started_at': datetime.now(),
            'execution_path': [],
            'errors': []
        }
        
        # Execute workflow
        final_state = await self.execute(initial_state)
        
        # Build result
        return {
            'success': len(final_state['errors']) == 0,
            'break_id': final_state['break_id'],
            'execution_path': final_state['execution_path'],
            'completed_stages': final_state['completed_stages'],
            'orchestrator_plan': final_state.get('orchestrator_plan', {}),  # NEW: Include orchestrator's plan
            'agents_to_invoke': final_state.get('agents_to_invoke', []),    # NEW: Agents that were planned
            'decision': final_state['decision_result'].get('decision', {}),
            'ticket': final_state['workflow_result'].get('ticket', {}),
            'errors': final_state['errors'],
            'duration_ms': (datetime.now() - final_state['started_at']).total_seconds() * 1000
        }
