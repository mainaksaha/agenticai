"""
DAG Executor - Executes agents in parallel based on dependency graph
"""
import asyncio
import time
from datetime import datetime
from typing import Dict, Any, List, Set
from .schemas import (
    ExecutionPlan, AgentNode, NodeExecution, 
    ExecutionGraph, DecisionCheckpoint
)


class DAGExecutor:
    """
    Executes agents according to a DAG plan with parallel execution
    """
    
    def __init__(self, agents: Dict[str, Any], max_parallel: int = 3):
        """
        Initialize DAG executor
        
        Args:
            agents: Dictionary of agent instances (name -> agent object)
            max_parallel: Maximum number of parallel executions
        """
        self.agents = agents
        self.max_parallel = max_parallel
        self.results = {}
        self.executions = []
    
    async def execute(
        self, 
        plan: ExecutionPlan, 
        break_data: Dict[str, Any]
    ) -> ExecutionGraph:
        """
        Execute the execution plan
        
        Args:
            plan: Execution plan to execute
            break_data: Break data to process
        
        Returns:
            ExecutionGraph with all execution results
        """
        start_time = time.time()
        completed = set()
        skipped = set()
        
        print(f"\n{'='*80}")
        print(f"[Dynamic Orchestrator v2] Starting execution")
        print(f"Break ID: {plan.break_profile.break_id}")
        print(f"Break Type: {plan.break_profile.break_type}")
        print(f"Risk Tier: {plan.break_profile.risk_tier}")
        print(f"Plan: {len(plan.nodes)} agents planned")
        print(f"{'='*80}\n")
        
        # Execute nodes according to DAG
        while len(completed) + len(skipped) < len(plan.nodes):
            # Get nodes ready to execute
            ready_nodes = self._get_ready_nodes(plan, completed, skipped)
            
            if not ready_nodes:
                # No more nodes can execute - check if we're stuck
                if len(completed) + len(skipped) < len(plan.nodes):
                    remaining = [n for n in plan.nodes if n.node_id not in completed and n.node_id not in skipped]
                    print(f"⚠️  Warning: Workflow stuck. Remaining nodes: {[n.agent_name for n in remaining]}")
                break
            
            # Limit parallel execution
            batch = ready_nodes[:self.max_parallel]
            
            # Execute batch in parallel
            print(f"\n[Stage] Executing {len(batch)} agent(s) in parallel: {[n.agent_name for n in batch]}")
            results = await self._execute_parallel(batch, break_data)
            
            # Update completed and results
            for node in batch:
                execution = results[node.node_id]
                self.executions.append(execution)
                
                if execution.status == "COMPLETED":
                    completed.add(node.node_id)
                    self.results[node.agent_name] = execution.result
                    print(f"  ✓ {node.agent_name} completed in {execution.duration_ms:.0f}ms")
                elif execution.status == "FAILED":
                    completed.add(node.node_id)  # Mark as completed to continue
                    print(f"  ✗ {node.agent_name} failed: {execution.error}")
                elif execution.status == "SKIPPED":
                    skipped.add(node.node_id)
                    print(f"  ⊘ {node.agent_name} skipped: {execution.skip_reason}")
            
            # Check decision checkpoints
            if plan.early_exit_enabled:
                can_exit, decision = self._check_decision_checkpoints(
                    plan, completed, self.results
                )
                if can_exit:
                    print(f"\n[Early Exit] Decision reached: {decision.get('action')}")
                    print(f"  Reason: {decision.get('explanation', 'Checkpoint condition met')}")
                    
                    # Mark remaining nodes as skipped
                    for node in plan.nodes:
                        if node.node_id not in completed and node.node_id not in skipped:
                            execution = NodeExecution(
                                node_id=node.node_id,
                                agent_name=node.agent_name,
                                status="SKIPPED",
                                skip_reason="Early decision reached"
                            )
                            self.executions.append(execution)
                            skipped.add(node.node_id)
                    
                    # Create execution graph and return
                    total_time = (time.time() - start_time) * 1000
                    graph = ExecutionGraph(
                        break_id=plan.break_profile.break_id,
                        plan_id=plan.plan_id,
                        executions=self.executions,
                        decision=decision,
                        early_exit=True,
                        early_exit_reason="Decision checkpoint met",
                        total_duration_ms=total_time,
                        agents_invoked=len(completed),
                        agents_skipped=len(skipped),
                        completed_at=datetime.now()
                    )
                    
                    print(f"\n{'='*80}")
                    print(f"[Dynamic Orchestrator v2] Execution complete (early exit)")
                    print(f"Agents invoked: {len(completed)}/{len(plan.nodes)}")
                    print(f"Agents skipped: {len(skipped)}")
                    print(f"Total time: {total_time:.0f}ms")
                    print(f"{'='*80}\n")
                    
                    return graph
        
        # Make final decision if not already made
        final_decision = self._make_final_decision(plan, self.results)
        
        total_time = (time.time() - start_time) * 1000
        
        # Create execution graph
        graph = ExecutionGraph(
            break_id=plan.break_profile.break_id,
            plan_id=plan.plan_id,
            executions=self.executions,
            decision=final_decision,
            early_exit=False,
            total_duration_ms=total_time,
            agents_invoked=len(completed),
            agents_skipped=len(skipped),
            completed_at=datetime.now()
        )
        
        print(f"\n{'='*80}")
        print(f"[Dynamic Orchestrator v2] Execution complete")
        print(f"Agents invoked: {len(completed)}/{len(plan.nodes)}")
        print(f"Agents skipped: {len(skipped)}")
        print(f"Total time: {total_time:.0f}ms")
        print(f"Decision: {final_decision.get('action')}")
        print(f"{'='*80}\n")
        
        return graph
    
    def _get_ready_nodes(
        self, 
        plan: ExecutionPlan, 
        completed: Set[str],
        skipped: Set[str]
    ) -> List[AgentNode]:
        """Get nodes whose dependencies are all completed"""
        ready = []
        for node in plan.nodes:
            # Skip if already processed
            if node.node_id in completed or node.node_id in skipped:
                continue
            
            # Check if all dependencies are met
            deps_met = all(
                dep in completed or dep in skipped 
                for dep in node.depends_on
            )
            
            if deps_met:
                ready.append(node)
        
        return ready
    
    async def _execute_parallel(
        self, 
        nodes: List[AgentNode], 
        break_data: Dict[str, Any]
    ) -> Dict[str, NodeExecution]:
        """Execute multiple nodes in parallel"""
        tasks = []
        for node in nodes:
            task = self._execute_node(node, break_data)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Map results back to nodes
        execution_map = {}
        for node, result in zip(nodes, results):
            if isinstance(result, Exception):
                # Handle exception
                execution = NodeExecution(
                    node_id=node.node_id,
                    agent_name=node.agent_name,
                    status="FAILED",
                    error=str(result),
                    started_at=datetime.now(),
                    completed_at=datetime.now()
                )
            else:
                execution = result
            
            execution_map[node.node_id] = execution
        
        return execution_map
    
    async def _execute_node(
        self, 
        node: AgentNode, 
        break_data: Dict[str, Any]
    ) -> NodeExecution:
        """Execute a single node"""
        start_time = time.time()
        started_at = datetime.now()
        
        try:
            # Get agent
            agent = self.agents.get(node.agent_name.lower())
            if not agent:
                raise ValueError(f"Agent not found: {node.agent_name}")
            
            # Execute agent based on type
            if node.agent_name == 'BREAK_INGESTION':
                result = agent.ingest_break(raw_break=break_data)
            elif node.agent_name == 'DATA_ENRICHMENT':
                result = agent.enrich_break(break_data)
            elif node.agent_name == 'MATCHING_CORRELATION':
                enriched = self.results.get('DATA_ENRICHMENT', {})
                result = agent.find_matches(break_data, enriched.get('enriched_data', {}))
            elif node.agent_name == 'RULES_TOLERANCE':
                enriched = self.results.get('DATA_ENRICHMENT', {})
                result = agent.evaluate_rules(break_data, enriched.get('enriched_data', {}))
            elif node.agent_name == 'PATTERN_INTELLIGENCE':
                rules = self.results.get('RULES_TOLERANCE', {})
                result = agent.analyze_patterns(break_data, rules.get('rules_evaluation', {}))
            elif node.agent_name == 'DECISIONING':
                result = agent.make_decision(
                    break_data,
                    self.results.get('DATA_ENRICHMENT', {}),
                    self.results.get('MATCHING_CORRELATION', {}),
                    self.results.get('RULES_TOLERANCE', {}),
                    self.results.get('PATTERN_INTELLIGENCE', {})
                )
            elif node.agent_name == 'WORKFLOW_FEEDBACK':
                decision = self.results.get('DECISIONING', {})
                result = agent.create_workflow(break_data, decision.get('decision', {}), self.results)
            else:
                raise ValueError(f"Unknown agent type: {node.agent_name}")
            
            duration_ms = (time.time() - start_time) * 1000
            
            return NodeExecution(
                node_id=node.node_id,
                agent_name=node.agent_name,
                status="COMPLETED",
                started_at=started_at,
                completed_at=datetime.now(),
                duration_ms=duration_ms,
                result=result
            )
        
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            return NodeExecution(
                node_id=node.node_id,
                agent_name=node.agent_name,
                status="FAILED",
                started_at=started_at,
                completed_at=datetime.now(),
                duration_ms=duration_ms,
                error=str(e)
            )
    
    def _check_decision_checkpoints(
        self, 
        plan: ExecutionPlan, 
        completed: Set[str],
        results: Dict[str, Any]
    ) -> tuple[bool, Dict[str, Any]]:
        """
        Check if any decision checkpoint is met
        
        Returns:
            (can_exit, decision)
        """
        for checkpoint in plan.decision_checkpoints:
            # Check if required nodes are completed
            required_nodes = [
                node for node in plan.nodes 
                if node.agent_name in checkpoint.after_nodes
            ]
            required_ids = [node.node_id for node in required_nodes]
            
            if not all(node_id in completed for node_id in required_ids):
                continue
            
            # Evaluate checkpoint condition
            can_decide = self._evaluate_checkpoint_condition(
                checkpoint, results
            )
            
            if can_decide:
                # Create decision based on checkpoint action
                decision = {
                    'action': checkpoint.action,
                    'checkpoint_id': checkpoint.checkpoint_id,
                    'condition': checkpoint.condition,
                    'confidence': checkpoint.confidence_threshold,
                    'explanation': f"Checkpoint {checkpoint.checkpoint_id} condition met: {checkpoint.condition}"
                }
                return True, decision
        
        return False, {}
    
    def _evaluate_checkpoint_condition(
        self, 
        checkpoint: DecisionCheckpoint,
        results: Dict[str, Any]
    ) -> bool:
        """Evaluate if checkpoint condition is met"""
        condition = checkpoint.condition
        
        # Simple condition evaluation
        if condition == "always":
            return True
        
        # Check rules tolerance
        if "within_tolerance" in condition:
            rules_result = results.get('RULES_TOLERANCE', {})
            rules_eval = rules_result.get('rules_evaluation', {})
            if rules_eval.get('within_tolerance'):
                # Check confidence if specified
                if "confidence" in condition:
                    ml_insights = results.get('PATTERN_INTELLIGENCE', {}).get('ml_insights', {})
                    confidence = ml_insights.get('confidence', 0)
                    return confidence >= checkpoint.confidence_threshold
                return True
        
        # Check matching
        if "match_found" in condition:
            matching_result = results.get('MATCHING_CORRELATION', {})
            match_candidates = matching_result.get('match_candidates', [])
            if match_candidates:
                # Check if best match is above threshold
                best_match = max(match_candidates, key=lambda x: x.get('similarity_score', 0))
                return best_match.get('similarity_score', 0) >= 0.9
        
        # Check rounding tolerance
        if "within_rounding_tolerance" in condition:
            rules_result = results.get('RULES_TOLERANCE', {})
            rules_eval = rules_result.get('rules_evaluation', {})
            return rules_eval.get('within_tolerance', False)
        
        # Default: condition not met
        return False
    
    def _make_final_decision(
        self, 
        plan: ExecutionPlan,
        results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Make final decision based on all results"""
        # If decisioning agent ran, use its decision
        if 'DECISIONING' in results:
            decision_result = results['DECISIONING']
            return decision_result.get('decision', {})
        
        # Otherwise, make simple decision based on rules
        if 'RULES_TOLERANCE' in results:
            rules_result = results['RULES_TOLERANCE']
            rules_eval = rules_result.get('rules_evaluation', {})
            
            if rules_eval.get('within_tolerance'):
                return {
                    'action': 'AUTO_RESOLVE',
                    'explanation': 'Within tolerance based on rules evaluation',
                    'confidence': 0.95
                }
            else:
                return {
                    'action': 'HIL_REVIEW',
                    'explanation': 'Outside tolerance, requires human review',
                    'confidence': 0.7
                }
        
        # Default: requires review
        return {
            'action': 'HIL_REVIEW',
            'explanation': 'Insufficient information for auto-resolve',
            'confidence': 0.5
        }
