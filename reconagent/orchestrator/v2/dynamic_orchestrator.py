"""
Dynamic Reconciliation Orchestrator v2
Non-linear, policy-driven orchestration with parallel execution
"""
import asyncio
import uuid
from typing import Dict, Any, Optional
from datetime import datetime

from agents.break_ingestion_agent import BreakIngestionAgent
from agents.data_enrichment_agent import DataEnrichmentAgent
from agents.matching_correlation_agent import MatchingCorrelationAgent
from agents.rules_tolerance_agent import RulesToleranceAgent
from agents.pattern_intelligence_agent import PatternIntelligenceAgent
from agents.decisioning_agent import DecisioningAgent
from agents.workflow_feedback_agent import WorkflowFeedbackAgent

from .break_classifier import BreakClassifier
from .policy_engine import PolicyEngine
from .dag_executor import DAGExecutor
from .schemas import ExecutionGraph


class DynamicReconciliationOrchestrator:
    """
    Dynamic orchestrator that routes breaks based on profile and policy
    
    Features:
    - Classifies breaks into profiles
    - Looks up routing policy
    - Executes agents in parallel where possible
    - Supports early exit on decision
    - Selective agent invocation
    """
    
    def __init__(self, policy_file: str = None):
        """
        Initialize dynamic orchestrator
        
        Args:
            policy_file: Path to YAML policy file (optional)
        """
        # Initialize components
        self.classifier = BreakClassifier()
        self.policy_engine = PolicyEngine(policy_file)
        
        # Initialize all agents
        self.agents = self._initialize_agents()
        
        # Create DAG executor
        self.dag_executor = DAGExecutor(self.agents, max_parallel=3)
        
        print("[Dynamic Orchestrator v2] Initialized")
        print(f"  - Break Classifier: ✓")
        print(f"  - Policy Engine: ✓")
        print(f"  - {len(self.agents)} Agents: ✓")
        print(f"  - DAG Executor: ✓\n")
    
    def _initialize_agents(self) -> Dict[str, Any]:
        """Initialize all available agents"""
        agents = {}
        
        # Initialize each agent
        try:
            agents['break_ingestion'] = BreakIngestionAgent()
            agents['data_enrichment'] = DataEnrichmentAgent()
            agents['matching_correlation'] = MatchingCorrelationAgent()
            agents['rules_tolerance'] = RulesToleranceAgent()
            agents['pattern_intelligence'] = PatternIntelligenceAgent()
            agents['decisioning'] = DecisioningAgent()
            agents['workflow_feedback'] = WorkflowFeedbackAgent()
        except Exception as e:
            print(f"Warning: Error initializing agents: {e}")
        
        return agents
    
    async def process_break_async(
        self, 
        break_id: str = None, 
        raw_break: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Process a break asynchronously using dynamic orchestration
        
        Args:
            break_id: Break ID to fetch, or
            raw_break: Raw break data
        
        Returns:
            Complete result with execution graph
        """
        conversation_id = f"CONV-{uuid.uuid4().hex[:8]}"
        
        # Step 1: Get break data
        if not raw_break:
            from mcp.tools.break_tools import get_break_by_id
            raw_break = get_break_by_id(break_id)
            if "error" in raw_break:
                return {
                    "error": "Failed to fetch break",
                    "details": raw_break,
                    "conversation_id": conversation_id
                }
        
        # Step 2: Classify break into profile
        print("[Step 1] Classifying break...")
        break_profile = self.classifier.classify(raw_break)
        print(f"  ✓ Break Profile:")
        print(f"    - Type: {break_profile.break_type}")
        print(f"    - Risk Tier: {break_profile.risk_tier}")
        print(f"    - Exposure: ${break_profile.exposure:,.2f}")
        print(f"    - Asset Class: {break_profile.asset_class}")
        print(f"    - Requires Matching: {break_profile.requires_matching}")
        print(f"    - Requires Pattern Analysis: {break_profile.requires_pattern_analysis}")
        
        # Step 3: Get execution plan from policy engine
        print("\n[Step 2] Creating execution plan...")
        execution_plan = self.policy_engine.create_execution_plan(break_profile)
        print(f"  ✓ Execution Plan:")
        print(f"    - Plan ID: {execution_plan.plan_id}")
        print(f"    - Agents Planned: {len(execution_plan.nodes)}")
        print(f"    - Max Parallel: {execution_plan.max_parallel}")
        print(f"    - Early Exit: {execution_plan.early_exit_enabled}")
        print(f"    - Decision Checkpoints: {len(execution_plan.decision_checkpoints)}")
        
        agent_names = [node.agent_name for node in execution_plan.nodes]
        print(f"    - Agent Sequence: {' → '.join(agent_names)}")
        
        # Step 4: Execute plan
        print("\n[Step 3] Executing agents...")
        execution_graph = await self.dag_executor.execute(execution_plan, raw_break)
        
        # Step 5: Generate reasoning for orchestration decisions
        orchestration_reasoning = self._generate_orchestration_reasoning(
            break_profile, execution_plan, execution_graph
        )
        
        # Step 6: Return complete result with reasoning
        return {
            "conversation_id": conversation_id,
            "break_id": break_profile.break_id,
            "break_profile": break_profile.dict(),
            "execution_plan": {
                "plan_id": execution_plan.plan_id,
                "agents_planned": len(execution_plan.nodes),
                "agents_invoked": execution_graph.agents_invoked,
                "agents_skipped": execution_graph.agents_skipped,
                "nodes": [node.dict() for node in execution_plan.nodes],
                "decision_checkpoints": [cp.dict() for cp in execution_plan.decision_checkpoints]
            },
            "execution_graph": execution_graph.dict(),
            "decision": execution_graph.decision,
            "orchestration_reasoning": orchestration_reasoning,
            "performance": {
                "total_duration_ms": execution_graph.total_duration_ms,
                "agents_invoked": execution_graph.agents_invoked,
                "agents_skipped": execution_graph.agents_skipped,
                "early_exit": execution_graph.early_exit,
                "efficiency": f"{(execution_graph.agents_invoked / len(execution_plan.nodes) * 100):.0f}%"
            }
        }
    
    def _generate_orchestration_reasoning(
        self, 
        break_profile, 
        execution_plan, 
        execution_graph
    ) -> Dict[str, Any]:
        """
        Generate detailed reasoning for orchestration decisions
        
        Args:
            break_profile: The classified break profile
            execution_plan: The generated execution plan
            execution_graph: The execution results
        
        Returns:
            Dictionary with detailed reasoning
        """
        reasoning = {
            "classification_reasoning": self._explain_classification(break_profile),
            "agent_selection_reasoning": self._explain_agent_selection(break_profile, execution_plan),
            "execution_strategy": self._explain_execution_strategy(execution_plan),
            "skip_reasoning": self._explain_skipped_agents(execution_graph),
            "checkpoint_reasoning": self._explain_checkpoints(execution_plan, execution_graph)
        }
        
        return reasoning
    
    def _explain_classification(self, profile) -> Dict[str, Any]:
        """Explain why break was classified this way"""
        reasons = []
        
        # Explain risk tier
        if profile.risk_tier == "LOW":
            reasons.append(f"Risk classified as LOW because exposure (${profile.exposure:,.2f}) < $5,000")
        elif profile.risk_tier == "MEDIUM":
            reasons.append(f"Risk classified as MEDIUM because exposure (${profile.exposure:,.2f}) is between $5K-$50K")
        elif profile.risk_tier == "HIGH":
            reasons.append(f"Risk classified as HIGH because exposure (${profile.exposure:,.2f}) is between $50K-$100K")
        else:
            reasons.append(f"Risk classified as CRITICAL because exposure (${profile.exposure:,.2f}) > $100K or regulatory type")
        
        # Explain requirements
        if profile.requires_matching:
            reasons.append(f"Matching required for break type: {profile.break_type}")
        else:
            reasons.append(f"Matching not required for break type: {profile.break_type}")
        
        if profile.requires_pattern_analysis:
            reasons.append(f"Pattern analysis required due to {profile.risk_tier} risk tier or complex break type")
        else:
            reasons.append(f"Pattern analysis not required for simple {profile.risk_tier} risk break")
        
        return {
            "break_type": profile.break_type,
            "risk_tier": profile.risk_tier,
            "exposure": profile.exposure,
            "asset_class": profile.asset_class,
            "reasons": reasons,
            "summary": f"{profile.break_type} classified as {profile.risk_tier} risk with ${profile.exposure:,.2f} exposure"
        }
    
    def _explain_agent_selection(self, profile, plan) -> Dict[str, Any]:
        """Explain why specific agents were selected"""
        selected_agents = [node.agent_name for node in plan.nodes]
        all_possible_agents = [
            "BREAK_INGESTION", "DATA_ENRICHMENT", "MATCHING_CORRELATION",
            "RULES_TOLERANCE", "PATTERN_INTELLIGENCE", "DECISIONING", "WORKFLOW_FEEDBACK"
        ]
        skipped_agents = [a for a in all_possible_agents if a not in selected_agents]
        
        reasons = []
        
        # Explain each selected agent
        for node in plan.nodes:
            if node.agent_name == "BREAK_INGESTION":
                reasons.append("✅ BREAK_INGESTION: Always required to normalize and validate incoming break data")
            elif node.agent_name == "DATA_ENRICHMENT":
                reasons.append("✅ DATA_ENRICHMENT: Always required to gather context from multiple data sources")
            elif node.agent_name == "MATCHING_CORRELATION":
                if node.is_mandatory:
                    reasons.append(f"✅ MATCHING_CORRELATION: Required for {profile.break_type} to find matching transactions")
                else:
                    reasons.append(f"✅ MATCHING_CORRELATION: Optional, included based on break profile requirements")
            elif node.agent_name == "RULES_TOLERANCE":
                reasons.append("✅ RULES_TOLERANCE: Required to check business rules and tolerance thresholds")
            elif node.agent_name == "PATTERN_INTELLIGENCE":
                if node.is_mandatory:
                    reasons.append(f"✅ PATTERN_INTELLIGENCE: Required for {profile.risk_tier} risk tier to identify root causes")
                else:
                    reasons.append(f"✅ PATTERN_INTELLIGENCE: Optional, included for pattern analysis")
            elif node.agent_name == "DECISIONING":
                reasons.append(f"✅ DECISIONING: Required for {profile.risk_tier} risk tier to make informed decision")
            elif node.agent_name == "WORKFLOW_FEEDBACK":
                reasons.append("✅ WORKFLOW_FEEDBACK: Required to create tickets and log audit trail")
        
        # Explain skipped agents
        for agent in skipped_agents:
            if agent == "MATCHING_CORRELATION" and not profile.requires_matching:
                reasons.append(f"⊘ MATCHING_CORRELATION: Skipped - not required for {profile.break_type}")
            elif agent == "PATTERN_INTELLIGENCE" and not profile.requires_pattern_analysis:
                reasons.append(f"⊘ PATTERN_INTELLIGENCE: Skipped - not required for {profile.risk_tier} risk tier")
            elif agent == "DECISIONING":
                reasons.append(f"⊘ DECISIONING: Skipped - simple rules-based decision sufficient")
            elif agent == "WORKFLOW_FEEDBACK":
                reasons.append(f"⊘ WORKFLOW_FEEDBACK: Skipped - will be invoked after decision if needed")
        
        return {
            "selected_agents": selected_agents,
            "skipped_agents": skipped_agents,
            "total_selected": len(selected_agents),
            "reasons": reasons,
            "summary": f"Selected {len(selected_agents)}/7 agents based on {profile.break_type} ({profile.risk_tier} risk)"
        }
    
    def _explain_execution_strategy(self, plan) -> Dict[str, Any]:
        """Explain the execution strategy"""
        parallel_groups = []
        
        # Build parallel groups from dependencies
        stage = 1
        processed = set()
        
        while len(processed) < len(plan.nodes):
            # Find nodes with no unprocessed dependencies
            ready = []
            for node in plan.nodes:
                if node.node_id in processed:
                    continue
                deps_met = all(dep in processed or dep == "" for dep in node.depends_on)
                if deps_met:
                    ready.append(node.agent_name)
            
            if not ready:
                break
            
            parallel_groups.append({
                "stage": stage,
                "agents": ready,
                "parallel": len(ready) > 1,
                "description": f"Stage {stage}: {' || '.join(ready) if len(ready) > 1 else ready[0]}"
            })
            
            # Mark as processed
            for node in plan.nodes:
                if node.agent_name in ready:
                    processed.add(node.node_id)
            
            stage += 1
        
        reasons = []
        reasons.append(f"Execution planned in {len(parallel_groups)} stages")
        reasons.append(f"Max parallel execution: {plan.max_parallel} agents")
        reasons.append(f"Early exit: {'Enabled' if plan.early_exit_enabled else 'Disabled'}")
        reasons.append(f"Decision checkpoints: {len(plan.decision_checkpoints)}")
        
        return {
            "stages": parallel_groups,
            "total_stages": len(parallel_groups),
            "max_parallel": plan.max_parallel,
            "early_exit_enabled": plan.early_exit_enabled,
            "reasons": reasons,
            "summary": f"Execution in {len(parallel_groups)} stages with up to {plan.max_parallel} parallel agents"
        }
    
    def _explain_skipped_agents(self, graph) -> Dict[str, Any]:
        """Explain why agents were skipped during execution"""
        skipped = [e for e in graph.executions if e.status == "SKIPPED"]
        
        if not skipped:
            return {
                "skipped_count": 0,
                "reasons": [],
                "summary": "No agents were skipped during execution"
            }
        
        reasons = []
        for execution in skipped:
            reasons.append(f"⊘ {execution.agent_name}: {execution.skip_reason}")
        
        return {
            "skipped_count": len(skipped),
            "skipped_agents": [e.agent_name for e in skipped],
            "reasons": reasons,
            "summary": f"{len(skipped)} agents skipped during execution"
        }
    
    def _explain_checkpoints(self, plan, graph) -> Dict[str, Any]:
        """Explain decision checkpoint logic"""
        if not plan.decision_checkpoints:
            return {
                "checkpoint_count": 0,
                "reasons": [],
                "summary": "No decision checkpoints configured"
            }
        
        reasons = []
        for checkpoint in plan.decision_checkpoints:
            reasons.append(
                f"Checkpoint after {checkpoint.after_nodes}: "
                f"If {checkpoint.condition}, then {checkpoint.action}"
            )
        
        if graph.early_exit:
            reasons.append(f"✓ Early exit triggered: {graph.early_exit_reason}")
        else:
            reasons.append("No early exit - all planned agents executed")
        
        return {
            "checkpoint_count": len(plan.decision_checkpoints),
            "early_exit": graph.early_exit,
            "early_exit_reason": graph.early_exit_reason if graph.early_exit else None,
            "reasons": reasons,
            "summary": f"{len(plan.decision_checkpoints)} checkpoints configured, early exit: {graph.early_exit}"
        }
    
    def process_break(
        self, 
        break_id: str = None, 
        raw_break: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Process a break (synchronous wrapper)
        
        Args:
            break_id: Break ID to fetch, or
            raw_break: Raw break data
        
        Returns:
            Complete result with execution graph
        """
        # Run async function in event loop
        return asyncio.run(self.process_break_async(break_id, raw_break))
    
    async def process_multiple_breaks_async(
        self, 
        limit: int = 5
    ) -> Dict[str, Any]:
        """
        Process multiple breaks asynchronously
        
        Args:
            limit: Number of breaks to process
        
        Returns:
            Results for all breaks
        """
        from mcp.tools.break_tools import get_breaks
        
        # Fetch breaks
        breaks_response = get_breaks(limit=limit)
        breaks = breaks_response.get('breaks', [])
        
        if not breaks:
            return {
                "error": "No breaks available",
                "count": 0
            }
        
        print(f"\n{'='*80}")
        print(f"[Dynamic Orchestrator v2] Processing {len(breaks)} breaks")
        print(f"{'='*80}\n")
        
        # Process each break
        results = []
        for idx, break_data in enumerate(breaks, 1):
            print(f"\n{'─'*80}")
            print(f"Processing break {idx}/{len(breaks)}: {break_data.get('break_id')}")
            print(f"{'─'*80}")
            
            result = await self.process_break_async(raw_break=break_data)
            results.append(result)
        
        # Summary statistics
        total_agents_planned = sum(r['execution_plan']['agents_planned'] for r in results)
        total_agents_invoked = sum(r['execution_plan']['agents_invoked'] for r in results)
        total_agents_skipped = sum(r['execution_plan']['agents_skipped'] for r in results)
        total_time = sum(r['performance']['total_duration_ms'] for r in results)
        
        early_exits = sum(1 for r in results if r['performance']['early_exit'])
        
        decisions = {}
        for r in results:
            action = r['decision'].get('action', 'UNKNOWN')
            decisions[action] = decisions.get(action, 0) + 1
        
        print(f"\n{'='*80}")
        print(f"[Dynamic Orchestrator v2] Batch Processing Complete")
        print(f"{'='*80}")
        print(f"Breaks Processed: {len(results)}")
        print(f"Total Agents Planned: {total_agents_planned}")
        print(f"Total Agents Invoked: {total_agents_invoked}")
        print(f"Total Agents Skipped: {total_agents_skipped}")
        print(f"Efficiency: {(total_agents_invoked / total_agents_planned * 100):.0f}%")
        print(f"Early Exits: {early_exits}/{len(results)}")
        print(f"Total Time: {total_time:.0f}ms")
        print(f"Average Time per Break: {total_time / len(results):.0f}ms")
        print(f"\nDecisions:")
        for action, count in decisions.items():
            print(f"  - {action}: {count}")
        print(f"{'='*80}\n")
        
        return {
            "breaks_processed": len(results),
            "results": results,
            "summary": {
                "total_agents_planned": total_agents_planned,
                "total_agents_invoked": total_agents_invoked,
                "total_agents_skipped": total_agents_skipped,
                "efficiency_percent": round((total_agents_invoked / total_agents_planned * 100), 1),
                "early_exits": early_exits,
                "total_duration_ms": total_time,
                "avg_duration_ms": round(total_time / len(results), 1),
                "decisions": decisions
            }
        }
    
    def process_multiple_breaks(self, limit: int = 5) -> Dict[str, Any]:
        """
        Process multiple breaks (synchronous wrapper)
        
        Args:
            limit: Number of breaks to process
        
        Returns:
            Results for all breaks
        """
        return asyncio.run(self.process_multiple_breaks_async(limit))
    
    def get_policy_info(self) -> Dict[str, Any]:
        """Get information about loaded policies"""
        break_types = self.policy_engine.policy_loader.list_break_types()
        
        policies = {}
        for break_type in break_types:
            risk_tiers = self.policy_engine.policy_loader.list_risk_tiers(break_type)
            policies[break_type] = risk_tiers
        
        return {
            "break_types": break_types,
            "policies": policies
        }
